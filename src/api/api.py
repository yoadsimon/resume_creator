#!/usr/bin/env python3
"""FastAPI server for resume generation."""

import os
import shutil
import logging
from typing import Optional, List
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import traceback
import docx2txt
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import PyPDF2
import io
import json
from pydantic import BaseModel, Field

from src.core.accomplishments import get_all_accomplishments, get_personal_details
from src.core.company_summary import get_company_summary
from src.core.job_description import get_job_description
from src.core.industry import extract_job_industry
from src.core.resume_text import generate_resume_text
from src.core.assemble import assemble_new_resume
from src.data.consts import (
    RESUME_TEXT_TEMP_FILE_NAME,
    JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME,
    COMPANY_SUMMARY_TEMP_FILE_NAME,
    FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME,
    JOB_INDUSTRY_TEMP_FILE_NAME,
    GENERATED_RESUME_TEXT,
    PERSONAL_DETAILS_TEMP_FILE_NAME,
)
from src.utils.general_utils import read_temp_file, save_to_temp_file
from src.utils.docx_writer import extract_text_from_docx

# Pydantic models for structured responses
class ExperienceItem(BaseModel):
    title: str = Field(description="Job title or position")
    place: str = Field(description="Company or organization name")
    date: str = Field(description="Date range for the position")
    description: List[str] = Field(description="List of achievements and responsibilities")

class ProjectItem(BaseModel):
    title: str = Field(description="Project name")
    date: str = Field(description="Date range for the project")
    description: List[str] = Field(description="List of project details and achievements")

class EducationItem(BaseModel):
    title: str = Field(description="Degree or certification name")
    place: str = Field(description="Institution name")
    date: str = Field(description="Date range or graduation date")
    description: List[str] = Field(default=[], description="Additional details about education")

class ProfessionalSummaryResponse(BaseModel):
    professional_summary: str = Field(description="Improved professional summary text")

class WorkExperienceResponse(BaseModel):
    work_experience: List[ExperienceItem] = Field(description="List of work experience items")

class PersonalProjectsResponse(BaseModel):
    personal_projects: List[ProjectItem] = Field(description="List of personal project items")

class EducationResponse(BaseModel):
    education: List[EducationItem] = Field(description="List of education items")

class SkillsLanguagesResponse(BaseModel):
    skills: List[str] = Field(description="List of technical and professional skills")
    languages: List[str] = Field(description="List of languages and proficiency levels")

# Add new models for granular editing after the existing response models

class EditSectionNameRequest(BaseModel):
    old_section_name: str = Field(description="Current section name")
    new_section_name: str = Field(description="New section name")

class EditItemRequest(BaseModel):
    section_key: str = Field(description="Section identifier")
    item_index: int = Field(description="Index of item to edit")
    field_name: str = Field(description="Field name to edit (title, place, date, etc.)")
    new_value: str = Field(description="New value for the field")

class EditBulletPointRequest(BaseModel):
    section_key: str = Field(description="Section identifier")
    item_index: int = Field(description="Index of item containing the bullet point")
    bullet_index: int = Field(description="Index of bullet point to edit")
    new_content: str = Field(description="New bullet point content")

class AddRemoveItemRequest(BaseModel):
    section_key: str = Field(description="Section identifier")
    operation: str = Field(description="'add' or 'remove'")
    item_index: Optional[int] = Field(default=None, description="Index for remove operation")
    item_data: Optional[dict] = Field(default=None, description="Data for add operation")

class AddRemoveBulletRequest(BaseModel):
    section_key: str = Field(description="Section identifier")
    item_index: int = Field(description="Index of item to modify")
    operation: str = Field(description="'add' or 'remove'")
    bullet_index: Optional[int] = Field(default=None, description="Index for remove operation")
    bullet_content: Optional[str] = Field(default=None, description="Content for add operation")

class GenericSuccessResponse(BaseModel):
    success: bool = Field(description="Whether operation was successful")
    message: str = Field(description="Success or error message")
    updated_data: Optional[dict] = Field(default=None, description="Updated section data")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}. Using environment variables directly.")

# Verify OpenAI API key is set
api_key = os.getenv("OPEN_AI_TOKEN")
if not api_key:
    raise ValueError("OPEN_AI_TOKEN environment variable is not set")

app = FastAPI(
    title="Resume Creator API",
    description="API for creating tailored resumes using LangChain and OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_url(url: str) -> str:
    """Extract text from a URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

@app.post("/generate_resume")
async def generate_resume(
    resume_file: UploadFile = File(...),
    accomplishments_file: Optional[UploadFile] = File(None),
    job_description_link: str = Form(...),
    company_base_link: str = Form(...),
    company_name: Optional[str] = Form(None),
    use_o1_model: bool = Form(False)
):
    """
    Generate a tailored, professionally formatted resume using the complete pipeline.
    """
    try:
        logger.info("Starting resume generation process")
        
        # Validate inputs
        if not resume_file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Resume file must be in .docx format")
        
        # Create necessary directories
        os.makedirs('temp', exist_ok=True)
        os.makedirs('result', exist_ok=True)
        logger.info("Created necessary directories")
        
        # Save uploaded files and extract text
        resume_file_path = f"temp/{resume_file.filename}"
        
        # Reset file pointer to beginning before reading
        await resume_file.seek(0)
        
        with open(resume_file_path, "wb") as buffer:
            content = await resume_file.read()
            buffer.write(content)
        logger.info(f"Saved resume file to {resume_file_path}")
        
        resume_text = extract_text_from_docx(resume_file_path)
        logger.info(f"Extracted resume text (first 100 chars): {resume_text[:100]}")
        save_to_temp_file(resume_text, RESUME_TEXT_TEMP_FILE_NAME)
        
        # Handle accomplishments file
        accomplishments_text = ""
        if accomplishments_file:
            accomplishments_file_path = f"temp/{accomplishments_file.filename}"
            
            # Reset file pointer to beginning before reading
            await accomplishments_file.seek(0)
            
            # Save the file to disk first
            with open(accomplishments_file_path, "wb") as buffer:
                content = await accomplishments_file.read()
                buffer.write(content)
            
            # Then read it as text
            with open(accomplishments_file_path, 'r', encoding='utf-8') as f:
                accomplishments_text = f.read()
            logger.info(f"Processed accomplishments file (first 100 chars): {accomplishments_text[:100]}")
        
        # Step 1: Generate combined accomplishments
        logger.info("Generating combined accomplishments")
        combined_accomplishments = get_all_accomplishments(
            resume_text, accomplishments_text
        )
        logger.info(f"Generated combined accomplishments (first 100 chars): {combined_accomplishments[:100]}")
        save_to_temp_file(combined_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
        
        # Step 2: Extract job description
        logger.info("Extracting job description")
        job_description = get_job_description(force_run=True, job_description_link=job_description_link)
        
        # Handle case where job description extraction fails
        if job_description is None:
            raise HTTPException(status_code=500, detail="Job description extraction failed for {job_description_link}, using fallback")

        logger.info(f"Extracted job description (first 100 chars): {job_description[:100]}")
        
        # Step 3: Create company summary
        logger.info("Creating company summary")
        company_summary = get_company_summary(
            force_run=True, 
            company_base_link=company_base_link, 
            company_name=company_name
        )
        logger.info(f"Created company summary (first 100 chars): {company_summary[:100]}")
        
        # Step 4: Extract job industry
        logger.info("Extracting job industry")
        job_industry = extract_job_industry(force_run=True)
        logger.info(f"Extracted job industry: {job_industry}")
        
        # Step 5: Generate resume text (JSON format)
        logger.info("Generating resume text")
        generated_resume_json = generate_resume_text(
            use_o1_model=use_o1_model
        )
        logger.info(f"Generated resume JSON (first 100 chars): {generated_resume_json[:100]}")
        
        # Step 6: Extract personal details
        logger.info("Extracting personal details")
        personal_details = get_personal_details(
            force_run=True, 
            resume_file_path=resume_file_path
        )
        logger.info(f"Extracted personal details (first 100 chars): {personal_details[:100]}")
        
        # Step 7: Assemble final formatted resume
        logger.info("Assembling final resume")
        assemble_new_resume(
            generated_resume_text=generated_resume_json,
            personal_info=personal_details,
            use_o1_model=use_o1_model
        )
        
        # Step 8: Save structured data for the viewer
        try:
            from src.core.assemble import read_generated_resume_text_to_dict, read_generated_personal_info_to_dict
            
            # Parse the structured data
            resume_dict = read_generated_resume_text_to_dict(generated_resume_json)
            personal_dict = read_generated_personal_info_to_dict(personal_details)
            
            # Combine and structure the data
            structured_resume = {
                "personal_info": {
                    "name": personal_dict.get("name", ""),
                    "email": personal_dict.get("email", ""),
                    "phone_number": personal_dict.get("phone_number", ""),
                    "address": personal_dict.get("address", ""),
                    "linkedin": personal_dict.get("linkedin", ""),
                    "github": personal_dict.get("github", "")
                },
                "professional_summary": resume_dict.get("professional_summary", ""),
                "work_experience": resume_dict.get("work_experience", []),
                "personal_projects": resume_dict.get("personal_projects", []),
                "education": resume_dict.get("education", []),
                "skills": resume_dict.get("skills", []),
                "languages": resume_dict.get("languages", [])
            }
            
            # Save structured data to a persistent file
            structured_data_file = 'result/resume_structured.json'
            with open(structured_data_file, 'w', encoding='utf-8') as f:
                json.dump(structured_resume, f, indent=2, ensure_ascii=False)
            logger.info("Saved structured resume data for viewer")
            
        except Exception as e:
            logger.warning(f"Could not save structured data: {str(e)}")
        
        logger.info("Successfully generated formatted resume")
        
        # Clean up temporary files
        try:
            shutil.rmtree('temp', ignore_errors=True)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
        
        # Return the properly formatted docx file
        result_file = 'result/resume.docx'
        if not os.path.exists(result_file):
            raise HTTPException(status_code=500, detail="Generated resume file not found")
        
        file_size = os.path.getsize(result_file)
        logger.info(f"Result file size: {file_size} bytes")
        
        if file_size < 1000:  # If file is suspiciously small
            with open(result_file, 'rb') as f:
                content = f.read()
                logger.error(f"Small file content: {content}")
            raise HTTPException(status_code=500, detail="Generated resume file is too small")
        
        return FileResponse(
            path=result_file,
            filename='resume.docx',
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error in resume generation: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error in resume generation: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring systems."""
    return {"status": "healthy", "service": "resume-creator"}

@app.get("/resume/content")
async def get_resume_content():
    """
    Get the content of the most recently generated resume as structured JSON.
    This endpoint returns the resume data in a format suitable for viewing and editing.
    """
    try:
        # Check for persistent structured data file first
        structured_data_file = 'result/resume_structured.json'
        result_file = 'result/resume.docx'
        
        if os.path.exists(structured_data_file):
            # Load structured data from persistent file
            with open(structured_data_file, 'r', encoding='utf-8') as f:
                structured_resume = json.load(f)
            
            return {
                "structured_content": structured_resume,
                "file_path": result_file,
                "file_size": os.path.getsize(result_file) if os.path.exists(result_file) else 0,
                "last_modified": os.path.getmtime(result_file) if os.path.exists(result_file) else 0
            }
        
        # Fallback to raw text if structured data is not available
        if not os.path.exists(result_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        resume_text = extract_text_from_docx(result_file)
        
        return {
            "raw_content": resume_text,
            "file_path": result_file,
            "file_size": os.path.getsize(result_file),
            "last_modified": os.path.getmtime(result_file),
            "note": "Structured data not available, returning raw text"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving resume content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving resume content: {str(e)}")

@app.get("/resume/download")
async def download_resume():
    """
    Download the most recently generated resume file.
    """
    try:
        result_file = 'result/resume.docx'
        if not os.path.exists(result_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        return FileResponse(
            path=result_file,
            filename='tailored_resume.docx',
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading resume: {str(e)}")

@app.post("/resume/edit-section")
async def edit_resume_section(
    section_key: str = Form(...),
    edit_prompt: str = Form(...),
    use_o1_model: bool = Form(False)
):
    """
    Edit a specific section of the resume using AI.
    """
    try:
        # Check if structured data exists
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Get the section to edit
        section_data = None
        if section_key == "professional_summary":
            section_data = resume_data.get("professional_summary", "")
        elif section_key == "work_experience":
            section_data = resume_data.get("work_experience", [])
        elif section_key == "personal_projects":
            section_data = resume_data.get("personal_projects", [])
        elif section_key == "education":
            section_data = resume_data.get("education", [])
        elif section_key == "skills_languages":
            section_data = {
                "skills": resume_data.get("skills", []),
                "languages": resume_data.get("languages", [])
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown section: {section_key}")
        
        # Use AI to edit the section with structured output
        from src.utils.langchain_utils import LangChainClient
        from langchain.schema import HumanMessage
        
        model_name = "o1-mini" if use_o1_model else "gpt-4o-mini"
        langchain_client = LangChainClient(model_name=model_name)
        
        # Determine the response model based on section type
        response_model = None
        if section_key == "professional_summary":
            response_model = ProfessionalSummaryResponse
        elif section_key == "work_experience":
            response_model = WorkExperienceResponse
        elif section_key == "personal_projects":
            response_model = PersonalProjectsResponse
        elif section_key == "education":
            response_model = EducationResponse
        elif section_key == "skills_languages":
            response_model = SkillsLanguagesResponse
        else:
            raise HTTPException(status_code=400, detail=f"Unknown section: {section_key}")
        
        # Create structured LLM
        structured_llm = langchain_client.llm.with_structured_output(response_model)
        
        # Create prompt for editing
        system_prompt = f"""You are an expert resume writer. You need to improve the following resume section based on the user's request.

Section: {section_key}
Current content: {json.dumps(section_data, indent=2)}

User's editing request: {edit_prompt}

Instructions:
1. Only modify the content according to the user's request
2. Maintain the same structure and format
3. Keep the professional tone and accuracy
4. Ensure all content is truthful and relevant
5. Return the improved section in the specified format

Improve the section based on the user's request and return it in the proper structured format."""

        # Get AI response with structured output
        try:
            response = structured_llm.invoke([HumanMessage(content=system_prompt)])
            
            # Update the resume data based on the structured response
            if section_key == "professional_summary":
                resume_data["professional_summary"] = response.professional_summary
            elif section_key == "work_experience":
                resume_data["work_experience"] = [item.dict() for item in response.work_experience]
            elif section_key == "personal_projects":
                resume_data["personal_projects"] = [item.dict() for item in response.personal_projects]
            elif section_key == "education":
                resume_data["education"] = [item.dict() for item in response.education]
            elif section_key == "skills_languages":
                resume_data["skills"] = response.skills
                resume_data["languages"] = response.languages
            
            # Save updated structured data
            with open(structured_data_file, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
            
            # Optionally regenerate the Word document
            try:
                from src.core.assemble import get_resume_details, assemble_new_resume
                
                # Create a simplified personal info and resume text for regeneration
                personal_info_json = json.dumps(resume_data["personal_info"])
                resume_text_json = json.dumps({
                    "professional_summary": resume_data["professional_summary"],
                    "work_experience": resume_data["work_experience"], 
                    "personal_projects": resume_data["personal_projects"],
                    "education": resume_data["education"],
                    "skills": resume_data["skills"],
                    "languages": resume_data["languages"]
                })
                
                # Regenerate the Word document
                assemble_new_resume(
                    generated_resume_text=resume_text_json,
                    personal_info=personal_info_json,
                    use_o1_model=use_o1_model
                )
                logger.info("Regenerated Word document with updated content")
                
            except Exception as e:
                logger.warning(f"Could not regenerate Word document: {str(e)}")
            
            return {
                "success": True,
                "message": f"Successfully updated {section_key}",
                "updated_section": resume_data.get(section_key) if section_key != "skills_languages" else {
                    "skills": resume_data.get("skills", []),
                    "languages": resume_data.get("languages", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get structured response: {str(e)}")
            logger.error(f"Response type: {type(response) if 'response' in locals() else 'No response'}")
            raise HTTPException(status_code=500, detail=f"AI editing failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error editing resume section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error editing resume section: {str(e)}")

# Add granular editing endpoints before the existing edit-section endpoint

@app.post("/resume/edit-item-field", response_model=GenericSuccessResponse)
async def edit_item_field(request: EditItemRequest):
    """
    Edit a specific field of an item in a resume section.
    """
    try:
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Handle professional_summary as a special case (it's a string, not a list)
        if request.section_key == 'professional_summary':
            if request.field_name == 'content':
                resume_data['professional_summary'] = request.new_value
                
                # Save updated data
                with open(structured_data_file, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, indent=2, ensure_ascii=False)
                
                # Optionally regenerate Word document
                _regenerate_word_document(resume_data)
                
                return GenericSuccessResponse(
                    success=True,
                    message="Successfully updated professional summary",
                    updated_data={"professional_summary": request.new_value}
                )
            else:
                raise HTTPException(status_code=400, detail="Professional summary only supports 'content' field")
        
        # Get the section data for other sections
        section_data = resume_data.get(request.section_key, [])
        if not isinstance(section_data, list):
            raise HTTPException(status_code=400, detail=f"Section {request.section_key} is not a list type")
        
        if request.item_index < 0 or request.item_index >= len(section_data):
            raise HTTPException(status_code=400, detail="Item index out of range")
        
        # Update the specific field
        if request.field_name not in section_data[request.item_index]:
            raise HTTPException(status_code=400, detail=f"Field '{request.field_name}' not found in item")
        
        section_data[request.item_index][request.field_name] = request.new_value
        
        # Save updated data
        with open(structured_data_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        # Optionally regenerate Word document
        _regenerate_word_document(resume_data)
        
        return GenericSuccessResponse(
            success=True,
            message=f"Successfully updated {request.field_name} in {request.section_key}",
            updated_data=section_data[request.item_index]
        )
        
    except Exception as e:
        logger.error(f"Error editing item field: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error editing item field: {str(e)}")

@app.post("/resume/edit-bullet-point", response_model=GenericSuccessResponse)
async def edit_bullet_point(request: EditBulletPointRequest):
    """
    Edit a specific bullet point in a resume item.
    """
    try:
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Get the section data
        section_data = resume_data.get(request.section_key, [])
        if not isinstance(section_data, list):
            raise HTTPException(status_code=400, detail=f"Section {request.section_key} is not a list type")
        
        if request.item_index < 0 or request.item_index >= len(section_data):
            raise HTTPException(status_code=400, detail="Item index out of range")
        
        # Get description array
        description = section_data[request.item_index].get('description', [])
        if not isinstance(description, list):
            raise HTTPException(status_code=400, detail="Item description is not a list")
        
        if request.bullet_index < 0 or request.bullet_index >= len(description):
            raise HTTPException(status_code=400, detail="Bullet point index out of range")
        
        # Update the bullet point
        description[request.bullet_index] = request.new_content
        
        # Save updated data
        with open(structured_data_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        # Optionally regenerate Word document
        _regenerate_word_document(resume_data)
        
        return GenericSuccessResponse(
            success=True,
            message=f"Successfully updated bullet point in {request.section_key}",
            updated_data=section_data[request.item_index]
        )
        
    except Exception as e:
        logger.error(f"Error editing bullet point: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error editing bullet point: {str(e)}")

@app.post("/resume/manage-item", response_model=GenericSuccessResponse)
async def manage_item(request: AddRemoveItemRequest):
    """
    Add or remove an entire item from a resume section.
    """
    try:
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Get the section data
        section_data = resume_data.get(request.section_key, [])
        if not isinstance(section_data, list):
            raise HTTPException(status_code=400, detail=f"Section {request.section_key} is not a list type")
        
        if request.operation == "add":
            if not request.item_data:
                raise HTTPException(status_code=400, detail="Item data is required for add operation")
            section_data.append(request.item_data)
            message = f"Successfully added item to {request.section_key}"
            
        elif request.operation == "remove":
            if request.item_index is None:
                raise HTTPException(status_code=400, detail="Item index is required for remove operation")
            if request.item_index < 0 or request.item_index >= len(section_data):
                raise HTTPException(status_code=400, detail="Item index out of range")
            removed_item = section_data.pop(request.item_index)
            message = f"Successfully removed item from {request.section_key}"
            
        else:
            raise HTTPException(status_code=400, detail="Operation must be 'add' or 'remove'")
        
        # Save updated data
        with open(structured_data_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        # Optionally regenerate Word document
        _regenerate_word_document(resume_data)
        
        return GenericSuccessResponse(
            success=True,
            message=message,
            updated_data=section_data
        )
        
    except Exception as e:
        logger.error(f"Error managing item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error managing item: {str(e)}")

@app.post("/resume/manage-bullet", response_model=GenericSuccessResponse)
async def manage_bullet_point(request: AddRemoveBulletRequest):
    """
    Add or remove a bullet point from a resume item.
    """
    try:
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Get the section data
        section_data = resume_data.get(request.section_key, [])
        if not isinstance(section_data, list):
            raise HTTPException(status_code=400, detail=f"Section {request.section_key} is not a list type")
        
        if request.item_index < 0 or request.item_index >= len(section_data):
            raise HTTPException(status_code=400, detail="Item index out of range")
        
        # Get description array
        description = section_data[request.item_index].get('description', [])
        if not isinstance(description, list):
            section_data[request.item_index]['description'] = []
            description = section_data[request.item_index]['description']
        
        if request.operation == "add":
            if not request.bullet_content:
                raise HTTPException(status_code=400, detail="Bullet content is required for add operation")
            description.append(request.bullet_content)
            message = f"Successfully added bullet point to {request.section_key}"
            
        elif request.operation == "remove":
            if request.bullet_index is None:
                raise HTTPException(status_code=400, detail="Bullet index is required for remove operation")
            if request.bullet_index < 0 or request.bullet_index >= len(description):
                raise HTTPException(status_code=400, detail="Bullet point index out of range")
            removed_bullet = description.pop(request.bullet_index)
            message = f"Successfully removed bullet point from {request.section_key}"
            
        else:
            raise HTTPException(status_code=400, detail="Operation must be 'add' or 'remove'")
        
        # Save updated data
        with open(structured_data_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        # Optionally regenerate Word document
        _regenerate_word_document(resume_data)
        
        return GenericSuccessResponse(
            success=True,
            message=message,
            updated_data=section_data[request.item_index]
        )
        
    except Exception as e:
        logger.error(f"Error managing bullet point: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error managing bullet point: {str(e)}")

@app.post("/resume/edit-bullet-with-ai", response_model=GenericSuccessResponse)
async def edit_bullet_with_ai(request: EditBulletPointRequest):
    """
    Edit a specific bullet point using AI enhancement.
    """
    try:
        structured_data_file = 'result/resume_structured.json'
        if not os.path.exists(structured_data_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Load current structured data
        with open(structured_data_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        # Get the section data
        section_data = resume_data.get(request.section_key, [])
        if not isinstance(section_data, list):
            raise HTTPException(status_code=400, detail=f"Section {request.section_key} is not a list type")
        
        if request.item_index < 0 or request.item_index >= len(section_data):
            raise HTTPException(status_code=400, detail="Item index out of range")
        
        # Get description array
        description = section_data[request.item_index].get('description', [])
        if not isinstance(description, list):
            raise HTTPException(status_code=400, detail="Item description is not a list")
        
        if request.bullet_index < 0 or request.bullet_index >= len(description):
            raise HTTPException(status_code=400, detail="Bullet point index out of range")
        
        # Get the current bullet point content
        current_bullet = description[request.bullet_index]
        
        # Use AI to enhance the bullet point
        from src.utils.langchain_utils import LangChainClient
        from langchain.schema import HumanMessage
        
        langchain_client = LangChainClient(model_name="gpt-4o-mini")
        
        # Create specific prompt for bullet point enhancement
        ai_prompt = f"""You are an expert resume writer. Improve the following bullet point to make it more impactful, quantified, and professional.

Current bullet point: {current_bullet}

User enhancement request: {request.new_content}

Guidelines:
1. Keep the content truthful and accurate
2. Add quantified metrics where possible (percentages, numbers, time frames)
3. Use strong action verbs
4. Make it more specific and impactful
5. Maintain professional tone
6. Return ONLY the improved bullet point, nothing else

Improved bullet point:"""

        try:
            response = langchain_client.llm.invoke([HumanMessage(content=ai_prompt)])
            improved_bullet = response.content.strip()
            
            # Remove any quotes or extra formatting
            improved_bullet = improved_bullet.strip('"').strip("'").strip()
            
            # Update the bullet point with AI-improved content
            description[request.bullet_index] = improved_bullet
            
            # Save updated data
            with open(structured_data_file, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
            
            # Optionally regenerate Word document
            _regenerate_word_document(resume_data)
            
            return GenericSuccessResponse(
                success=True,
                message=f"Successfully enhanced bullet point with AI in {request.section_key}",
                updated_data=section_data[request.item_index]
            )
            
        except Exception as e:
            logger.error(f"Failed to get AI enhancement: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI enhancement failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error enhancing bullet point with AI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enhancing bullet point with AI: {str(e)}")

def _regenerate_word_document(resume_data: dict, use_o1_model: bool = False):
    """
    Helper function to regenerate the Word document after edits.
    """
    try:
        from src.core.assemble import assemble_new_resume
        
        # Create simplified data for regeneration
        personal_info_json = json.dumps(resume_data["personal_info"])
        resume_text_json = json.dumps({
            "professional_summary": resume_data["professional_summary"],
            "work_experience": resume_data["work_experience"], 
            "personal_projects": resume_data["personal_projects"],
            "education": resume_data["education"],
            "skills": resume_data["skills"],
            "languages": resume_data["languages"]
        })
        
        # Regenerate the Word document
        assemble_new_resume(
            generated_resume_text=resume_text_json,
            personal_info=personal_info_json,
            use_o1_model=use_o1_model
        )
        logger.info("Regenerated Word document with updated content")
        
    except Exception as e:
        logger.warning(f"Could not regenerate Word document: {str(e)}")

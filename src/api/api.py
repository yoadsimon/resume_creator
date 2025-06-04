#!/usr/bin/env python3
"""FastAPI server for resume generation."""

import os
import shutil
import logging
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import traceback
from typing import List
import docx2txt
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import PyPDF2
import io

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
)
from src.utils.general_utils import read_temp_file, save_to_temp_file
from src.utils.docx_writer import extract_text_from_docx

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
    Get the content of the most recently generated resume as JSON.
    This endpoint will be used for viewing and future editing functionality.
    """
    try:
        result_file = 'result/resume.docx'
        if not os.path.exists(result_file):
            raise HTTPException(status_code=404, detail="No resume found. Please generate a resume first.")
        
        # Extract text content from the docx file
        resume_text = extract_text_from_docx(result_file)
        
        # For now, return the raw text. In the future, this could be enhanced
        # to return structured JSON with sections, formatting, etc.
        return {
            "content": resume_text,
            "file_path": result_file,
            "file_size": os.path.getsize(result_file),
            "last_modified": os.path.getmtime(result_file)
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

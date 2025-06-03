from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import traceback
import logging
from typing import Optional, List
import docx2txt
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import asyncio
import PyPDF2
import io

# Import the proper resume generation functions
from _5_generate_resume_text import generate_resume_text
from _6_assemble_new_resume import assemble_new_resume
from _1_get_accomplishments_and_personal_details import generate_combined_accomplishments, get_personal_details
from _2_create_company_summary import create_company_summary
from _3_extract_job_description_text import extract_job_description_text
from _4_extract_job_industry import extract_job_industry
from utils.general_utils import save_to_temp_file
from inputs.consts import RESUME_TEXT_TEMP_FILE_NAME, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    return docx2txt.process(file_path)

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
        with open(resume_file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
        logger.info(f"Saved resume file to {resume_file_path}")
        
        resume_text = extract_text_from_docx(resume_file_path)
        save_to_temp_file(resume_text, RESUME_TEXT_TEMP_FILE_NAME)
        
        # Handle accomplishments file
        accomplishments_text = ""
        if accomplishments_file:
            accomplishments_file_path = f"temp/{accomplishments_file.filename}"
            with open(accomplishments_file_path, "wb") as buffer:
                shutil.copyfileobj(accomplishments_file.file, buffer)
            with open(accomplishments_file_path, 'r') as f:
                accomplishments_text = f.read()
            logger.info("Processed accomplishments file")
        
        # Step 1: Generate combined accomplishments
        logger.info("Generating combined accomplishments")
        combined_accomplishments = generate_combined_accomplishments(
            resume_text, accomplishments_text, use_langchain=True
        )
        save_to_temp_file(combined_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
        
        # Step 2: Extract job description
        logger.info("Extracting job description")
        extract_job_description_text(force_run=True, job_description_link=job_description_link)
        
        # Step 3: Create company summary
        logger.info("Creating company summary")
        create_company_summary(
            force_run=True, 
            company_base_link=company_base_link, 
            company_name=company_name
        )
        
        # Step 4: Extract job industry
        logger.info("Extracting job industry")
        extract_job_industry(force_run=True)
        
        # Step 5: Generate resume text (JSON format)
        logger.info("Generating resume text")
        generated_resume_json = generate_resume_text(
            use_o1_model=use_o1_model
        )
        
        # Step 6: Extract personal details
        logger.info("Extracting personal details")
        personal_details = get_personal_details(
            force_run=True, 
            resume_file_path=resume_file_path, 
            use_langchain=True
        )
        
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

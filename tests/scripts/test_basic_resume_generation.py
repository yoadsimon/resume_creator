#!/usr/bin/env python3
"""Basic tests for resume generation."""

import os
import sys
import logging
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from run_all import create_resume_for_job_application
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_basic_resume_generation():
    """
    Test the basic resume generation functionality without using LangChain features.
    """
    logging.info("Testing basic resume generation...")
    
    # Ensure the sample files exist
    resume_path = 'tests/data/sample_resume.docx'
    accomplishments_path = 'tests/data/sample_accomplishments.txt'
    
    if not os.path.exists(resume_path) or not os.path.exists(accomplishments_path):
        logging.error("Sample files not found. Please run generate_test_files.py first.")
        return False
    
    # Sample job description and company links
    job_description_link = "https://example.com/job"
    company_base_link = "https://example.com"
    
    try:
        # Run the resume generation
        create_resume_for_job_application(
            resume_file_path=resume_path,
            accomplishments_file_path=accomplishments_path,
            job_description_link=job_description_link,
            company_base_link=company_base_link,
            force_run_all=True,
            use_o1_model=False
        )
        
        # Check if the result file was created
        result_file = 'result/resume.docx'
        if os.path.exists(result_file):
            logging.info("Basic resume generation test passed! Resume created at: %s", result_file)
            return True
        else:
            logging.error("Resume file not created.")
            return False
            
    except Exception as e:
        logging.error("Error during basic resume generation: %s", str(e))
        return False

if __name__ == "__main__":
    # First make sure we have the sample files
    if not os.path.exists('tests/data/sample_resume.docx'):
        logging.info("Sample files not found. Running generate_test_files.py...")
        try:
            from generate_test_files import generate_all_sample_files
            generate_all_sample_files()
        except Exception as e:
            logging.error("Failed to generate sample files: %s", str(e))
            sys.exit(1)
    
    # Run the test
    success = test_basic_resume_generation()
    
    if success:
        logging.info("All tests passed!")
        sys.exit(0)
    else:
        logging.error("Tests failed!")
        sys.exit(1)
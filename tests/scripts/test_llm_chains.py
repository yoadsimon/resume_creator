#!/usr/bin/env python3
"""Tests for LLM chains."""

import os
import sys
import logging
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.langchain_utils import (
    LangChainClient,
    create_resume_generation_chain,
    create_accomplishments_extraction_chain,
    create_combined_accomplishments_chain,
    create_personal_details_extraction_chain
)
from src.utils.open_ai import OpenAIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_llm_chains():
    """
    Test the LLM chains functionality using LangChain.
    This tests the various chains used in the resume generation process.
    """
    logging.info("Testing LLM chains functionality...")
    
    # Ensure the sample files exist
    accomplishments_path = 'tests/data/sample_accomplishments.txt'
    
    if not os.path.exists(accomplishments_path):
        logging.error("Sample accomplishments file not found. Please run generate_test_files.py first.")
        return False
    
    try:
        # Read the accomplishments file
        with open(accomplishments_path, 'r') as f:
            accomplishments = f.read()
        
        # Create a LangChain client
        client = LangChainClient()
        
        # Test 1: Accomplishments Extraction Chain
        logging.info("\nTesting Accomplishments Extraction Chain:")
        
        # Sample resume text
        resume_text = """
        John Doe
        Software Engineer
        
        Experience:
        - Senior Software Engineer at ABC Tech (2020-Present)
          * Developed cloud applications using Python and AWS
          * Led a team of 5 engineers
        
        - Software Engineer at XYZ Solutions (2017-2020)
          * Built RESTful APIs using Django and Flask
          * Optimized database queries
        
        Education:
        - Bachelor of Science in Computer Science, University of Technology (2013-2017)
        """
        
        # Create and run the accomplishments extraction chain
        accomplishments_chain = create_accomplishments_extraction_chain(client)
        result = accomplishments_chain({"resume_text": resume_text})
        
        # Check if we got a result
        if "accomplishments" not in result or not result["accomplishments"]:
            logging.error("No accomplishments extracted")
            return False
        
        logging.info(f"Extracted accomplishments: {result['accomplishments'][:200]}...")
        
        # Test 2: Personal Details Extraction Chain
        logging.info("\nTesting Personal Details Extraction Chain:")
        
        # Create and run the personal details extraction chain
        details_chain = create_personal_details_extraction_chain(client)
        result = details_chain({"resume_text": resume_text})
        
        # Check if we got a result
        if "personal_details" not in result or not result["personal_details"]:
            logging.error("No personal details extracted")
            return False
        
        logging.info(f"Extracted personal details: {result['personal_details']}")
        
        # Test 3: Resume Generation Chain
        logging.info("\nTesting Resume Generation Chain:")
        
        # Sample data for resume generation
        job_description = "We are looking for a software engineer with experience in Python, cloud technologies, and machine learning."
        company_summary = "ABC Tech is a leading technology company specializing in cloud solutions and machine learning applications."
        job_industry = "Technology"
        
        # Create and run the resume generation chain
        resume_chain = create_resume_generation_chain(client)
        result = resume_chain({
            "job_description": job_description,
            "company_summary": company_summary,
            "accomplishments": accomplishments,
            "job_industry": job_industry
        })
        
        # Check if we got a result
        if "resume" not in result or not result["resume"]:
            logging.error("No resume generated")
            return False
        
        logging.info(f"Generated resume: {result['resume'][:200]}...")
        
        logging.info("\nLLM chains test completed successfully!")
        return True
            
    except Exception as e:
        logging.error("Error during LLM chains test: %s", str(e))
        return False

if __name__ == "__main__":
    # First make sure we have the sample files
    if not os.path.exists('tests/data/sample_accomplishments.txt'):
        logging.info("Sample files not found. Running generate_test_files.py...")
        try:
            from generate_test_files import generate_sample_accomplishments
            generate_sample_accomplishments()
        except Exception as e:
            logging.error("Failed to generate sample files: %s", str(e))
            sys.exit(1)
    
    # Run the test
    success = test_llm_chains()
    
    if success:
        logging.info("All tests passed!")
        sys.exit(0)
    else:
        logging.error("Tests failed!")
        sys.exit(1)
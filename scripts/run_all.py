#!/usr/bin/env python3
"""Main script to run the complete resume generation pipeline."""

import os
import argparse
from typing import Optional
import logging

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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_resume_for_job_application(
        resume_file_path: str,
        accomplishments_file_path: str,
        job_description_link: str,
        company_base_link: str,
        company_name: str = None,
        force_run_all: bool = False,
        use_o1_model: bool = False
) -> None:
    """Create a tailored resume for a job application.

    Args:
        resume_file_path: Path to the resume file
        accomplishments_file_path: Path to the accomplishments file
        job_description_link: Link to the job description
        company_base_link: Base link of the company website
        company_name: Name of the company (optional)
        force_run_all: Whether to force run all steps
        use_o1_model: Whether to use the o1 model
    """
    logging.info("Starting resume creation process")

    # Get accomplishments and personal details
    all_accomplishments = get_all_accomplishments(
        resume_file_path=resume_file_path,
        accomplishments_file_path=accomplishments_file_path,
        force_run=force_run_all
    )
    personal_details = get_personal_details(
        force_run=force_run_all,
        resume_file_path=resume_file_path
    )

    # Get company and job information
    company_summary = get_company_summary(
        company_base_link=company_base_link,
        company_name=company_name,
        force_run=force_run_all
    )
    job_description_text = get_job_description(
        job_description_link=job_description_link,
        force_run=force_run_all
    )
    job_industry = extract_job_industry(
        force_run=force_run_all,
        job_description=job_description_text,
        company_summary=company_summary
    )

    # Generate and assemble resume
    resume_text = generate_resume_text(
        accomplishments=all_accomplishments,
        company_summary=company_summary,
        job_description=job_description_text,
        job_industry=job_industry,
        use_o1_model=use_o1_model
    )
    assemble_new_resume(
        generated_resume_text=resume_text,
        personal_info=personal_details,
        use_o1_model=use_o1_model
    )

    logging.info("Resume creation process completed")


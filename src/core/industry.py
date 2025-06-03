#!/usr/bin/env python3
"""Module for extracting job industry from job description."""

from typing import Optional

from src.data.consts import (
    JOB_INDUSTRY_TEMP_FILE_NAME,
    JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME,
    COMPANY_SUMMARY_TEMP_FILE_NAME
)
from src.utils.general_utils import read_temp_file, save_to_temp_file
from src.utils.langchain_utils import LangChainClient, create_industry_extraction_chain

def extract_job_industry(
    force_run: bool = False,
    job_description: Optional[str] = None,
    company_summary: Optional[str] = None
) -> str:
    """Extract the primary industry from job description and company summary.
    
    Args:
        force_run: Whether to force extraction even if cached
        job_description: Job description text (uses cached if None)
        company_summary: Company summary text (uses cached if None)
        
    Returns:
        Extracted industry name
    """
    job_industry = read_temp_file(JOB_INDUSTRY_TEMP_FILE_NAME)
    if job_industry and not force_run:
        return job_industry

    if not job_description:
        job_description = read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    if not company_summary:
        company_summary = read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)

    # Create and run the industry extraction chain
    client = LangChainClient()
    chain = create_industry_extraction_chain(client)
    result = chain({
        "job_description": job_description,
        "company_summary": company_summary
    })
    
    job_industry = result["industry"].strip()
    save_to_temp_file(job_industry, JOB_INDUSTRY_TEMP_FILE_NAME)
    return job_industry

#
# if __name__ == "__main__":
#     extract_job_industry()

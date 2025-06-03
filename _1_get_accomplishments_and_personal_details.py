#!/usr/bin/env python3
"""Module for extracting accomplishments and personal details from resume."""

import docx2txt
from typing import Optional

from inputs.consts import (
    RESUME_TEXT_TEMP_FILE_NAME,
    DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
    FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME,
    SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
    PERSONAL_DETAILS_TEMP_FILE_NAME,
)
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient
from utils.langchain_utils import (
    LangChainClient, 
    create_accomplishments_extraction_chain,
    create_combined_accomplishments_chain,
    create_personal_details_extraction_chain
)

def extract_text_from_resume_docx(docx_file_path: Optional[str] = None, force_run: bool = False) -> str:
    """Extract text from a resume docx file.

    Args:
        docx_file_path: Path to the docx file (uses default if None)
        force_run: Whether to force extraction even if cached

    Returns:
        Extracted text from the resume
    """
    text = read_temp_file(RESUME_TEXT_TEMP_FILE_NAME)
    if text and not force_run:
        return text

    text = docx2txt.process(docx_file_path)
    save_to_temp_file(text, RESUME_TEXT_TEMP_FILE_NAME)
    return text

def generate_combined_accomplishments(resume_text: str, existing_accomplishments: Optional[str]) -> str:
    """Generate combined accomplishments from resume text and existing accomplishments.

    Args:
        resume_text: Text extracted from resume
        existing_accomplishments: Previously documented accomplishments (optional)

    Returns:
        Combined and formatted accomplishments
    """
        langchain_client = LangChainClient()
    chain = (create_combined_accomplishments_chain(langchain_client) if existing_accomplishments else create_accomplishments_extraction_chain(langchain_client))
    result = chain({ "existing_accomplishments": (existing_accomplishments or ""), "resume_text": resume_text })
    return (result["combined_accomplishments"] if existing_accomplishments else result["accomplishments"]).strip()

def get_all_accomplishments(force_run: bool = False, accomplishments_file_path: Optional[str] = None, resume_file_path: Optional[str] = None) -> str:
    """Get all accomplishments from resume and accomplishments file.

    Args:
        force_run: Whether to force extraction even if cached
        accomplishments_file_path: Path to accomplishments file (optional)
        resume_file_path: Path to resume file (optional)

    Returns:
        Combined accomplishments from all sources
    """
    updated_accomplishments = read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    if updated_accomplishments and not force_run:
        return updated_accomplishments
    resume_text = extract_text_from_resume_docx(docx_file_path=resume_file_path, force_run=force_run)
    existing_accomplishments = read_temp_file(accomplishments_file_path)
    updated_accomplishments = generate_combined_accomplishments(resume_text, existing_accomplishments)
    save_to_temp_file(updated_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    return updated_accomplishments

def get_personal_details(force_run: bool = False, resume_file_path: Optional[str] = None) -> str:
    """Get personal details from resume.

    Args:
        force_run: Whether to force extraction even if cached
        resume_file_path: Path to resume file (optional)

    Returns:
        Personal details in JSON format
    """
    personal_details = read_temp_file(PERSONAL_DETAILS_TEMP_FILE_NAME)
    if personal_details and not force_run:
        return personal_details
    resume_text = extract_text_from_resume_docx(docx_file_path=resume_file_path, force_run=force_run)
        langchain_client = LangChainClient()
        chain = create_personal_details_extraction_chain(langchain_client)
    result = chain({ "resume_text": resume_text })
        personal_details = result["personal_details"].strip()
    save_to_temp_file(personal_details, PERSONAL_DETAILS_TEMP_FILE_NAME)
    return personal_details
# if __name__ == "__main__":
#     get_all_accomplishments()


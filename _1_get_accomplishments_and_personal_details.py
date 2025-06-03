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

def generate_combined_accomplishments(
    resume_text: str,
    existing_accomplishments: Optional[str],
    use_langchain: bool = True
) -> str:
    """Generate combined accomplishments from resume text and existing accomplishments.
    
    Args:
        resume_text: Text extracted from resume
        existing_accomplishments: Previously documented accomplishments
        use_langchain: Whether to use LangChain for generation
        
    Returns:
        Combined and formatted accomplishments
    """
    if use_langchain:
        langchain_client = LangChainClient()
        chain = (
            create_combined_accomplishments_chain(langchain_client)
            if existing_accomplishments
            else create_accomplishments_extraction_chain(langchain_client)
        )
        result = chain({
            "existing_accomplishments": existing_accomplishments or "",
            "resume_text": resume_text
        })
        return result["combined_accomplishments" if existing_accomplishments else "accomplishments"].strip()

    openai_client = OpenAIClient()
    prompt = (
        DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT.format(
            existing_accomplishments=existing_accomplishments,
            resume_text=resume_text
        ) if existing_accomplishments else
        SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT.format(
            resume_text=resume_text
        )
    )
    return openai_client.generate_text(prompt).strip()

def get_all_accomplishments(
    force_run: bool = False,
    accomplishments_file_path: Optional[str] = None,
    resume_file_path: Optional[str] = None,
    use_langchain: bool = True
) -> str:
    """Get all accomplishments from resume and accomplishments file.
    
    Args:
        force_run: Whether to force extraction even if cached
        accomplishments_file_path: Path to accomplishments file
        resume_file_path: Path to resume file
        use_langchain: Whether to use LangChain for generation
        
    Returns:
        Combined accomplishments from all sources
    """
    updated_accomplishments = read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    if updated_accomplishments and not force_run:
        return updated_accomplishments

    resume_text = extract_text_from_resume_docx(
        docx_file_path=resume_file_path,
        force_run=force_run
    )
    existing_accomplishments = read_temp_file(accomplishments_file_path)

    updated_accomplishments = generate_combined_accomplishments(
        resume_text,
        existing_accomplishments,
        use_langchain=use_langchain
    )
    save_to_temp_file(updated_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    return updated_accomplishments

def get_personal_details(
    force_run: bool = False,
    resume_file_path: Optional[str] = None,
    use_langchain: bool = True
) -> str:
    """Get personal details from resume.
    
    Args:
        force_run: Whether to force extraction even if cached
        resume_file_path: Path to resume file
        use_langchain: Whether to use LangChain for extraction
        
    Returns:
        Personal details in JSON format
    """
    personal_details = read_temp_file(PERSONAL_DETAILS_TEMP_FILE_NAME)
    if personal_details and not force_run:
        return personal_details

    resume_text = extract_text_from_resume_docx(
        docx_file_path=resume_file_path,
        force_run=force_run
    )

    if use_langchain:
        langchain_client = LangChainClient()
        chain = create_personal_details_extraction_chain(langchain_client)
        result = chain({"resume_text": resume_text})
        personal_details = result["personal_details"].strip()
    else:
        openai_client = OpenAIClient()
        prompt = f"""
        Extract and return ONLY the personal details mentioned in the following text in the JSON format with keys: name, phone_number, linkedin, github, email, and address:

        {resume_text}
        """
        personal_details = openai_client.generate_text(prompt).strip()

    save_to_temp_file(personal_details, PERSONAL_DETAILS_TEMP_FILE_NAME)
    return personal_details
# if __name__ == "__main__":
#     get_all_accomplishments()


#!/usr/bin/env python3
"""Module for assembling the final resume."""

import json
import re
from typing import Optional, Dict, Any

from src.data.consts import (
    RESUME_TEXT_TEMP_FILE_NAME,
    PERSONAL_DETAILS_TEMP_FILE_NAME,
    GENERATED_RESUME_TEXT,
)
from src.utils.general_utils import read_temp_file, save_to_temp_file
from src.utils.resume_details import ResumeDetails
from src.utils.docx_writer import write_resume_to_docx
from src.core.resume_text import generate_resume_text

def read_generated_resume_text_to_dict(
    generated_resume_text: Optional[str] = None,
    max_retries: int = 3,
    use_o1_model: bool = False
) -> Dict[str, Any]:
    """Convert generated resume text to a dictionary with normalized keys.
    
    Args:
        generated_resume_text: JSON-formatted resume text (uses cached if None)
        max_retries: Number of retries if JSON parsing fails
        use_o1_model: Whether to use o1 model for regeneration
        
    Returns:
        Dictionary with normalized keys (lowercase, underscores)
        
    Raises:
        ValueError: If no valid JSON content is found after retries
    """
    if generated_resume_text is None:
        generated_resume_text = read_temp_file(GENERATED_RESUME_TEXT)

    json_match = re.search(r'\{.*\}', generated_resume_text, re.DOTALL)
    if json_match:
        json_content = json_match.group(0)
        resume_dict = json.loads(json_content)
        return {key.lower().replace(" ", "_"): value for key, value in resume_dict.items()}

    if max_retries > 0:
        return read_generated_resume_text_to_dict(
            generate_resume_text(use_o1_model=use_o1_model),
            max_retries - 1,
            use_o1_model
        )

    raise ValueError("No JSON content found in the generated resume text")

def read_generated_personal_info_to_dict(personal_info: Optional[str] = None) -> Dict[str, Any]:
    """Convert personal info text to a dictionary with normalized keys.
    
    Args:
        personal_info: JSON-formatted personal info (uses cached if None)
        
    Returns:
        Dictionary with normalized keys (lowercase, underscores)
        
    Raises:
        ValueError: If no valid JSON content is found
    """
    if personal_info is None:
        personal_info = read_temp_file(PERSONAL_DETAILS_TEMP_FILE_NAME)

    json_match = re.search(r'\{.*\}', personal_info, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON content found in the personal info text")
        
    json_content = json_match.group(0)
    personal_info = json.loads(json_content)
    return {key.lower().replace(" ", "_"): value for key, value in personal_info.items()}

def get_resume_details(
    generated_resume_text: Optional[str] = None,
    personal_info: Optional[str] = None,
    use_o1_model: bool = False
) -> ResumeDetails:
    """Create ResumeDetails object from generated text and personal info.
    
    Args:
        generated_resume_text: JSON-formatted resume text (uses cached if None)
        personal_info: JSON-formatted personal info (uses cached if None)
        use_o1_model: Whether to use o1 model for regeneration
        
    Returns:
        ResumeDetails object with all resume information
    """
    resume_dict = read_generated_resume_text_to_dict(
        generated_resume_text,
        use_o1_model=use_o1_model
    )
    personal_info = read_generated_personal_info_to_dict(personal_info)
    return ResumeDetails(**resume_dict, **personal_info)

def assemble_new_resume(
    generated_resume_text: Optional[str] = None,
    personal_info: Optional[str] = None,
    use_o1_model: bool = False
) -> None:
    """Assemble and write the final resume document.
    
    Args:
        generated_resume_text: JSON-formatted resume text (uses cached if None)
        personal_info: JSON-formatted personal info (uses cached if None)
        use_o1_model: Whether to use o1 model for regeneration
    """
    resume_details = get_resume_details(
        generated_resume_text,
        personal_info,
        use_o1_model
    )
    write_resume_to_docx(resume_details)


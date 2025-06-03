#!/usr/bin/env python3
"""Module for extracting job description text from a URL."""

import os
from typing import Optional
import requests
from bs4 import BeautifulSoup
import time

from src.data.consts import JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME
from src.utils.general_utils import read_temp_file, save_to_temp_file

def extract_text_from_link(url: str) -> Optional[str]:
    """Extract text content from a URL with retry logic.
    
    Args:
        url: URL to extract text from

    Returns:
        Extracted text or None if extraction fails
    """
    try:
        for attempt in range(10):
            response = requests.get(url)
            if response.status_code != 202:
                response.raise_for_status()
                break
            print(f"Attempt {attempt + 1}: Still processing, waiting 5 seconds...")
            time.sleep(5)
        else:
            print("Request is still not processed after several attempts.")
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    blacklist = {
        '[document]', 'noscript', 'header', 'html', 'meta',
        'head', 'input', 'script', 'style'
    }
    
    output = ' '.join(
        text.strip()
        for text in soup.find_all(text=True)
        if text.parent.name not in blacklist
    ).strip()
    
    save_to_temp_file(output, JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    return output

def extract_job_description_text(
    force_run: bool = False,
    job_description_link: Optional[str] = None
) -> Optional[str]:
    """Extract job description text from a URL with caching.
    
    Args:
        force_run: Whether to force extraction even if cached
        job_description_link: URL of the job description
        
    Returns:
        Extracted job description text or None if extraction fails
    """
    job_description_text = read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    if job_description_text and not force_run:
        return job_description_text

    return extract_text_from_link(job_description_link)

def get_job_description(
    force_run: bool = False,
    job_description_link: Optional[str] = None
) -> Optional[str]:
    """Get job description text, either from cache or by extracting from URL.
    
    Args:
        force_run: Whether to force extraction even if cached
        job_description_link: URL of the job description
        
    Returns:
        Extracted job description text or None if extraction fails
    """
    return extract_job_description_text(
        force_run=force_run,
        job_description_link=job_description_link
    )


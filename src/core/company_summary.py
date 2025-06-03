#!/usr/bin/env python3
"""Module for creating company summary from job description."""

import os
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import signal

from src.data.consts import (
    COMPANY_SUMMARY_TEMP_FILE_NAME,
    COMPANY_DATA_TEXT_TEMP_FILE_NAME,
    COMPANY_NAME_TEMP_FILE_NAME,
    COMPANY_SUMMARY_START_PROMPT,
    COMPANY_SUMMARY_END_PROMPT,
)
from src.utils.general_utils import save_to_temp_file, read_temp_file
from src.utils.npl_utils import Encoder
from src.utils.open_ai import OpenAIClient

# In-memory cache for company summaries
_company_cache = {}

def timeout_handler(signum, frame):
    raise TimeoutError("Company data extraction timed out")

def extract_text_from_single_page(url, timeout=10):
    """Extract text from a single page with timeout.
    
    Args:
        url: URL to extract text from
        timeout: Maximum time to wait for the request
        
    Returns:
        str: Extracted text or empty string if failed
    """
    try:
        response = requests.get(
            url, 
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; ResumeBot/1.0)'}
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        
        # Limit text length to prevent token overflow
        if len(text) > 10000:
            text = text[:10000] + "..."
            
        return f"Content from {url}:\n{text}\n\n"
        
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {str(e)}")
        return ""

def get_company_text_data_fast(company_base_link, max_time=25):
    """Extract company text data with strict time limits and fallbacks.
    
    Args:
        company_base_link: Base URL of the company website
        max_time: Maximum time in seconds to spend on crawling
        
    Returns:
        str: Processed company text data
    """
    company_text_data = read_temp_file(COMPANY_DATA_TEXT_TEMP_FILE_NAME)
    if company_text_data is not None:
        return company_text_data
    
    print(f"🕐 Fast crawling {company_base_link} (max {max_time}s)...")
    
    # Set up timeout signal
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(max_time)
    
    all_text = []
    
    try:
        # Strategy 1: Try to get main page content quickly
        main_content = extract_text_from_single_page(company_base_link, timeout=8)
        if main_content:
            all_text.append(main_content)
        
        # Strategy 2: Try to get a few key pages concurrently
        domain = urlparse(company_base_link).netloc
        common_pages = [
            urljoin(company_base_link, "/about"),
            urljoin(company_base_link, "/about-us"),
            urljoin(company_base_link, "/company"),
            urljoin(company_base_link, "/services"),
            urljoin(company_base_link, "/products"),
        ]
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(extract_text_from_single_page, url, 5): url 
                for url in common_pages
            }
            
            # Collect results with remaining time
            for future in future_to_url:
                try:
                    result = future.result(timeout=3)  # Short timeout per page
                    if result:
                        all_text.append(result)
                except (FuturesTimeoutError, Exception) as e:
                    print(f"⚠️ Skipped {future_to_url[future]}: {str(e)}")
                    continue
        
        # Combine all text
        company_text_data = ' '.join(all_text)
        
        # Fallback: If we got very little content, try just the main page with more time
        if len(company_text_data.strip()) < 500:
            print("📄 Fallback: Extracting just main page content...")
            company_text_data = extract_text_from_single_page(company_base_link, timeout=15)
        
        # Final fallback: Use domain name as minimal data
        if len(company_text_data.strip()) < 100:
            print("⚠️ Generating minimal company data from domain...")
            domain = urlparse(company_base_link).netloc
            # Extract company name from domain
            company_name_guess = domain.replace('www.', '').split('.')[0].title()
            company_text_data = f"""
Company: {company_name_guess}
Website: {company_base_link}
Domain: {domain}
Business Type: Technology/Software company
Industry: Based on domain and web presence
Note: Limited information available due to website access restrictions.
Company appears to be in the technology sector based on their web domain.
"""
        
    except TimeoutError:
        print(f"⏰ Crawling timed out after {max_time}s")
        if all_text:
            company_text_data = ' '.join(all_text)
        else:
            # Emergency fallback with better data
            domain = urlparse(company_base_link).netloc
            company_name_guess = domain.replace('www.', '').split('.')[0].title()
            company_text_data = f"""
Company: {company_name_guess}
Website: {company_base_link}
Domain: {domain}
Business Type: Technology/Software company
Note: Website crawling timed out after {max_time} seconds.
"""
    
    except Exception as e:
        print(f"❌ Crawling failed: {str(e)}")
        # Emergency fallback with better data
        domain = urlparse(company_base_link).netloc
        company_name_guess = domain.replace('www.', '').split('.')[0].title()
        company_text_data = f"""
Company: {company_name_guess}
Website: {company_base_link}
Domain: {domain}
Business Type: Technology/Software company
Note: Website crawling failed due to technical issues.
"""
    
    finally:
        # Disable the alarm
        signal.alarm(0)
    
    # Limit token count
    encoder = Encoder()
    max_tokens = 5000
    if encoder.get_num_tokens(company_text_data) > max_tokens:
        company_text_data = encoder.truncate_text(company_text_data, max_tokens)
    
    # Save and return
    save_to_temp_file(company_text_data, COMPANY_DATA_TEXT_TEMP_FILE_NAME)
    print(f"✅ Extracted {len(company_text_data)} chars from {company_base_link}")
    
    return company_text_data

def get_company_summary(force_run=False, company_base_link=None, company_name=None):
    """Generate a summary for a company using cached results when available.
    
    Args:
        force_run: If True, bypass cache and regenerate summary
        company_base_link: Company website URL
        company_name: Company name
        
    Returns:
        str: Company summary
    """
    cache_key = None
    if company_name:
        cache_key = company_name.lower().strip()
    elif company_base_link:
        domain = urlparse(company_base_link).netloc
        cache_key = domain.lower().strip()
    
    if cache_key and not force_run and cache_key in _company_cache:
        print(f"✅ Using cached summary for: {cache_key}")
        return _company_cache[cache_key]
    
    company_summary = read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)
    if company_summary and not force_run:
        if cache_key:
            _company_cache[cache_key] = company_summary
            print(f"💾 Cached summary for: {cache_key}")
        return company_summary

    print(f"🔄 Processing company summary for: {cache_key or 'unknown'}")
    company_text_data = get_company_text_data_fast(company_base_link=company_base_link)
    openai_client = OpenAIClient()

    if not company_name:
        prompt = f"Extract and return ONLY the company name mentioned in the following text:\n{company_text_data}"
        company_name = openai_client.generate_text(prompt).strip()
        cache_key = company_name.lower().strip()

    prompt = f"{COMPANY_SUMMARY_START_PROMPT.format(COMPANY_NAME=company_name)}\n\nStart of company details:\n{company_text_data}\nEnd of company details\n\n{COMPANY_SUMMARY_END_PROMPT}"
    company_summary = openai_client.generate_text(prompt)
    save_to_temp_file(company_summary, COMPANY_SUMMARY_TEMP_FILE_NAME)
    
    if cache_key:
        _company_cache[cache_key] = company_summary
        print(f"💾 Cached summary for: {cache_key}")
    
    return company_summary

def clear_company_cache():
    """Clear the in-memory company summary cache."""
    global _company_cache
    _company_cache.clear()
    print("🗑️ Company cache cleared")

def get_cache_info():
    """Get information about the current cache state.
    
    Returns:
        dict: Cache information including cached companies and cache size
    """
    return {
        "cached_companies": list(_company_cache.keys()),
        "cache_size": len(_company_cache)
    }
# if __name__ == "__main__":
#     create_company_summary(force_run=True)


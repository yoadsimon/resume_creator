#!/usr/bin/env python3
"""Module for creating company summary from job description."""

import os
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from tqdm import tqdm

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

def crawl_and_extract_text(base_url, all_text, visited_urls, encoder, max_tokens=100000, max_depth=1, delay=0.1):
    """Crawl a website and extract text content up to a maximum token limit.
    
    Args:
        base_url: Starting URL to crawl
        all_text: List to store extracted text
        visited_urls: Set of already visited URLs
        encoder: Token encoder instance
        max_tokens: Maximum number of tokens to extract
        max_depth: Maximum crawl depth
        delay: Delay between requests in seconds
    """
    def is_same_domain(url):
        return urlparse(url).netloc == domain

    def handle_url(url, depth):
        if url in visited_urls or depth > max_depth:
            return

        if encoder.get_num_tokens(' '.join(all_text)) > max_tokens:
            return

        time.sleep(0.01)

        try:
            response = requests.get(url)
            if response.status_code == 202:
                while response.status_code == 202:
                    time.sleep(1)
                    response = requests.get(url)
            visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = f"'{url}:\n{soup.get_text(separator=' ', strip=True)}'"
            all_text.append(page_text)
            for link in tqdm(soup.find_all('a', href=True), desc=f"Crawling {url}", leave=False):
                full_url = urljoin(base_url, link['href'])
                if is_same_domain(full_url) and full_url not in visited_urls:
                    time.sleep(delay)
                    handle_url(full_url, depth + 1)
        except Exception as e:
            raise e

    domain = urlparse(base_url).netloc
    handle_url(base_url, 0)

def get_company_text_data(company_base_link):
    """Extract and process company text data from the given URL.
    
    Args:
        company_base_link: Base URL of the company website
        
    Returns:
        str: Processed company text data
    """
    company_text_data = read_temp_file(COMPANY_DATA_TEXT_TEMP_FILE_NAME)
    encoder = Encoder()
    max_tokens = 5000
    
    if company_text_data is None:
        visited_urls = set()
        all_text = []
        crawl_and_extract_text(
            base_url=company_base_link,
            all_text=all_text,
            visited_urls=visited_urls,
            encoder=encoder,
            max_tokens=max_tokens,
            max_depth=1
        )
        company_text_data = ' '.join(all_text)
        
    if encoder.get_num_tokens(company_text_data) > max_tokens:
        company_text_data = encoder.truncate_text(company_text_data, max_tokens)
        
    save_to_temp_file(company_text_data, COMPANY_DATA_TEXT_TEMP_FILE_NAME)
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
    company_text_data = get_company_text_data(company_base_link=company_base_link)
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


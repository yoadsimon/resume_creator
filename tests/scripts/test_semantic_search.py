#!/usr/bin/env python3
"""Tests for semantic search functionality."""

import os
import sys
import logging
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.langchain_utils import LangChainClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_semantic_search():
    """
    Test the semantic search functionality using LangChain.
    This tests the ability to find relevant accomplishments for a job description.
    """
    logging.info("Testing semantic search functionality...")
    
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
        
        # Create a vector store from the accomplishments
        logging.info("Creating vector store from accomplishments...")
        vector_store = client.create_vector_store_from_text(accomplishments)
        
        # Sample job descriptions to test
        job_descriptions = [
            "We are looking for a machine learning engineer with experience in predictive modeling and data analysis.",
            "We need a software engineer with experience in microservices architecture and API optimization.",
            "Looking for a developer with open-source contributions and experience in React and Firebase."
        ]
        
        # Test semantic search with each job description
        for i, job_desc in enumerate(job_descriptions):
            logging.info(f"\nTesting job description {i+1}:")
            logging.info(f"Job Description: {job_desc}")
            
            # Perform semantic search
            results = client.semantic_search(vector_store, job_desc, k=2)
            
            # Print the results
            logging.info("Top 2 relevant accomplishments:")
            for j, doc in enumerate(results):
                logging.info(f"{j+1}. {doc.page_content.strip()}")
            
            # Simple validation - we should have 2 results
            if len(results) != 2:
                logging.error(f"Expected 2 results, got {len(results)}")
                return False
        
        logging.info("\nSemantic search test completed successfully!")
        return True
            
    except Exception as e:
        logging.error("Error during semantic search test: %s", str(e))
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
    success = test_semantic_search()
    
    if success:
        logging.info("All tests passed!")
        sys.exit(0)
    else:
        logging.error("Tests failed!")
        sys.exit(1)
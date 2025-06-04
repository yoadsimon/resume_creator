#!/usr/bin/env python3
"""Script to run all tests."""

import os
import sys
import logging
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.general_utils import read_temp_file, save_to_temp_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of test modules to run
TEST_MODULES = [
    "generate_test_files",
    "test_basic_resume_generation",
    "test_semantic_search",
    "test_llm_chains",
    "test_chat_interface"
]

def run_all_tests():
    """
    Run all test scripts in sequence.
    """
    logging.info("Starting all tests...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the scripts directory
    os.chdir(current_dir)
    
    # First, generate the test files
    logging.info("\n\n=== Generating test files ===\n")
    try:
        from generate_test_files import generate_all_sample_files
        generate_all_sample_files()
    except Exception as e:
        logging.error(f"Failed to generate test files: {str(e)}")
        return False
    
    # Run each test module
    all_passed = True
    for module_name in TEST_MODULES[1:]:  # Skip the first one (generate_test_files) as we already ran it
        logging.info(f"\n\n=== Running {module_name} ===\n")
        
        try:
            # Run the test as a subprocess to isolate it
            result = subprocess.run([sys.executable, f"{module_name}.py"], 
                                   capture_output=True, text=True)
            
            # Print the output
            if result.stdout:
                print(result.stdout)
            
            # Check if the test passed
            if result.returncode != 0:
                logging.error(f"{module_name} failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
                all_passed = False
            else:
                logging.info(f"{module_name} passed!")
        
        except Exception as e:
            logging.error(f"Error running {module_name}: {str(e)}")
            all_passed = False
    
    # Print summary
    if all_passed:
        logging.info("\n\n=== All tests passed! ===\n")
    else:
        logging.error("\n\n=== Some tests failed. Please check the logs for details. ===\n")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
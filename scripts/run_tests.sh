#!/bin/bash

# Run all tests for the Resume Creator API

# Change to the tests/scripts directory
cd tests/scripts

# Run the test runner script
python run_all_tests.py

# Store the exit code
EXIT_CODE=$?

# Change back to the root directory
cd ../..

# Exit with the same code as the test runner
exit $EXIT_CODE
# Resume Creator API Tests

This directory contains test scripts for the Resume Creator API, focusing on testing the core functionality and features.

## Test Structure

The tests are organized as follows:

- `scripts/`: Contains the test scripts for different features
- `data/`: Contains sample data files used by the tests

## Running the Tests

Before running the tests, make sure you have installed all the required dependencies:

```bash
pip install -r ../requirements.txt
```

Also, ensure you have set up your OpenAI API credentials in the `.env` file in the root directory:

```
OPEN_AI_ORGANIZATION_ID=your_organization_id
OPEN_AI_PROJECT_ID=your_project_id
OPEN_AI_TOKEN=your_api_key
```

### Generating Sample Test Files

First, generate the sample test files:

```bash
cd tests/scripts
python generate_test_files.py
```

This will create a sample resume in DOCX format and a sample accomplishments file in the `data/` directory.

### Running Individual Tests

You can run each test script individually:

#### 1. Basic Resume Generation Test

Tests the basic resume generation functionality:

```bash
python test_basic_resume_generation.py
```

#### 2. Interactive Chat Interface Test

Tests the interactive chat interface for resume generation:

```bash
python test_chat_interface.py
```

### Running All Tests

To run all tests at once, you can use the provided run_all_tests.py script:

```bash
cd tests/scripts
python run_all_tests.py
```

This script will:
1. Generate the sample test files
2. Run each test script in sequence
3. Display the output from each test
4. Provide a summary of which tests passed and which failed

Alternatively, you can use unittest to discover and run all tests:

```bash
cd tests/scripts
python -m unittest discover -p "test_*.py"
```

## Test Descriptions

### 1. Basic Resume Generation Test

This test verifies that the basic resume generation functionality works correctly. It:

- Loads sample resume and accomplishments files
- Calls the resume generation function
- Checks if a resume file is created

### 2. Interactive Chat Interface Test

This test verifies that the interactive chat interface works correctly. It:

- Creates a chat session with sample data
- Sends messages and checks if responses are received
- Tests getting chat history
- Tests deleting the chat session

## Troubleshooting

If you encounter any issues while running the tests:

1. Make sure your OpenAI API credentials are correct
2. Check that you have installed all the required dependencies
3. Ensure you have generated the sample test files
4. Check the error messages for specific issues

If you still have issues, please open an issue on the GitHub repository.

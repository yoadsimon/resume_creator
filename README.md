# Resume Creator API

Resume Creator API is a Python-based tool designed to automate the creation of a tailored resume for specific job applications. It leverages OpenAI's GPT models to generate customized resume content by analyzing your existing resume, additional accomplishments, the job description, and company information.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the API](#running-the-api)
- [Using the API](#using-the-api)
  - [Endpoint](#endpoint)
  - [Request Parameters](#request-parameters)
- [Cleaning Temporary Files](#cleaning-temporary-files)
- [Notes](#notes)

## Features

- **Accomplishment Extraction**: Extracts your professional accomplishments from your existing resume and an additional accomplishments file.
- **Company Summary Generation**: Crawls the company's website to generate a comprehensive summary.
- **Job Description Parsing**: Extracts and processes the job description from a provided URL.
- **Industry Identification**: Determines the primary industry related to the job.
- **Resume Generation**: Creates a customized resume in JSON format, focusing on relevant skills and experiences.
- **Resume Assembly**: Converts the generated JSON resume into a well-formatted Word document.
- **API Interface**: Provides a RESTful API to interact with the resume generation process.

## Prerequisites

- **Python 3.7 or higher**
- **OpenAI API access** (API key and organization ID)
- **Required Python packages** (listed in `requirements.txt`):
  - `fastapi`
  - `uvicorn`
  - `docx2txt`
  - `beautifulsoup4`
  - `requests`
  - `tqdm`
  - `python-dotenv`
  - `python-docx`
  - `tiktoken`

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yoadsimon/resume_creator.git
cd resume_creator
```

### 2. Create a Virtual Environment

```bash
python -m venv resume_creator_venv
```

### 3. Activate the Virtual Environment

- On macOS and Linux:

  ```bash
  source resume_creator_venv/bin/activate
  ```

- On Windows:

  ```bash
  resume_creator_venv\Scripts\activate
  ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and add your OpenAI credentials:

```dotenv
OPEN_AI_ORGANIZATION_ID=your_organization_id
OPEN_AI_PROJECT_ID=your_project_id
OPEN_AI_TOKEN=your_api_key
```

Replace `your_organization_id`, `your_project_id`, and `your_api_key` with your actual OpenAI credentials.

## Running the API

To start the Resume Creator API server, run the following command:

```bash
uvicorn api:app --reload
```

- **`api:app`** tells Uvicorn to look for the `app` object in the `api.py` file.
- **`--reload`** enables auto-reload, making the server restart when you make changes to the code (useful during development).

The server will start and listen on `http://127.0.0.1:8000` by default.

## Using the API

### Endpoint

**POST** `/generate_resume`

This endpoint accepts your resume file, accomplishments file, and other relevant information to generate a tailored resume.

### Request Parameters

The API expects a multipart/form-data POST request with the following parameters:

| Parameter                | Type    | Description                                                        | Required |
|--------------------------|---------|--------------------------------------------------------------------|----------|
| `resume_file`            | File    | Your current resume in `.docx` format                              | Yes      |
| `accomplishments_file`   | File    | Additional accomplishments in a text file                          | Yes      |
| `job_description_link`   | String  | URL to the job description                                         | Yes      |
| `company_base_link`      | String  | Base URL of the company's website                                  | Yes      |
| `company_name`           | String  | Name of the company *(if not provided, it will be extracted)*      | No       |
| `force_run_all`          | Boolean | If `true`, the script ignores cached data (default is `false`)     | No       |



### Accessing Interactive API Documentation

After starting the server, you can access the interactive API documentation provided by FastAPI at:

```
http://127.0.0.1:8000/docs
```

This interface allows you to interact with the API directly from your browser, providing a user-friendly way to test the endpoint.

## Cleaning Temporary Files

The API generates temporary files during processing, stored in the `temp` and `result` directories. To clean up these files after processing, you can run the provided script:

```bash
python clean_temp_files.py
```

This script removes the `temp` directory and its contents.

## Notes

- **OpenAI API Usage**: Ensure that your OpenAI API credentials are valid and that you have sufficient quota to make API calls.
- **File Formats**: The `resume_file` should be in `.docx` format, and the `accomplishments_file` should be a plaintext file.
- **Error Handling**: If the API returns an error, check the server logs for detailed error messages.
- **Security Considerations**: Be cautious with the files you upload and ensure they are from trusted sources.
- **Performance**: The resume generation process can take some time due to API calls to OpenAI. Please be patient after sending a request.
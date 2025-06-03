# Resume Creator API

A FastAPI-based application that generates tailored resumes using LangChain and OpenAI's GPT models. This tool helps create customized resumes by analyzing job descriptions and company information to highlight the most relevant skills and experiences.

## 🚀 Quick Start with Docker (Recommended)

**Optimized for Python 3.13 with fast CI/CD builds!**

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API credentials

### Fast Setup (30 seconds to running!)

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd resume_creator
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI credentials
   ```

3. **Build and run with optimizations:**
   ```bash
   ./docker-build-fast.sh
   ```

Your API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ⚡ Performance Optimizations

This project includes several CI/CD and deployment optimizations:

### 🐳 Docker Optimizations
- **Multi-stage builds** for 70% smaller final images
- **BuildKit** enabled for parallel layer builds
- **ChromaDB** instead of FAISS for Python 3.13 compatibility
- **Optimized dependencies** for faster installs
- **Layer caching** for 5x faster rebuilds
- **Non-root user** for security

### 📦 Dependency Optimizations
- Replaced `faiss-cpu` with `chromadb` (Python 3.13 compatible)
- Updated LangChain to latest versions (0.3.x series)
- Minimized dependencies to essential packages only
- Pinned versions for reproducible builds

### 🔧 Build Time Improvements
- **Before**: 10-15 minutes (with FAISS compilation)
- **After**: 2-3 minutes (with optimized dependencies)
- **Rebuild**: 30-60 seconds (with layer caching)

## 🛠 Technical Stack

- **Runtime**: Python 3.13
- **Web Framework**: FastAPI
- **LLM Integration**: LangChain 0.3.x + OpenAI
- **Vector Database**: ChromaDB (replaces FAISS)
- **Document Processing**: python-docx, BeautifulSoup4
- **Containerization**: Docker with BuildKit
- **API Documentation**: Swagger/OpenAPI

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the API](#running-the-api)
- [Using the API](#using-the-api)
  - [Endpoint](#endpoint)
  - [Request Parameters](#request-parameters)
- [Interactive Chat Interface](#interactive-chat-interface)
  - [Chat Endpoints](#chat-endpoints)
- [LangChain Integration](#langchain-integration)
  - [Semantic Search](#semantic-search)
  - [Prompt Templates](#prompt-templates)
  - [LLM Chains](#llm-chains)
  - [Controlling LangChain Features](#controlling-langchain-features)
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
- **Semantic Search**: Uses vector databases to find the most relevant accomplishments for the job description.
- **Prompt Templates**: Uses LangChain's prompt templates for dynamic content creation.
- **LLM Chains**: Implements multi-step LLM chains for the resume generation workflow.

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
  - `langchain`
  - `langchain-openai`
  - `faiss-cpu`

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

| Parameter                | Type    | Description                                                                                | Required |
|--------------------------|---------|--------------------------------------------------------------------------------------------|----------|
| `resume_file`            | File    | Your current resume in `.docx` format                                                      | Yes      |
| `accomplishments_file`   | File    | Additional accomplishments in a text file                                                  | Yes      |
| `job_description_link`   | String  | URL to the job description                                                                 | Yes      |
| `company_base_link`      | String  | Base URL of the company's website                                                          | Yes      |
| `company_name`           | String  | Name of the company *(if not provided, it will be extracted)*                              | No       |
| `force_run_all`          | Boolean | If `true`, the script ignores cached data (default is `false`)                             | No       |
| `use_o1_model`           | Boolean | If `true`, uses OpenAI's o1 model for better results (default is `false`)                  | No       |
| `use_langchain`          | Boolean | If `true`, uses LangChain for enhanced resume generation (default is `true`)               | No       |
| `use_semantic_search`    | Boolean | If `true`, uses semantic search for better matching with job description (default is `true`)| No       |



### Accessing Interactive API Documentation

After starting the server, you can access the interactive API documentation provided by FastAPI at:

```
http://127.0.0.1:8000/docs
```

This interface allows you to interact with the API directly from your browser, providing a user-friendly way to test the endpoint.

## Interactive Chat Interface

The Resume Creator API now provides an interactive chat interface for resume generation. This allows users to have a conversation with the system to refine their resume, ask questions about the job description or company, and get feedback on their resume.

### Chat Endpoints

The API provides the following endpoints for interactive resume generation:

#### Create Chat Session

**POST** `/chat/create`

This endpoint creates a new chat session for interactive resume generation. It takes the same parameters as the `/generate_resume` endpoint, processes the files, extracts the necessary information, and creates a chat session with the extracted information.

#### Send Message

**POST** `/chat/message/{session_id}`

This endpoint sends a message to the chat session and gets a response. It takes a session ID and a message, and returns the response from the chat.

Request body:
```json
{
  "message": "Can you help me highlight my skills that match this job description?"
}
```

Response:
```json
{
  "response": "Based on the job description, I'd recommend highlighting the following skills..."
}
```

#### Get Chat History

**GET** `/chat/history/{session_id}`

This endpoint gets the chat history for a session. It takes a session ID and returns the chat history as a list of messages.

Response:
```json
{
  "history": [
    {
      "role": "user",
      "content": "Hello, I need help tailoring my resume for a job application."
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help you tailor your resume! What specific aspect would you like to work on first?"
    },
    ...
  ]
}
```

#### Delete Chat Session

**DELETE** `/chat/{session_id}`

This endpoint deletes a chat session. It takes a session ID and returns a success message if the session was deleted.

Response:
```json
{
  "message": "Chat session deleted successfully"
}
```

## LangChain Integration

The Resume Creator API now integrates LangChain to enhance the resume generation process. LangChain provides a framework for developing applications powered by language models, offering tools for prompt management, chaining, and semantic search.

### Semantic Search

Semantic search is used to find the most relevant accomplishments for the job description. This is implemented using:

- **Vector Databases**: The accomplishments are stored in a FAISS vector database, which allows for efficient similarity search.
- **Embeddings**: OpenAI's embeddings are used to convert text into vectors that capture semantic meaning.
- **Retrieval**: When generating a resume, the system retrieves the most relevant accomplishments based on their semantic similarity to the job description.

This approach ensures that the resume highlights the most relevant experiences and skills for the specific job, improving the match between the candidate and the job requirements.

### Prompt Templates

LangChain's prompt templates are used to create dynamic prompts for the language model. These templates:

- **Modularize Prompts**: Break down complex prompts into reusable components.
- **Inject Variables**: Allow for dynamic insertion of variables like job description, company summary, and accomplishments.
- **Standardize Format**: Ensure consistent prompt structure across different parts of the application.

For example, the resume generation process uses a template that includes the job description, company summary, extracted skills, and accomplishments, with specific instructions for formatting the output.

### LLM Chains

LLM chains are used to orchestrate multi-step workflows in the resume generation process:

- **Sequential Chains**: Chain multiple LLM calls together, where the output of one step becomes the input for the next.
- **Skill Extraction**: First extract key skills from the job description.
- **Resume Generation**: Then use those skills to generate a tailored resume.

This approach allows for more focused and effective resume generation, as each step can concentrate on a specific task rather than trying to do everything at once.

### Controlling LangChain Features

The API provides parameters to control the use of LangChain features:

- **use_langchain**: Whether to use LangChain for enhanced resume generation (default is true).
- **use_semantic_search**: Whether to use semantic search for better matching between resume and job description (default is true).

These parameters can be set when making a request to the API, allowing for flexibility in how the resume is generated.

## Cleaning Temporary Files

The API generates temporary files during processing, stored in the `temp` and `result` directories. To clean up these files after processing, you can run the provided script:

```bash
python clean_temp_files.py
```

This script removes the `temp` directory and its contents.

## Testing

The project includes a comprehensive test suite to verify the functionality of the Resume Creator API, including the LangChain integration. The tests are located in the `tests` directory.

### Running the Tests

To run all tests, you can use the provided shell script:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

This will run all the tests and display the results.

For more detailed information about the tests and how to run individual tests, see the [tests/README.md](tests/README.md) file.

## Notes

- **OpenAI API Usage**: Ensure that your OpenAI API credentials are valid and that you have sufficient quota to make API calls.
- **File Formats**: The `resume_file` should be in `.docx` format, and the `accomplishments_file` should be a plaintext file.
- **Error Handling**: If the API returns an error, check the server logs for detailed error messages.
- **Security Considerations**: Be cautious with the files you upload and ensure they are from trusted sources.
- **Performance**: The resume generation process can take some time due to API calls to OpenAI. Please be patient after sending a request.

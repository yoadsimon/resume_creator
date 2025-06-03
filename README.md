# Resume Creator API

A FastAPI-based application that generates tailored resumes using OpenAI's GPT models. This tool helps create customized resumes by analyzing job descriptions and company information to highlight the most relevant skills and experiences.

---

## 🗂️ Project Structure

```
resume_creator/
├── api.py                  # FastAPI app and endpoints
├── _1_get_accomplishments_and_personal_details.py
├── _2_create_company_summary.py
├── _3_extract_job_description_text.py
├── _4_extract_job_industry.py
├── _5_generate_resume_text.py
├── _6_assemble_new_resume.py
├── utils/                  # Utility modules (OpenAI, etc.)
├── inputs/                 # Input files (resumes, prompts, etc.)
├── temp/                   # Temporary files (auto-generated)
├── result/                 # Output resumes
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd resume_creator
   ```
2. **Set up your environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp env.example .env  # Add your OpenAI credentials to .env
   ```
3. **Start the API server:**
   ```bash
   uvicorn api:app --reload
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000)

---

## 📊 API Overview

### Generate Resume
**POST** `/generate_resume`
- **Description:** Generate a tailored resume based on your resume, accomplishments, job description, and company info.
- **Request:** `multipart/form-data`
  - `resume_file`: `.docx` file (required)
  - `accomplishments_file`: `.txt` file (required)
  - `job_description_link`: URL (required)
  - `company_base_link`: URL (required)
  - `company_name`: string (optional)
  - `use_o1_model`: boolean (optional)
- **Response:** JSON with generated resume content

### Interactive API Docs
- Visit [http://localhost:8000/docs](http://localhost:8000/docs) after starting the server for a full, interactive OpenAPI/Swagger UI.

---

## 📝 Example Workflow Diagram

```
[Resume DOCX]   [Accomplishments TXT]   [Job Description URL]   [Company URL]
      |                  |                        |                     |
      |                  |                        |                     |
      +------------------+------------------------+---------------------+
                                 |
                        [API: /generate_resume]
                                 |
                        [LLM Processing Pipeline]
                                 |
                        [Generated Resume JSON]
                                 |
                        [DOCX Resume Output]
```

---

## 📚 More Info
- All temporary and output files are stored in `temp/` and `result/`.
- For advanced usage, see the code in the numbered modules and `api.py`.
- For testing, see the `tests/` directory.

---

**Questions?** Open an issue or see the code for more details.

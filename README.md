# Resume Creator API

A FastAPI-based application that generates tailored resumes using OpenAI's GPT models. This tool helps create customized resumes by analyzing job descriptions and company information to highlight the most relevant skills and experiences.

---

## 🗂️ Project Structure

```
resume_creator/
├── src/                      # Source code (importable as a package)
│   ├── core/                # Core resume creation logic (main pipeline steps)
│   ├── api/                 # FastAPI server
│   ├── utils/               # Utility modules (OpenAI, LangChain, docx, etc.)
│   └── data/                # Constants and config
├── tests/                   # All tests (unit, integration, E2E)
│   ├── scripts/            # Integration/E2E test scripts
│   └── data/               # Test data (sample resumes, etc.)
├── scripts/                 # Helper scripts (run, test, API test, etc.)
├── data/                    # Input, temp, and result files (runtime data)
│   ├── inputs/             # Input files (job descriptions, etc.)
│   ├── temp/               # Temporary files generated during processing
│   └── result/             # Output files (generated resumes)
├── docker/                  # Docker configuration files
├── requirements/            # Python dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Files and folders to ignore in git
└── README.md
```

### Directory Descriptions

- `src/`: All source code, importable as a package
  - `core/`: Main business logic for resume creation
  - `api/`: FastAPI server
  - `utils/`: Utility modules (OpenAI, LangChain, docx, etc.)
  - `data/`: Constants and configuration
- `tests/`: All tests (unit, integration, E2E)
  - `scripts/`: Integration/E2E test scripts
  - `data/`: Test data (sample resumes, etc.)
- `scripts/`: Helper scripts for running the application and tests
- `data/`: Runtime data (inputs, temp, results)
- `docker/`: Docker configuration files
- `requirements/`: Python package requirements files
- `.env.example`: Example environment variables (copy to `.env` and fill in your secrets)
- `.gitignore`: Files and folders to ignore in git

---

## 🚀 Development Workflow

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
3. **Run the API server:**
   ```bash
   uvicorn src.api.api:app --reload
   ```
4. **Run all tests:**
   ```bash
   bash scripts/run_tests.sh
   # or
   python -m pytest tests/
   ```
5. **Generate test data:**
   ```bash
   python tests/scripts/generate_test_files.py
   ```

---

## 📦 .env and .gitignore

- **.env.example**: Copy to `.env` and fill in your OpenAI and other secrets. Never commit `.env` to git.
- **.gitignore**: Ignores venv, temp, result, .env, and other non-source files.

---

## 📚 More Info
- All temporary and output files are stored in `data/temp/` and `data/result/`.
- For advanced usage, see the code in the numbered modules and `api.py`.
- For testing, see the `tests/` directory.

---

**Questions?** Open an issue or see the code for more details.

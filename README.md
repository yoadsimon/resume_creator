# Resume Creator - Full-Stack Application

A modern full-stack application that generates tailored resumes using OpenAI's GPT models. This tool helps create customized resumes by analyzing job descriptions and company information to highlight the most relevant skills and experiences.

## 🏗️ Architecture

- **Frontend**: React TypeScript with Tailwind CSS
- **Backend**: FastAPI with Python
- **Containerization**: Docker & Docker Compose
- **AI Integration**: OpenAI GPT models

---

## 🚀 Quick Start

**The easiest way to run the application:**

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd resume_creator
   cp env.example .env  # Add your OpenAI credentials to .env
   ```

2. **Run the application:**
   ```bash
   ./run_app.sh
   ```

3. **Access the application:**
   - **Frontend UI**: http://localhost:3000 ← **Start here!**
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

That's it! The script handles everything - stopping old containers, building, and starting both frontend and backend.

---

## 🗂️ Project Structure

```
resume_creator/
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.tsx         # Main application component
│   │   └── index.tsx       # Application entry point
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   ├── Dockerfile          # Production frontend container
│   └── Dockerfile.dev      # Development frontend container
├── src/                     # Backend source code (importable as a package)
│   ├── core/               # Core resume creation logic (main pipeline steps)
│   ├── api/                # FastAPI server
│   ├── utils/              # Utility modules (OpenAI, LangChain, docx, etc.)
│   └── data/               # Constants and config
├── tests/                  # All tests (unit, integration, E2E)
├── scripts/               # Helper scripts
├── data/                  # Input, temp, and result files (runtime data)
├── docker/               # Docker configuration files
│   ├── docker-compose.yml     # Production setup
│   ├── docker-compose.dev.yml # Development setup
│   └── Dockerfile.backend     # Backend container
├── run_app.sh            # 🚀 Main script to run the application
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
└── README.md
```

---

## 🎯 Features

### Current Features
- **Modern React UI**: Clean, responsive interface with Tailwind CSS
- **File Upload**: Drag & drop support for resume (.docx) and accomplishments (.txt) files
- **AI-Powered Generation**: Uses OpenAI GPT models to create tailored resumes
- **Company Analysis**: Analyzes job descriptions and company information
- **Resume Viewer**: View generated resume content in the browser
- **Download**: Download generated resumes as .docx files
- **Docker Support**: Full containerization for easy deployment

### Coming Soon
- **Resume Editor**: Edit resume content directly in the browser
- **Section Management**: Add, remove, and reorder resume sections
- **Real-time Preview**: See changes as you edit
- **Multiple Export Formats**: PDF, HTML, and other formats
- **Template Selection**: Choose from different resume templates
- **Version History**: Track and revert to previous versions

---

## 🔧 Alternative Running Methods

### Option 1: Development with Hot Reload
```bash
bash scripts/run_dev.sh
```

### Option 2: Manual Development Setup

**Backend:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env  # Add your OpenAI credentials
uvicorn src.api.api:app --reload
```

**Frontend (in another terminal):**
```bash
cd frontend
npm install
npm start
```

### Option 3: Docker Commands
```bash
# Production build and run
cd docker && docker compose up --build

# Development with hot reload
cd docker && docker compose -f docker-compose.dev.yml up --build

# Stop services
cd docker && docker compose down
```

---

## 📦 Environment Variables

Copy `env.example` to `.env` and fill in your credentials:

```bash
# OpenAI Configuration
OPEN_AI_TOKEN=your_openai_api_key
OPEN_AI_ORGANIZATION_ID=your_org_id  # Optional
OPEN_AI_PROJECT_ID=your_project_id  # Optional
```

---

## 🔧 API Endpoints

- `POST /generate_resume` - Generate a tailored resume
- `GET /resume/content` - Get resume content as JSON
- `GET /resume/download` - Download the generated resume file
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

---

## 🧪 Testing

```bash
# Run all tests
bash scripts/run_tests.sh
# or
python -m pytest tests/

# Generate test data
python tests/scripts/generate_test_files.py
```

---

## 🚀 Deployment

The application is fully containerized and ready for deployment to any Docker-compatible platform:

- **Docker Compose**: Use the provided docker-compose.yml
- **Kubernetes**: Convert Docker Compose to K8s manifests
- **Cloud Platforms**: Deploy to AWS ECS, Google Cloud Run, Azure Container Instances, etc.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Questions?** Open an issue or see the code for more details.

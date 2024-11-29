# Resume Creator

This project is a Python-based tool designed to automate the creation of a tailored resume for a specific job application. It leverages OpenAI's GPT models to generate customized resume content by analyzing your existing resume, the job description, company information, and your professional accomplishments.

## Features

- **Accomplishment Extraction**: Extracts your professional accomplishments from your existing resume.
- **Company Summary Generation**: Crawls the company's website to generate a comprehensive summary.
- **Job Description Parsing**: Extracts and processes the job description from a provided URL.
- **Industry Identification**: Determines the primary industry related to the job.
- **Resume Generation**: Creates a customized resume in JSON format, focusing on relevant skills and experiences.
- **Resume Assembly**: Converts the generated JSON resume into a well-formatted Word document.

## Prerequisites

- Python 3.7 or higher
- OpenAI API access (API key and organization ID)
- Required Python packages:
  - `docx2txt`
  - `beautifulsoup4`
  - `requests`
  - `tqdm`
  - `dotenv`
  - `python-docx`
  - `tiktoken`
  - `gitignore-parser`

## Setup and Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/resume_creator.git
   cd resume_creator
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv resume_creator_venv
   ```

3. **Activate the Virtual Environment**

   - On macOS and Linux:

     ```bash
     source resume_creator_venv/bin/activate
     ```

   - On Windows:

     ```bash
     resume_creator_venv\Scripts\activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**

   Create a `.env` file in the root directory and add your OpenAI credentials:

   ```dotenv
   OPEN_AI_ORGANIZATION_ID=your_organization_id
   OPEN_AI_PROJECT_ID=your_project_id
   OPEN_AI_TOKEN=your_api_key
   ```

## Configuration

1. **Update Input Constants**

   In the `inputs/consts.py` file, update the following constants with your own information:

   ```python
   RESUME_FILE_PATH = "inputs/resume.docx"
   JOB_DESCRIPTION_LINK = "https://www.examplecompany.com/job-description"
   COMPANY_BASE_LINK = "https://www.examplecompany.com/"
   COMPANY_NAME = "ExampleCompany"
   ```

2. **Place Your Resume**

   Ensure your current resume is placed at the path specified in `RESUME_FILE_PATH`.

## How to Run

Run the main script to generate your tailored resume:

```bash
python run_all.py
```

This script performs the following steps:

1. **Extract All Accomplishments**

   - Parses your existing resume to extract all professional accomplishments.

2. **Create Company Summary**

   - Crawls the company's website to generate a comprehensive summary using OpenAI's GPT.

3. **Extract Job Description Text**

   - Fetches and processes the job description from the provided link.

4. **Extract Job Industry**

   - Determines the primary industry related to the job position.

5. **Generate Resume Text**

   - Uses OpenAI's GPT to generate a tailored resume in JSON format, focusing on relevant experiences and skills.

6. **Assemble New Resume**

   - Converts the generated JSON resume into a formatted Word document, ready for application.

The final resume will be saved in the `result` directory as `resume.docx`.

## Notes

- **Force Run All Steps**

  If you want to force the script to run all steps and ignore any cached data, modify the `force_run_all` parameter:

  ```python
  create_resume_for_job_application(force_run_all=True)
  ```

- **Customizing Personal Details**

  Ensure your personal details are included in the `PERSONAL_DETAILS_TEMP_FILE_NAME` file if required.

## License

This project is licensed under the MIT License.

# Short Summary

This README provides an overview of the Resume Creator project, instructions on how to set it up, configure it with your personal and job application details, and run the script to generate a tailored resume using OpenAI's GPT models.
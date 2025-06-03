#!/usr/bin/env python3
"""Module for generating tailored resume text based on job requirements."""

from typing import Optional

from inputs.consts import (
    RESUME_TEXT_TEMP_FILE_NAME,
    JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME,
    COMPANY_SUMMARY_TEMP_FILE_NAME,
    FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME,
    JOB_INDUSTRY_TEMP_FILE_NAME,
    GENERATED_RESUME_TEXT
)
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient
from utils.langchain_utils import LangChainClient, create_resume_generation_chain

def generate_resume_text(job_description: Optional[str] = None, company_summary: Optional[str] = None, accomplishments: Optional[str] = None, job_industry: Optional[str] = None, use_o1_model: bool = False) -> str:
    """Generate a tailored resume text in JSON format for proper docx formatting.
    
    Args:
        job_description: Job description text (uses cached if None)
        company_summary: Company summary text (uses cached if None)
        accomplishments: Accomplishments text (uses cached if None)
        job_industry: Industry name (uses cached if None)
        use_o1_model: (Optional) Whether to use o1 model (default: False)
        
    Returns:
        Generated resume text in JSON format
    """
    if not all([accomplishments, job_description, company_summary, job_industry]):
        accomplishments = accomplishments or read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
        job_description = job_description or read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
        company_summary = company_summary or read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)
        job_industry = job_industry or read_temp_file(JOB_INDUSTRY_TEMP_FILE_NAME)

    model_name = "gpt-4-turbo-preview" if not use_o1_model else "o1-preview-2024-09-12"

    openai_client = OpenAIClient(model=model_name)
    prompt = (f"You are an expert resume writer specializing in ATS-optimized resumes for the {job_industry} industry. "
            f"Create a compelling, tailored resume that aligns with the job requirements.\n\n"
            f"**Job Description:**\n{job_description}\n\n"
            f"**Company Summary:**\n{company_summary}\n\n"
            f"**My Accomplishments and Experience:**\n{accomplishments}\n\n"
            f"**CRITICAL: Return ONLY valid JSON in this exact format:**\n"
            f"{{\n"
            f"  \"Professional Summary\": \"3-4 sentence compelling summary\",\n"
            f"  \"Work Experience\": [\n"
            f"    {{\"title\": \"Job Title\", \"place\": \"Company Name\", \"date\": \"Date Range\", \"description\": [\"Achievement 1\", \"Achievement 2\", \"Achievement 3\"]}},\n"
            f"    {{\"title\": \"Job Title 2\", \"place\": \"Company Name 2\", \"date\": \"Date Range 2\", \"description\": [\"Achievement 1\", \"Achievement 2\"]}}\n"
            f"  ],\n"
            f"  \"Personal Projects\": [\n"
            f"    {{\"title\": \"Project Name\", \"date\": \"Date Range\", \"description\": [\"Project detail 1\", \"Project detail 2\"]}}\n"
            f"  ],\n"
            f"  \"Education\": [\n"
            f"    {{\"title\": \"Degree Name\", \"place\": \"Institution\", \"date\": \"Date Range\", \"description\": [\"Relevant coursework\", \"Honors or achievements\"]}}\n"
            f"  ],\n"
            f"  \"Skills\": [\"Skill1\", \"Skill2\", \"Skill3\", \"Skill4\"],\n"
            f"  \"Languages\": [\"Language1\", \"Language2\"]\n"
            f"}}\n\n"
            f"IMPORTANT GUIDELINES:\n"
            f"- Use exact keywords from the job description\n"
            f"- Quantify achievements with metrics when possible\n"
            f"- Focus only on relevant experiences\n"
            f"- Use strong action verbs\n"
            f"- Return ONLY the JSON, no additional text or explanations\n"
            f"- Ensure all JSON keys match exactly as shown above")
    generated_resume_text = openai_client.generate_text(prompt)

    save_to_temp_file(generated_resume_text, GENERATED_RESUME_TEXT)
    return generated_resume_text
# if __name__ == "__main__":
#     generate_resume_text()


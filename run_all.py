#!/usr/bin/env python3
"""Main script to run the complete resume generation process."""

import logging
from _1_get_accomplishments_and_personal_details import get_all_accomplishments, get_personal_details
from _2_create_company_summary import create_company_summary
from _3_extract_job_description_text import extract_job_description_text
from _4_extract_job_industry import extract_job_industry
from _5_generate_resume_text import generate_resume_text
from _6_assemble_new_resume import assemble_new_resume

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_resume_for_job_application(
        resume_file_path: str,
        accomplishments_file_path: str,
        job_description_link: str,
        company_base_link: str,
        company_name: str = None,
        force_run_all: bool = False,
        use_o1_model: bool = False,
        use_langchain: bool = True,
        use_semantic_search: bool = True
) -> None:
    """Create a tailored resume for a job application.
    
    Args:
        resume_file_path: Path to the resume file
        accomplishments_file_path: Path to the accomplishments file
        job_description_link: Link to the job description
        company_base_link: Base link of the company website
        company_name: Name of the company (optional)
        force_run_all: Whether to force run all steps
        use_o1_model: Whether to use the o1 model
        use_langchain: Whether to use LangChain for enhanced resume generation
        use_semantic_search: Whether to use semantic search for better matching
    """
    logging.info("Starting resume creation process")

    # Get accomplishments and personal details
    all_accomplishments = get_all_accomplishments(
        resume_file_path=resume_file_path,
        accomplishments_file_path=accomplishments_file_path,
        force_run=force_run_all,
        use_langchain=use_langchain
    )
    personal_details = get_personal_details(
        force_run=force_run_all,
        resume_file_path=resume_file_path,
        use_langchain=use_langchain
    )

    # Get company and job information
    company_summary = create_company_summary(
        company_base_link=company_base_link,
        company_name=company_name,
        force_run=force_run_all
    )
    job_description_text = extract_job_description_text(
        job_description_link=job_description_link,
        force_run=force_run_all
    )
    job_industry = extract_job_industry(
        force_run=force_run_all,
        job_description=job_description_text,
        company_summary=company_summary
    )

    # Generate and assemble resume
    resume_text = generate_resume_text(
        accomplishments=all_accomplishments,
        company_summary=company_summary,
        job_description=job_description_text,
        job_industry=job_industry,
        use_o1_model=use_o1_model,
        use_semantic_search=use_semantic_search
    )
    assemble_new_resume(
        generated_resume_text=resume_text,
        personal_info=personal_details,
        use_o1_model=use_o1_model
    )

    logging.info("Resume creation process completed")

# if __name__ == "__main__":
#     create_resume_for_job_application(force_run_all=True,
#                                       resume_file_path="temp/resume.docx",
#                                       accomplishments_file_path="temp/short_accomplishments.txt",
#                                       job_description_link="https://www.nimbleway.com/job/nlp-engineer-628de?transaction_id=102930a437339b8514403b73014016&coref=1.10.s8C_64E&submissionGuid=8e59a49b-b30a-46b4-8ff1-0ca026118b65&aff_id=29&offer_id=8&344e6a5d_page=2",
#                                       company_base_link="https://www.nimbleway.com/",
#                                       company_name=None
#                                       )

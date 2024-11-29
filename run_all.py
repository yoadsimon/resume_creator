import logging
from _1_get_all_accomplishments import get_all_accomplishments
from _2_create_company_summary import create_company_summary
from _3_extract_job_description_text import extract_job_description_text
from _4_extract_job_industry import extract_job_industry
from _5_generate_resume_text import generate_resume_text
from _6_assemble_new_resume import assemble_new_resume

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_resume_for_job_application(force_run_all=False):
    logging.info("Starting resume creation process.")

    logging.info("Fetching all accomplishments.")
    all_accomplishments = get_all_accomplishments(force_run=force_run_all)

    logging.info("Creating company summary.")
    company_summary = create_company_summary(force_run=force_run_all)

    logging.info("Extracting job description text.")
    job_description_text = extract_job_description_text(force_run=force_run_all)

    logging.info("Extracting job industry.")
    job_industry = extract_job_industry(force_run=force_run_all, job_description=job_description_text,
                                        company_summary=company_summary)

    logging.info("Generating resume text.")
    resume_text = generate_resume_text(accomplishments=all_accomplishments, company_summary=company_summary,
                                       job_description=job_description_text, job_industry=job_industry)

    # TODO ADD personal_info
    logging.info("Assembling new resume.")
    assemble_new_resume(generated_resume_text=resume_text)

    logging.info("Resume creation process completed.")
    return


if __name__ == "__main__":
    create_resume_for_job_application(force_run_all=False)
from inputs.consts import JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME, \
    COMPANY_SUMMARY_TEMP_FILE_NAME, JOB_INDUSTRY_TEMP_FILE_NAME
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient


def extract_job_industry(
        force_run=False,
        job_description=None,
        company_summary=None,
):
    job_industry = read_temp_file(JOB_INDUSTRY_TEMP_FILE_NAME)
    if job_industry and not force_run:
        return job_industry

    if not job_description:
        job_description = read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    if not company_summary:
        company_summary = read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)
    openai_client = OpenAIClient()
    prompt = f"""
            Please identify the primary industry for the following job posting based on the job description and company summary provided.
            
            ### Job Description:
            {job_description}
            
            ### Company Summary:
            {company_summary}
            
            ### Instructions:
            - Analyze the texts to determine the main industry.
            - Provide a concise answer with only the industry name.
            - Do not include any additional information or commentary.
            - DO not include the word "industry" in your response.
            ### Response:
            """

    job_industry = openai_client.generate_text(prompt)
    job_industry = job_industry.strip()
    save_to_temp_file(job_industry, JOB_INDUSTRY_TEMP_FILE_NAME)
    return job_industry

#
# if __name__ == "__main__":
#     extract_job_industry()

RESUME_FILE_PATH =  "inputs/resume.docx"

JOB_DESCRIPTION_LINK = "https://www.nimbleway.com/job/nlp-engineer-628de?transaction_id=102930a437339b8514403b73014016&coref=1.10.s8C_64E&submissionGuid=8e59a49b-b30a-46b4-8ff1-0ca026118b65&aff_id=29&offer_id=8&344e6a5d_page=2"
COMPANY_BASE_LINK = "https://www.nimbleway.com/"
COMPANY_NAME = "nimbleway"


############ temp files names ############
RESUME_TEXT_TEMP_FILE_NAME = "resume_text"
SHORT_ACCOMPLISHMENTS_TEMP_FILE_NAME = "short_accomplishments"
FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME = "full_accomplishments"


JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME = "job_description_text"
COMPANY_DATA_TEXT_TEMP_FILE_NAME = "company_data_text"
COMPANY_SUMMARY_TEMP_FILE_NAME = "company_summary"
JOB_INDUSTRY_TEMP_FILE_NAME = "job_industry"
PERSONAL_DETAILS_TEMP_FILE_NAME = "personal_details"
##
GENERATED_RESUME_TEXT = "generated_resume_text"

############ temp files names ############


############ company summary prompts ############
COMPANY_SUMMARY_START_PROMPT = (
    f"Please provide a comprehensive summary of the company {COMPANY_NAME} that includes: "
    "\n1. Core business activities and main products/services "
    "\n2. Company culture and values "
    "\n3. Industry position and market differentiation "
    "\n4. Recent developments and growth trajectory "
    "\n5. Technology stack and innovation focus "
    "\n6. Leadership style and organizational structure"
)

COMPANY_SUMMARY_END_PROMPT = (
    "Ensure the summary is thorough and informative, highlighting key themes and insights that could "
    "help in identifying core areas useful for topic modeling analysis. "
    "This summary will be used to generate a company profile to assist in writing a tailored resume "
    "for a job application to this company.\n"
    "Return ONLY the summary text."
)
############ company summary prompts ############

############ accomplishments bullets points prompts ############
DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT = """
You are a professional resume assistant.

Given the following existing accomplishments:

{existing_accomplishments}

And the following resume text:

{resume_text}

Please extract any new accomplishments not already included in the existing accomplishments.
Merge them into the existing accomplishments under the appropriate headings:
- "Professional Experience"
- "Personal Projects"
- "Education"

Ensure the final result is a consolidated list of accomplishments with no duplicate entries,
presented in the same format.

Do not include any additional explanations or text. Provide only the updated accomplishments.
"""

SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT = """
You are a professional resume assistant.

Please extract accomplishments from the following resume text:

{resume_text}

Organize the accomplishments under the appropriate headings:
- "Professional Experience"
- "Personal Projects"
- "Education"

Ensure the final result is a consolidated list of accomplishments presented in a clear, consistent format.

Do not include any additional explanations or text. Provide only the accomplishments.
"""

############ accomplishments bullets points prompts ############

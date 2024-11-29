from inputs.consts import RESUME_TEXT_TEMP_FILE_NAME, JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME, \
    COMPANY_SUMMARY_TEMP_FILE_NAME, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME, JOB_INDUSTRY_TEMP_FILE_NAME, \
    GENERATED_RESUME_TEXT
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient


def generate_resume_text(
        job_description=None,
        company_summary=None,
        accomplishments=None,
        job_industry=None):

    if not accomplishments:
        accomplishments = read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    if not job_description:
        job_description = read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    if not company_summary:
        company_summary = read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)
    if not job_industry:
        job_industry = read_temp_file(JOB_INDUSTRY_TEMP_FILE_NAME)
    openai_client = OpenAIClient()
    # prompt = (
    #     f"You are an expert resume writer specializing in crafting resumes for professionals in the {job_industry} industry. "
    #     f"Your task is to create a compelling, tailored resume that aligns with the job I'm applying for, highlighting my most relevant skills and experiences.\n\n"
    #     f"**Job Description:**\n{job_description}\n\n"
    #     f"**Company Summary:**\n{company_summary}\n\n"
    #     f"**My Accomplishments and Experience:**\n{accomplishments}\n\n"
    #     f"**Instructions:**\n"
    #     f"- **Focus on Relevance**: Prioritize skills, experiences, and accomplishments that are most relevant to the job description and company values.\n"
    #     f"- **Use Professional Language**: Employ a professional tone with strong action verbs and industry-specific terminology.\n"
    #     f"- **Quantify Achievements**: Include measurable results and specific examples to demonstrate the impact of my work.\n"
    #     f"- **Incorporate Keywords**: Use keywords from the job description to optimize the resume for Applicant Tracking Systems (ATS).\n"
    #     f"- **Format**: Structure the resume in the following JSON format:\n"
    #     f"```\n"
    #     f"{{\n"
    #     f"  \"Professional Summary\": \"Your professional summary here.\",\n"
    #     f"  \"Work Experience\": [\n"
    #     f"    {{\"title\": \"Job Title 1\", \"place\": \"Company Name 1\", \"date\": \"Date Range 1\", \"description\": \"[Description of responsibilities and achievements in this role in bullets points.]\"}},\n"
    #     f"    {{\"title\": \"Job Title 2\", \"place\": \"Company Name 2\", \"date\": \"Date Range 2\", \"description\": \"[Description of responsibilities and achievements in this role in bullets points.]\"}},\n"
    #     f"    ...\n"
    #     f"  ],\n"
    #     f"  \"Personal Projects\": [\n"
    #     f"    {{\"title\": \"Project Title 1\", \"date\": \"Date Range 1\", \"description\": \"[Description of the project, your role, and achievements. in bullets points.]\"}},\n"
    #     f"    {{\"title\": \"Project Title 2\", \"date\": \"Date Range 2\", \"description\": \"[Description of the project, your role, and achievements. in bullets points.]\"}},\n"
    #     f"    ...\n"
    #     f"  ],\n"
    #     f"  \"Education\": [\n"
    #     f"    {{\"title\": \"Degree or Certification 1\", \"place\": \"Institution Name 1\",  \"description\": \"[Relevant coursework, honors, or achievements. in bullets points.]\"}},\n"
    #     f"    {{\"title\": \"Degree or Certification 2\", \"place\": \"Institution Name 2\",  \"description\": \"[Relevant coursework, honors, or achievements. in bullets points.]\"}},\n"
    #     f"    ...\n"
    #     f"  ],\n"
    #     f"  \"Skills\": [\"Skill1\", \"Skill2\", ...],\n"
    #     f"  \"Languages\": [\"Language1\", \"Language2\", ...]\n"
    #     f"}}\n"
    #     f"```\n"
    #     f"- **Formatting Preferences**: Provide the output strictly in the JSON format shown above without any additional text or explanations.\n"
    #     f"- **Customization**: Tailor each section to demonstrate how my background makes me an ideal candidate for this specific position.\n"
    #     f"- **Exclude Personal Information**: Do not include personal details such as age, marital status, or photo.\n"
    #     f"- **Avoid Repetition**: Ensure that the content is varied and that each point provides new information.\n\n"
    #     f"Please generate the resume accordingly, ensuring that it is polished, professional, and positions me as a strong candidate for the role. Output the result in the specified JSON format only."
    # )
    prompt = (
        f"You are an expert resume writer specializing in crafting resumes for professionals in the {job_industry} industry. "
        f"Your task is to create a compelling, tailored resume that aligns with the job I'm applying for, highlighting my most relevant skills and experiences.\n\n"
        f"**Job Description:**\n{job_description}\n\n"
        f"**Company Summary:**\n{company_summary}\n\n"
        f"**My Accomplishments and Experience:**\n{accomplishments}\n\n"
        f"**Instructions:**\n"
        f"- **Focus on Relevance**: Only include skills, experiences, and accomplishments that are directly relevant to the job description and company values.\n"
        f"- **Exclude Irrelevant Content**: Do not include any accomplishments or experiences that are not pertinent to the job requirements.\n"
        f"- **Use Professional Language**: Employ a professional tone with strong action verbs and industry-specific terminology.\n"
        f"- **Quantify Achievements**: Include measurable results and specific examples to demonstrate the impact of my work.\n"
        f"- **Incorporate Keywords**: Use keywords from the job description to optimize the resume for Applicant Tracking Systems (ATS).\n"
        f"- **Format**: Structure the resume in the following JSON format:\n"
        f"```\n"
        f"{{\n"
        f"  \"Professional Summary\": \"Your professional summary here.\",\n"
        f"  \"Work Experience\": [\n"
        f"    {{\"title\": \"Job Title 1\", \"place\": \"Company Name 1\", \"date\": \"Date Range 1\", \"description\": \"[Description of responsibilities and achievements in bullet points.]\"}},\n"
        f"    {{\"title\": \"Job Title 2\", \"place\": \"Company Name 2\", \"date\": \"Date Range 2\", \"description\": \"[Description of responsibilities and achievements in bullet points.]\"}},\n"
        f"    ...\n"
        f"  ],\n"
        f"  \"Personal Projects\": [\n"
        f"    {{\"title\": \"Project Title 1\", \"date\": \"Date Range 1\", \"description\": \"[Description of the project, your role, and achievements in bullet points.]\"}},\n"
        f"    {{\"title\": \"Project Title 2\", \"date\": \"Date Range 2\", \"description\": \"[Description of the project, your role, and achievements in bullet points.]\"}},\n"
        f"    ...\n"
        f"  ],\n"
        f"  \"Education\": [\n"
        f"    {{\"title\": \"Degree or Certification 1\", \"place\": \"Institution Name 1\", \"description\": \"[Relevant coursework, honors, or achievements in bullet points.]\"}},\n"
        f"    {{\"title\": \"Degree or Certification 2\", \"place\": \"Institution Name 2\", \"description\": \"[Relevant coursework, honors, or achievements in bullet points.]\"}},\n"
        f"    ...\n"
        f"  ],\n"
        f"  \"Skills\": [\"Skill1\", \"Skill2\", ...],\n"
        f"  \"Languages\": [\"Language1\", \"Language2\", ...]\n"
        f"}}\n"
        f"```\n"
        f"- **Formatting Preferences**: Provide the output strictly in the JSON format shown above without any additional text or explanations.\n"
        f"- **Customization**: Tailor each section to demonstrate how my background makes me an ideal candidate for this specific position.\n"
        f"- **Exclude Personal Information**: Do not include personal details such as age, marital status, or photo.\n"
        f"- **Avoid Repetition**: Ensure that the content is varied and that each point provides new information.\n"
        f"- **Emphasize Relevance**: Exclude any information that is not directly related to the job description or required qualifications.\n\n"
        f"Please generate the resume accordingly, ensuring that it is polished, professional, and positions me as a strong candidate for the role. Output the result in the specified JSON format only."
    )

    generated_resume_text = openai_client.generate_text(prompt)
    save_to_temp_file(generated_resume_text, GENERATED_RESUME_TEXT)
    # print(generated_resume_text)
    return generated_resume_text


# if __name__ == "__main__":
#     generate_resume_text()

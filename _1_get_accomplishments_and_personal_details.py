import docx2txt
from inputs.consts import (
    RESUME_TEXT_TEMP_FILE_NAME,
    DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
    FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME, SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
    PERSONAL_DETAILS_TEMP_FILE_NAME,
)
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient


def extract_text_from_resume_docx(docx_file_path=None, force_run=False):
    text = read_temp_file(RESUME_TEXT_TEMP_FILE_NAME)
    if text and not force_run:
        return text

    text = docx2txt.process(docx_file_path)
    save_to_temp_file(text, RESUME_TEXT_TEMP_FILE_NAME)
    return text


def generate_combined_accomplishments(resume_text, existing_accomplishments):
    openai_client = OpenAIClient()
    if existing_accomplishments:
        prompt = DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT.format(
            existing_accomplishments=existing_accomplishments,
            resume_text=resume_text
        )
    else:
        prompt = SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT.format(
            resume_text=resume_text
        )
    generated_text = openai_client.generate_text(prompt)
    return generated_text.strip()


def get_all_accomplishments(force_run=False, accomplishments_file_path=None, resume_file_path=None):
    updated_accomplishments = read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    if updated_accomplishments and not force_run:
        return updated_accomplishments

    resume_text = extract_text_from_resume_docx(docx_file_path=resume_file_path, force_run=force_run)
    existing_accomplishments = read_temp_file(accomplishments_file_path)

    updated_accomplishments = generate_combined_accomplishments(resume_text, existing_accomplishments)
    save_to_temp_file(updated_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    return updated_accomplishments


def get_personal_details(force_run=False, resume_file_path=None):
    personal_details = read_temp_file(PERSONAL_DETAILS_TEMP_FILE_NAME)
    if personal_details and not force_run:
        return personal_details

    resume_text = extract_text_from_resume_docx(docx_file_path=resume_file_path, force_run=force_run)
    openai_client = OpenAIClient()
    prompt = f"""
    Extract and return ONLY the personal details mentioned in the following text in the JSON format with keys: name, phone_number, linkedin, github, email, and address:

    {resume_text}
    """
    personal_details = openai_client.generate_text(prompt).strip()
    save_to_temp_file(personal_details, PERSONAL_DETAILS_TEMP_FILE_NAME)

    return personal_details

# if __name__ == "__main__":
#     get_all_accomplishments()

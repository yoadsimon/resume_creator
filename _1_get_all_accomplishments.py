import docx2txt
from inputs.consts import (
    RESUME_FILE_PATH,
    RESUME_TEXT_TEMP_FILE_NAME,
    SHORT_ACCOMPLISHMENTS_TEMP_FILE_NAME, DEFAULT_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
    FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME, SECONDARY_ACCOMPLISHMENTS_BULLETS_POINTS_PROMPT,
)
from utils.general_utils import read_temp_file, save_to_temp_file
from utils.open_ai import OpenAIClient


def extract_text_from_docx(docx_file_path):
    text = docx2txt.process(docx_file_path)
    save_to_temp_file(text, RESUME_TEXT_TEMP_FILE_NAME)
    return text


def get_resume_text():
    resume_text = read_temp_file(RESUME_TEXT_TEMP_FILE_NAME)
    if resume_text is None:
        resume_text = extract_text_from_docx(RESUME_FILE_PATH)
    return resume_text


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


def get_all_accomplishments(force_run=False):
    updated_accomplishments = read_temp_file(FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    if updated_accomplishments and not force_run:
        return updated_accomplishments

    resume_text = get_resume_text()
    existing_accomplishments = read_temp_file(SHORT_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    updated_accomplishments = generate_combined_accomplishments(resume_text, existing_accomplishments)
    save_to_temp_file(updated_accomplishments, FULL_ACCOMPLISHMENTS_TEMP_FILE_NAME)
    return updated_accomplishments


# if __name__ == "__main__":
#     get_all_accomplishments()

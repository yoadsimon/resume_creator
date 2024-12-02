from inputs.consts import GENERATED_RESUME_TEXT, PERSONAL_DETAILS_TEMP_FILE_NAME
from utils.docx_writer import write_resume_to_docx
from utils.general_utils import read_temp_file
from _5_generate_resume_text import generate_resume_text
import json
import re

from utils.resume_details import ResumeDetails


def read_generated_resume_text_to_dict(generated_resume_text=None, max_retries=3, use_o1_model=False):
    if generated_resume_text is None:
        generated_resume_text = read_temp_file(GENERATED_RESUME_TEXT)

    json_match = re.search(r'\{.*\}', generated_resume_text, re.DOTALL)

    if json_match:
        json_content = json_match.group(0)
        resume_dict = json.loads(json_content)
        # lower the keys and replace spaces with underscores
        resume_dict = {key.lower().replace(" ", "_"): value for key, value in resume_dict.items()}
        return resume_dict

    if max_retries > 0:
        return read_generated_resume_text_to_dict(generate_resume_text(use_o1_model=use_o1_model), max_retries - 1)

    raise ValueError("No JSON content found in the generated resume text.")


def read_generated_personal_info_to_dict(personal_info):
    if personal_info is None:
        personal_info = read_temp_file(PERSONAL_DETAILS_TEMP_FILE_NAME)

    json_match = re.search(r'\{.*\}', personal_info, re.DOTALL)

    if not json_match:
        raise ValueError("No JSON content found in the personal info text.")
    json_content = json_match.group(0)
    personal_info = json.loads(json_content)
    personal_info = {key.lower().replace(" ", "_"): value for key, value in personal_info.items()}
    return personal_info


def get_resume_details(generated_resume_text=None, personal_info=None, use_o1_model=False) -> ResumeDetails:
    resume_dict = read_generated_resume_text_to_dict(generated_resume_text, use_o1_model=use_o1_model)
    personal_info = read_generated_personal_info_to_dict(personal_info)
    resume_details = ResumeDetails(**resume_dict, **personal_info)
    return resume_details


def assemble_new_resume(generated_resume_text=None,
                        personal_info=None,
                        use_o1_model=False):
    resume_details: ResumeDetails = get_resume_details(generated_resume_text, personal_info, use_o1_model)
    write_resume_to_docx(resume_details)
    return

# if __name__ == "__main__":
#     assemble_new_resume()

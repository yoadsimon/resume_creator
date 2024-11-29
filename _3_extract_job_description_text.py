import requests
from bs4 import BeautifulSoup
import time

from inputs.consts import JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME
from utils.general_utils import read_temp_file, save_to_temp_file


def extract_text_from_link(url):
    try:
        for i in range(10):  # Retry up to 10 times
            response = requests.get(url)
            if response.status_code != 202:
                response.raise_for_status()
                break
            print(f"Attempt {i + 1}: Still processing, waiting 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds before the next retry
        else:
            print("Request is still not processed after several attempts.")
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.find_all(text=True)
    output = ''
    blacklist = [
        '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'
    ]

    for text in texts:
        if text.parent.name not in blacklist:
            output += '{} '.format(text)

    job_description_text = output.strip()
    save_to_temp_file(job_description_text, JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    return job_description_text


def extract_job_description_text(force_run=False, job_description_link=None):
    job_description_text = read_temp_file(JOB_DESCRIPTION_TEXT_TEMP_FILE_NAME)
    if job_description_text and not force_run:
        return job_description_text

    job_description_text = extract_text_from_link(job_description_link)
    return job_description_text

# if __name__ == "__main__":
#     run()

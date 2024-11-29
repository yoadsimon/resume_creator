import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from tqdm import tqdm

from inputs.consts import COMPANY_BASE_LINK, COMPANY_DATA_TEXT_TEMP_FILE_NAME, COMPANY_SUMMARY_START_PROMPT, \
    COMPANY_SUMMARY_END_PROMPT, COMPANY_SUMMARY_TEMP_FILE_NAME
from utils.general_utils import save_to_temp_file, read_temp_file
from utils.npl_utils import Encoder
from utils.open_ai import OpenAIClient


def crawl_and_extract_text(base_url, all_text, visited_urls, encoder, max_tokens=100000, max_depth=1, delay=0.1):
    def is_same_domain(url):
        return urlparse(url).netloc == domain

    def handle_url(url, depth):
        if url in visited_urls or depth > max_depth:
            return

        if encoder.get_num_tokens(' '.join(all_text)) > max_tokens:
            print("Reached max tokens limit")
            return

        print(f"Current tokens: {encoder.get_num_tokens(' '.join(all_text))}")
        time.sleep(0.01)

        try:
            response = requests.get(url)
            if response.status_code == 202:
                while response.status_code == 202:
                    print("Received 202 response, waiting for 1 seconds")
                    time.sleep(1)
                    response = requests.get(url)
            visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = f"'{url}:\n{soup.get_text(separator=' ', strip=True)}'"
            all_text.append(page_text)
            for link in tqdm(soup.find_all('a', href=True), desc=f"Crawling {url}", leave=False):
                full_url = urljoin(base_url, link['href'])
                if is_same_domain(full_url) and full_url not in visited_urls:
                    time.sleep(delay)
                    handle_url(full_url, depth + 1)
        except Exception as e:
            raise e

    domain = urlparse(base_url).netloc
    handle_url(base_url, 0)


def get_company_text_data():
    company_text_data = read_temp_file(COMPANY_DATA_TEXT_TEMP_FILE_NAME)
    if company_text_data is None:
        visited_urls = set()
        all_text = []
        crawl_and_extract_text(base_url=COMPANY_BASE_LINK,
                               all_text=all_text,
                               visited_urls=visited_urls,
                               encoder=Encoder(),
                               max_depth=1)
        company_text_data = ' '.join(all_text)
        save_to_temp_file(company_text_data, COMPANY_DATA_TEXT_TEMP_FILE_NAME)
    return company_text_data


def create_company_summary(force_run=False):
    company_summary = read_temp_file(COMPANY_SUMMARY_TEMP_FILE_NAME)
    if company_summary and not force_run:
        return company_summary

    company_text_data = get_company_text_data()
    openai_client = OpenAIClient()
    prompt = f"{COMPANY_SUMMARY_START_PROMPT}\n\nStart of company details:\n{company_text_data}\nEnd of company details\n\n{COMPANY_SUMMARY_END_PROMPT}"
    company_summary = openai_client.generate_text(prompt)
    save_to_temp_file(company_summary, COMPANY_SUMMARY_TEMP_FILE_NAME)
    return company_summary

#
# if __name__ == "__main__":
#     create_company_summary()

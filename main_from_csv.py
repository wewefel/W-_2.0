import os
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
BING_API_KEY = os.getenv('BING_API_KEY')
CUSTOM_CONFIG_ID = os.getenv('CUSTOM_CONFIG_ID')

# Feel free to change "num_results". It controls the amount of URLs the function will look at.
def bing_search(company_name, api_key, custom_config_id, num_results=5, excluded_site=''):
    search_query = f'intext:"{company_name}" company sustainability -site:{excluded_site}' if excluded_site else f'intext:"{company_name}" company sustainability'
    search_url = f"https://api.bing.microsoft.com/v7.0/custom/search?q={search_query}&customconfig={custom_config_id}"
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    params = {'count': num_results}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to retrieve search results: {response.status_code}, {response.text}")
        return []
    results = response.json().get('webPages', {}).get('value', [])
    if not results:
        print("No results found.")
        return []
    urls = [result['url'] for result in results if excluded_site not in result['url']]
    print(f"Found URLs: {urls}")
    return urls

# Function to scrape the webpage
def scrape_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_driver_path = r"C:\....\chromedriver.exe" # Change this to your own chromedriver.exe path
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        texts = soup.stripped_strings
        content = "\n".join(texts)
    except TimeoutException:
        print(f"Timeout while trying to scrape {url}")
        content = ""
    finally:
        driver.quit()
    return content

# Function to filter sustainability content using GPT-4o-mini.
# The prompt may be fine-tuned to give better results.
def filter_sustainability_content(chunk):
    prompt = (
        "Please extract and retain only the information related to the specific company's sustainability (environmental, social, governance) claims and efforts. "
        "Also get info about the company's address and company size or number of employees. If no sustainability information is found in the current chunk, do not write anything. "
        "Also, while filtering the text, make sure to remove any empty lines or empty spaces. The final extracted results should only be organized, complete sentences about the company's sustainability practices."
        "from the following text:\n\n"
        f"{chunk}\n\n"
        "Filtered content:"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that filters text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0.5,
    )
    return response.choices[0].message['content'].strip()

def split_text_into_chunks(text, max_tokens=4096):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Double check to make sure company name is in website's text
def contains_exact_company_name(text, company_name):
    return company_name.lower() in text.lower()

def main():
    with open('companies.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        companies = list(reader)
    
    for company in companies:
        company_name = company['Company']
        excluded_site = company['Website']
        urls = bing_search(company_name, BING_API_KEY, CUSTOM_CONFIG_ID, excluded_site=excluded_site)
        print(f"Found {len(urls)} URLs for {company_name}")

        filtered_content = []

        with open(f"{company_name}_unfiltered.txt", "w", encoding="utf-8") as file:
            # Use ThreadPoolExecutor to scrape URLs in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust the number of workers as needed
                future_to_url = {executor.submit(scrape_url, url): url for url in urls}
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        content = future.result()
                        if contains_exact_company_name(content, company_name):
                            print(f"Scraped {url} and found exact company name.")
                            file.write(f"URL: {url}\n")
                            file.write(content)
                            file.write("\n" + "="*80 + "\n")
                            filtered_content.append(content)
                        else:
                            print(f"Scraped {url} but did not find the exact company name.")
                    except Exception as exc:
                        print(f"Error scraping {url}: {exc}")

        print(f"Scraping complete for {company_name}. Content saved to {company_name}_unfiltered.txt")

        with open(f"{company_name}_unfiltered.txt", "r", encoding="utf-8") as file:
            data = file.read()

        chunks = split_text_into_chunks(data, max_tokens=4000)
        filtered_content = []

        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} for {company_name}...")
            filtered_chunk = filter_sustainability_content(chunk)
            filtered_content.append(filtered_chunk)

        with open(f"{company_name}_filtered.txt", "w", encoding="utf-8") as file:
            file.write("\n\n".join(filtered_content))

        print(f"Filtering complete for {company_name}. Content saved to {company_name}_filtered.txt")

        # Sleep to avoid Bing request limit
        time.sleep(5)

if __name__ == "__main__":
    main()

<a name="top"></a>

# Sustainability Web Scraper 2.0

## Table of Contents
1. [Overview](#overview)
   - [Features](#features)
2. [Setup](#setup)
   - [Prerequisites](#prerequisites)
   - [Running the script](#running-the-script)
3. [Limitations](#limitations)


## Overview
This project consists of a Python web scraper that searches for and extracts information related to environmental and sustainability efforts of a specified company from URLs that are not the company's official website.  
  
We use selenium for scraping and GPT-4o-mini for text processing.

### Features
- **Custom Bing Search API**: Leverages Bing's Custom Search JSON API to retrieve relevant URLs based on the query.
- **Content Filtering**: Excludes URLs that are from the company's official website or contain undesirable paths (e.g., downloads or lists).
- **Concurrency**: Uses `ThreadPoolExecutor` for concurrent scraping, enhancing the speed and efficiency of data collection (might remove).
- **Text Classification**: Employs GPt-4o-mini API to organize text and extract only information related to sustainability.




## Setup

### Prerequisites

**1. Ensure Python >= 3.10 is installed:**
* You can check this by running python3 --version in your terminal or command prompt. If it’s not installed, you may install it from the official Python website [here](https://www.python.org/downloads).

**2. Create an account for Bing Custom Search API (HSG members: no need to create your own account and instance; just copy my key and ID from Slack).**
* Go [here](https://www.microsoft.com/en-us/bing/apis/bing-custom-search-api) and sign into your Microsoft account.
* Create 'New Instance'
* In Configuration, add an Active, Blocked, or Pinned URL (any arbitrary URL) so you can click 'Publish' in the top right.
* Then go to 'Production, then copy the Custom Configuration ID.
* Then click 'Click to issue free trial key' and follow the steps to obtain your API_KEY.
* Add your `API_KEY` and `CUSTOM_CONFIG_ID` to the .env file.

**3. Create an OpenAI account and get an API key (or just use mine from Slack):**
* Go [here](https://platform.openai.com/docs/overview) to create an account and make your own API key.

**4. Install ChromeDriver:**
* Find your version by opening Chrome, click on the three dots in the upper right, go to **Help** > **About Google Chrome**, and note the version number of your Chrome browser.
* If your version is > 115, go [here](https://googlechromelabs.github.io/chrome-for-testing/)
* After downloading ChromeDriver, extract the contents of the ZIP file.
* Optional: to make ChromeDriver accessible globally, move the extracted 'chromedriver.exe' to a directory of your choice (e.g., 'C:\WebDrivers'), edit the sustem environment variables, edit the 'Path' variable, and click New and add the path to the directory where you placed 'chromedriver.exe'.
* Copy the path to 'chromedriver.exe' and paste in line 46 of main.py.

**4. Clone Github Repo:**
* Go to the [Github repo](https://github.com/wewefel/Sustainability_Web_Scraper_2.0)
* Method 1: Click code, download as zip file, then extract all.
  * Method 2: Use 'git clone'
  * Open your terminal or command prompt
  * Navigate to the directory where you want to clone the repository (this example uses desktop as the directory, but feel free to change).  
  * On Windows:
   ``` sh
   cd Desktop
   ```
  * On Mac or Linux:
   ``` sh
   cd ~/Desktop
   ```
  * Then clone the repository:
   ``` sh
   git clone https://github.com/wewefel/Sustainability_Web_Scraper_2.0.git
   ```
**5. Install Requirements:**
* Open terminal or command prompt (recommended: create a virtual environment first):
  ``` sh
  pip install openai requests beautifulsoup4 python-dotenv selenium
  ```
  
[Back to Top](#top)

## Limitations

* Last updated 7/30/2024
  * I have created a version of the code that is capable of taking a .csv file containing a list of companies and their corresponding websites for large-scale 3rd party capture, but this is not complete yet.
  * Once code is capable of taking .csv file of list of companies, the code will make a separate .txt file for each company.
  * Incorrect company name can lead to incorrect or lack of search engine results.
  * Areas in need of improvement: fine-tuning the GPT prompt, fine-tuning the search input (current uses "{company_name} company sustainability" as input), removing the stupid concurrency features I added because the random error notifications in the terminal are so annoying and I don't even think it improved the scraping speed by that much.

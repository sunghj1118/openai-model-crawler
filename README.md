# OpenAI GPT Model Specification Crawler

This project contains a Python script that automatically crawls the official OpenAI API documentation to gather specifications for all listed GPT models. It uses Selenium to control a web browser, ensuring that dynamically loaded content is captured correctly. The collected data is then cleaned to remove duplicates and saved into a structured CSV file for easy analysis.

## Features

* **Dynamic Content Handling**: Uses Selenium and ChromeDriver to render JavaScript on the target page, allowing it to scrape content that is loaded dynamically.

* **Robust Scraping**: Navigates from the main models page to each individual model's detail page to gather specific information like context window and max output tokens.

* **Data Cleaning**: Automatically removes duplicate entries based on the model name and URL to ensure the final dataset is clean.

* **Structured Output**: Saves the scraped data into a `gpt_model_specs.csv` file with clear headers for model name, description, URL, and technical specifications.

* **Respectful Crawling**: Includes a `User-Agent` header to identify as a standard browser and incorporates a small delay between requests to avoid overwhelming the server.

## File Structure

Here is an overview of the project's file structure:

```
└── 📁gpt-spec-crawler
└── 📁.venv               # Directory for the Python virtual environment
├── .gitignore            # Specifies files for Git to ignore (e.g., .venv, .csv)
├── gpt_crawler.py        # The main Python script that performs the web crawling
├── gpt_model_specs.csv   # The output CSV file where scraped data is stored
├── poetry.lock           # Poetry lock file for deterministic dependency installation
├── pyproject.toml        # Poetry/pyproject configuration file for managing dependencies
├── README.md             # This documentation file
└── requirements.txt      # Lists the Python dependencies required for the project
```
## Requirements

The script relies on several Python libraries. You can install them using pip with the provided `requirements.txt` file:

`pip install -r requirements.txt`


The required libraries are:

* `requests`

* `beautifulsoup4`

* `pandas`

* `selenium`

* `webdriver-manager`

## Usage

To run the crawler, simply execute the Python script from your terminal:  

`python gpt_crawler.py`

The script will launch a headless Chrome browser, scrape the data, and print the results to the console. A `gpt_model_specs.csv` file will be created or overwritten in the project directory with the latest model specifications.
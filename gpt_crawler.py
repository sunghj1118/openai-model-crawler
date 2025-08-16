import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Installation Note ---
# This script now requires Selenium and webdriver-manager.
# You can install them using pip:
# pip install selenium webdriver-manager

def get_model_specs():
    """
    Crawls the OpenAI models page using Selenium to handle JavaScript rendering
    and extracts specifications for each model.

    Returns:
        pandas.DataFrame: A DataFrame containing the model specifications,
                          or an empty DataFrame if the page cannot be accessed.
    """
    base_url = "https://platform.openai.com"
    url = f"{base_url}/docs/models"
    
    # Add a User-Agent header to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Setup Selenium WebDriver
    # webdriver-manager will automatically download and manage the correct chromedriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser window)
    options.add_argument(f'user-agent={headers["User-Agent"]}') # Set user agent
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        # Wait for the model links to be present on the page.
        # This is crucial for pages that load content dynamically.
        # We wait for up to 10 seconds for an element with href starting with '/docs/models/'
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/docs/models/']"))
        )
        
        # Get the page source after JavaScript has loaded the content
        page_source = driver.page_source
        
    except Exception as e:
        print(f"Error during Selenium page load: {e}")
        return pd.DataFrame()
    finally:
        if 'driver' in locals():
            driver.quit() # Always close the browser

    soup = BeautifulSoup(page_source, 'html.parser')

    model_links = soup.find_all('a', href=lambda href: href and href.startswith('/docs/models/'))

    if not model_links:
        print("Could not find any links to model detail pages even after using Selenium. The website structure may have changed significantly.")
        return pd.DataFrame()

    model_data = []

    # We iterate through the links found on the main page
    for link in model_links:
        try:
            model_name_element = link.find('div', class_='font-semibold')
            model_name = model_name_element.text.strip() if model_name_element else 'N/A'

            description_element = link.find('div', class_='text-sm')
            description = description_element.text.strip() if description_element else 'No description available.'
            
            details_url = f"{base_url}{link['href']}"
            
            if details_url == url:
                continue

            specs = {
                "Model": model_name,
                "Description": description,
                "Details URL": details_url,
                "Context Window": "N/A",
                "Max Output": "N/A"
            }
            
            # Since we are already making many requests, we can continue to use requests for detail pages
            # This is often faster than using Selenium for every single page.
            try:
                time.sleep(0.1) 
                details_response = requests.get(details_url, headers=headers)
                details_response.raise_for_status()
                details_soup = BeautifulSoup(details_response.content, 'html.parser')
                
                spec_table = details_soup.find('table')
                if spec_table:
                    for row in spec_table.find('tbody').find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) == 2:
                            spec_name = cells[0].text.strip().lower()
                            spec_value = cells[1].text.strip()
                            
                            if 'context window' in spec_name:
                                specs["Context Window"] = spec_value
                            elif 'max output' in spec_name:
                                specs["Max Output"] = spec_value

            except requests.exceptions.RequestException as e:
                print(f"Could not fetch or parse details for {model_name} from {details_url}: {e}")
            
            model_data.append(specs)

        except Exception as e:
            print(f"Error parsing a model link block: {e}")
            continue

    return pd.DataFrame(model_data)

if __name__ == "__main__":
    model_specs_df = get_model_specs()
    if not model_specs_df.empty:
        # Remove duplicate rows based on the 'Model' and 'Details URL' columns
        model_specs_df.drop_duplicates(subset=['Model', 'Details URL'], inplace=True)

        print("Successfully crawled GPT model specifications:")
        print(model_specs_df.to_string())
        
        try:
            model_specs_df.to_csv("gpt_model_specs.csv", index=False)
            print("\nData saved to gpt_model_specs.csv")
        except IOError as e:
            print(f"\nError saving data to CSV: {e}")


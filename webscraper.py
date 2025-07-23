from crewai.tools import tool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


@tool("Web scraper tool")
def webscraper(url: str):
    """
    Loads a URL using a headless Chrome browser with Selenium

    :param url: The URL to load
    :return: The text content of the page
    """
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        # Wait for the page to load and flight results to appear
        time.sleep(25)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract text content
        content = soup.get_text(separator='\n', strip=True)
        
        return content
        
    except Exception as e:
        return f"Error loading page: {str(e)}"
    
    finally:
        driver.quit() 

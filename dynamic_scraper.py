from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import requests
import time
import os

# Website to scrape (replace with your dynamic website URL)
url = "https://quotes.toscrape.com/js/"  # A JavaScript-rendered quotes website for testing

# Your Groq API key (replace with your actual key)
API_KEY = "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"

# Groq API endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def setup_driver():
    """Setup and return an Edge WebDriver with appropriate options"""
    try:
        edge_options = Options()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36")
        
        try:
            # Use EdgeChromiumDriverManager to handle driver installation
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
            return driver
        except Exception as e:
            print(f"EdgeDriver setup failed: {e}")
            print("Please make sure Microsoft Edge is installed on your system.")
            raise
    except Exception as e:
        print(f"Failed to setup Edge driver: {e}")
        print("Please make sure Microsoft Edge is installed on your system.")
        raise

# Fetch HTML content from the website using Selenium
def fetch_content(url):
    driver = setup_driver()
    try:
        print("Loading page with Selenium...")
        driver.get(url)
        # Wait for the page to load (adjust timeout and conditions as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Add a small delay to ensure dynamic content loads
        time.sleep(2)
        return driver.page_source
    finally:
        driver.quit()

# Extract structured text from HTML
def extract(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Extract text from all visible elements
    def is_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        return True

    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings_text = ' '.join([h.get_text(strip=True) for h in headings if is_visible(h)])

    paragraphs = soup.find_all('p')
    paragraphs_text = ' '.join([p.get_text(strip=True) for p in paragraphs if is_visible(p)])

    links = soup.find_all('a', href=True)
    links_text = ' '.join([a.get_text(strip=True) for a in links if is_visible(a)])

    lists = soup.find_all(['ul', 'ol'])
    lists_text = ' '.join([l.get_text(strip=True) for l in lists if is_visible(l)])

    # Also get text from div elements that might contain dynamic content
    divs = soup.find_all('div')
    divs_text = ' '.join([d.get_text(strip=True) for d in divs if is_visible(d) and d.get_text(strip=True)])

    return (
        f"Headings:\n{headings_text}\n\n"
        f"Paragraphs:\n{paragraphs_text}\n\n"
        f"Links:\n{links_text}\n\n"
        f"Lists:\n{lists_text}\n\n"
        f"Additional Dynamic Content:\n{divs_text}\n\n"
    )

# Function to get response from Groq API
def get_groq_response(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    resp_json = response.json()
    return resp_json['choices'][0]['message']['content']

# Interactive console to chat with Groq
def console(extracted_text):
    print("Dynamic Website Scraper")
    print("Hello! Ask questions about the dynamic website content. Type 'exit' to quit.")
    while True:
        user_input = input("YOU: ")
        if user_input.lower() == "exit":
            break
        prompt = f"Question: {user_input}\nBased on the following info:\n{extracted_text}"
        answer = get_groq_response(prompt)
        print(f"Groq: {answer}")

if __name__ == "__main__":
    print(f"Fetching content from {url}")
    content = fetch_content(url)
    print("Extracting text...")
    extracted_text = extract(content)
    console(extracted_text) 
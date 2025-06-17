import requests
from bs4 import BeautifulSoup

# Website to scrape (replace with your static website URL)
url = "https://en.wikipedia.org/wiki/Web_scraping"

# Your Groq API key (replace with your actual key)
API_KEY = "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"

# Groq API endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Fetch HTML content from the website
def fetch_content(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.text

# Extract structured text from HTML
def extract(content):
    soup = BeautifulSoup(content, 'html.parser')

    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings_text = ' '.join([h.get_text(strip=True) for h in headings])

    paragraphs = soup.find_all('p')
    paragraphs_text = ' '.join([p.get_text(strip=True) for p in paragraphs])

    links = soup.find_all('a', href=True)
    links_text = ' '.join([a.get_text(strip=True) for a in links])

    lists = soup.find_all(['ul', 'ol'])
    lists_text = ' '.join([l.get_text(strip=True) for l in lists])

    return (
        f"Headings:\n{headings_text}\n\n"
        f"Paragraphs:\n{paragraphs_text}\n\n"
        f"Links:\n{links_text}\n\n"
        f"Lists:\n{lists_text}\n\n"
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
    print("Static Website Scraper")
    print("Hello! Ask questions about the static website content. Type 'exit' to quit.")
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
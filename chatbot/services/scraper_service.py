import requests
from bs4 import BeautifulSoup
from services import db

def scrape_url(url):
    """Scrape content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text, None
    except Exception as e:
        return None, f"Error scraping URL: {str(e)}"

def process_scraped_content(url, user_id, save=False):
    """Process scraped content and optionally save it to the database"""
    content, error = scrape_url(url)
    
    if error:
        return None, error
    
    result = {
        'content': content,
        'url': url
    }
    
    # Save scraped content as a document if requested
    if save and content:
        doc_result = db.save_scraped_content(user_id, url, content)
        result['document_id'] = str(doc_result.inserted_id)
    
    return result, None 
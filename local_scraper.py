import requests
from bs4 import BeautifulSoup
# I chose to use ollama in my project as i was really interesetd in the new llama 3.3 and it was free as well!!!
from ollama import chat, ChatResponse

#? Define the URL of the website to be scraped you can use the url of any website that allows it
url = "https://en.wikipedia.org/wiki/Web_scraping"

# we can also utilize proxies if we want but as i'm not going to mass scrape i've made the
# decision to keep the code simple

#!Fetches the HTML content of a webpage.
def fetch_content(url):
    """
    *Parametedrs:
    url (str): The URL of the webpage to fetch.


    *Returns:
    str: The HTML content of the webpage.
    """
    r = requests.get(url)
    return r.text

#! Fetch the content of the specified URL
content = fetch_content(url)

def extract(content):
    soup = BeautifulSoup(content, 'html.parser')
    
    #! Extract headings (h1 to h6 tags)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings_text = ' '.join([heading.get_text() for heading in headings])
    
    #! Extract paragraphs (p tags)
    paragraphs = soup.find_all('p')
    paragraphs_text = ' '.join([para.get_text() for para in paragraphs])

    #! Extract links (a tags with href attribute)
    links = soup.find_all('a', href=True)
    links_text = ' '.join([link.get_text() for link in links])

    #! Extract lists (ul and ol tags)
    lists = soup.find_all(['ul', 'ol'])
    lists_text = ' '.join([lst.get_text() for lst in lists])

    #! Structure the extracted information IN one single string
    structured_text = (
        f"Headings:\n{headings_text}\n\n"
        f"Paragraphs:\n{paragraphs_text}\n\n"
        f"Links:\n{links_text}\n\n"
        f"Lists:\n{lists_text}\n\n"
    )
    # print(structured_text)
    return structured_text

#! Provokes Ollama to generate the response.
def get_ollama_response(prompt):
    """
    *Parameters:
    prompt (str): The prompt or question:

    *Returns:
    str: The respone that was geneerated by Ollama.
    """
    r = chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
    return r['message']['content']

#! Runs an interactive console interacting with the bot
def console(extracted_text):
    """
    *Parameters:
    extracted_text (str): The structured text containing extracted information from the webpage.
    """
    print("Hello. How is your day going? We can start with the evaluation. When done, type 'exit' to quit.")
    while True:
        user_input = input("YOU: ")
        if user_input.lower() == 'exit':
            break
        
        prompt = f"Question: {user_input}\nBased on the following info:\n{extracted_text}"
        r = get_ollama_response(prompt)
        print(f"Ollama: {r}")

if content:
    #! store the contents in the text variable to pass it to the console function
    text = extract(content)
    #! used to run the code
    console(text)

    
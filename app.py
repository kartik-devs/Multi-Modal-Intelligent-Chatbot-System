import os
import requests
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

app = Flask(__name__)
HARDCODED_API_KEY = "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"  
DEFAULT_API_KEY = os.environ.get("GROQ_API_KEY", HARDCODED_API_KEY)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"  # For Groq
LOCAL_MODEL = "llama3"  # For Ollama

class DocumentProcessor:
    @staticmethod
    def read_pdf(file_path):
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text

    @staticmethod
    def read_docx(file_path):
        doc = Document(file_path)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text

    @staticmethod
    def read_txt(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    @staticmethod
    def read_document(file_path):
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == '.pdf':
            return DocumentProcessor.read_pdf(file_path)
        elif extension == '.docx':
            return DocumentProcessor.read_docx(file_path)
        elif extension == '.txt':
            return DocumentProcessor.read_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

class WebScraper:
    @staticmethod
    def scrape_url(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator='\n')
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            return f"Error scraping URL: {str(e)}"

class AIModelHandler:
    @staticmethod
    def get_groq_response(prompt, api_key=None, model=DEFAULT_MODEL):
        
        api_key = api_key or DEFAULT_API_KEY
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()
            resp_json = response.json()
            return resp_json['choices'][0]['message']['content']
        except Exception as e:
            return f"Error getting response from Groq: {str(e)}"

    @staticmethod
    def get_ollama_response(prompt, model=LOCAL_MODEL):
        """Get response from local Ollama instance"""
        if not OLLAMA_AVAILABLE:
            return "Ollama is not available in this environment. Please use Groq API instead."
            
        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error getting response from Ollama: {str(e)}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    context = data.get('context', '')
    model_type = data.get('model_type', 'groq')  # 'ollama' or 'groq'
    api_key = data.get('api_key')  # Custom API key 
    
    if not user_input:
        return jsonify({'response': 'Please enter a message'})
    
    prompt = f"""Question: {user_input}
    
Based on the following context:

{context[:4000]}  # Limiting content length to avoid token limits

Please provide a concise and accurate answer based solely on the provided context."""

    if model_type == 'groq':
        response = AIModelHandler.get_groq_response(prompt, api_key)
    elif model_type == 'ollama':
        response = AIModelHandler.get_ollama_response(prompt)
    else:
        return jsonify({'response': 'Invalid model type specified'})
        
    return jsonify({'response': response})

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'content': 'Please enter a URL'})
    
    content = WebScraper.scrape_url(url)
    return jsonify({'content': content})
    


if not os.path.exists('uploads'):
    os.makedirs('uploads')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
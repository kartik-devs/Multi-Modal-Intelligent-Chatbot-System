import os
import requests
from PyPDF2 import PdfReader
from docx import Document
import tkinter as tk
from tkinter import filedialog

# Your Groq API key (replace with your actual key)
API_KEY = "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"

# Groq API endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def read_pdf(file_path): 
    """Extract text from PDF file"""
    with open(file_path, 'rb') as file:
        pdf = PdfReader(file)
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

def read_docx(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def read_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_document(file_path):
    """Read document based on file extension"""
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == '.pdf':
        return read_pdf(file_path)
    elif extension == '.docx':
        return read_docx(file_path)
    elif extension == '.txt':
        return read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")

def get_groq_response(prompt):
    """Get response from Groq API"""
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

def select_file():
    """Open file dialog to select document"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select Document",
        filetypes=[
            ("Documents", "*.pdf;*.docx;*.txt"),
            ("PDF files", "*.pdf"),
            ("Word files", "*.docx"),
            ("Text files", "*.txt")
        ]
    )
    return file_path

def chat_with_document():
    """Main function to chat about document content"""
    print("Welcome to Document Chat!")
    print("Please select a document file (PDF, DOCX, or TXT)...")
    
    file_path = select_file()
    if not file_path:
        print("No file selected. Exiting...")
        return

    print(f"\nReading document: {os.path.basename(file_path)}")
    try:
        document_text = read_document(file_path)
        print("\nDocument loaded successfully!")
        print("\nYou can now ask questions about the document. Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYOU: ")
            if user_input.lower() == 'exit':
                break
                
            prompt = f"""Question: {user_input}
            
Based on the following document content:

{document_text[:4000]}  # Limiting content length to avoid token limits

Please provide a concise and accurate answer based solely on the document content."""

            print("\nThinking...")
            try:
                answer = get_groq_response(prompt)
                print(f"\nASSISTANT: {answer}")
            except Exception as e:
                print(f"\nError getting response: {e}")
                print("Please try again or type 'exit' to quit.")

    except Exception as e:
        print(f"\nError reading document: {e}")

if __name__ == "__main__":
    chat_with_document() 
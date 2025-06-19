import os
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from werkzeug.utils import secure_filename
from services import config, db

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

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
    doc = DocxDocument(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def read_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
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

def process_uploaded_file(file, user_id):
    """Process an uploaded file and save it to the database"""
    if not file or file.filename == '':
        return None, "No file selected"
        
    if not allowed_file(file.filename):
        return None, f"File type not allowed. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    # Create user directory if it doesn't exist
    user_dir = os.path.join(config.UPLOAD_FOLDER, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        
    # Save file
    file_path = os.path.join(user_dir, filename)
    file.save(file_path)
    
    # Extract text from document
    try:
        text = read_document(file_path)
    except Exception as e:
        return None, f"Error processing document: {str(e)}"
        
    # Save document metadata to database
    result = db.save_document(user_id, filename, file_path, text)
    
    return {
        'id': str(result.inserted_id),
        'filename': filename,
        'preview': text[:200] + '...' if len(text) > 200 else text
    }, None 
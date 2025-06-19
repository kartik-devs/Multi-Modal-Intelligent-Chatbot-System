import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/chatbot")

# API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
LOCAL_MODEL = "llama3"

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) 
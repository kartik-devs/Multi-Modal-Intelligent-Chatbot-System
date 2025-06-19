# Multi-Modal Intelligent Chatbot System

A versatile chatbot application that can process content from multiple sources (documents, web pages) and provide intelligent responses using AI. This version includes user authentication, document management, conversation history, and more.

## Features

- **User Authentication**: Secure login and registration with JWT tokens
- **Document Processing**: Extract text from PDF, DOCX, and TXT files
- **Web Scraping**: Extract content from websites
- **AI-powered Responses**: Uses Groq API or local Ollama models
- **Conversation History**: Save and retrieve past conversations
- **RESTful API**: Well-structured API for frontend integration
- **Database Integration**: MongoDB for data persistence

## Project Structure

```
chatbot/
│
├── api/                    # API routes
│   ├── __init__.py
│   ├── auth_routes.py      # Authentication routes
│   ├── chat_routes.py      # Chat functionality
│   ├── conversation_routes.py # Conversation management
│   ├── document_routes.py  # Document management
│   └── scraper_routes.py   # Web scraping endpoints
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── ai_service.py       # AI model integration
│   ├── config.py           # Configuration settings
│   ├── db.py               # Database models and functions
│   ├── document_service.py # Document processing
│   └── scraper_service.py  # Web scraping functionality
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── auth_utils.py       # Authentication utilities
│
├── uploads/                # Folder for uploaded documents
│
├── static/                 # Static files (CSS, JS)
│
├── templates/              # HTML templates
│   └── index.html          # Main template
│
├── app.py                  # Main Flask application
├── requirements.txt        # Project dependencies
└── .env.example            # Example environment variables
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- Groq API key (or Ollama for local models)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/chatbot.git
   cd chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the API at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/register`: Register a new user
- `POST /api/login`: Login a user
- `GET /api/user`: Get current user information

### Documents
- `POST /api/documents/upload`: Upload a document
- `GET /api/documents`: Get all user documents
- `GET /api/documents/{id}`: Get a specific document

### Conversations
- `GET /api/conversations`: Get all user conversations
- `GET /api/conversations/{id}`: Get a specific conversation

### Chat
- `POST /api/chat`: Send a message and get AI response

### Web Scraping
- `POST /api/scrape`: Scrape content from a URL

## Legacy Endpoints (for backward compatibility)
- `POST /chat`: Get AI response without authentication
- `POST /scrape`: Scrape URL without authentication

## Environment Variables

- `MONGO_URI`: MongoDB connection string
- `GROQ_API_KEY`: Groq API key for AI responses
- `JWT_SECRET_KEY`: Secret key for JWT token generation

## Acknowledgments

- Built with Flask, a lightweight Python web framework
- Uses MongoDB for data storage
- Integrates with Groq API for AI processing
- Optional integration with Ollama for local processing 
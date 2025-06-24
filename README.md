# Multi-Modal Intelligent Chatbot System

A powerful chatbot system that can interact with AI models, manage documents, and scrape web content.

## Features

- **Multi-Provider AI Chat**: Support for multiple AI providers (Groq, OpenAI, Anthropic, Ollama)
- **Document Processing**: Upload and chat with document context (PDF, DOCX, TXT)
- **Web Scraping**: Extract content from websites for chatting
- **User Authentication**: Register, login, and protected routes
- **API Key Management**: Add and manage API keys for different providers
- **MongoDB Integration**: Scalable database backend

## Architecture

- **Backend**: Python/Flask
- **Frontend**: React/Bootstrap
- **Database**: MongoDB

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd chatbot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   # MongoDB Connection
   MONGO_URI=your_mongodb_connection_string

   # API Keys
   GROQ_API_KEY=your_groq_api_key

   # JWT Configuration
   JWT_SECRET_KEY=your_secret_key
   ```

4. Run the server:
   ```
   python wsgi.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd chatbot-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables in `.env`:
   ```
   REACT_APP_API_URL=http://127.0.0.1:5000
   ```

4. Run the development server:
   ```
   npm start
   ```

## Usage

1. Register or login with your credentials
2. Upload documents or scrape web content
3. Chat with AI about the uploaded content
4. Manage your API keys in the settings

## License

MIT 
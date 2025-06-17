# Multi-Modal Intelligent Chatbot System

A versatile chatbot application that can process content from multiple sources (documents, web pages) and provide intelligent responses using AI.

## Features

- **Multi-modal input**: Process text from documents or web pages
- **AI-powered responses**: Uses cloud-based Groq API by default or local Ollama models
- **Document processing**: Extracts text from PDF, DOCX, and TXT files
- **Web scraping**: Extracts content from websites
- **Clean web interface**: Easy-to-use UI for interacting with the chatbot
- **Mobile-friendly**: Responsive design works on phones and tablets
- **Cloud deployable**: Ready to deploy to Render for interviews
- **Security-focused**: Supports environment variables for API keys

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flask and other dependencies
- (Optional) Ollama for local model processing
- Private GitHub repository (to protect API keys)

### Local Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   cd YOUR-REPOSITORY
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For local model support, install Ollama:
   - Visit [Ollama's website](https://ollama.ai/) for installation instructions
   - Pull the llama3 model: `ollama pull llama3`

4. (Optional) Set the environment variable for the Groq API key:
   ```bash
   # On Windows
   set GROQ_API_KEY=your_api_key_here
   
   # On macOS/Linux
   export GROQ_API_KEY=your_api_key_here
   ```

### Running Locally

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Cloud Deployment (Recommended for Interviews)

For a permanent, interview-ready deployment:

1. **Make your repository private** to protect the API key
2. Follow the instructions in `deploy_instructions.md` to deploy to Render
3. Set up environment variables in Render for secure API key storage
4. Generate a QR code for your permanent URL
5. Share the QR code with interviewers to access your application

## How to Use

1. **Document Mode**:
   - Paste document content directly into the text area
   - Click "Use Document Content" to set the context
   - Ask questions about the document in the chat

2. **Web Mode**:
   - Enter a URL and click "Scrape Content"
   - Review the extracted content
   - Click "Use Web Content" to set the context
   - Ask questions about the web content

3. **Settings**:
   - Choose between cloud (Groq API) or local (Ollama) AI models
   - By default, the application uses the included Groq API key
   - Toggle "Use custom API key" if you want to use your own key

## Interview Recommendations

For the best interview experience:

1. **Use a private repository** to protect your API key
2. **Deploy to Render** following the instructions in `deploy_instructions.md`
3. **Set up environment variables** in Render for the API key
4. **Create a QR code** for your Render URL
5. **Test the deployment** before your interview
6. **Wake up the app** by visiting the URL ~5 minutes before your interview

## Project Structure

- `app.py`: Main Flask application
- `templates/index.html`: Web interface
- `requirements.txt`: Required Python packages
- `render.yaml`: Configuration for Render deployment
- `deploy_instructions.md`: Step-by-step deployment guide

## Security Considerations

- The repository should be kept private to protect the API key
- For production, always use environment variables instead of hardcoded keys
- The application is configured to prioritize environment variables over hardcoded keys
- Render provides secure storage for environment variables

## Default Configuration

- Uses Groq API with environment variable or fallback to hardcoded key
- Connects to llama-3.3-70b-versatile model
- Option to switch to local Ollama for offline use
- Mobile-responsive interface

## Acknowledgments

- Built with Flask, a lightweight Python web framework
- Utilizes Groq API for cloud AI processing
- Optional integration with Ollama for local processing

## Future Enhancements

- File upload support for documents
- Chat history persistence
- Additional AI model options
- PDF and image processing capabilities

## Acknowledgments

- Built with Flask, a lightweight Python web framework
- Utilizes Ollama for local AI processing
- Optional integration with Groq API for cloud processing 
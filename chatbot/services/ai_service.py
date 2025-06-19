import requests
from services import config, db

# Check if Ollama is available
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

def get_groq_response(prompt, api_key=None, model=config.DEFAULT_MODEL):
    """Get response from Groq API using the default API key if none provided"""
    # Use provided API key, or fall back to default
    api_key = api_key or config.GROQ_API_KEY
    
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
        response = requests.post(config.GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        resp_json = response.json()
        return resp_json['choices'][0]['message']['content'], None
    except Exception as e:
        return None, f"Error getting response from Groq: {str(e)}"

def get_ollama_response(prompt, model=config.LOCAL_MODEL):
    """Get response from local Ollama instance"""
    if not OLLAMA_AVAILABLE:
        return None, "Ollama is not available in this environment. Please use Groq API instead."
        
    try:
        response = ollama.chat(model=model, messages=[
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'], None
    except Exception as e:
        return None, f"Error getting response from Ollama: {str(e)}"

def create_prompt(user_input, context):
    """Create a prompt for the AI model"""
    return f"""Question: {user_input}
    
Based on the following context:

{context[:4000]}  # Limiting content length to avoid token limits

Please provide a concise and accurate answer based solely on the provided context."""

def process_chat(user_id, user_input, context, model_type='groq', api_key=None, conversation_id=None, document_id=None):
    """Process a chat message and get AI response"""
    # Get document content if document_id is provided
    if document_id:
        doc = db.get_document(document_id, user_id)
        if doc:
            context = doc.get('full_content', doc.get('content', ''))
    
    # Create prompt
    prompt = create_prompt(user_input, context)
    
    # Get AI response
    if model_type == 'groq':
        response, error = get_groq_response(prompt, api_key)
    elif model_type == 'ollama':
        response, error = get_ollama_response(prompt)
    else:
        return None, "Invalid model type specified"
        
    if error:
        return None, error
    
    # Save conversation
    if conversation_id:
        # Add to existing conversation
        try:
            db.add_message_to_conversation(conversation_id, user_id, "user", user_input)
            db.add_message_to_conversation(conversation_id, user_id, "assistant", response)
            conv = db.get_conversation(conversation_id, user_id)
            if not conv:
                conversation_id = None
        except Exception as e:
            conversation_id = None
    
    if not conversation_id:
        # Create new conversation
        title = user_input[:30] + ('...' if len(user_input) > 30 else '')
        result = db.save_conversation(user_id, title, context, user_input, response, document_id)
        conversation_id = result.inserted_id
    
    return {
        'response': response,
        'conversation_id': str(conversation_id)
    }, None 
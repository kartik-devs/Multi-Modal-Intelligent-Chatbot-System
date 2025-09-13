import requests
import json
from services import config, db
from services import api_manager

# Check if Ollama is available
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

def get_groq_response(prompt, api_key=None, model=None):
    """Get response from Groq API using the default API key if none provided"""
    # Use provided API key, or fall back to default
    api_key = api_key or config.GROQ_API_KEY
    
    if not api_key:
        return None, "No Groq API key provided. Please add an API key in settings."
        
    model = model or api_manager.AI_PROVIDERS['groq']['default_model']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,  # Add temperature parameter for more stable responses
        "max_tokens": 1024   # Limit response length
    }
    
    # Add retry logic
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.post(
                api_manager.AI_PROVIDERS['groq']['url'], 
                headers=headers, 
                json=data,
                timeout=30  # Add timeout to prevent hanging requests
            )
            
            if response.status_code == 401:
                return None, f"Authentication error: Invalid or expired API key for Groq. Please update your API key in settings."
            
            response.raise_for_status()
            resp_json = response.json()
            return resp_json['choices'][0]['message']['content'], None
            
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP error from Groq API: {str(e)}"
        
        except requests.exceptions.ConnectionError:
            retry_count += 1
            if retry_count >= max_retries:
                return None, "Connection error: Could not connect to Groq API after multiple attempts. Please check your internet connection."
            # Continue to next retry attempt
            
        except requests.exceptions.ReadTimeout:
            retry_count += 1
            if retry_count >= max_retries:
                return None, "Timeout error: The request to Groq API timed out after multiple attempts."
            # Continue to next retry attempt
            
        except Exception as e:
            return None, f"Error getting response from Groq: {str(e)}"
    
    # This should not be reached, but just in case
    return None, "Failed to get response from Groq API after multiple attempts."

def get_openai_response(prompt, api_key, model=None):
    """Get response from OpenAI API"""
    if not api_key:
        return None, "No OpenAI API key provided. Please add an API key in settings."
        
    model = model or api_manager.AI_PROVIDERS['openai']['default_model']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    try:
        response = requests.post(api_manager.AI_PROVIDERS['openai']['url'], headers=headers, json=data)
        
        if response.status_code == 401:
            return None, f"Authentication error: Invalid or expired API key for OpenAI. Please update your API key in settings."
        
        response.raise_for_status()
        resp_json = response.json()
        return resp_json['choices'][0]['message']['content'], None
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP error from OpenAI API: {str(e)}"
    except requests.exceptions.ConnectionError:
        return None, "Connection error: Could not connect to OpenAI API. Please check your internet connection."
    except Exception as e:
        return None, f"Error getting response from OpenAI: {str(e)}"

def get_anthropic_response(prompt, api_key, model=None):
    """Get response from Anthropic API"""
    model = model or api_manager.AI_PROVIDERS['anthropic']['default_model']
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024
    }
    try:
        response = requests.post(api_manager.AI_PROVIDERS['anthropic']['url'], headers=headers, json=data)
        response.raise_for_status()
        resp_json = response.json()
        return resp_json['content'][0]['text'], None
    except Exception as e:
        return None, f"Error getting response from Anthropic: {str(e)}"

def get_ollama_response(prompt, model=None):
    """Get response from local Ollama instance"""
    if not OLLAMA_AVAILABLE:
        return None, "Ollama is not available in this environment. Please use another provider instead."
    
    model = model or api_manager.AI_PROVIDERS['ollama']['default_model']
    
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

Use internet and provide accurate and proper responce using the documents provided

Always show the output as a list of steps to undertake."""

def process_chat(user_id, user_input, context, provider='groq', model=None, api_key=None, conversation_id=None, document_id=None):
    """Process a chat message and get AI response using the specified provider"""
    # Ensure user_input is a string
    user_input = str(user_input) if user_input is not None else ""
    
    # Get document content if document_id is provided
    if document_id:
        doc = db.get_document(document_id, user_id)
        if doc:
            context = doc.get('full_content', doc.get('content', ''))
    
    # Create prompt
    prompt = create_prompt(user_input, context)
    
    # If no API key provided, try to get default for the provider
    if not api_key and provider != 'ollama':
        api_key_data = api_manager.get_default_api_key(user_id, provider)
        if api_key_data:
            api_key = api_key_data['api_key']
            api_key_id = api_key_data.get('id')
        else:
            return None, f"No API key available for {provider}. Please add an API key in settings."
    
    # Get AI response based on provider
    if provider == 'groq':
        response, error = get_groq_response(prompt, api_key, model)
        if not error and api_key_id:
            api_manager.record_api_usage(user_id, provider, api_key_id, 'chat')
    elif provider == 'openai':
        response, error = get_openai_response(prompt, api_key, model)
        if not error and api_key_id:
            api_manager.record_api_usage(user_id, provider, api_key_id, 'chat')
    elif provider == 'anthropic':
        response, error = get_anthropic_response(prompt, api_key, model)
        if not error and api_key_id:
            api_manager.record_api_usage(user_id, provider, api_key_id, 'chat')
    elif provider == 'ollama':
        response, error = get_ollama_response(prompt, model)
    else:
        return None, "Invalid provider specified"
        
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
        conversation_id = result["inserted_id"] if isinstance(result, dict) else result.inserted_id
    
    return {
        'response': response,
        'conversation_id': str(conversation_id),
        'provider': provider,
        'model': model
    }, None 
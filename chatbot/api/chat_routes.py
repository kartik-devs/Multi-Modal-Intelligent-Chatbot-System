from flask import Blueprint, request, jsonify
from utils import auth_utils
from services import ai_service

# Create blueprint
blueprint = Blueprint('chat', __name__)

@blueprint.route('/chat', methods=['POST'])
@auth_utils.token_required
def chat(current_user):
    data = request.json
    user_input = data.get('message', '')
    context = data.get('context', '')
    model_type = data.get('model_type', 'groq')
    api_key = data.get('api_key')
    conversation_id = data.get('conversation_id')
    document_id = data.get('document_id')
    
    if not user_input:
        return jsonify({'message': 'Message is required'}), 400
    
    # Process chat
    result, error = ai_service.process_chat(
        str(current_user['_id']),
        user_input,
        context,
        model_type,
        api_key,
        conversation_id,
        document_id
    )
    
    if error:
        return jsonify({'message': error}), 400
    
    return jsonify(result), 200

def legacy_chat_handler():
    """Handler for the legacy /chat route"""
    data = request.json
    user_input = data.get('message', '')
    context = data.get('context', '')
    model_type = data.get('model_type', 'groq')
    api_key = data.get('api_key')
    
    if not user_input:
        return jsonify({'response': 'Please enter a message'})
    
    # Create prompt
    prompt = ai_service.create_prompt(user_input, context)
    
    # Get AI response
    if model_type == 'groq':
        response, error = ai_service.get_groq_response(prompt, api_key)
    elif model_type == 'ollama':
        response, error = ai_service.get_ollama_response(prompt)
    else:
        return jsonify({'response': 'Invalid model type specified'})
    
    if error:
        return jsonify({'response': error})
        
    return jsonify({'response': response}) 
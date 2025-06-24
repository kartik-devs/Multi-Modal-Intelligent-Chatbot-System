from flask import Blueprint, request, jsonify
from utils import auth_utils
from services import api_manager

# Create blueprint
blueprint = Blueprint('api_keys', __name__)

@blueprint.route('/api-keys', methods=['GET'])
@auth_utils.token_required
def get_api_keys(current_user):
    """Get all API keys for the current user"""
    keys = api_manager.get_api_keys(str(current_user['_id']))
    
    # Mask API keys for security
    for key in keys:
        if key['api_key']:
            prefix_length = min(4, len(key['api_key']))
            suffix_length = min(4, len(key['api_key']))
            masked_length = len(key['api_key']) - prefix_length - suffix_length
            key['api_key'] = key['api_key'][:prefix_length] + '*' * masked_length + key['api_key'][-suffix_length:]
    
    return jsonify({
        'api_keys': keys
    }), 200

@blueprint.route('/api-keys', methods=['POST'])
@auth_utils.token_required
def add_api_key(current_user):
    """Add a new API key"""
    data = request.json
    api_key = data.get('api_key', '')
    provider = data.get('provider')
    is_default = data.get('is_default', False)
    name = data.get('name', '')
    
    if not api_key:
        return jsonify({'message': 'API key is required'}), 400
    
    # If provider not specified, try to detect it
    if not provider:
        provider = api_manager.detect_api_provider(api_key)
        if not provider:
            return jsonify({'message': 'Could not detect API provider. Please specify the provider.'}), 400
    
    # Check if provider is valid
    if provider not in api_manager.AI_PROVIDERS:
        return jsonify({'message': f'Invalid provider: {provider}'}), 400
    
    # Save API key
    key_id = api_manager.save_api_key(str(current_user['_id']), provider, api_key, is_default, name)
    
    return jsonify({
        'message': 'API key added successfully',
        'key_id': key_id,
        'provider': provider,
        'is_default': is_default,
        'name': name
    }), 201

@blueprint.route('/api-keys/<key_id>', methods=['DELETE'])
@auth_utils.token_required
def delete_api_key(current_user, key_id):
    """Delete an API key"""
    # Connect to database
    import sqlite3
    from services import config
    
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Check if key belongs to user
    cursor.execute(
        "SELECT * FROM api_keys WHERE id = ? AND user_id = ?",
        (key_id, str(current_user['_id']))
    )
    
    key = cursor.fetchone()
    if not key:
        conn.close()
        return jsonify({'message': 'API key not found'}), 404
    
    # Delete key
    cursor.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'API key deleted successfully'}), 200

@blueprint.route('/api-keys/<key_id>/default', methods=['PUT'])
@auth_utils.token_required
def set_default_api_key(current_user, key_id):
    """Set an API key as default"""
    # Connect to database
    import sqlite3
    from services import config
    
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Check if key belongs to user
    cursor.execute(
        "SELECT * FROM api_keys WHERE id = ? AND user_id = ?",
        (key_id, str(current_user['_id']))
    )
    
    key = cursor.fetchone()
    if not key:
        conn.close()
        return jsonify({'message': 'API key not found'}), 404
    
    # Get provider
    provider = key[2]  # provider is the 3rd column
    
    # Reset all defaults for this provider
    cursor.execute(
        "UPDATE api_keys SET is_default = 0 WHERE user_id = ? AND provider = ?",
        (str(current_user['_id']), provider)
    )
    
    # Set this key as default
    cursor.execute("UPDATE api_keys SET is_default = 1 WHERE id = ?", (key_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'API key set as default successfully'}), 200

@blueprint.route('/providers', methods=['GET'])
@auth_utils.token_required
def get_providers(current_user):
    """Get available AI providers"""
    providers = api_manager.get_available_providers()
    
    # Format providers for frontend
    formatted_providers = []
    for key, provider in providers.items():
        formatted_providers.append({
            'id': key,
            'name': provider['name'],
            'models': provider['models'],
            'default_model': provider['default_model'],
            'requires_key': provider['requires_key']
        })
    
    return jsonify({
        'providers': formatted_providers
    }), 200 
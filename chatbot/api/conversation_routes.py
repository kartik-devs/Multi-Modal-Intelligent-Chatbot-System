from flask import Blueprint, jsonify
from utils import auth_utils
from services import db

# Create blueprint
blueprint = Blueprint('conversations', __name__)

@blueprint.route('/conversations', methods=['GET'])
@auth_utils.token_required
def get_conversations(current_user):
    user_conversations = db.get_user_conversations(str(current_user['_id']))
    
    return jsonify({
        'conversations': [{
            'id': str(conv['_id']),
            'title': conv.get('title', 'Untitled Conversation'),
            'created_at': conv['created_at'].isoformat(),
            'message_count': len(conv.get('messages', []))
        } for conv in user_conversations]
    }), 200

@blueprint.route('/conversations/<conversation_id>', methods=['GET'])
@auth_utils.token_required
def get_conversation(current_user, conversation_id):
    conv = db.get_conversation(conversation_id, str(current_user['_id']))
    
    if not conv:
        return jsonify({'message': 'Conversation not found'}), 404
        
    return jsonify({
        'id': str(conv['_id']),
        'title': conv.get('title', 'Untitled Conversation'),
        'created_at': conv['created_at'].isoformat(),
        'context': conv.get('context', ''),
        'messages': [{
            'role': msg['role'],
            'content': msg['content'],
            'timestamp': msg['timestamp'].isoformat()
        } for msg in conv.get('messages', [])]
    }), 200 
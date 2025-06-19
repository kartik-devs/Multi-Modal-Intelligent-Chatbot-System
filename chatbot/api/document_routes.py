from flask import Blueprint, request, jsonify
from utils import auth_utils
from services import db, document_service

# Create blueprint
blueprint = Blueprint('documents', __name__)

@blueprint.route('/documents/upload', methods=['POST'])
@auth_utils.token_required
def upload_document(current_user):
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    
    # Process uploaded file
    document, error = document_service.process_uploaded_file(file, str(current_user['_id']))
    
    if error:
        return jsonify({'message': error}), 400
        
    return jsonify({
        'message': 'Document uploaded successfully',
        'document': document
    }), 201

@blueprint.route('/documents', methods=['GET'])
@auth_utils.token_required
def get_documents(current_user):
    user_documents = db.get_user_documents(str(current_user['_id']))
    
    return jsonify({
        'documents': [{
            'id': str(doc['_id']),
            'filename': doc['filename'],
            'preview': doc.get('content', ''),
            'created_at': doc['created_at'].isoformat()
        } for doc in user_documents]
    }), 200

@blueprint.route('/documents/<document_id>', methods=['GET'])
@auth_utils.token_required
def get_document(current_user, document_id):
    doc = db.get_document(document_id, str(current_user['_id']))
    
    if not doc:
        return jsonify({'message': 'Document not found'}), 404
        
    return jsonify({
        'id': str(doc['_id']),
        'filename': doc['filename'],
        'content': doc.get('full_content', doc.get('content', '')),
        'created_at': doc['created_at'].isoformat()
    }), 200 
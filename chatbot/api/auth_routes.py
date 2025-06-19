from flask import Blueprint, request, jsonify
from utils import auth_utils

# Create blueprint
blueprint = Blueprint('auth', __name__)

@blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    # Register user
    user, error = auth_utils.register_user(data['email'], data['password'], data.get('name', ''))
    
    if error:
        return jsonify({'message': error}), 400
        
    return jsonify({
        'message': 'User created successfully',
        'token': user['token'],
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
    }), 201

@blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    # Login user
    user, error = auth_utils.login_user(data['email'], data['password'])
    
    if error:
        return jsonify({'message': error}), 401
        
    return jsonify({
        'message': 'Login successful',
        'token': user['token'],
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
    }), 200

@blueprint.route('/user', methods=['GET'])
@auth_utils.token_required
def get_user(current_user):
    return jsonify({
        'id': str(current_user['_id']),
        'email': current_user['email'],
        'name': current_user.get('name', '')
    }), 200 
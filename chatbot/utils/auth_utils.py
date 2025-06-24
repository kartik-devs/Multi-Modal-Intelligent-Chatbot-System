import bcrypt
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from services import config, db

def hash_password(password):
    """Hash a password for storing"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def generate_token(user_id):
    """Generate a JWT token for authentication"""
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.datetime.utcnow(),
        'sub': str(user_id)
    }
    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm='HS256'
    )

def decode_token(token):
    """Decode a JWT token"""
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=['HS256']
        )
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 401
            
        current_user = db.get_user_by_id(user_id)
        if not current_user:
            return jsonify({'message': 'User not found'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def register_user(email, password, username=""):
    """Register a new user"""
    # Check if user already exists
    if db.get_user_by_email(email):
        return None, "User already exists"
    
    # Hash password and create user
    password_hash = hash_password(password)
    result = db.create_user(email, password_hash, username)
    
    # Generate token
    token = generate_token(result["inserted_id"])
    
    return {
        'id': result["inserted_id"],
        'email': email,
        'name': username,
        'token': token
    }, None

def login_user(email, password):
    """Login a user"""
    # Find user
    user = db.get_user_by_email(email)
    if not user:
        return None, "Invalid email or password"
    
    # Check password
    if not verify_password(user['password'], password):
        return None, "Invalid email or password"
    
    # Generate token
    token = generate_token(user['_id'])
    
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'name': user.get('name', ''),
        'token': token
    }, None 
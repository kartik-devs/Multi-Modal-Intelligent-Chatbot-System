import datetime
import uuid
from pymongo import MongoClient
from services import config

# MongoDB connection
client = MongoClient(config.MONGO_URI)
db = client.get_database()

# Collections
users = db.users
documents = db.documents
conversations = db.conversations
messages = db.messages

# User Functions
def create_user(email, password_hash, username=""):
    """Create a new user in the database"""
    user_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow()
    
    user_data = {
        "_id": user_id,
        "email": email,
        "password": password_hash,
        "name": username,
        "username": username,
        "created_at": created_at
    }
    
    result = users.insert_one(user_data)
    return {"inserted_id": user_id}

def get_user_by_email(email):
    """Get a user by email"""
    user = users.find_one({"email": email})
    
    # Ensure the _id is always a string for compatibility with auth_utils
    if user and '_id' in user:
        if not isinstance(user['_id'], str):
            user['_id'] = str(user['_id'])
    
    return user

def get_user_by_id(user_id):
    """Get a user by ID"""
    # Ensure user_id is treated as string
    user = users.find_one({"_id": user_id})
    
    # Ensure the _id is always a string for compatibility with auth_utils
    if user and '_id' in user:
        if not isinstance(user['_id'], str):
            user['_id'] = str(user['_id'])
    
    return user

# Document Functions
def save_document(user_id, filename, file_path, content):
    """Save a document to the database"""
    doc_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow()
    preview = content[:1000] + "..." if len(content) > 1000 else content
    
    document_data = {
        "_id": doc_id,
        "user_id": user_id,
        "filename": filename,
        "file_path": file_path,
        "content": preview,
        "full_content": content,
        "created_at": created_at,
        "uploadDate": created_at  # For compatibility with frontend
    }
    
    result = documents.insert_one(document_data)
    return {"inserted_id": doc_id}

def get_user_documents(user_id):
    """Get all documents for a user"""
    return list(documents.find({"user_id": user_id}).sort("created_at", -1))

def get_document(doc_id, user_id):
    """Get a document by ID and user ID"""
    return documents.find_one({"_id": doc_id, "user_id": user_id})

# Conversation Functions
def save_conversation(user_id, title, context, user_message, assistant_response, document_id=None):
    """Save a new conversation"""
    conversation_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow()
    
    conversation_data = {
        "_id": conversation_id,
        "user_id": user_id,
        "title": title,
        "context": context,
        "document_id": document_id,
        "created_at": created_at
    }
    
    conversations.insert_one(conversation_data)
    
    # Save user message
    user_message_id = str(uuid.uuid4())
    user_message_data = {
        "_id": user_message_id,
        "conversation_id": conversation_id,
        "role": "user",
        "content": user_message,
        "timestamp": created_at
    }
    messages.insert_one(user_message_data)
    
    # Save assistant response
    assistant_message_id = str(uuid.uuid4())
    assistant_message_data = {
        "_id": assistant_message_id,
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": assistant_response,
        "timestamp": datetime.datetime.utcnow()
    }
    messages.insert_one(assistant_message_data)
    
    return {"inserted_id": conversation_id}

def add_message_to_conversation(conversation_id, user_id, role, content):
    """Add a message to an existing conversation"""
    # Verify conversation exists and belongs to user
    conversation = conversations.find_one({"_id": conversation_id, "user_id": user_id})
    if not conversation:
        return False
    
    message_id = str(uuid.uuid4())
    message_data = {
        "_id": message_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.utcnow()
    }
    
    result = messages.insert_one(message_data)
    return True

def get_user_conversations(user_id):
    """Get all conversations for a user"""
    return list(conversations.find({"user_id": user_id}).sort("created_at", -1))

def get_conversation(conversation_id, user_id):
    """Get a conversation by ID with its messages"""
    conversation = conversations.find_one({"_id": conversation_id, "user_id": user_id})
    if not conversation:
        return None
    
    conversation_messages = list(messages.find({"conversation_id": conversation_id}).sort("timestamp", 1))
    conversation["messages"] = conversation_messages
    
    return conversation

def save_scraped_content(user_id, url, content):
    """Save scraped web content as a document"""
    filename = url.split("//")[-1].split("/")[0]
    created_at = datetime.datetime.utcnow()
    doc_id = str(uuid.uuid4())
    preview = content[:1000] + "..." if len(content) > 1000 else content
    
    document_data = {
        "_id": doc_id,
        "user_id": user_id,
        "filename": f"Scraped: {filename}",
        "source_url": url,
        "content": preview,
        "full_content": content,
        "created_at": created_at,
        "uploadDate": created_at  # For compatibility with frontend
    }
    
    result = documents.insert_one(document_data)
    return {"inserted_id": doc_id} 
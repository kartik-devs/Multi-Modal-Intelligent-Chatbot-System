from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
from services import config

# Connect to MongoDB
client = MongoClient(config.MONGO_URI)
db = client.chatbot_db

# Collections
users = db.users
conversations = db.conversations
documents = db.documents

# User Functions
def create_user(email, password_hash, name=""):
    """Create a new user in the database"""
    user = {
        "email": email,
        "password": password_hash,
        "name": name,
        "created_at": datetime.datetime.utcnow()
    }
    return users.insert_one(user)

def get_user_by_email(email):
    """Get a user by email"""
    return users.find_one({"email": email})

def get_user_by_id(user_id):
    """Get a user by ID"""
    return users.find_one({"_id": ObjectId(user_id)})

# Document Functions
def save_document(user_id, filename, file_path, content):
    """Save a document to the database"""
    document = {
        "user_id": ObjectId(user_id),
        "filename": filename,
        "file_path": file_path,
        "content": content[:1000] + "..." if len(content) > 1000 else content,  # Store preview
        "full_content": content,  # Store full content
        "created_at": datetime.datetime.utcnow()
    }
    return documents.insert_one(document)

def get_user_documents(user_id):
    """Get all documents for a user"""
    return list(documents.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))

def get_document(doc_id, user_id):
    """Get a document by ID and user ID"""
    return documents.find_one({"_id": ObjectId(doc_id), "user_id": ObjectId(user_id)})

# Conversation Functions
def save_conversation(user_id, title, context, user_message, assistant_response, document_id=None):
    """Save a new conversation"""
    timestamp = datetime.datetime.utcnow()
    conversation = {
        "user_id": ObjectId(user_id),
        "title": title,
        "created_at": timestamp,
        "context": context,
        "document_id": ObjectId(document_id) if document_id else None,
        "messages": [
            {
                "role": "user",
                "content": user_message,
                "timestamp": timestamp
            },
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": timestamp
            }
        ]
    }
    return conversations.insert_one(conversation)

def add_message_to_conversation(conversation_id, user_id, role, content):
    """Add a message to an existing conversation"""
    timestamp = datetime.datetime.utcnow()
    return conversations.update_one(
        {"_id": ObjectId(conversation_id), "user_id": ObjectId(user_id)},
        {"$push": {"messages": {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }}}
    )

def get_user_conversations(user_id):
    """Get all conversations for a user"""
    return list(conversations.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))

def get_conversation(conversation_id, user_id):
    """Get a conversation by ID and user ID"""
    return conversations.find_one({"_id": ObjectId(conversation_id), "user_id": ObjectId(user_id)})

# Web Scraping Functions
def save_scraped_content(user_id, url, content):
    """Save scraped web content as a document"""
    document = {
        "user_id": ObjectId(user_id),
        "filename": f"Scraped: {url[:50]}{'...' if len(url) > 50 else ''}",
        "source_url": url,
        "content": content[:1000] + "..." if len(content) > 1000 else content,  # Store preview
        "full_content": content,  # Store full content
        "created_at": datetime.datetime.utcnow()
    }
    return documents.insert_one(document) 
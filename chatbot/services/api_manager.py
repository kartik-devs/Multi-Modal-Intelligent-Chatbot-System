import os
import json
import datetime
import random
import sqlite3
from services import config

# Define available AI providers
AI_PROVIDERS = {
    'groq': {
        'name': 'Groq',
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'models': ['llama-3.3-70b-versatile', 'llama-3.1-8b-versatile'],
        'default_model': 'llama-3.3-70b-versatile',
        'requires_key': True,
        'header_format': 'Bearer {api_key}',
        'free_tier_limit': 100,  # requests per month
    },
    'openai': {
        'name': 'OpenAI',
        'url': 'https://api.openai.com/v1/chat/completions',
        'models': ['gpt-3.5-turbo', 'gpt-4o'],
        'default_model': 'gpt-3.5-turbo',
        'requires_key': True,
        'header_format': 'Bearer {api_key}',
        'free_tier_limit': 0,  # No free tier
    },
    'ollama': {
        'name': 'Ollama (Local)',
        'url': 'http://localhost:11434/api/chat',
        'models': ['llama3', 'mistral'],
        'default_model': 'llama3',
        'requires_key': False,
        'header_format': '',
        'free_tier_limit': float('inf'),  # Unlimited (local)
    },
    'anthropic': {
        'name': 'Anthropic',
        'url': 'https://api.anthropic.com/v1/messages',
        'models': ['claude-3-opus', 'claude-3-sonnet'],
        'default_model': 'claude-3-sonnet',
        'requires_key': True,
        'header_format': 'x-api-key: {api_key}',
        'free_tier_limit': 0,  # No free tier
    }
}

# Database initialization
def init_api_db():
    """Initialize the API keys database"""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Create API keys table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        api_key TEXT NOT NULL,
        name TEXT,
        is_default BOOLEAN DEFAULT 0,
        usage_count INTEGER DEFAULT 0,
        last_used TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create API usage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_usage (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        api_key_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        request_type TEXT NOT NULL,
        tokens_used INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database on import
init_api_db()

def save_api_key(user_id, provider, api_key, is_default=False, name=None):
    """Save an API key to the database"""
    import uuid
    
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    key_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat()
    
    # If this is set as default, unset any existing default for this provider
    if is_default:
        cursor.execute(
            "UPDATE api_keys SET is_default = 0 WHERE user_id = ? AND provider = ?",
            (user_id, provider)
        )
    
    cursor.execute(
        "INSERT INTO api_keys (id, user_id, provider, api_key, name, is_default, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (key_id, user_id, provider, api_key, name, is_default, created_at)
    )
    
    conn.commit()
    conn.close()
    
    return key_id

def get_api_keys(user_id):
    """Get all API keys for a user"""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM api_keys WHERE user_id = ? ORDER BY provider, is_default DESC",
        (user_id,)
    )
    
    keys = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return keys

def get_default_api_key(user_id, provider):
    """Get the default API key for a provider"""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # First try to get the user's default key for this provider
    cursor.execute(
        "SELECT * FROM api_keys WHERE user_id = ? AND provider = ? AND is_default = 1",
        (user_id, provider)
    )
    
    key = cursor.fetchone()
    
    # If no default key, try to get any key for this provider
    if not key:
        cursor.execute(
            "SELECT * FROM api_keys WHERE user_id = ? AND provider = ? LIMIT 1",
            (user_id, provider)
        )
        key = cursor.fetchone()
    
    # If still no key, use system default if available
    if not key and provider == 'groq':
        # Return system default key
        conn.close()
        return {
            'provider': 'groq',
            'api_key': config.GROQ_API_KEY
        }
    
    conn.close()
    
    if key:
        return dict(key)
    return None

def record_api_usage(user_id, provider, api_key_id, request_type, tokens_used=0):
    """Record API usage"""
    import uuid
    
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    usage_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()
    
    cursor.execute(
        "INSERT INTO api_usage (id, user_id, provider, api_key_id, timestamp, request_type, tokens_used) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (usage_id, user_id, provider, api_key_id, timestamp, request_type, tokens_used)
    )
    
    # Update usage count for the API key
    cursor.execute(
        "UPDATE api_keys SET usage_count = usage_count + 1, last_used = ? WHERE id = ?",
        (timestamp, api_key_id)
    )
    
    conn.commit()
    conn.close()

def detect_api_provider(api_key):
    """Detect which provider an API key belongs to based on its format"""
    if not api_key:
        return None
        
    # Groq API keys start with "gsk_"
    if api_key.startswith('gsk_'):
        return 'groq'
    
    # OpenAI API keys start with "sk-"
    if api_key.startswith('sk-'):
        return 'openai'
    
    # Anthropic API keys are typically 32-48 characters
    if len(api_key) >= 32 and len(api_key) <= 48 and api_key.startswith('sk-ant-'):
        return 'anthropic'
    
    # If we can't detect, return None
    return None

def get_least_used_api_key(user_id, provider):
    """Get the least used API key for a provider to implement rotation"""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM api_keys WHERE user_id = ? AND provider = ? ORDER BY usage_count ASC LIMIT 1",
        (user_id, provider)
    )
    
    key = cursor.fetchone()
    conn.close()
    
    if key:
        return dict(key)
    return None

def get_available_providers():
    """Get a list of available AI providers"""
    return AI_PROVIDERS 
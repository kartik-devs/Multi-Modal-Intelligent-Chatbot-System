from services import config

# Import the appropriate database implementation based on config
if config.DB_TYPE == "mongodb":
    from services.mongodb import (
        create_user,
        get_user_by_email,
        get_user_by_id,
        save_document,
        get_user_documents,
        get_document,
        save_conversation,
        add_message_to_conversation,
        get_user_conversations,
        get_conversation,
        save_scraped_content
    )
else:
    # SQLite implementation (existing code)
    import datetime
    import sqlite3
    import json
    import uuid
    
    # Database connection function
    def get_db_connection():
        conn = sqlite3.connect(config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Initialize database
    def init_db():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            username TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Create documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT,
            content TEXT,
            full_content TEXT,
            source_url TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            context TEXT,
            document_id TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # Initialize the database on import
    init_db()
    
    # Helper function to convert SQLite row to dict
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    # User Functions
    def create_user(email, password_hash, username=""):
        """Create a new user in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        
        cursor.execute(
            "INSERT INTO users (id, email, password, name, username, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, email, password_hash, username, username, created_at)
        )
        
        conn.commit()
        conn.close()
        
        return {"inserted_id": user_id}
    
    def get_user_by_email(email):
        """Get a user by email"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            user['_id'] = user['id']
        
        return user
    
    def get_user_by_id(user_id):
        """Get a user by ID"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            user['_id'] = user['id']
        
        return user
    
    # Document Functions
    def save_document(user_id, filename, file_path, content):
        """Save a document to the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        doc_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        preview = content[:1000] + "..." if len(content) > 1000 else content
        
        cursor.execute(
            "INSERT INTO documents (id, user_id, filename, file_path, content, full_content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (doc_id, user_id, filename, file_path, preview, content, created_at)
        )
        
        conn.commit()
        conn.close()
        
        return {"inserted_id": doc_id}
    
    def get_user_documents(user_id):
        """Get all documents for a user"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        )
        documents_list = cursor.fetchall()
        
        conn.close()
        
        # Add _id field for compatibility with MongoDB version
        for doc in documents_list:
            doc['_id'] = doc['id']
        
        return documents_list
    
    def get_document(doc_id, user_id):
        """Get a document by ID and user ID"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?", 
            (doc_id, user_id)
        )
        document = cursor.fetchone()
        
        conn.close()
        
        if document:
            document['_id'] = document['id']
        
        return document
    
    # Conversation Functions
    def save_conversation(user_id, title, context, user_message, assistant_response, document_id=None):
        """Save a new conversation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conversation_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        
        cursor.execute(
            "INSERT INTO conversations (id, user_id, title, context, document_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conversation_id, user_id, title, context, document_id, created_at)
        )
        
        # Save user message
        message_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (message_id, conversation_id, "user", user_message, created_at)
        )
        
        # Save assistant response
        response_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (response_id, conversation_id, "assistant", assistant_response, datetime.datetime.utcnow().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        return {"inserted_id": conversation_id}
    
    def add_message_to_conversation(conversation_id, user_id, role, content):
        """Add a message to an existing conversation"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Check if conversation exists and belongs to user
        cursor.execute(
            "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        )
        conversation = cursor.fetchone()
        
        if not conversation:
            conn.close()
            return False
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (message_id, conversation_id, role, content, timestamp)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_user_conversations(user_id):
        """Get all conversations for a user"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        conversations_list = cursor.fetchall()
        
        conn.close()
        
        # Add _id field for compatibility with MongoDB version
        for conv in conversations_list:
            conv['_id'] = conv['id']
        
        return conversations_list
    
    def get_conversation(conversation_id, user_id):
        """Get a conversation by ID with its messages"""
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Get conversation
        cursor.execute(
            "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        )
        conversation = cursor.fetchone()
        
        if not conversation:
            conn.close()
            return None
        
        # Get messages
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        )
        messages_list = cursor.fetchall()
        
        conn.close()
        
        # Add messages to conversation
        conversation['messages'] = messages_list
        conversation['_id'] = conversation['id']
        
        return conversation
    
    def save_scraped_content(user_id, url, content):
        """Save scraped web content as a document"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        doc_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        filename = url.split("//")[-1].split("/")[0]
        preview = content[:1000] + "..." if len(content) > 1000 else content
        
        cursor.execute(
            "INSERT INTO documents (id, user_id, filename, source_url, content, full_content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (doc_id, user_id, f"Scraped: {filename}", url, preview, content, created_at)
        )
        
        conn.commit()
        conn.close()
        
        return {"inserted_id": doc_id} 
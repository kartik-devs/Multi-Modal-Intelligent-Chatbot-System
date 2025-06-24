from flask import Blueprint, jsonify
import logging
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from services import config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
blueprint = Blueprint('db_status', __name__)

@blueprint.route('/db-status', methods=['GET'])
def db_status():
    """Check database connection status"""
    response = {
        "db_type": config.DB_TYPE,
        "status": "unknown"
    }
    
    try:
        if config.DB_TYPE == "mongodb":
            # Import here to avoid circular imports
            from services.mongodb import client
            
            if not client:
                response["status"] = "error"
                response["message"] = "MongoDB client is not initialized"
                return jsonify(response), 500
                
            # Test the connection
            client.admin.command('ismaster')
            
            # Get database stats
            from services.mongodb import db
            stats = db.command("dbstats")
            
            response["status"] = "connected"
            response["details"] = {
                "database": db.name,
                "collections": len(db.list_collection_names()),
                "storage_size": f"{stats.get('storageSize', 0) / (1024 * 1024):.2f} MB",
                "objects": stats.get('objects', 0)
            }
            
        else:  # sqlite
            import sqlite3
            from services.db import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            response["status"] = "connected"
            response["details"] = {
                "database": config.SQLITE_DB_PATH,
                "tables": len(tables)
            }
            
        return jsonify(response), 200
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Database connection error: {str(e)}")
        response["status"] = "error"
        response["message"] = str(e)
        response["environment"] = "production" if os.environ.get('RENDER') == 'true' else "development"
        
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Error checking database status: {str(e)}")
        response["status"] = "error"
        response["message"] = str(e)
        
        return jsonify(response), 500 
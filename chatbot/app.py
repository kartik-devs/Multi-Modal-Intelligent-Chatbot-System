from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports from other modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import modules
    from api import auth_routes, document_routes, conversation_routes, chat_routes, scraper_routes, api_routes
    from services import config
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    raise

# Initialize Flask app
app = Flask(__name__)

# Enable CORS with simple configuration
CORS(app, supports_credentials=False)

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # Do not add credentials support when using '*' for Allow-Origin
    return response

# Set maximum content length for file uploads
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Error handlers
@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Not found", "message": str(e)}), 404

@app.errorhandler(401)
def unauthorized_error(e):
    return jsonify({"error": "Unauthorized", "message": str(e)}), 401

# Debug: Print routes being registered
logger.info("Registering blueprints...")

try:
    # Register API routes
    app.register_blueprint(auth_routes.blueprint, url_prefix='/api')
    app.register_blueprint(document_routes.blueprint, url_prefix='/api')
    app.register_blueprint(conversation_routes.blueprint, url_prefix='/api')
    app.register_blueprint(chat_routes.blueprint, url_prefix='/api')
    app.register_blueprint(scraper_routes.blueprint, url_prefix='/api')
    app.register_blueprint(api_routes.blueprint, url_prefix='/api')
    
    # Debug: Print all registered routes
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"{rule.endpoint}: {rule.rule}")
except Exception as e:
    logger.error(f"Error registering blueprints: {str(e)}")
    raise

# Root route for health check
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "API server is running"}), 200

# Legacy routes (for backward compatibility)
@app.route('/chat', methods=['POST'])
def legacy_chat():
    return chat_routes.legacy_chat_handler()

@app.route('/scrape', methods=['POST'])
def legacy_scrape():
    return scraper_routes.legacy_scrape_handler()

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 
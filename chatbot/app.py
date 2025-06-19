from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory to sys.path to allow imports from other modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import modules
from api import auth_routes, document_routes, conversation_routes, chat_routes, scraper_routes
from services import config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Set maximum content length for file uploads
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Register API routes
app.register_blueprint(auth_routes.blueprint, url_prefix='/api')
app.register_blueprint(document_routes.blueprint, url_prefix='/api')
app.register_blueprint(conversation_routes.blueprint, url_prefix='/api')
app.register_blueprint(chat_routes.blueprint, url_prefix='/api')
app.register_blueprint(scraper_routes.blueprint, url_prefix='/api')

# Legacy routes (for backward compatibility)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def legacy_chat():
    return chat_routes.legacy_chat_handler()

@app.route('/scrape', methods=['POST'])
def legacy_scrape():
    return scraper_routes.legacy_scrape_handler()

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
import os
from chatbot.app import app

# Enable debug mode in development
if os.environ.get('RENDER') != 'true':
    app.debug = True

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
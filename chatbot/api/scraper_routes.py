from flask import Blueprint, request, jsonify
from utils import auth_utils
from services import scraper_service

# Create blueprint
blueprint = Blueprint('scraper', __name__)

@blueprint.route('/scrape', methods=['POST'])
@auth_utils.token_required
def scrape(current_user):
    data = request.json
    url = data.get('url', '')
    save = data.get('save', False)
    
    if not url:
        return jsonify({'message': 'URL is required'}), 400
    
    # Process scraped content
    result, error = scraper_service.process_scraped_content(url, str(current_user['_id']), save)
    
    if error:
        return jsonify({'message': error}), 400
    
    return jsonify(result), 200

def legacy_scrape_handler():
    """Handler for the legacy /scrape route"""
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'content': 'Please enter a URL'})
    
    content, error = scraper_service.scrape_url(url)
    
    if error:
        return jsonify({'content': error})
        
    return jsonify({'content': content}) 
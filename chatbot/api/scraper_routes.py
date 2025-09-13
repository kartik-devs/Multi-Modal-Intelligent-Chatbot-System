from flask import Blueprint, request, jsonify
from utils import auth_utils
from services import scraper_service
from services.playwright_ucr import fetch_ucr_fee, parse_ucr_html

# Create blueprint
blueprint = Blueprint('scraper', __name__)

@blueprint.route('/scrape', methods=['POST'])
@auth_utils.token_required
def scrape(current_user):
    data = request.json
    url = data.get('url', '')
    save = data.get('save', False)
    form_data = data.get('form_data', None)
    method = data.get('method', 'GET')
    
    if not url:
        return jsonify({'message': 'URL is required'}), 400
    
    # Process scraped content
    result, error = scraper_service.process_scraped_content(
        url, str(current_user['_id']), save, form_data, method
    )
    
    if error:
        return jsonify({'message': error}), 400
    
    return jsonify(result), 200

def legacy_scrape_handler():
    """Handler for the legacy /scrape route"""
    data = request.json
    url = data.get('url', '')
    form_data = data.get('form_data', None)
    method = data.get('method', 'GET')
    
    if not url:
        return jsonify({'content': 'Please enter a URL'})
    
    content, error = scraper_service.scrape_url(url, form_data, method)
    
    if error:
        return jsonify({'content': error})
        
    return jsonify({'content': content}) 


@blueprint.route('/scrape/ucr', methods=['POST'])
@auth_utils.token_required
def scrape_ucr(current_user):
    data = request.json or {}
    acct_key = data.get('acctkey', '')
    service_date = data.get('serviceDate') or data.get('service_date') or ''
    procedure_code = data.get('procedureCode') or data.get('procedure_code') or ''
    zip_code = data.get('zipCode') or data.get('zip_code') or ''
    percentile = data.get('percentile', '50')

    if not acct_key:
        # Try to derive from URL if provided
        url = data.get('url', '')
        if 'acctkey=' in url:
            acct_key = url.split('acctkey=')[1]

    if not all([acct_key, service_date, zip_code]) or (not procedure_code):
        return jsonify({'message': 'acctkey, serviceDate, zipCode and procedureCode are required'}), 400

    html, error = fetch_ucr_fee(
        acct_key=acct_key,
        service_date=service_date,
        procedure_code=procedure_code,
        zip_code=zip_code,
        percentile=str(percentile),
    )

    if error:
        return jsonify({'message': error}), 500

    parsed = parse_ucr_html(html or "")

    debug = bool(data.get('debug'))
    response = {'data': parsed}
    if debug:
        response['raw_html'] = html

    return jsonify(response), 200
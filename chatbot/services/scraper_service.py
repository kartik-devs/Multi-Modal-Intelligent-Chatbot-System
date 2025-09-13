import requests
from bs4 import BeautifulSoup
from services import db

def scrape_url(url, form_data=None, method='GET'):
    """Scrape content from a URL, optionally with form data"""
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        if method.upper() == 'POST' and form_data:
            # For UCR Fee Viewer, we need to get the actual form from the middle frame
            if 'feeinfo.com/DecisionPointUCR' in url:
                # Extract the account key from the URL
                if 'acctkey=' in url:
                    acctkey = url.split('acctkey=')[1]
                    # Get the actual form page from the middle frame
                    form_url = f"https://www.feeinfo.com/DecisionPointUCR/welcome.html/getBody/?acctkey={acctkey}"
                    print(f"DEBUG: UCR detected, form_url set to: {form_url}")
                else:
                    form_url = url
                    print(f"DEBUG: No acctkey found, using original URL: {form_url}")
            else:
                form_url = url
                print(f"DEBUG: Not UCR, using original URL: {form_url}")
            
            # First, get the page to extract any CSRF tokens or session data
            get_response = session.get(form_url, headers=headers)
            get_response.raise_for_status()
            
            # Parse the page to find form fields
            soup = BeautifulSoup(get_response.text, 'html.parser')
            
            # Find the form and its action URL
            form = soup.find('form')
            form_action = form_url  # Default to the form URL we just fetched
            if form and form.get('action'):
                form_action = form.get('action')
                if not form_action.startswith('http'):
                    # Relative URL, make it absolute
                    from urllib.parse import urljoin
                    form_action = urljoin(form_url, form_action)
            
            # Look for all form inputs (hidden and visible)
            all_inputs = soup.find_all('input')
            form_fields = {}
            
            for input_field in all_inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                input_type = input_field.get('type', 'text')
                
                if name:
                    form_fields[name] = value
            
            # Also look for select elements
            selects = soup.find_all('select')
            for select in selects:
                name = select.get('name')
                if name:
                    # Get the first option value or empty string
                    first_option = select.find('option')
                    form_fields[name] = first_option.get('value', '') if first_option else ''
            
            # Add the provided form data, mapping to correct field names
            if isinstance(form_data, dict):
                # Map our generic names to the actual form field names
                field_mapping = {
                    'service_date': 'serviceDate',
                    'procedure_code': 'procedureCode', 
                    'zip_code': 'zipCode',
                    'percentile': 'percentile',
                    'modifier': 'modifier'
                }
                
                for our_key, our_value in form_data.items():
                    actual_field = field_mapping.get(our_key, our_key)
                    form_fields[actual_field] = our_value
            else:
                # If form_data is a string, try to parse it
                try:
                    import json
                    parsed_data = json.loads(form_data)
                    form_fields.update(parsed_data)
                except:
                    form_fields.update(form_data)
            
            # Update headers for POST request
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.feeinfo.com',
                'Referer': url,
                'Sec-Fetch-Site': 'same-origin'
            })
            
            # Debug: Log what we're sending
            debug_info = f"Form URL: {form_url}\n"
            debug_info += f"Form Action URL: {form_action}\n"
            debug_info += f"Form Fields: {form_fields}\n\n"
            
            # Add a small delay to avoid rate limiting
            import time
            time.sleep(1)
            
            response = session.post(form_action, data=form_fields, headers=headers)
            
            # For UCR Fee Viewer, wait a bit for JavaScript to load results
            if 'feeinfo.com/DecisionPointUCR' in form_action:
                debug_info += f"⏳ Waiting 5 seconds for AJAX to complete...\n"
                time.sleep(5)  # Wait 5 seconds for AJAX to complete
                
                # Try to get the results by making another request to the form page
                debug_info += f"🔍 Making follow-up request to get results...\n"
                try:
                    # Make another request to the form page to see if results are now loaded
                    followup_response = session.get(form_url, headers=headers)
                    if followup_response.status_code == 200:
                        # Check if the response contains results (not just the form)
                        if "Loading your estimated charge" not in followup_response.text and len(followup_response.text) > 20000:
                            response = followup_response
                            debug_info += f"✅ Successfully got results from follow-up request (length: {len(followup_response.text)})\n"
                        else:
                            debug_info += f"❌ Follow-up request still shows loading or form (length: {len(followup_response.text)})\n"
                    else:
                        debug_info += f"❌ Follow-up request failed (status: {followup_response.status_code})\n"
                except Exception as e:
                    debug_info += f"❌ Error in follow-up request: {str(e)}\n"
        else:
            # For GET requests
            response = session.get(url, headers=headers)
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text with better formatting
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace but preserve structure
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Add debug information
        debug_info = f"Status Code: {response.status_code}\n"
        debug_info += f"Response Headers: {dict(response.headers)}\n"
        debug_info += f"URL: {response.url}\n"
        debug_info += f"Content Length: {len(response.text)} characters\n"
        
        # Show which URL we actually requested
        if method.upper() == 'POST' and form_data:
            debug_info += f"Requested URL: {form_url}\n"
        
        # Add form analysis if this was a POST request
        if method.upper() == 'POST' and form_data:
            debug_info += f"\nForm Analysis:\n"
            debug_info += f"Form Action URL: {form_action}\n"
            debug_info += f"Form Fields Sent: {form_fields}\n"
            
            # Check if we got redirected
            if response.url != form_action:
                debug_info += f"Redirected to: {response.url}\n"
            
            # Check for common error indicators
            if "error" in text.lower() or "invalid" in text.lower():
                debug_info += f"\n⚠️  Possible Error Indicators Found in Response\n"
            
            # Check if we got the same page back (form not submitted)
            if "Context4 Reference-based Pricing UCR Fee Viewer" in text and len(text) < 1000:
                debug_info += f"\n⚠️  Warning: Got page title only - form may not have been submitted properly\n"
                debug_info += f"Possible issues:\n"
                debug_info += f"- Missing required form fields\n"
                debug_info += f"- CSRF token mismatch\n"
                debug_info += f"- JavaScript validation required\n"
                debug_info += f"- Session expired\n"
            
            debug_info += f"\n"
        
        # If text is too short, show raw HTML for debugging
        if len(text) < 500:
            debug_info += f"🔍 Raw HTML (first 2000 chars):\n{response.text[:2000]}\n\n"
        
        # Special handling for UCR Fee Viewer frameset
        if 'feeinfo.com/DecisionPointUCR' in response.url and '<frameset' in response.text:
            debug_info += f"🎯 Frameset Detected - This is the main page, not the form\n"
            debug_info += f"📋 Frame URLs found:\n"
            # Extract frame URLs from the HTML
            import re
            frame_pattern = r'<frame[^>]*src="([^"]*)"'
            frames = re.findall(frame_pattern, response.text)
            for i, frame_url in enumerate(frames, 1):
                debug_info += f"  Frame {i}: {frame_url}\n"
        
        debug_info += f"Content:\n{text}"
        
        return debug_info, None
    except Exception as e:
        return None, f"Error scraping URL: {str(e)}"

def process_scraped_content(url, user_id, save=False, form_data=None, method='GET'):
    """Process scraped content and optionally save it to the database"""
    content, error = scrape_url(url, form_data, method)
    
    if error:
        return None, error
    
    result = {
        'content': content,
        'url': url,
        'method': method
    }
    
    if form_data:
        result['form_data'] = form_data
    
    # Save scraped content as a document if requested
    if save and content:
        doc_result = db.save_scraped_content(user_id, url, content)
        result['document_id'] = str(doc_result["inserted_id"]) if isinstance(doc_result, dict) else str(doc_result.inserted_id)
    
    return result, None 
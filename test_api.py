import requests
import json

# Test the API endpoint
url = "http://127.0.0.1:5000/api/scrape/batch-json"
data = {
    "acctkey": "C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs",
    "line_items": [
        {
            "ZipCode": "90001",
            "CPTcode": "99214", 
            "date": "2025-04-25"
        }
    ]
}

try:
    print("Sending request to API...")
    response = requests.post(url, json=data, timeout=120)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

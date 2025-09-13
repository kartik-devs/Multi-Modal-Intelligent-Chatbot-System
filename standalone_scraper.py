#!/usr/bin/env python3
"""
Standalone UCR Fee Scraper
Can be called directly from n8n or any external system
"""

import sys
import json
import argparse
from typing import Dict, List
from datetime import datetime
import re

# Add the chatbot services to the path
sys.path.append('chatbot')

from chatbot.services.playwright_ucr import fetch_ucr_fee_sync, parse_ucr_html


def process_json_input(json_data: dict, acctkey: str) -> dict:
    """Process JSON input and return JSON results."""
    results = []
    
    line_items = json_data.get("line_items", [])
    if not line_items:
        return {"error": "No line_items found in input JSON"}
    
    for index, item in enumerate(line_items, start=1):
        # Extract and normalize data from JSON
        zip_code = str(item.get("ZipCode", "")).strip()
        cpt_code = str(item.get("CPTcode", "")).strip()
        date_str = str(item.get("date", "")).strip()
        
        # Normalize date format (convert from YYYY-MM-DD to MM/DD/YYYY)
        def normalize_date(date_input: str) -> str:
            if not date_input:
                return ""
            try:
                # Try YYYY-MM-DD format first
                if "-" in date_input and len(date_input) == 10:
                    dt = datetime.strptime(date_input, "%Y-%m-%d")
                    return dt.strftime("%m/%d/%Y")
                # Try MM/DD/YYYY format
                elif "/" in date_input:
                    dt = datetime.strptime(date_input, "%m/%d/%Y")
                    return dt.strftime("%m/%d/%Y")
                else:
                    return date_input
            except Exception:
                return date_input
        
        service_date = normalize_date(date_str)
        procedure_code = re.sub(r"\D", "", cpt_code).strip()  # digits only
        zip_code = re.sub(r"\D", "", zip_code).strip().zfill(5)  # exactly 5 digits
        
        # Basic validations
        if len(service_date) != 10 or service_date.count('/') != 2:
            error_result = {
                "procedureCode": procedure_code,
                "percentiles": {},
                "currency": "USD",
                "zip_code": int(zip_code) if zip_code.isdigit() else 0,
                "date": service_date,
                "line_number": index,
                "error": f"Invalid date format: '{date_str}' (expected YYYY-MM-DD or MM/DD/YYYY)"
            }
            results.append(error_result)
            print(f"Line {index}: error invalid date '{date_str}'", flush=True)
            continue
            
        if not procedure_code:
            error_result = {
                "procedureCode": "",
                "percentiles": {},
                "currency": "USD",
                "zip_code": int(zip_code) if zip_code.isdigit() else 0,
                "date": service_date,
                "line_number": index,
                "error": "Missing CPT code"
            }
            results.append(error_result)
            print(f"Line {index}: error missing CPT", flush=True)
            continue
            
        if not re.match(r"^\d{5}$", zip_code):
            error_result = {
                "procedureCode": procedure_code,
                "percentiles": {},
                "currency": "USD",
                "zip_code": int(zip_code) if zip_code.isdigit() else 0,
                "date": service_date,
                "line_number": index,
                "error": f"Invalid ZIP code: '{zip_code}' (expected 5 digits)"
            }
            results.append(error_result)
            print(f"Line {index}: error invalid ZIP '{zip_code}'", flush=True)
            continue
        
        print(f"Line {index}: date={service_date} cpt={procedure_code} zip={zip_code} ...", flush=True)
        
        # Scrape UCR data
        html, err = fetch_ucr_fee_sync(
            acct_key=acctkey,
            service_date=service_date,
            procedure_code=procedure_code,
            zip_code=zip_code,
            percentile="50",
            timeout_ms=20000,
        )
        
        if not err and html:
            parsed = parse_ucr_html(html)
            
            # Create result without description field
            result = {
                "procedureCode": parsed.get("procedureCode", procedure_code),
                "percentiles": parsed.get("percentiles", {}),
                "currency": parsed.get("currency", "USD"),
                "zip_code": int(zip_code),
                "date": service_date,
                "line_number": index
            }
            
            # Add error field if no percentiles found
            if not parsed.get("percentiles"):
                result["error"] = "No percentiles found in response"
            
            results.append(result)
            print(f"Line {index}: {json.dumps(result, indent=2)}", flush=True)
            
        else:
            # Create error result
            error_result = {
                "procedureCode": procedure_code,
                "percentiles": {},
                "currency": "USD",
                "zip_code": int(zip_code),
                "date": service_date,
                "line_number": index,
                "error": f"Scraping failed: {err}" if err else "Unknown error"
            }
            results.append(error_result)
            print(f"Line {index}: error {err}", flush=True)
    
    return {
        "results": results,
        "total_processed": len(results),
        "successful": len([r for r in results if not r.get("error")]),
        "failed": len([r for r in results if r.get("error")])
    }


def main():
    parser = argparse.ArgumentParser(description='UCR Fee Scraper - Standalone Version')
    parser.add_argument('--json', type=str, help='JSON input as string')
    parser.add_argument('--file', type=str, help='JSON input file path')
    parser.add_argument('--acctkey', type=str, required=True, help='UCR account key')
    parser.add_argument('--output', type=str, help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Get JSON input
    if args.json:
        try:
            json_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"Error reading file: {e}"}))
            sys.exit(1)
    else:
        # Read from stdin
        try:
            json_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON from stdin: {e}"}))
            sys.exit(1)
    
    # Process the data
    result = process_json_input(json_data, args.acctkey)
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

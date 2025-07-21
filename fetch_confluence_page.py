#!/usr/bin/env python3
import requests
import base64
import yaml
import json
from urllib.parse import urlparse, parse_qs

def load_atlassian_config():
    """Load Atlassian configuration from YAML file"""
    with open('config/atlassian_config.yaml', 'r') as file:
        return yaml.safe_load(file)

def extract_page_id(url):
    """Extract page ID from Confluence URL"""
    # URL format: https://accton-group.atlassian.net/wiki/spaces/ECSP/pages/323682357/...
    parts = url.split('/')
    try:
        pages_index = parts.index('pages')
        page_id = parts[pages_index + 1]
        return page_id
    except (ValueError, IndexError):
        raise ValueError(f"Could not extract page ID from URL: {url}")

def fetch_confluence_page(page_id, config):
    """Fetch Confluence page content using REST API v2"""
    # Create authentication header
    auth_string = f"{config['email']}:{config['api_token']}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Use Confluence REST API v2
    base_url = config['domain'].rstrip('/')
    api_url = f"{base_url}/wiki/api/v2/pages/{page_id}"
    
    # Add expand parameters to get content and metadata
    params = {
        'body-format': 'atlas_doc_format',
        'include-labels': 'true',
        'include-properties': 'true'
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

def main():
    # Configuration
    confluence_url = "https://accton-group.atlassian.net/wiki/spaces/ECSP/pages/491356175/Edgecore+SONiC+202111.11+Feature+Support+on+2025+Apr"
    
    try:
        # Load configuration
        config = load_atlassian_config()
        print(f"Loaded config for: {config['email']}")
        
        # Extract page ID
        page_id = extract_page_id(confluence_url)
        print(f"Page ID: {page_id}")
        
        # Fetch page content
        page_data = fetch_confluence_page(page_id, config)
        
        if page_data:
            print("\n" + "="*80)
            print(f"Page Title: {page_data.get('title', 'N/A')}")
            print(f"Page ID: {page_data.get('id', 'N/A')}")
            print(f"Space: {page_data.get('spaceId', 'N/A')}")
            print(f"Status: {page_data.get('status', 'N/A')}")
            print(f"Created: {page_data.get('createdAt', 'N/A')}")
            
            # Print content if available
            if 'body' in page_data:
                print("\n" + "-"*80)
                print("Content:")
                print("-"*80)
                # The content is in Atlas Document Format (ADF)
                body = page_data['body']
                if 'atlas_doc_format' in body:
                    content = body['atlas_doc_format'].get('value', {})
                    print(json.dumps(content, indent=2))
                else:
                    print("No atlas_doc_format content found")
                    print("Available body formats:", list(body.keys()))
            else:
                print("No body content found in response")
                
            # Save full response to file for inspection
            with open('confluence_page_data.json', 'w') as f:
                json.dump(page_data, f, indent=2)
            print(f"\nFull page data saved to: confluence_page_data.json")
            
        else:
            print("Failed to fetch page content")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
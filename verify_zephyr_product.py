#!/usr/bin/env python3
"""
Zephyr Product Verification Script

This script helps determine which Zephyr product you're using and
provides guidance on the correct authentication method.

Usage:
    python verify_zephyr_product.py
"""

import requests
import yaml
import sys

def load_config(config_path='config/atlassian_config.yaml'):
    """Load configuration"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return config['zephy_scale']
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def test_zephyr_endpoints():
    """Test different Zephyr API endpoints to determine the product"""
    config = load_config()
    
    print("=" * 80)
    print("ZEPHYR PRODUCT VERIFICATION")
    print("=" * 80)
    print(f"Domain: {config['domain']}")
    print(f"Token: {config['access_token'][:20]}...")
    print(f"Project ID: {config['projectId']}")
    print()
    
    # Test different API endpoints
    endpoints = [
        {
            'name': 'Zephyr Scale Cloud (v2)',
            'url': 'https://api.zephyrscale.smartbear.com/v2/projects',
            'auth': f"Bearer {config['access_token']}",
            'headers': {'Authorization': f"Bearer {config['access_token']}", 'Accept': 'application/json'}
        },
        {
            'name': 'Zephyr Scale Cloud (v1)', 
            'url': 'https://api.zephyrscale.smartbear.com/v1/projects',
            'auth': f"Bearer {config['access_token']}",
            'headers': {'Authorization': f"Bearer {config['access_token']}", 'Accept': 'application/json'}
        },
        {
            'name': 'Zephyr Squad Cloud',
            'url': 'https://prod-api.zephyr4jiracloud.com/connect/public/rest/api/1.0/config/timetracking',
            'auth': f"Bearer {config['access_token']}",
            'headers': {'Authorization': f"Bearer {config['access_token']}", 'zapiAccessKey': config['access_token']}
        },
        {
            'name': 'Atlassian REST API (Jira Cloud)',
            'url': f"{config['domain'].rstrip('/')}/rest/api/3/project/{config['projectId']}",
            'auth': f"Bearer {config['access_token']}",
            'headers': {'Authorization': f"Bearer {config['access_token']}", 'Accept': 'application/json'}
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"Testing {endpoint['name']}:")
        print(f"  URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], headers=endpoint['headers'], timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:5]
                        print(f"  Response keys: {keys}")
                    results.append((endpoint['name'], 'SUCCESS', response.status_code, response.text[:200]))
                except:
                    results.append((endpoint['name'], 'SUCCESS', response.status_code, response.text[:200]))
            elif response.status_code == 401:
                print(f"  ❌ Authentication failed")
                print(f"  Response: {response.text[:100]}")
                results.append((endpoint['name'], 'AUTH_FAILED', response.status_code, response.text[:200]))
            elif response.status_code == 403:
                print(f"  ❌ Forbidden (token valid but no permissions)")
                results.append((endpoint['name'], 'FORBIDDEN', response.status_code, response.text[:200]))
            elif response.status_code == 404:
                print(f"  ❌ Not found")
                results.append((endpoint['name'], 'NOT_FOUND', response.status_code, response.text[:200]))
            else:
                print(f"  ❌ Unexpected status: {response.status_code}")
                print(f"  Response: {response.text[:100]}")
                results.append((endpoint['name'], 'OTHER', response.status_code, response.text[:200]))
                
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout")
            results.append((endpoint['name'], 'TIMEOUT', 0, 'Request timed out'))
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            results.append((endpoint['name'], 'ERROR', 0, str(e)))
        
        print()
    
    # Analysis
    print("=" * 80)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 80)
    
    successful = [r for r in results if r[1] == 'SUCCESS']
    auth_failed = [r for r in results if r[1] == 'AUTH_FAILED']
    
    if successful:
        print("🎉 WORKING ENDPOINTS:")
        for result in successful:
            print(f"  ✅ {result[0]} - Status {result[2]}")
        
        print(f"\nRECOMMENDATION:")
        print(f"  Your token works with: {', '.join([r[0] for r in successful])}")
        
    elif auth_failed:
        print("🔐 AUTHENTICATION ISSUES DETECTED:")
        for result in auth_failed:
            print(f"  🔑 {result[0]} - {result[3][:100]}")
        
        print(f"\nCOMMON SOLUTIONS:")
        print(f"  1. Check if your token is still valid in Jira")
        print(f"  2. Regenerate the API access token")
        print(f"  3. Verify you're using the correct Zephyr product")
        print(f"  4. Check token permissions in Jira settings")
        
    else:
        print("⚠️  NO CLEAR PATTERN DETECTED")
        print("   Manual investigation required")
    
    print(f"\nTOKEN VALIDATION STEPS:")
    print(f"  1. Log into Jira: {config['domain']}")
    print(f"  2. Go to: Apps → Zephyr Scale → API Access Tokens")
    print(f"  3. Verify your token: {config['access_token'][:10]}...{config['access_token'][-10:]}")
    print(f"  4. Check token status and regenerate if needed")

if __name__ == "__main__":
    test_zephyr_endpoints()
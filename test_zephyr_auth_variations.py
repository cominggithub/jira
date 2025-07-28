#!/usr/bin/env python3
"""
Test different authentication methods for Zephyr Scale Cloud

This script tests various authentication header formats to find the correct one.
"""

import requests
import yaml
import sys

def load_config():
    """Load configuration"""
    with open('config/atlassian_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        return config['zephy_scale']

def test_auth_variations():
    """Test different authentication header formats"""
    config = load_config()
    token = config['access_token']
    
    print("=" * 80)
    print("TESTING ZEPHYR SCALE AUTHENTICATION VARIATIONS")
    print("=" * 80)
    print(f"Token: {token[:20]}...")
    print()
    
    # Different auth header variations to test
    auth_variations = [
        {
            'name': 'Bearer Token (Standard)',
            'headers': {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        },
        {
            'name': 'Bearer Token (Alternative)',
            'headers': {'Authorization': f'bearer {token}', 'Accept': 'application/json'}
        },
        {
            'name': 'Access Token Header',
            'headers': {'Access-Token': token, 'Accept': 'application/json'}
        },
        {
            'name': 'API Key Header',
            'headers': {'X-API-Key': token, 'Accept': 'application/json'}
        },
        {
            'name': 'Zephyr Scale Token',
            'headers': {'X-Zephyr-Token': token, 'Accept': 'application/json'}
        },
        {
            'name': 'Custom Auth Header',
            'headers': {'X-Access-Token': token, 'Accept': 'application/json'}
        }
    ]
    
    base_url = "https://api.zephyrscale.smartbear.com/v2"
    test_endpoints = [
        "/projects",
        f"/projects/{config['projectId']}",
        "/healthcheck"
    ]
    
    for auth_var in auth_variations:
        print(f"Testing: {auth_var['name']}")
        print(f"Headers: {auth_var['headers']}")
        
        success_count = 0
        
        for endpoint in test_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, headers=auth_var['headers'], timeout=5)
                status = response.status_code
                
                if status == 200:
                    print(f"  ✅ {endpoint} - SUCCESS ({status})")
                    success_count += 1
                elif status == 401:
                    print(f"  🔑 {endpoint} - Auth failed ({status})")
                elif status == 403:
                    print(f"  🚫 {endpoint} - Forbidden ({status}) - Token valid but no permission")
                    success_count += 1  # Token is recognized
                elif status == 404:
                    print(f"  ❓ {endpoint} - Not found ({status})")
                else:
                    print(f"  ❌ {endpoint} - Status {status}: {response.text[:50]}")
                    
            except Exception as e:
                print(f"  💥 {endpoint} - Error: {str(e)[:50]}")
        
        if success_count > 0:
            print(f"  🎉 POTENTIAL SUCCESS! {success_count}/{len(test_endpoints)} endpoints responded positively")
        
        print("-" * 40)
    
    print()
    print("If none of the above worked, the issue might be:")
    print("1. Token expired or invalid")
    print("2. Wrong Zephyr product (Scale vs Squad)")
    print("3. API endpoint changed")
    print("4. Additional authentication requirements")

if __name__ == "__main__":
    test_auth_variations()
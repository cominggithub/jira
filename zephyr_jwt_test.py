#!/usr/bin/env python3
"""
Zephyr Squad Cloud JWT Authentication Test

This script generates JWT tokens for Zephyr Squad Cloud API authentication.
Zephyr Squad Cloud requires JWT tokens with specific claims for API access.

Usage:
    python zephyr_jwt_test.py
"""

import requests
import yaml
import json
import jwt
import hashlib
import hmac
import time
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus

class ZephyrJWTAuthenticator:
    def __init__(self, config_path='config/atlassian_config.yaml'):
        """Initialize with Zephyr configuration"""
        self.config = self.load_config(config_path)
        # These would need to be added to your config for JWT authentication
        self.access_key = self.config.get('access_token', '')  # This is actually the access key
        self.secret_key = self.config.get('secret_key', '')    # You need to add this to config
        self.account_id = self.config.get('account_id', '')    # You need to add this to config
        self.base_url = "https://prod-api.zephyr4jiracloud.com/connect"
    
    def load_config(self, config_path):
        """Load Zephyr configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['zephy_scale']
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except KeyError:
            print("zephy_scale configuration not found in config file")
            sys.exit(1)
    
    def generate_qsh(self, method, uri, query_params=None):
        """Generate Query String Hash (QSH) for JWT"""
        method = method.upper()
        
        # Normalize URI
        if not uri.startswith('/'):
            uri = '/' + uri
        
        # Normalize query parameters
        if query_params:
            sorted_params = sorted(query_params.items())
            query_string = '&'.join([f"{quote_plus(str(k))}={quote_plus(str(v))}" for k, v in sorted_params])
        else:
            query_string = ''
        
        # Create canonical request
        canonical_request = f"{method}&{quote_plus(uri)}&{quote_plus(query_string)}"
        
        # Generate QSH
        qsh = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        return qsh
    
    def generate_jwt_token(self, method, uri, query_params=None):
        """Generate JWT token for Zephyr API"""
        if not self.access_key or not self.secret_key or not self.account_id:
            print("❌ Missing required configuration for JWT generation:")
            print(f"   Access Key: {'✓' if self.access_key else '❌ Missing'}")
            print(f"   Secret Key: {'✓' if self.secret_key else '❌ Missing'}")
            print(f"   Account ID: {'✓' if self.account_id else '❌ Missing'}")
            print("\nFor Zephyr Squad Cloud, you need:")
            print("1. Access Key and Secret Key from Zephyr API Keys section")
            print("2. Account ID from your Atlassian profile URL")
            return None
        
        # JWT claims
        now = int(time.time())
        exp = now + 3600  # Token expires in 1 hour
        
        qsh = self.generate_qsh(method, uri, query_params)
        
        payload = {
            'iss': self.access_key,      # Issuer (access key)
            'sub': self.account_id,      # Subject (account ID)
            'qsh': qsh,                  # Query String Hash
            'iat': now,                  # Issued at
            'exp': exp                   # Expiration time
        }
        
        # Generate JWT token
        try:
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
        except Exception as e:
            print(f"❌ Error generating JWT token: {e}")
            return None
    
    def test_jwt_authentication(self):
        """Test JWT authentication with Zephyr API"""
        print("Testing Zephyr Squad Cloud JWT Authentication...")
        print(f"Base URL: {self.base_url}")
        print(f"Access Key: {self.access_key[:10]}..." if self.access_key else "❌ No access key")
        print(f"Account ID: {self.account_id}" if self.account_id else "❌ No account ID")
        print("-" * 60)
        
        # Test endpoint
        method = "GET"
        uri = "/public/rest/api/1.0/config/timetracking"
        
        # Generate JWT token
        jwt_token = self.generate_jwt_token(method, uri)
        if not jwt_token:
            return False
        
        print(f"Generated JWT token: {jwt_token[:50]}...")
        
        # Make API request
        headers = {
            'Authorization': f'JWT {jwt_token}',
            'Content-Type': 'application/json',
            'zapiAccessKey': self.access_key
        }
        
        url = f"{self.base_url}{uri}"
        
        try:
            response = requests.get(url, headers=headers)
            print(f"\nGET {url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ JWT Authentication successful!")
                return True
            else:
                print("❌ JWT Authentication failed!")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def check_configuration_requirements(self):
        """Check what configuration is needed"""
        print("=" * 80)
        print("ZEPHYR CONFIGURATION ANALYSIS")
        print("=" * 80)
        
        print(f"Current config structure:")
        print(f"  Domain: {self.config.get('domain', 'N/A')}")
        print(f"  Email: {self.config.get('email', 'N/A')}")
        print(f"  Project ID: {self.config.get('projectId', 'N/A')}")
        print(f"  Access Token: {self.config.get('access_token', 'N/A')[:20]}..." if self.config.get('access_token') else "N/A")
        
        print(f"\nZephyr Product Detection:")
        
        # Try to determine which Zephyr product based on current token format
        access_token = self.config.get('access_token', '')
        if len(access_token) == 36 and access_token.count('-') == 4:
            print("  Token format suggests: Zephyr Scale Cloud (UUID format)")
            print("  Expected auth: Bearer token")
        elif len(access_token) > 100:
            print("  Token format suggests: Zephyr Squad Cloud (Long key format)")
            print("  Expected auth: JWT with access/secret keys")
        else:
            print("  Token format: Unknown")
        
        print(f"\nRequired for Zephyr Scale Cloud:")
        print(f"  ✓ API Access Token (Bearer authentication)")
        print(f"  ✓ Project ID")
        
        print(f"\nRequired for Zephyr Squad Cloud:")
        print(f"  ? Access Key (from API Keys section)")
        print(f"  ? Secret Key (from API Keys section)")  
        print(f"  ? Account ID (from profile URL)")
        
        print(f"\nRecommendation:")
        print(f"  Based on your UUID-format token, try accessing Zephyr Scale Cloud directly")
        print(f"  through Jira: [Jira] → [Apps] → [Zephyr Scale] → [API Access Tokens]")

def main():
    """Main function"""
    try:
        authenticator = ZephyrJWTAuthenticator()
        
        # First analyze the configuration
        authenticator.check_configuration_requirements()
        
        # Try JWT authentication if we have the required fields
        print(f"\n" + "=" * 80)
        print("TESTING JWT AUTHENTICATION")
        print("=" * 80)
        
        success = authenticator.test_jwt_authentication()
        
        print(f"\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if success:
            print("🎉 JWT Authentication successful!")
        else:
            print("⚠️  JWT Authentication failed. Check configuration.")
            print("\nNext steps:")
            print("1. Verify you're using the correct Zephyr product (Scale vs Squad)")
            print("2. Generate proper API keys from Jira → Apps → Zephyr")
            print("3. Update your config with access_key, secret_key, and account_id")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
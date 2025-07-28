#!/usr/bin/env python3
"""
Zephyr Scale API Test Script

This script tests the connection to Zephyr Scale Cloud API using the configuration
from atlassian_config.yaml file.

Usage:
    python test_zephyr_scale_api.py
"""

import requests
import yaml
import json
import sys
from datetime import datetime

class ZephyrScaleAPITester:
    def __init__(self, config_path='config/atlassian_config.yaml'):
        """Initialize the API tester with configuration"""
        self.config = self.load_config(config_path)
        self.base_url = "https://api.zephyrscale.smartbear.com/v2"
        self.session = requests.Session()
        self.setup_headers()
    
    def load_config(self, config_path):
        """Load Zephyr Scale configuration from YAML file"""
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
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def setup_headers(self):
        """Setup authentication headers for API requests"""
        self.session.headers.update({
            'Authorization': f"Bearer {self.config['access_token']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        print(f"Using Bearer token: {self.config['access_token'][:20]}...")
    
    def test_connection(self):
        """Test basic API connection"""
        print("Testing Zephyr Scale API connection...")
        print(f"Base URL: {self.base_url}")
        print(f"Project ID: {self.config['projectId']}")
        print(f"Headers: {dict(self.session.headers)}")
        print("-" * 60)
        
        # Test multiple endpoints to diagnose the issue
        test_endpoints = [
            f"/projects/{self.config['projectId']}",
            "/projects",
            "/healthcheck"
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url)
                
                print(f"\nGET {url}")
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("✅ Connection successful!")
                        if endpoint.startswith('/projects/'):
                            print(f"Project Name: {data.get('name', 'N/A')}")
                            print(f"Project Key: {data.get('key', 'N/A')}")
                        return True
                    except json.JSONDecodeError:
                        print(f"✅ Response successful but not JSON: {response.text[:200]}")
                        return True
                else:
                    print("❌ Connection failed!")
                    print(f"Response: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
        
        return False
    
    def get_test_cases(self, limit=5):
        """Get test cases from the project"""
        print(f"\nFetching test cases (limit: {limit})...")
        print("-" * 60)
        
        try:
            url = f"{self.base_url}/testcases"
            params = {
                'projectId': self.config['projectId'],
                'maxResults': limit
            }
            
            response = self.session.get(url, params=params)
            print(f"GET {url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                print(f"✅ Found {len(values)} test cases")
                
                for i, test_case in enumerate(values, 1):
                    print(f"\n{i}. Test Case:")
                    print(f"   ID: {test_case.get('id', 'N/A')}")
                    print(f"   Key: {test_case.get('key', 'N/A')}")
                    print(f"   Name: {test_case.get('name', 'N/A')}")
                    print(f"   Status: {test_case.get('status', {}).get('name', 'N/A')}")
                    
                return True
            else:
                print("❌ Failed to fetch test cases!")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def get_test_cycles(self, limit=5):
        """Get test cycles from the project"""
        print(f"\nFetching test cycles (limit: {limit})...")
        print("-" * 60)
        
        try:
            url = f"{self.base_url}/testcycles"
            params = {
                'projectId': self.config['projectId'],
                'maxResults': limit
            }
            
            response = self.session.get(url, params=params)
            print(f"GET {url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                print(f"✅ Found {len(values)} test cycles")
                
                for i, cycle in enumerate(values, 1):
                    print(f"\n{i}. Test Cycle:")
                    print(f"   ID: {cycle.get('id', 'N/A')}")
                    print(f"   Key: {cycle.get('key', 'N/A')}")
                    print(f"   Name: {cycle.get('name', 'N/A')}")
                    print(f"   Status: {cycle.get('status', {}).get('name', 'N/A')}")
                    
                return True
            else:
                print("❌ Failed to fetch test cycles!")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 80)
        print("ZEPHYR SCALE API TEST RESULTS")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Config: {self.config['email']} - Project ID: {self.config['projectId']}")
        print()
        
        results = []
        
        # Test 1: Basic connection
        results.append(self.test_connection())
        
        # Test 2: Get test cases
        results.append(self.get_test_cases())
        
        # Test 3: Get test cycles
        results.append(self.get_test_cycles())
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        passed = sum(results)
        total = len(results)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Zephyr Scale API is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the API configuration.")
        
        return passed == total

def main():
    """Main function"""
    try:
        tester = ZephyrScaleAPITester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
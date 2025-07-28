#!/usr/bin/env python3
"""
Get ESTS Project Information from Jira

This script retrieves the ESTS project details from Jira using the Jira REST API.
"""

import requests
import base64
import yaml
import json
import sys

def load_config():
    """Load Jira configuration"""
    try:
        with open('config/atlassian_config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            return config['jira']
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def setup_auth(config):
    """Setup authentication for Jira API"""
    auth_string = f"{config['email']}:{config['api_token']}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    return {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def get_project_by_key(config, project_key):
    """Get project information by project key"""
    headers = setup_auth(config)
    base_url = config['domain'].rstrip('/')
    
    # Get project by key
    url = f"{base_url}/rest/api/3/project/{project_key}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"❌ Project '{project_key}' not found")
            return None
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def search_projects_with_ests(config):
    """Search for projects containing 'ESTS' in name or key"""
    headers = setup_auth(config)
    base_url = config['domain'].rstrip('/')
    
    # Get all projects and filter for ESTS
    url = f"{base_url}/rest/api/3/project/search"
    params = {
        'query': 'ESTS',
        'expand': 'description,lead,issueTypes,url,projectKeys'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('values', [])
        else:
            print(f"❌ Search failed: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

def get_all_projects(config):
    """Get all projects to find ESTS-related ones"""
    headers = setup_auth(config)
    base_url = config['domain'].rstrip('/')
    
    url = f"{base_url}/rest/api/3/project"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            # Filter for ESTS-related projects
            ests_projects = [p for p in projects if 'ESTS' in p.get('name', '').upper() or 'ESTS' in p.get('key', '').upper()]
            return ests_projects
        else:
            print(f"❌ Failed to get projects: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

def main():
    """Main function"""
    config = load_config()
    
    print("=" * 80)
    print("SEARCHING FOR ESTS PROJECT IN JIRA")
    print("=" * 80)
    print(f"Jira Domain: {config['domain']}")
    print(f"User: {config['email']}")
    print()
    
    # Method 1: Try direct lookup with ESTS key
    print("1. Looking up project with key 'ESTS'...")
    print("-" * 40)
    ests_project = get_project_by_key(config, 'ESTS')
    
    if ests_project:
        print("✅ Found ESTS project!")
        print(f"   Project Key: {ests_project.get('key', 'N/A')}")
        print(f"   Project Name: {ests_project.get('name', 'N/A')}")
        print(f"   Project ID: {ests_project.get('id', 'N/A')}")
        print(f"   Description: {ests_project.get('description', 'N/A')}")
        print(f"   Lead: {ests_project.get('lead', {}).get('displayName', 'N/A')}")
        print(f"   Project Type: {ests_project.get('projectTypeKey', 'N/A')}")
        
        # Save detailed project info
        with open('ests_project_details.json', 'w') as f:
            json.dump(ests_project, f, indent=2)
        print(f"   📄 Full details saved to: ests_project_details.json")
    else:
        print("❌ Project 'ESTS' not found")
    
    print()
    
    # Method 2: Search for ESTS in project names/keys
    print("2. Searching all projects for 'ESTS'...")
    print("-" * 40)
    ests_related = search_projects_with_ests(config)
    
    if ests_related:
        print(f"✅ Found {len(ests_related)} ESTS-related projects:")
        for project in ests_related:
            print(f"   • {project.get('key', 'N/A')} - {project.get('name', 'N/A')}")
    else:
        print("❌ No ESTS-related projects found in search")
    
    print()
    
    # Method 3: Get all projects and filter manually
    print("3. Checking all accessible projects...")
    print("-" * 40)
    all_ests = get_all_projects(config)
    
    if all_ests:
        print(f"✅ Found {len(all_ests)} projects with 'ESTS' in name/key:")
        for project in all_ests:
            print(f"   • {project.get('key', 'N/A')} - {project.get('name', 'N/A')} (ID: {project.get('id', 'N/A')})")
    else:
        print("❌ No projects containing 'ESTS' found")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if ests_project:
        print(f"🎉 ESTS project found!")
        print(f"   Project Key: {ests_project['key']}")
        print(f"   Project ID: {ests_project['id']}")
        print(f"   Use this in your Zephyr Scale configuration.")
    elif ests_related or all_ests:
        print(f"🔍 Found related projects but no exact 'ESTS' match.")
        print(f"   Check the project keys listed above.")
    else:
        print(f"❌ No ESTS projects found.")
        print(f"   Possible reasons:")
        print(f"   - Project doesn't exist")
        print(f"   - No access permissions")
        print(f"   - Different project key name")

if __name__ == "__main__":
    main()
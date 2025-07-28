"""
Zephyr Scale API utility module

This module provides functions to interact with Zephyr Scale Cloud API
for retrieving test cases, test cycles, and other test management data.
"""

import requests
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ZephyrScaleAPI:
    """Zephyr Scale Cloud API client"""
    
    def __init__(self, config_path: str = 'config/atlassian_config.yaml'):
        """Initialize API client with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = "https://api.zephyrscale.smartbear.com/v2"
        self.session = requests.Session()
        self._setup_auth()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load Zephyr Scale configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['zephy_scale']
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except KeyError:
            logger.error("zephy_scale configuration not found in config file")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _setup_auth(self):
        """Setup authentication headers for API requests"""
        self.session.headers.update({
            'Authorization': f"Bearer {self.config['access_token']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Zephyr Scale API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects"""
        data = self._make_request("/projects")
        return data.get('values', []) if data else []
    
    def get_project_by_key(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Get specific project by key"""
        projects = self.get_projects()
        for project in projects:
            if project.get('key') == project_key:
                return project
        return None
    
    def get_test_cases(self, project_key: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get test cases, optionally filtered by project"""
        params = {'maxResults': max_results}
        
        if project_key:
            # Get project ID from key
            project = self.get_project_by_key(project_key)
            if project:
                params['projectId'] = project['id']
            else:
                logger.warning(f"Project with key '{project_key}' not found")
                return []
        
        data = self._make_request("/testcases", params)
        return data.get('values', []) if data else []
    
    def get_test_case_details(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific test case"""
        return self._make_request(f"/testcases/{test_case_id}")
    
    def get_test_cycles(self, project_key: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get test cycles, optionally filtered by project"""
        params = {'maxResults': max_results}
        
        if project_key:
            # Get project ID from key
            project = self.get_project_by_key(project_key)
            if project:
                params['projectId'] = project['id']
            else:
                logger.warning(f"Project with key '{project_key}' not found")
                return []
        
        data = self._make_request("/testcycles", params)
        return data.get('values', []) if data else []
    
    def get_ests_test_cases(self) -> List[Dict[str, Any]]:
        """Get test cases specifically for ESTS project"""
        # First try the configured project key
        project_key = self.config.get('projectKey', 'ESTS')
        test_cases = self.get_test_cases(project_key, max_results=1000)
        
        # If no test cases found with configured key, try to get all test cases
        if not test_cases:
            logger.info(f"No test cases found for project key '{project_key}', getting all available test cases")
            test_cases = self.get_test_cases(max_results=1000)
        
        # Enrich test cases with additional processing
        enriched_cases = []
        for case in test_cases:
            enriched_case = self._enrich_test_case(case)
            enriched_cases.append(enriched_case)
        
        return enriched_cases
    
    def _enrich_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich test case with additional metadata and formatting"""
        enriched = test_case.copy()
        
        # Extract category from labels or name
        enriched['category'] = self._extract_category(test_case)
        
        # Extract feature key from labels or custom fields
        enriched['feature_key'] = self._extract_feature_key(test_case)
        
        # Format labels as comma-separated string
        labels = test_case.get('labels', [])
        enriched['labels_str'] = ', '.join(labels) if labels else ''
        
        # Add formatted creation date
        created_on = test_case.get('createdOn')
        if created_on:
            try:
                dt = datetime.fromisoformat(created_on.replace('Z', '+00:00'))
                enriched['created_date'] = dt.strftime('%Y-%m-%d')
            except:
                enriched['created_date'] = created_on
        else:
            enriched['created_date'] = ''
        
        # Add test case URL for Zephyr Scale
        base_domain = self.config.get('domain', '').rstrip('/')
        if base_domain and test_case.get('key'):
            enriched['url'] = f"{base_domain}/plugins/servlet/tm/testcase/{test_case['key']}"
        else:
            enriched['url'] = ''
        
        return enriched
    
    def _extract_category(self, test_case: Dict[str, Any]) -> str:
        """Extract test category from test case metadata"""
        # Try to extract from labels first
        labels = test_case.get('labels', [])
        category_keywords = ['functional', 'performance', 'security', 'reliability', 'compliance', 'regression']
        
        for label in labels:
            label_lower = label.lower()
            for keyword in category_keywords:
                if keyword in label_lower:
                    return keyword.title()
        
        # Try to extract from name
        name = test_case.get('name', '').lower()
        for keyword in category_keywords:
            if keyword in name:
                return keyword.title()
        
        # Default category
        return 'Functional'
    
    def _extract_feature_key(self, test_case: Dict[str, Any]) -> str:
        """Extract feature key from test case metadata"""
        # Try to extract from labels
        labels = test_case.get('labels', [])
        for label in labels:
            # Look for labels that might be feature keys (pattern: uppercase with underscores)
            if '_' in label and label.isupper():
                return label
            # Look for labels starting with common prefixes
            if any(label.startswith(prefix) for prefix in ['FEAT_', 'SONIC_', 'BGP_', 'VLAN_', 'LAG_']):
                return label
        
        # Try to extract from custom fields or other metadata
        custom_fields = test_case.get('customFields', {})
        for field_name, field_value in custom_fields.items():
            if 'feature' in field_name.lower() and field_value:
                return str(field_value)
        
        # Default to test case key if no feature key found
        return test_case.get('key', '')
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API connection status and basic info"""
        try:
            projects = self.get_projects()
            ests_project = self.get_project_by_key(self.config.get('projectKey', 'ESTS'))
            
            return {
                'status': 'connected',
                'projects_count': len(projects),
                'ests_project_found': ests_project is not None,
                'ests_project_id': ests_project.get('id') if ests_project else None,
                'base_url': self.base_url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'base_url': self.base_url,
                'timestamp': datetime.now().isoformat()
            }

# Convenience function for easy import
def get_zephyr_api() -> ZephyrScaleAPI:
    """Get configured Zephyr Scale API instance"""
    return ZephyrScaleAPI()
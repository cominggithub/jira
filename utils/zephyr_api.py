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

import base64

class ZephyrScaleAPI:
    """Zephyr Scale Cloud API client"""
    
    def __init__(self, config_path: str = 'config/atlassian_config.yaml'):
        """Initialize API client with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = "https://api.zephyrscale.smartbear.com/v2"
        self.session = requests.Session()
        self._setup_auth()
        self.jira_config = self._load_jira_config(config_path)

    def _load_jira_config(self, config_path: str) -> Dict[str, Any]:
        """Load Jira configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['jira']
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except KeyError:
            logger.error("jira configuration not found in config file")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise

    def _get_jira_project_name(self, jira_project_id: int) -> Optional[str]:
        """Get project name from Jira API"""
        auth_string = f"{self.jira_config['email']}:{self.jira_config['api_token']}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        url = f"{self.jira_config['domain'].rstrip('/')}/rest/api/3/project/{jira_project_id}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('name')
            else:
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Jira API request failed for project {jira_project_id}: {e}")
            return None
    
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
        """Make authenticated request to Zephyr Scale API, handling pagination"""
        all_results = []
        url = f"{self.base_url}{endpoint}"
        current_params = params.copy() if params else {}
        current_params['maxResults'] = 100 # Fetch 100 results per page
        current_params['startAt'] = 0

        while True:
            try:
                response = self.session.get(url, params=current_params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                values = data.get('values', [])
                all_results.extend(values)
                
                if data.get('isLast', True):
                    break
                
                current_params['startAt'] += current_params['maxResults']

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed for {endpoint}: {e}")
                return None
        
        return {'values': all_results, 'total': len(all_results), 'isLast': True}
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects"""
        data = self._make_request("/projects")
        projects = data.get('values', []) if data else []
        for project in projects:
            jira_project_id = project.get('jiraProjectId')
            if jira_project_id:
                project['name'] = self._get_jira_project_name(jira_project_id)
            else:
                project['name'] = None
        return projects
    
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
    
    def search_test_case_by_ests_format(self, ests_key: str) -> Optional[Dict[str, Any]]:
        """Search for test case using ESTS format (e.g., ESTS-T333)
        
        Args:
            ests_key: Test case key in ESTS format (e.g., "ESTS-T333")
            
        Returns:
            Test case data if found, None otherwise
        """
        # Extract number from ESTS format (e.g., "ESTS-T333" -> "333")
        if not ests_key.startswith('ESTS-T'):
            logger.warning(f"Invalid ESTS format: {ests_key}")
            return None
            
        test_number = ests_key.replace('ESTS-T', '')
        logger.info(f"Searching for ESTS test case {ests_key} (test number: {test_number})")
        
        # Get all test cases from the ESTS project (Jira ID 14601)
        # This will include all test cases from SS, T650, NTC, etc. projects
        all_test_cases = self.get_ests_test_cases()
        
        # Search for test cases with matching test number
        for case in all_test_cases:
            case_key = case.get('key', '')
            
            # Check if the test number matches (e.g., SS-T333, T650-T333, NTC-T333)
            if '-' in case_key:
                prefix, number = case_key.split('-', 1)
                # Remove 'T' prefix if present (e.g., T333 -> 333)
                clean_number = number.replace('T', '') if number.startswith('T') else number
                
                if clean_number == test_number:
                    logger.info(f"Found ESTS test case {ests_key} as {case_key}")
                    return case
        
        # If exact match not found, try broader search
        logger.info(f"Exact match not found for {ests_key}, trying broader search")
        for case in all_test_cases:
            case_key = case.get('key', '')
            case_name = case.get('name', '').lower()
            
            # Check if test number appears anywhere in key or name
            if test_number in case_key or test_number in case_name:
                logger.info(f"Found potential match for {ests_key}: {case_key}")
                return case
                
        logger.info(f"ESTS test case {ests_key} not found in ESTS project data")
        return None
    
    def get_enhanced_test_case_info(self, test_case_key: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive test case information including related data
        
        Args:
            test_case_key: Test case key in ESTS format (ESTS-T333, ESTS-T1, etc.)
            
        Returns:
            Enhanced test case information
        """
        # All test cases should be searched using ESTS format
        if not test_case_key.startswith('ESTS-T'):
            logger.warning(f"Expected ESTS format, got: {test_case_key}")
            return None
            
        # Use ESTS search to find the underlying test case
        test_case = self.search_test_case_by_ests_format(test_case_key)
        
        if not test_case:
            return None
            
        # Get detailed information using the original key
        original_key = test_case.get('key')  # This is the original SS-T1, NTC-T423 format
        test_case_id = test_case.get('id')
        if test_case_id:
            detailed_case = self.get_test_case_details(test_case_id)
            if detailed_case:
                test_case.update(detailed_case)
        
        # Enrich with our standard processing
        enhanced_case = self._enrich_test_case(test_case)
        enhanced_case = self._add_ests_mapping(enhanced_case)
        
        # Add additional analysis
        enhanced_case['analysis'] = self._analyze_test_case(enhanced_case)
        
        return enhanced_case
    
    def _analyze_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test case and provide additional insights"""
        analysis = {
            'complexity': 'Unknown',
            'automation_feasible': False,
            'dependencies': [],
            'risk_level': 'Medium'
        }
        
        name = test_case.get('name', '').lower()
        description = test_case.get('description', '').lower()
        labels = test_case.get('labels', [])
        
        # Analyze complexity based on keywords
        complexity_indicators = {
            'high': ['integration', 'end-to-end', 'performance', 'load', 'stress', 'security'],
            'medium': ['functional', 'api', 'interface', 'workflow'],
            'low': ['unit', 'basic', 'simple', 'check', 'verify', 'version']
        }
        
        for level, keywords in complexity_indicators.items():
            if any(keyword in name or keyword in description for keyword in keywords):
                analysis['complexity'] = level.title()
                break
        
        # Check automation feasibility
        automation_keywords = ['api', 'cli', 'automated', 'script', 'check', 'verify', 'status']
        manual_keywords = ['manual', 'visual', 'physical', 'human', 'observe']
        
        if any(keyword in name or keyword in description for keyword in automation_keywords):
            analysis['automation_feasible'] = True
        elif any(keyword in name or keyword in description for keyword in manual_keywords):
            analysis['automation_feasible'] = False
        
        # Analyze risk level based on category and complexity
        category = test_case.get('category', '').lower()
        if category in ['security', 'performance'] or analysis['complexity'] == 'High':
            analysis['risk_level'] = 'High'
        elif category in ['functional', 'reliability'] or analysis['complexity'] == 'Medium':
            analysis['risk_level'] = 'Medium'
        else:
            analysis['risk_level'] = 'Low'
        
        # Extract potential dependencies from labels
        dependency_keywords = ['prerequisite', 'depends', 'requires', 'after']
        for label in labels:
            if any(keyword in label.lower() for keyword in dependency_keywords):
                analysis['dependencies'].append(label)
        
        return analysis
    
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
        # ESTS in Jira (project ID 14601) aggregates test cases from multiple Zephyr Scale projects
        # Use the Jira project ID directly to get the correct test cases
        
        logger.info("Fetching test cases from Jira ESTS project (ID: 14601)")
        
        # Get test cases using Jira project ID 14601
        test_cases = []
        page = 0
        max_pages = 10  # Reasonable limit to avoid excessive API calls
        
        while page < max_pages:
            try:
                params = {
                    'projectId': 14601,  # Jira ESTS project ID
                    'maxResults': 100,
                    'startAt': page * 100
                }
                
                data = self._make_request("/testcases", params)
                if not data:
                    break
                    
                values = data.get('values', [])
                test_cases.extend(values)
                
                logger.info(f"Fetched page {page + 1}: {len(values)} test cases")
                
                # Check if we've reached the last page
                if data.get('isLast', True):
                    logger.info("Reached last page of test cases")
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        logger.info(f"Total test cases retrieved: {len(test_cases)}")
        
        # Enrich test cases with additional processing
        enriched_cases = []
        for case in test_cases:
            enriched_case = self._enrich_test_case(case)
            # Add ESTS-specific enrichment
            enriched_case = self._add_ests_mapping(enriched_case)
            enriched_cases.append(enriched_case)
        
        return enriched_cases
    
    def _add_ests_mapping(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Add ESTS-specific mapping and context"""
        enriched = test_case.copy()
        
        # Get the original project key from the test case key
        original_key = enriched.get('key', '')
        if original_key and '-' in original_key:
            project_prefix = original_key.split('-')[0]
            test_number = original_key.split('-')[1]
            
            # Store the original key for reference
            enriched['original_key'] = original_key
            enriched['source_project'] = project_prefix
            
            # Replace the key with ESTS format for display
            enriched['key'] = f"ESTS-{test_number}"
            enriched['ests_url_format'] = f"ESTS-{test_number}"
            
            # Add project mapping information
            enriched['project_mapping'] = f"ESTS → {project_prefix}"
            enriched['ests_context'] = True
        else:
            # Fallback for cases without proper key format
            enriched['original_key'] = original_key
            enriched['key'] = f"ESTS-{original_key}"
            enriched['ests_url_format'] = f"ESTS-{original_key}"
            enriched['project_mapping'] = "ESTS → Unknown"
            enriched['source_project'] = 'Unknown'
            enriched['ests_context'] = True
            
        return enriched
    
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
        
        # Add test case URL for Zephyr Scale (use original key for URL if available)
        base_domain = self.config.get('domain', '').rstrip('/')
        # Use the original test case key from before ESTS mapping
        url_key = test_case.get('key')  # This is the original key before mapping
        if base_domain and url_key:
            enriched['url'] = f"{base_domain}/plugins/servlet/tm/testcase/{url_key}"
        else:
            enriched['url'] = ''

        # Extract status name by making another API call if necessary
        status_data = test_case.get('status')
        if isinstance(status_data, dict) and 'self' in status_data:
            status_details = self._make_request(status_data['self'].replace(self.base_url, ''))
            if status_details:
                enriched['status_name'] = status_details.get('name')
            else:
                enriched['status_name'] = None
        elif isinstance(status_data, str):
            enriched['status_name'] = status_data
        else:
            enriched['status_name'] = None
        
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
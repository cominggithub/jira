# Zephyr Scale Integration Specification

## Requirements

### Functional Requirements

1. **API Integration**
   - Connect to Zephyr Scale Cloud REST API v2
   - Authenticate using JWT tokens
   - Retrieve test cases, test cycles, and project information
   - Handle API rate limiting and error responses

2. **Test Case Management**
   - Display test cases in tabular format with filtering
   - Categorize test cases (Functional, Performance, Security, etc.)
   - Map test cases to SONiC feature keys
   - Support label-based organization and search

3. **Data Processing**
   - Enrich test case data with metadata
   - Extract feature keys from labels and custom fields
   - Generate statistics and analytics
   - Export data in multiple formats (CSV, JSON)

4. **User Interface**
   - Responsive web interface for test case browsing
   - Real-time filtering and search capabilities
   - Sortable columns and pagination
   - Export functionality with progress indicators

### Non-Functional Requirements

1. **Performance**
   - API response time < 3 seconds
   - Support 1000+ test cases without performance degradation
   - Efficient data caching and pagination
   - Minimal memory footprint

2. **Reliability**
   - Handle API timeouts and network failures gracefully
   - Retry mechanisms for transient failures
   - Data consistency and validation
   - Comprehensive error logging

3. **Usability**
   - Intuitive interface design
   - Clear error messages and status indicators
   - Mobile-responsive layout
   - Accessibility compliance

## Feature Description

### Core Components

#### 1. Zephyr Scale API Client
**File**: `utils/zephyr_api.py`
**Class**: `ZephyrScaleAPI`

**Capabilities**:
- JWT token-based authentication
- RESTful API communication
- Error handling and retry logic
- Response caching and optimization

**Methods**:
```python
def get_projects() -> List[Dict[str, Any]]
def get_project_by_key(project_key: str) -> Optional[Dict[str, Any]]
def get_test_cases(project_key: str, max_results: int) -> List[Dict[str, Any]]
def get_test_case_details(test_case_id: str) -> Optional[Dict[str, Any]]
def get_test_cycles(project_key: str, max_results: int) -> List[Dict[str, Any]]
def get_ests_test_cases() -> List[Dict[str, Any]]
```

#### 2. Web Interface
**Route**: `/ests/test-cases`
**Template**: `templates/ests_test_cases.html`

**Features**:
- Statistics dashboard with key metrics
- Filterable and sortable data table
- Category-based organization
- Export capabilities
- Responsive design with theme support

#### 3. Data Enrichment
**Purpose**: Enhance raw API data with additional metadata

**Enrichment Process**:
1. Category classification from labels/names
2. Feature key extraction from metadata
3. Label formatting and organization
4. URL generation for external links
5. Date formatting and localization

## Configuration

### API Configuration
```yaml
# config/atlassian_config.yaml
zephy_scale:
  domain: "https://accton-group.atlassian.net/"
  email: "peter_lin@edge-core.com"
  projectKey: ESTS
  access_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### API Endpoints
```python
# Base URL for Zephyr Scale API
BASE_URL = "https://api.zephyrscale.smartbear.com/v2"

# Key endpoints
ENDPOINTS = {
    "projects": "/projects",
    "test_cases": "/testcases", 
    "test_cycles": "/testcycles",
    "project_detail": "/projects/{project_id}",
    "test_case_detail": "/testcases/{test_case_id}"
}
```

### Authentication Headers
```python
headers = {
    'Authorization': f"Bearer {access_token}",
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

## Test Criteria

### Unit Tests
- [ ] API client initialization and configuration
- [ ] Authentication token validation
- [ ] HTTP request/response handling
- [ ] Data parsing and validation
- [ ] Error handling for various scenarios

### Integration Tests
- [ ] End-to-end API communication
- [ ] Data retrieval and processing
- [ ] Web interface functionality
- [ ] Export feature operation
- [ ] Performance under load

### API Tests
- [ ] Connection establishment
- [ ] Project discovery and selection
- [ ] Test case retrieval with pagination
- [ ] Error response handling
- [ ] Rate limiting compliance

### UI Tests
- [ ] Table rendering and data display
- [ ] Filtering and search functionality
- [ ] Sorting operations
- [ ] Export feature
- [ ] Responsive design on various devices

## Source Code Structure

```
/
├── utils/
│   └── zephyr_api.py               # Zephyr Scale API client
├── templates/
│   └── ests_test_cases.html        # Test cases web interface
├── static/
│   ├── css/                        # Styling for test cases page
│   └── js/                         # JavaScript for interactions
├── config/
│   └── atlassian_config.yaml       # API configuration
├── app.py                          # Flask routes integration
└── tests/
    ├── test_zephyr_api.py          # API client tests
    ├── test_zephyr_integration.py  # Integration tests
    └── fixtures/
        ├── api_responses.json       # Mock API responses
        └── test_cases_sample.json   # Sample test case data
```

## Temporary Folders

### Working Directories
- `tmp/zephyr/` - Temporary API response cache
- `exports/` - Generated export files
- `logs/api/` - API operation logs

### Cache Locations
- `cache/zephyr_projects.json` - Projects cache
- `cache/test_cases_{project_key}.json` - Test cases cache
- `cache/api_status.json` - API status cache

## Test Files Structure

```
tests/zephyr/
├── test_api_client.py              # API client unit tests
├── test_data_enrichment.py         # Data processing tests
├── test_web_interface.py           # Web UI tests
├── test_export_functionality.py   # Export feature tests
├── fixtures/
│   ├── mock_responses/             # Mock API responses
│   │   ├── projects.json           # Projects API response
│   │   ├── test_cases.json         # Test cases API response
│   │   └── test_cycles.json        # Test cycles API response
│   ├── sample_data/                # Sample processed data
│   │   ├── enriched_test_cases.json # Enriched test case data
│   │   └── statistics.json         # Sample statistics
│   └── config/                     # Test configurations
│       └── test_config.yaml        # Test API configuration
├── integration/
│   ├── test_api_integration.py     # Full API integration tests
│   └── test_web_integration.py     # Web interface integration
└── performance/
    ├── test_api_performance.py     # API performance tests
    └── test_ui_performance.py      # UI performance tests
```

## API Response Processing

### Test Case Data Structure
```json
{
  "id": "173931926",
  "key": "SS-T1", 
  "name": "Check version",
  "status": {
    "name": "Approved"
  },
  "labels": ["system", "version", "basic"],
  "createdOn": "2024-01-15T10:30:00Z",
  "project": {
    "id": "410465",
    "key": "SS"
  },
  "customFields": {
    "feature_key": "SYSTEM_INFO",
    "category": "Functional"
  }
}
```

### Enriched Data Structure
```json
{
  "id": "173931926",
  "key": "SS-T1",
  "name": "Check version", 
  "category": "Functional",
  "feature_key": "SYSTEM_INFO",
  "labels_str": "system, version, basic",
  "status": {"name": "Approved"},
  "created_date": "2024-01-15",
  "url": "https://accton-group.atlassian.net/plugins/servlet/tm/testcase/SS-T1"
}
```

## Data Processing Pipeline

### 1. API Data Retrieval
```python
# Retrieve test cases from API
test_cases = api_client.get_test_cases(project_key="ESTS", max_results=1000)
```

### 2. Data Enrichment
```python
# Enrich each test case with additional metadata
for case in test_cases:
    enriched_case = api_client._enrich_test_case(case)
    enriched_cases.append(enriched_case)
```

### 3. Category Classification
```python
def _extract_category(self, test_case: Dict[str, Any]) -> str:
    """Extract test category from labels or name"""
    # Priority: labels -> name -> default
    category_keywords = ['functional', 'performance', 'security', 'reliability']
    # Implementation logic...
```

### 4. Feature Key Extraction
```python
def _extract_feature_key(self, test_case: Dict[str, Any]) -> str:
    """Extract feature key from metadata"""
    # Priority: labels -> custom fields -> test key
    # Implementation logic...
```

## Error Handling

### API Error Categories
1. **Authentication Errors** (401)
   - Invalid or expired JWT token
   - Missing authentication headers
   - Token refresh requirements

2. **Authorization Errors** (403)  
   - Insufficient permissions
   - Project access restrictions
   - Feature limitations

3. **Not Found Errors** (404)
   - Project not found
   - Test case not found
   - Invalid endpoint

4. **Rate Limiting** (429)
   - API quota exceeded
   - Request frequency limits
   - Retry-after headers

5. **Server Errors** (5xx)
   - Zephyr Scale service issues
   - Network connectivity problems
   - Timeout errors

### Error Recovery Strategies
```python
def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Make authenticated request with error handling"""
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(2 ** attempt)  # Exponential backoff
            logger.error(f"API request failed (attempt {attempt + 1}): {e}")
    return None
```

## Performance Optimization

### Caching Strategy
- Project list cached for 1 hour
- Test cases cached for 15 minutes
- API status cached for 5 minutes
- Client-side caching for static data

### Request Optimization
- Batch API requests where possible
- Use pagination for large datasets
- Implement request deduplication
- Connection pooling and reuse

### UI Performance
- Virtual scrolling for large tables
- Lazy loading of test case details
- Debounced search and filtering
- Progressive data loading

## Security Considerations

### API Token Management
- Secure token storage in configuration
- Token validation and expiration handling
- Environment-specific token management
- Audit logging for token usage

### Data Protection
- Input sanitization for search queries
- XSS prevention in data display
- CSRF protection for form submissions
- Secure export file generation

### Access Control
- Project-level access validation
- User permission checking
- API endpoint access restrictions
- Rate limiting and abuse prevention

## Monitoring and Analytics

### API Metrics
- Request success/failure rates
- Response time distribution
- Error categorization and trends
- API quota usage tracking

### User Analytics
- Page view and interaction tracking
- Feature usage statistics
- Export operation metrics
- Performance bottleneck identification

### Alerting
- API connectivity issues
- High error rates
- Performance degradation
- Quota threshold warnings
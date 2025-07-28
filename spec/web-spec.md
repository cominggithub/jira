# Web Application Specification

## Requirements

### Functional Requirements

1. **Feature Management**
   - Display SONiC feature support matrix across different branches
   - Filter features by labels, branches, and support status
   - Import features from Excel files
   - Manage feature classifications (EC proprietary vs community)

2. **Test Case Management**
   - Integration with Zephyr Scale API for test case retrieval
   - Display test cases with categorization and feature mapping
   - Filter and search test cases
   - Export test case data

3. **SAI Analysis**
   - Parse and analyze SAI recording files
   - Generate comprehensive reports
   - Visualize SAI API usage patterns
   - Feature mapping between SAI and SONiC

4. **MCP Integration**
   - Interface with MCP servers for AI-powered analysis
   - Display MCP server status and configuration
   - Execute MCP tools through web interface

### Non-Functional Requirements

1. **Performance**
   - Page load time < 3 seconds
   - Support 1000+ test cases without performance degradation
   - Efficient database queries with pagination

2. **Usability**
   - Responsive design for mobile and desktop
   - Multiple theme support (Dark, Neon, Tron, Pink, Pony, White)
   - Intuitive navigation with dropdown menus

3. **Security**
   - Secure API token storage
   - Input validation and sanitization
   - HTTPS support in production

## Feature Description

### Core Components

#### 1. SONiC Feature Matrix
- **Route**: `/feature-list`
- **Purpose**: Display comprehensive feature support across SONiC branches
- **Features**:
  - Filterable table with branch support status
  - Label-based categorization
  - Community vs EC proprietary classification
  - Export capabilities

#### 2. ESTS Test Case Management
- **Route**: `/ests/test-cases`
- **Purpose**: Zephyr Scale integration for test case management
- **Features**:
  - Real-time API integration
  - Category-based organization
  - Feature key mapping
  - Label management
  - Export to CSV

#### 3. SAI Analysis Suite
- **Routes**: `/sai/*`
- **Purpose**: SAI recording analysis and reporting
- **Features**:
  - File upload and processing
  - API usage analysis
  - Feature mapping visualization
  - Report generation

#### 4. MCP Server Interface
- **Route**: `/mcp`
- **Purpose**: MCP server management and interaction
- **Features**:
  - Server status monitoring
  - Configuration management
  - Tool execution interface

## Configuration

### Application Configuration
```python
# config/base.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    DATABASE_URIS = {
        'primary': 'postgresql://...',
        'analytics': 'postgresql://...',
        'cache': 'sqlite:///cache_dev.db'
    }
```

### Zephyr Scale Configuration
```yaml
# config/atlassian_config.yaml
zephy_scale:
  domain: "https://accton-group.atlassian.net/"
  email: "peter_lin@edge-core.com"
  projectKey: ESTS
  access_token: "JWT_TOKEN"
```

### Theme Configuration
- CSS files in `static/css/`
- JavaScript theme switcher in `static/js/theme-switcher.js`
- Local storage for theme persistence

## Test Criteria

### Unit Tests
- [ ] Route handlers return correct status codes
- [ ] Template rendering with proper context
- [ ] API integration error handling
- [ ] Database query optimization

### Integration Tests
- [ ] Zephyr Scale API connectivity
- [ ] Database operations across all schemas
- [ ] File upload and processing
- [ ] Theme switching functionality

### User Acceptance Tests
- [ ] Navigation menu functionality
- [ ] Filter and search operations
- [ ] Data export features
- [ ] Responsive design on various devices
- [ ] Performance under load

## Source Code Structure

```
/
├── app.py                          # Main Flask application
├── routes_sqlalchemy.py            # Database routes
├── config/                         # Configuration modules
│   ├── base.py                     # Base configuration
│   ├── database.py                 # Database configuration
│   └── atlassian_config.yaml       # API configuration
├── templates/                      # Jinja2 templates
│   ├── base.html                   # Base template
│   ├── ests_test_cases.html        # Test cases page
│   ├── feature_list.html           # Feature matrix
│   ├── sai_*.html                  # SAI analysis pages
│   └── mcp.html                    # MCP interface
├── static/                         # Static assets
│   ├── css/                        # Theme stylesheets
│   ├── js/                         # JavaScript files
│   └── images/                     # Images and assets
├── models/                         # Database models
│   ├── base.py                     # Base model class
│   └── sonic_feature.py            # SONiC feature models
└── utils/                          # Utility modules
    └── zephyr_api.py               # Zephyr Scale API client
```

## Temporary Folders

### Working Directories
- `instance/` - Flask instance folder for runtime data
- `log_analysis/` - SAI analysis working directory
- `tmp/` - Temporary file processing (auto-created)

### Cache Locations
- `cache_dev.db` - SQLite cache database
- `requests.log` - HTTP request logging
- `*.log` - Various application logs

## Test Files Structure

```
tests/
├── test_app.py                     # Main application tests
├── test_routes.py                  # Route testing
├── test_models.py                  # Model testing
├── test_api_integration.py         # API integration tests
├── fixtures/                       # Test data
│   ├── sample_features.json        # Sample feature data
│   ├── test_cases.json             # Sample test cases
│   └── sai_recordings/             # Sample SAI files
└── conftest.py                     # Test configuration
```

### Test Data Requirements
- Sample Excel files for import testing
- Mock API responses for Zephyr Scale
- Sample SAI recording files
- Database fixtures for various scenarios

## API Endpoints

### Internal APIs
- `GET /api/features` - Feature data API
- `GET /api/test-cases` - Test case data API
- `POST /api/upload` - File upload endpoint
- `GET /api/status` - System status API

### External Integrations
- Zephyr Scale REST API v2
- PostgreSQL databases (primary, analytics)
- SQLite cache database

## Security Considerations

### Authentication
- JWT tokens for Zephyr Scale API
- Basic authentication for database connections
- API token management through configuration

### Data Protection
- Input sanitization for all user inputs
- SQL injection prevention through SQLAlchemy ORM
- XSS protection in templates
- Secure file upload validation

## Performance Optimization

### Database
- Connection pooling
- Query optimization with indexing
- Pagination for large datasets
- Caching frequently accessed data

### Frontend
- CSS/JS minification in production
- Image optimization
- Lazy loading for large tables
- Client-side filtering for better UX

## Deployment Configuration

### Development
```bash
python app.py
# Runs on http://localhost:5000
```

### Production
```bash
FLASK_ENV=production python app.py
# Or use Docker deployment
./docker/build_docker.sh --prod --deploy
```
# CLI Tools Specification

## Requirements

### Functional Requirements

1. **Feature Import Tools**
   - Import SONiC features from Excel files
   - Validate data integrity and format
   - Support batch processing
   - Handle EC proprietary vs community classification

2. **Test Case Management**
   - Import ESTS test cases from Excel files
   - Validate test case structure and metadata
   - Support label management and categorization
   - Generate import reports

3. **Data Analysis Tools**
   - Analyze Excel file structures
   - Generate schema documentation
   - Validate data consistency
   - Export analysis reports

4. **Confluence Integration**
   - Fetch Confluence pages via API
   - Extract tables from Confluence content
   - Convert to Excel format
   - Generate SONiC release notes

### Non-Functional Requirements

1. **Performance**
   - Handle large Excel files (10,000+ rows)
   - Efficient memory usage during processing
   - Progress reporting for long operations

2. **Reliability**
   - Comprehensive error handling
   - Data validation and rollback capabilities
   - Logging and audit trails

3. **Usability**
   - Clear command-line interface
   - Help documentation
   - Verbose and quiet modes
   - Configuration file support

## Feature Description

### Core CLI Tools

#### 1. Feature Importer (`feature_importer.py`)
```bash
python feature_importer.py [options]
```

**Purpose**: Import SONiC features from Excel files into database

**Options**:
- `--file FILE` - Specific Excel file to import
- `--dry-run` - Preview changes without committing
- `--validate` - Validation only mode
- `--force` - Force import with warnings
- `--sheet SHEET` - Specific sheet name
- `--verbose` - Detailed output

#### 2. Test Case Importer (`testcase_importer.py`)
```bash
python testcase_importer.py [options]
```

**Purpose**: Import ESTS test cases from Excel files

**Options**:
- `--file FILE` - Specific test case file
- `--dry-run` - Preview import without changes
- `--validate` - Validation mode only
- `--category CATEGORY` - Filter by category
- `--project PROJECT` - Target project

#### 3. Excel Inspector (`excel_inspector.py`)
```bash
python excel_inspector.py <file> [options]
```

**Purpose**: Analyze Excel file structure and content

**Options**:
- `--sheet SHEET` - Analyze specific sheet
- `--summary` - Show summary statistics
- `--schema` - Generate schema information
- `--output FORMAT` - Output format (json, yaml, txt)

#### 4. Confluence Tools
- `confluence_to_excel.py` - Convert Confluence tables to Excel
- `fetch_confluence_page.py` - Download Confluence pages
- `extract_sonic_release_notes.py` - Extract SONiC release information

#### 5. Test Case Inspector (`testcase_inspector.py`)
```bash
python testcase_inspector.py [options]
```

**Purpose**: Analyze and validate test case data

**Options**:
- `--stats` - Show statistics
- `--validate` - Validate test case format
- `--duplicates` - Find duplicate entries
- `--coverage` - Analyze feature coverage

## Configuration

### Environment Configuration
```bash
# Virtual environment activation
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Database Configuration
```python
# Uses same config as web application
from config.database import DatabaseConfig
```

### Atlassian Configuration
```yaml
# config/atlassian_config.yaml
jira:
  domain: "https://accton-group.atlassian.net/"
  email: "peter_lin@edge-core.com"
  api_token: "ATATT3x..."
```

### File Locations
- Input data: `data/` directory
- Excel files: `data/EC_SONiC_Feature.*.xlsx`
- Test cases: `data/ESTS_Test_Case.*.xlsx`
- Archive: `data/archive/` for old versions

## Test Criteria

### Unit Tests
- [ ] File parsing and validation
- [ ] Database operations (CRUD)
- [ ] Data transformation logic
- [ ] Error handling scenarios
- [ ] Configuration loading

### Integration Tests
- [ ] End-to-end import workflows
- [ ] Database schema compatibility
- [ ] Excel file format variations
- [ ] API integration (Confluence/Jira)
- [ ] Command-line argument parsing

### Data Quality Tests
- [ ] Excel file validation
- [ ] Data integrity checks
- [ ] Duplicate detection
- [ ] Referential integrity
- [ ] Character encoding handling

### Performance Tests
- [ ] Large file processing (>10MB)
- [ ] Memory usage under load
- [ ] Import speed benchmarks
- [ ] Concurrent operation handling

## Source Code Structure

```
/
├── feature_importer.py             # Main feature import tool
├── testcase_importer.py            # Test case import tool
├── excel_inspector.py              # Excel analysis tool
├── testcase_inspector.py           # Test case analysis
├── confluence_to_excel.py          # Confluence integration
├── fetch_confluence_page.py        # Page fetching utility
├── extract_sonic_release_notes.py  # Release notes extraction
├── db_manager.py                   # Database management
├── schema_reader.py                # Schema documentation
├── merge_excel_sheets.py           # Excel manipulation
├── merge_feature_tables.py         # Data merging utilities
├── find_feature_support_tables.py  # Table discovery
├── find_version_url.py             # Version URL extraction
└── read_ec_switches.py             # Switch information reader
```

### Utility Modules
```
models/
├── base.py                         # Base model definitions
└── sonic_feature.py                # SONiC feature models

config/
├── base.py                         # Configuration base
└── database.py                     # Database configuration
```

## Temporary Folders

### Working Directories
- `tmp/` - Temporary processing files (auto-created)
- `logs/` - CLI operation logs
- `backup/` - Database backup files (before imports)
- `reports/` - Generated analysis reports

### Cache Locations
- `.cache/` - Downloaded file cache
- `instance/` - Runtime data (shared with web app)

## Test Files Structure

```
tests/cli/
├── test_feature_importer.py        # Feature import tests
├── test_testcase_importer.py       # Test case import tests
├── test_excel_inspector.py         # Excel analysis tests
├── test_confluence_tools.py        # Confluence integration tests
├── fixtures/
│   ├── sample_features.xlsx        # Sample feature file
│   ├── sample_testcases.xlsx       # Sample test cases
│   ├── invalid_format.xlsx         # Invalid format test
│   └── empty_file.xlsx             # Edge case testing
├── mock_data/
│   ├── confluence_responses.json   # Mock API responses
│   └── database_fixtures.sql       # Test database data
└── conftest.py                     # Test configuration
```

## Command-Line Interface Design

### Standard Options
All CLI tools support these standard options:
```bash
--help, -h          Show help message
--verbose, -v       Verbose output
--quiet, -q         Quiet mode (errors only)
--config CONFIG     Configuration file path
--log-level LEVEL   Logging level (DEBUG, INFO, WARN, ERROR)
--dry-run          Preview mode without changes
```

### Exit Codes
- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Database error
- `5` - API error

### Progress Reporting
```python
# Progress bar for long operations
from tqdm import tqdm

for item in tqdm(items, desc="Processing"):
    process_item(item)
```

## Error Handling

### Error Categories
1. **File Errors**
   - File not found
   - Invalid format
   - Corruption detection
   - Permission issues

2. **Data Errors**
   - Validation failures
   - Constraint violations
   - Data type mismatches
   - Missing required fields

3. **System Errors**
   - Database connection failures
   - Network timeouts
   - Memory limitations
   - API rate limits

### Error Recovery
- Automatic retry for transient failures
- Rollback capabilities for partial imports
- Detailed error logging with context
- User-friendly error messages

## Integration Points

### Database Integration
- PostgreSQL primary database
- SQLite cache for performance
- Schema migration support
- Connection pooling

### Web Application Integration
- Shared configuration files
- Common database models
- Consistent data formats
- Logging integration

### External APIs
- Jira/Confluence REST APIs
- Zephyr Scale integration
- Excel file processing
- Authentication management

## Performance Optimization

### Memory Management
- Streaming Excel processing
- Chunked database operations
- Memory-efficient data structures
- Garbage collection optimization

### Processing Speed
- Parallel processing where applicable
- Database bulk operations
- Optimized SQL queries
- Caching frequently used data

### Scalability
- Configurable batch sizes
- Progress checkpointing
- Resume capability for interrupted operations
- Resource usage monitoring

## Deployment and Distribution

### Development Setup
```bash
# Clone repository
git clone <repository>
cd project

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tools
python feature_importer.py --help
```

### Production Deployment
- Docker container support
- Scheduled execution via cron
- Monitoring and alerting
- Log rotation and archival
# SONiC Feature Management System

A modern Flask web application for managing SONiC (Software for Open Networking in the Cloud) features and test cases. Features multi-database support, comprehensive schema documentation, Excel data import utilities, and a dynamic theme system with six distinct visual styles.

## Features

### 🎨 Theme System
- **Green Neon Theme**: Bright green cyberpunk style with glowing effects and animations
- **Pink Neon Theme**: Deep pink cyberpunk style with magenta neon glow effects
- **Tron Theme**: Blue futuristic grid-based design with scanning animations
- **Dark Theme**: Professional dark theme with purple accents
- **White Theme**: Clean light theme with blue accents
- **Pony Theme**: Magical pastel theme with rainbow effects, sparkles, and unicorn emojis

### 🗄️ Database Features
- **SONiC Feature Management**: Track SONiC community and Edgecore proprietary features
- **Test Case Management**: Comprehensive test case documentation and labeling
- **Multi-Database Support**: Primary, Analytics, Cache databases
- **PostgreSQL Integration**: Production-ready database with connection probing
- **Real-time Schema Documentation**: Interactive web-based schema viewer
- **Database Connection Monitoring**: Live connection status and health checks

### 🛠️ Technical Features
- **Flask Application Factory**: Modular application structure
- **Environment-based Configuration**: Development/Production/Testing environments
- **Excel Data Import**: Automated import from EC SONiC Feature Excel files
- **Interactive Schema Viewer**: Web-based database documentation with search and export
- **Real-time Connection Probing**: Database health monitoring on startup
- **Comprehensive Request Logging**: Console + file logging with detailed metrics
- **Responsive Design**: Mobile-friendly across all themes
- **Client-side Theme Switching**: Persistent theme preferences

### 📊 Data Management Features
- **Excel Import Utility**: Import EC SONiC features from Excel files with validation
- **Support Status Mapping**: Automatic conversion of O/X/D codes to readable text
- **Label Processing**: Comma-separated label splitting and normalization
- **Data Validation**: Schema validation and error reporting
- **Batch Processing**: Efficient bulk data operations with transaction safety

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git
- PostgreSQL 12+ (for production) or SQLite (for development)
- Excel files with SONiC feature data (optional)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd jira
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configurations
# You can use any text editor, for example:
nano .env
```

### Step 5: Configure Environment Variables
Edit the `.env` file and customize the following variables:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Primary Database URLs (SONiC Features & Test Cases)
PRIMARY_DEV_DB_URL=postgresql://postgres:password@localhost:5432/ESTS_Dev
PRIMARY_PROD_DB_URL=postgresql://postgres:password@10.102.6.16:15432/ESTS_Dev
PRIMARY_TEST_DB_URL=sqlite:///primary_test.db

# Analytics Database URLs
ANALYTICS_DEV_DB_URL=postgresql://postgres:password@localhost:5432/ESTS_Dev
ANALYTICS_PROD_DB_URL=postgresql://postgres:password@10.102.6.16:15432/ESTS_Dev
ANALYTICS_TEST_DB_URL=sqlite:///analytics_test.db

# Cache Database URLs
CACHE_DEV_DB_URL=sqlite:///cache_dev.db
CACHE_PROD_DB_URL=redis://localhost:6379/0
CACHE_TEST_DB_URL=sqlite:///cache_test.db
```

## Running the Application

### Development Mode
```bash
# Make sure virtual environment is activated
python app.py
```

The application will start on `http://localhost:5002` (or `http://172.30.116.234:5002` from Windows if running in WSL)

You'll see database connection probing on startup:
```
============================================================
DATABASE CONNECTION PROBE
============================================================
✓ PRIMARY: CONNECTED
  URL: postgresql://postgres:password@10.102.6.16:15432/ESTS_Dev
  Type: postgresql
  Message: Connected successfully. PostgreSQL version: 17.4
============================================================
```

### Alternative: Using Flask CLI
```bash
# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the application
flask run
```

### Production Mode
```bash
# Set production environment
export FLASK_ENV=production

# Run with a production WSGI server (install gunicorn first)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## Project Structure

```
jira/
├── app.py                    # Main application file
├── feature_importer.py       # Excel data import utility
├── schema_reader.py          # Database schema documentation generator
├── excel_inspector.py        # Excel file structure analyzer
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── FEATURE_IMPORT_GUIDE.md  # Data import documentation
├── README.md                # This file
├── config/                  # Configuration files
│   ├── __init__.py
│   ├── base.py             # Base configuration classes
│   └── database.py         # Database configuration and connection probing
├── data/                    # Excel data files
│   ├── EC_SONiC_Feature.YYYYMMDD.xlsx  # SONiC feature data
│   └── ESTS_Test_Case.xlsx             # Test case data
├── static/                  # Static assets
│   ├── css/                # Theme stylesheets
│   │   ├── base.css        # Base styles with database styling
│   │   ├── schema.css      # Schema viewer styles
│   │   ├── neon.css        # Green neon theme
│   │   ├── pink-neon.css   # Pink neon theme
│   │   ├── tron.css        # Tron theme
│   │   ├── dark.css        # Dark theme
│   │   ├── white.css       # White theme
│   │   └── pony.css        # Pony theme
│   └── js/
│       ├── theme-switcher.js  # Theme switching logic
│       └── schema-viewer.js   # Interactive schema viewer
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Home page
│   ├── about.html          # About page
│   ├── db_info.html        # Database info and schema links
│   └── schema.html         # Interactive schema viewer
├── schema_*.md             # Generated database schema documentation
│   ├── schema_primary.md   # Primary database schema
│   ├── schema_analytics.md # Analytics database schema
│   └── schema_cache.md     # Cache database schema
└── requests.log            # Application request logs
```

## Using the Theme System

### Theme Switching
- **UI Method**: Use the theme buttons in the header
- **Keyboard Shortcuts**: 
  - `Ctrl+Shift+1`: Green Neon theme
  - `Ctrl+Shift+2`: Pink Neon theme
  - `Ctrl+Shift+3`: Tron theme
  - `Ctrl+Shift+4`: Dark theme
  - `Ctrl+Shift+5`: White theme
  - `Ctrl+Shift+6`: Pony theme

### Theme Persistence
- Themes are automatically saved to browser localStorage
- Your theme preference will persist across sessions
- System theme detection for initial load (if no preference saved)

## Configuration

### Database Configuration
The application supports multiple database configurations:

1. **Primary Database**: Main application data
2. **Analytics Database**: Analytics and reporting data
3. **Cache Database**: Caching and temporary data

### Environment-Specific Settings
- **Development**: Uses SQLite databases by default
- **Production**: Configured for PostgreSQL/Redis
- **Testing**: Separate test databases

### Adding New Themes
1. Create a new CSS file in `static/css/`
2. Define CSS custom properties for colors
3. Add theme button to `templates/base.html`
4. Update `theme-switcher.js` if needed

## Available Routes

- `/` - Home page with theme showcase
- `/about` - About page with project information
- `/db-info` - Database configuration details with schema links
- `/schema` - Interactive database schema viewer (all databases)
- `/schema/<db_name>` - Individual database schema viewer
- `/sonic-switch` - AI fabric interface
- `/readme` - Interactive documentation viewer

## SONiC Feature Data Management

### Excel Data Import

Import SONiC feature data from Excel files using the automated import utility:

```bash
# Activate virtual environment
source venv/bin/activate

# Import latest feature file
python feature_importer.py

# Import specific date file
python feature_importer.py --date 20250626

# Preview import without making changes
python feature_importer.py --dry-run

# Import without clearing existing data
python feature_importer.py --no-clear
```

### Excel File Format

Place Excel files in the `data/` directory with the naming pattern:
- `EC_SONiC_Feature.YYYYMMDD.xlsx` - SONiC feature data
- `ESTS_Test_Case.xlsx` - Test case data

### Support Status Mapping

The import utility automatically converts Excel codes to readable text:
- **O** → `Support`
- **X** → `Not Support`
- **D** → `Under Development`

### Data Processing Features

- **Automatic Label Splitting**: Comma-separated labels are split into individual records
- **Feature Key Generation**: Missing feature keys are auto-generated from category + feature name
- **Data Validation**: Schema validation with detailed error reporting
- **Transaction Safety**: All-or-nothing import with rollback on errors
- **Duplicate Handling**: Configurable insert/update behavior

## Database Schema Documentation

### Interactive Schema Viewer

Access comprehensive database documentation through the web interface:

1. **Visit `/db-info`** - View database connection status and schema links
2. **Click "View Schema"** - Open interactive schema viewer
3. **Switch between databases** - Use tabs to navigate between Primary/Analytics/Cache
4. **Multiple view modes**: Rendered markdown, source code, or split view
5. **Export schemas** - Download documentation as markdown files

### Schema Generation

Generate fresh schema documentation:

```bash
# Generate all database schemas
python schema_reader.py

# This creates:
# - schema_primary.md    - Primary database (SONiC features & test cases)
# - schema_analytics.md  - Analytics database  
# - schema_cache.md      - Cache database
```

### Schema Content

The generated documentation includes:
- **Table structures** with column details and descriptions
- **Primary keys and foreign keys** with relationship mapping
- **Indexes** with uniqueness and column information
- **Data types** with precision and constraints
- **Business context** explaining the purpose of each field
- **SONiC domain knowledge** integrated into field descriptions

## Database Schema Overview

### Primary Database Tables

1. **s_feature_map** - Core SONiC feature tracking
   - Tracks community and Edgecore proprietary features
   - Support status across different SONiC branches (2111, 2211, 2311)
   - Virtual Switch and fabric implementation status
   - JIRA component associations

2. **s_feature_label** - Feature categorization
   - Many-to-many relationship with features
   - Flexible labeling system for feature classification
   - Supports comma-separated label import from Excel

3. **s_test_case** - Test case management
   - Comprehensive test case documentation
   - Topology, validation, and traffic pattern specifications
   - Project and customer associations
   - Pytest marker integration

4. **s_test_case_label** - Test case categorization
   - Links test cases to classification labels
   - Enables flexible test case organization and filtering

## Request Logging

The application includes comprehensive request logging functionality:

### Features
- **Console Logging**: Real-time request information displayed in terminal
- **File Logging**: All requests logged to `requests.log` file
- **Request Details**: Timestamp, HTTP method, URL path, client IP address

### Log Format
```
[2025-06-24 16:20:01] GET /sonic-switch - 172.30.112.1
[2025-06-24 16:20:01] GET /static/css/dark.css - 172.30.112.1
```

### Log File Location
- File: `requests.log` (in project root)
- Auto-created on first request
- Appends new requests (not overwritten)
- Excluded from git via `.gitignore`

## Development

### Adding New Routes
Add routes in the `create_app()` function in `app.py`:

```python
@app.route('/new-route')
def new_route():
    return render_template('new_template.html')
```

### Database Models
Add new models in the `models/` directory and import them in `models/__init__.py`.

### Custom Themes
Create new theme files following the pattern in existing theme CSS files, using CSS custom properties for easy customization.

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Database Connection Issues**
   - Check your `.env` file configuration
   - Ensure database URLs are correct
   - For PostgreSQL, make sure the server is running
   - Check the connection probe output on startup

3. **Excel Import Issues**
   ```bash
   # Check Excel file format and location
   python excel_inspector.py
   
   # Test import without making changes
   python feature_importer.py --dry-run
   
   # Check for missing dependencies
   pip install pandas openpyxl psycopg2-binary
   ```

4. **Schema Documentation Issues**
   ```bash
   # Regenerate schema files
   python schema_reader.py
   
   # Check database connection first
   python -c "from config.database import DatabaseConfig; print(DatabaseConfig.probe_database_connections())"
   ```

5. **Theme Not Loading**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify static files are being served correctly

6. **Port Already in Use**
   ```bash
   # Use a different port
   python app.py --port 5001
   # Or kill the process using the port
   lsof -ti:5002 | xargs kill -9  # macOS/Linux
   ```

### Development Tips

- Use browser developer tools to inspect theme CSS
- Check Flask debug output for configuration issues
- Use `flask shell` for interactive database testing
- Monitor `flask.log` for application logs

## Dependencies

### Core Web Framework
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities
- **python-dotenv**: Environment variable management

### Database & ORM
- **psycopg2-binary**: PostgreSQL database adapter
- **SQLAlchemy**: Database ORM and schema introspection

### Data Processing
- **pandas**: Excel file reading and data manipulation
- **openpyxl**: Excel file format support
- **numpy**: Numerical computing support (pandas dependency)

### Development & Utilities
- **marked.js**: Client-side markdown rendering (CDN)
- **python-dateutil**: Date/time parsing utilities

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

For more information or support, please check the project documentation or open an issue.
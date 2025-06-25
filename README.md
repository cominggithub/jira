# Flask Web Project with Multi-Theme System

A modern Flask web application featuring SQLAlchemy integration, multi-database support, comprehensive request logging, and a dynamic theme system with six distinct visual styles.

## Features

### 🎨 Theme System
- **Green Neon Theme**: Bright green cyberpunk style with glowing effects and animations
- **Pink Neon Theme**: Deep pink cyberpunk style with magenta neon glow effects
- **Tron Theme**: Blue futuristic grid-based design with scanning animations
- **Dark Theme**: Professional dark theme with purple accents
- **White Theme**: Clean light theme with blue accents
- **Pony Theme**: Magical pastel theme with rainbow effects, sparkles, and unicorn emojis

### 🗄️ Database Features
- SQLAlchemy ORM integration
- Multi-database support (Primary, Analytics, Cache)
- Environment-specific database configurations
- Support for SQLite (development) and PostgreSQL (production)

### 🛠️ Technical Features
- Flask application factory pattern
- Environment-based configuration system
- Comprehensive request logging (console + file)
- Responsive design across all themes
- Client-side theme switching with persistence
- Keyboard shortcuts for theme switching
- System theme detection
- Real-time request monitoring

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git

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

# Primary Database URLs
PRIMARY_DEV_DB_URL=sqlite:///primary_dev.db
PRIMARY_PROD_DB_URL=postgresql://user:password@localhost/primary_prod
PRIMARY_TEST_DB_URL=sqlite:///primary_test.db

# Analytics Database URLs
ANALYTICS_DEV_DB_URL=sqlite:///analytics_dev.db
ANALYTICS_PROD_DB_URL=postgresql://user:password@localhost/analytics_prod
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
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── config/              # Configuration files
│   ├── __init__.py
│   ├── base.py         # Base configuration classes
│   └── database.py     # Database configuration
├── models/              # SQLAlchemy models
│   └── __init__.py     # User model example
├── static/              # Static assets
│   ├── css/            # Theme stylesheets
│   │   ├── base.css    # Base styles
│   │   ├── neon.css    # Green neon theme
│   │   ├── pink-neon.css # Pink neon theme
│   │   ├── tron.css    # Tron theme
│   │   ├── dark.css    # Dark theme
│   │   ├── white.css   # White theme
│   │   └── pony.css    # Pony theme
│   └── js/
│       └── theme-switcher.js  # Theme switching logic
└── templates/           # HTML templates
    ├── base.html       # Base template
    ├── index.html      # Home page
    ├── about.html      # About page
    └── db_info.html    # Database info page
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
- `/db-info` - Database configuration details
- `/sonic-switch` - AI fabric interface

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

3. **Theme Not Loading**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify static files are being served correctly

4. **Port Already in Use**
   ```bash
   # Use a different port
   python app.py --port 5001
   # Or kill the process using the port
   lsof -ti:5000 | xargs kill -9  # macOS/Linux
   ```

### Development Tips

- Use browser developer tools to inspect theme CSS
- Check Flask debug output for configuration issues
- Use `flask shell` for interactive database testing
- Monitor `flask.log` for application logs

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM integration
- **SQLAlchemy**: Database ORM  
- **python-dotenv**: Environment variable management
- **Werkzeug**: WSGI utilities

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
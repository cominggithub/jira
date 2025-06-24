# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development
```bash
# Activate virtual environment (required for all operations)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
# Alternative: FLASK_APP=app.py flask run

# Run in production mode
FLASK_ENV=production python app.py
```

### Environment Setup
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your database URLs and secret key
```

### Database Operations
```bash
# Check database configuration
python -c "from config.database import DatabaseConfig; print(DatabaseConfig.get_database_configs())"

# Access Flask shell for database operations
FLASK_APP=app.py flask shell
```

## Architecture Overview

### Application Factory Pattern
The application uses Flask's application factory pattern in `app.py`. The `create_app()` function:
- Determines environment from `FLASK_ENV` environment variable
- Loads configuration from `config/base.py` based on environment
- Initializes SQLAlchemy with the app
- Defines all routes inline (not using blueprints)

### Multi-Database Configuration System
The project supports three databases configured via `config/database.py`:
- **Primary**: Main application data
- **Analytics**: Reporting and analytics data  
- **Cache**: Session and temporary data

Database URLs are environment-specific and configured through environment variables:
- Development: SQLite files (default)
- Production: PostgreSQL/Redis (configured via env vars)
- Testing: Separate SQLite test databases

Configuration classes in `config/base.py`:
- `Config` (base class)
- `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`
- Loaded via `config` dictionary mapping environment names to classes

### Theme System Architecture
The project features a comprehensive 4-theme system:

**CSS Architecture**: 
- `static/css/base.css`: Base styles with CSS custom properties
- `static/css/{theme}.css`: Theme-specific variable overrides (neon, tron, dark, white)

**JavaScript Architecture**:
- `static/js/theme-switcher.js`: Client-side theme switching with localStorage persistence
- Themes switched by updating CSS custom properties dynamically
- Supports keyboard shortcuts (Ctrl+Shift+1-4) and system theme detection

**Template Integration**:
- `templates/base.html`: Base template with theme switching UI in header
- Theme CSS loaded dynamically via `id="theme-stylesheet"`
- All pages extend base template with consistent theme support

### Route Structure
All routes defined in `app.py` within `create_app()`:
- `/` → `index.html` (home/project overview)
- `/sonic-switch` → `sonic_switch.html` (AI fabric interface)
- `/about` → `about.html` (project information)
- `/db-info` → `db_info.html` (database configuration display)

### Static Asset Organization
```
static/
├── css/
│   ├── base.css           # Base styles + CSS variables
│   ├── {theme}.css        # Theme overrides (neon, tron, dark, white)
│   └── sonic-switch.css   # Page-specific styles
└── js/
    ├── theme-switcher.js  # Global theme management
    └── sonic-switch.js    # Page-specific interactions
```

### Template Inheritance
- `base.html`: Master template with navigation, theme switcher, footer
- Page templates extend base and define content blocks
- Theme CSS dynamically loaded based on user preference
- JavaScript modules loaded per-page via blocks

## Key Integration Points

### Adding New Routes
Routes are defined inline within `create_app()` in `app.py`. New routes should:
- Follow the existing pattern of rendering templates with `config=app.config`
- Use `DatabaseConfig.get_database_url()` for database connections if needed
- Pass environment context for display (see existing routes)

### Database Configuration
- Environment variables control database URLs (see `.env.example`)
- `DatabaseConfig` class provides methods to get URLs by database name and environment
- Multiple databases accessed via the same SQLAlchemy `db` instance

### Theme Development
- New themes require CSS file in `static/css/` with CSS custom property overrides
- Add theme button to `templates/base.html` navigation
- Update `theme-switcher.js` if special handling needed
- Themes must define all CSS custom properties from `base.css`

### Environment Management
The application behavior changes significantly based on `FLASK_ENV`:
- **development**: Debug mode, SQLite databases, detailed error pages
- **production**: No debug, PostgreSQL/Redis, security headers
- **testing**: Testing mode, separate test databases

Always verify environment-specific configuration when making changes that affect database connections or application behavior.
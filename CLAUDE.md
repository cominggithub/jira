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

### Deployment Commands
```bash
# Docker deployment to VM
./docker/build_docker.sh --prod --deploy

# Standalone deployment to VM
chmod +x deploy_standalone.sh
./deploy_standalone.sh

# Simple deployment alternative
chmod +x deploy_simple.sh
./deploy_simple.sh
```

## Architecture Overview

### Application Factory Pattern
The application uses Flask's application factory pattern in `app.py`. The `create_app()` function:
- Determines environment from `FLASK_ENV` environment variable
- Loads configuration from `config/base.py` based on environment
- Initializes SQLAlchemy with the app
- Defines all routes inline (not using blueprints)
- Includes comprehensive request logging middleware

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

### Advanced Theme System Architecture
The project features a comprehensive 6-theme system with advanced animations:

**CSS Architecture**: 
- `static/css/base.css`: Base styles with CSS custom properties
- `static/css/{theme}.css`: Theme-specific variable overrides
- Available themes: neon, pink-neon, tron, dark, white, pony

**Theme Details**:
1. **Green Neon** (`neon.css`): Cyberpunk green with glowing effects
2. **Pink Neon** (`pink-neon.css`): Cyberpunk pink with magenta glow
3. **Tron** (`tron.css`): Blue futuristic grid with scanning animations
4. **Dark** (`dark.css`): Professional dark with purple accents
5. **White** (`white.css`): Clean light theme with blue accents
6. **Pony** (`pony.css`): Magical pastel theme with rainbow effects, sparkles, and unicorn emojis

**JavaScript Architecture**:
- `static/js/theme-switcher.js`: Client-side theme switching with localStorage persistence
- Themes switched by updating CSS custom properties dynamically
- Supports keyboard shortcuts (Ctrl+Shift+1-6) and system theme detection
- Theme events and programmatic switching API

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
- `/readme` → `readme.html` (interactive documentation viewer)

### Sonic Switch AI Fabric Interface
Advanced interactive dashboard with sophisticated animations:
- **Animated Logo System**: Rotating rings with physics-based animations
- **Feature Cards**: Neural Processing, Sonic Interface, AI Fabric, Quantum Switch
- **Control Panel**: Mode switching, status indicators, action buttons
- **Modal System**: Detailed feature information popups
- **Real-time Animations**: Network nodes, sonic waves, particle systems
- **Theme Integration**: Animations adapt to current theme colors

### Documentation Viewer System
Interactive README viewer accessible via `/readme`:
- **Multi-Document Support**: README.md, FEATURES.md, DEPLOY.md
- **View Modes**: Rendered, Source, Split view
- **Tab Navigation**: Easy switching between documents
- **Real-time Rendering**: Client-side markdown processing using Marked.js
- **Keyboard Shortcuts**: Fast document navigation
- **Word Count Statistics**: Document metrics

### Request Logging System
Comprehensive request tracking functionality:
- **Dual Output**: Console logging + file logging to `requests.log`
- **Detailed Information**: Timestamp, method, URL, IP address, user agent
- **Performance Optimized**: Minimal impact on request processing
- **Error Handling**: Graceful failure handling for logging operations

### Static Asset Organization
```
static/
├── css/
│   ├── base.css           # Base styles + CSS variables
│   ├── neon.css           # Green neon cyberpunk theme
│   ├── pink-neon.css      # Pink neon cyberpunk theme
│   ├── tron.css           # Blue futuristic grid theme
│   ├── dark.css           # Professional dark theme
│   ├── white.css          # Clean light theme
│   ├── pony.css           # Magical pastel theme with animations
│   ├── sonic-switch.css   # Sonic Switch page styles
│   └── readme.css         # Documentation viewer styles
├── js/
│   ├── theme-switcher.js  # Global theme management
│   ├── sonic-switch.js    # Sonic Switch interactions
│   └── readme-viewer.js   # Documentation viewer functionality
└── images/
    ├── bg1.png           # Background image assets
    └── bg2.jpg           # Additional background assets
```

### Template Inheritance
- `base.html`: Master template with navigation, theme switcher, footer
- Page templates extend base and define content blocks
- Theme CSS dynamically loaded based on user preference
- JavaScript modules loaded per-page via blocks
- Responsive design across all templates

### Deployment Infrastructure
The project includes comprehensive deployment options:

**Docker Deployment**:
- `docker/Dockerfile`: Multi-stage production-ready container
- `docker/docker-compose.yml`: Container orchestration with PostgreSQL/Redis
- `docker/build_docker.sh`: Automated build, test, and deploy script
- Health checks, logging, and security best practices

**VM Deployment Scripts**:
- `deploy_standalone.sh`: Comprehensive deployment with systemd service
- `deploy_simple.sh`: Simple deployment alternative
- SSH-based automated deployment to remote VMs
- Process management and monitoring capabilities

## Key Integration Points

### Adding New Routes
Routes are defined inline within `create_app()` in `app.py`. New routes should:
- Follow the existing pattern of rendering templates with `config=app.config`
- Use `DatabaseConfig.get_database_url()` for database connections if needed
- Pass environment context for display (see existing routes)
- Include request logging if needed

### Database Configuration
- Environment variables control database URLs (see `.env.example`)
- `DatabaseConfig` class provides methods to get URLs by database name and environment
- Multiple databases accessed via the same SQLAlchemy `db` instance
- Support for SQLite (development) and PostgreSQL/Redis (production)

### Theme Development
To add a new theme:
1. Create CSS file in `static/css/` with CSS custom property overrides
2. Define all CSS custom properties from `base.css`
3. Add theme button to `templates/base.html` navigation
4. Update `theme-switcher.js` keyboard shortcuts if needed
5. Test across all pages and components
6. Update documentation in README.md and FEATURES.md

### Adding Interactive Components
For new interactive features like Sonic Switch:
1. Create page-specific CSS file in `static/css/`
2. Create page-specific JavaScript in `static/js/`
3. Use CSS custom properties for theme integration
4. Follow existing animation and interaction patterns
5. Ensure mobile responsiveness and accessibility

### Environment Management
The application behavior changes significantly based on `FLASK_ENV`:
- **development**: Debug mode, SQLite databases, detailed error pages
- **production**: No debug, PostgreSQL/Redis, security headers
- **testing**: Testing mode, separate test databases

Always verify environment-specific configuration when making changes that affect database connections or application behavior.

### Request Logging Integration
The request logging system is automatically enabled. For custom logging:
- Use the existing `@app.after_request` decorator pattern
- Log to both console and file for consistency
- Include timestamp, method, path, and IP address
- Handle exceptions gracefully to avoid breaking request flow

### Deployment Best Practices
When deploying:
1. Use `deploy_standalone.sh` for VMs without Docker
2. Use Docker deployment for containerized environments
3. Ensure environment variables are properly configured
4. Test database connections before deployment
5. Monitor logs for successful startup
6. Verify theme assets load correctly
7. Test interactive components functionality

## Important Notes

### Security Considerations
- Secrets should never be committed to the repository
- Use environment variables for sensitive configuration
- SQLAlchemy ORM provides SQL injection protection
- Jinja2 templates auto-escape for XSS protection
- HTTPS should be used in production

### Performance Optimization
- CSS animations use hardware acceleration
- JavaScript uses efficient DOM manipulation
- Themes leverage CSS custom properties for fast switching
- Static assets are optimized for caching
- Database queries use SQLAlchemy ORM optimizations

### Browser Compatibility
- Modern ES6+ JavaScript (Chrome 60+, Firefox 55+, Safari 10.1+)
- CSS Grid and Flexbox (IE 11+ with fallbacks)
- CSS custom properties (IE 15+, all modern browsers)
- Hardware-accelerated animations (all modern browsers)

### Mobile Responsiveness
- All themes are mobile-responsive
- Touch-friendly interactive elements
- Optimized animations for mobile devices
- Accessible navigation on small screens
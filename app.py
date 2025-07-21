import os
import logging
from datetime import datetime
from flask import Flask, render_template, request
from flask_migrate import Migrate
from dotenv import load_dotenv
from config.base import config
from config.database import DatabaseConfig
from models.base import db
from models import FeatureMap, FeatureLabel
from routes_sqlalchemy import feature_list_sqlalchemy

# Load environment variables from .env file
load_dotenv()

def log_request_info():
    """Log connection request info to console and file"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        remote_addr = request.environ.get('REMOTE_ADDR', 'Unknown')
        user_agent = request.headers.get('User-Agent', 'Unknown')
        method = request.method
        url = request.url
        
        # Create log message
        log_message = f"[{timestamp}] {method} {url} - IP: {remote_addr} - Agent: {user_agent}"
        
        # Print to console
        print(f"REQUEST INFO: {log_message}")
        
        # Write to log file
        log_file = 'requests.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{log_message}\n")
    except Exception as e:
        print(f"Error in request logging: {e}")

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_obj = config[config_name]()
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    
    # Initialize SQLAlchemy and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Add custom template filters
    @app.template_filter('timestamp_to_date')
    def timestamp_to_date(timestamp):
        from datetime import datetime
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)
    
    # Database connection probe
    print("=" * 60)
    print("DATABASE CONNECTION PROBE")
    print("=" * 60)
    
    db_results = DatabaseConfig.probe_database_connections()
    for db_name, result in db_results.items():
        status_symbol = "✓" if result['status'] == 'connected' else "✗" if result['status'] == 'failed' else "○"
        print(f"{status_symbol} {db_name.upper()}: {result['status'].upper()}")
        print(f"  URL: {result['url']}")
        print(f"  Type: {result['type']}")
        print(f"  Message: {result['message']}")
        print()
    
    print("=" * 60)
    
    
    # Request logging - outputs to console and file
    @app.after_request
    def log_requests(response):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {request.method} {request.path} - {request.remote_addr}"
        print(f"REQUEST: {log_msg}")
        with open('requests.log', 'a') as f:
            f.write(f"{log_msg}\n")
        return response
    
    @app.route('/')
    def hello():
        env = os.environ.get('FLASK_ENV', 'development')
        return render_template('index.html', env=env, config=app.config)

    @app.route('/about')
    def about():
        return render_template('about.html', config=app.config)
    
    @app.route('/db-info')
    def db_info():
        env = os.environ.get('FLASK_ENV', 'development')
        db_results = DatabaseConfig.probe_database_connections()
        return render_template('db_info.html', env=env, config=app.config, db_results=db_results)
    
    @app.route('/sonic-switch')
    def sonic_switch():
        return render_template('sonic_switch.html', config=app.config)
    
    @app.route('/sonic-feature')
    def sonic_feature():
        return render_template('sonic_feature.html', config=app.config)
    
    @app.route('/feature-list')
    def feature_list():
        return feature_list_sqlalchemy(app.config)
    
    @app.route('/sonic-mgmt')
    def sonic_mgmt():
        return render_template('sonic_mgmt.html', config=app.config)
    
    @app.route('/ests')
    def ests():
        return render_template('ests.html', config=app.config)
    
    @app.route('/mcp')
    def mcp():
        import json
        import subprocess
        import os
        from pathlib import Path
        
        # Read MCP configuration
        mcp_config = {}
        try:
            with open('mcp_config.json', 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
        except FileNotFoundError:
            mcp_config = {"mcpServers": {}}
        except Exception as e:
            mcp_config = {"error": f"Error reading config: {str(e)}"}
        
        # Check MCP server status
        server_status = {}
        for server_name, server_config in mcp_config.get('mcpServers', {}).items():
            try:
                # Check if server file exists
                script_path = Path(server_config.get('args', [''])[0])
                if script_path.exists():
                    server_status[server_name] = {
                        'file_exists': True,
                        'file_path': str(script_path.absolute()),
                        'file_size': script_path.stat().st_size,
                        'last_modified': script_path.stat().st_mtime
                    }
                else:
                    server_status[server_name] = {
                        'file_exists': False,
                        'file_path': str(script_path.absolute()),
                        'error': 'Server file not found'
                    }
            except Exception as e:
                server_status[server_name] = {
                    'error': f'Error checking server: {str(e)}'
                }
        
        # Read MCP demo readme
        mcp_readme = ""
        try:
            with open('MCP_DEMO_README.md', 'r', encoding='utf-8') as f:
                mcp_readme = f.read()
        except FileNotFoundError:
            mcp_readme = "# MCP Demo README not found"
        except Exception as e:
            mcp_readme = f"# Error reading MCP readme: {str(e)}"
        
        return render_template('mcp.html', 
                             mcp_config=mcp_config, 
                             server_status=server_status,
                             mcp_readme=mcp_readme,
                             config=app.config)
    
    @app.route('/readme')
    def readme():
        import os
        
        # Read markdown files
        docs = {}
        doc_files = {
            'README': 'README.md',
            'FEATURES': 'FEATURES.md', 
            'DEPLOY': 'DEPLOY.md'
        }
        
        for key, filename in doc_files.items():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    docs[key] = f.read()
            except FileNotFoundError:
                docs[key] = f"# {filename} not found\n\nThe {filename} file could not be located."
            except Exception as e:
                docs[key] = f"# Error reading {filename}\n\nError: {str(e)}"
        
        return render_template('readme.html', docs=docs, config=app.config)
    
    @app.route('/schema')
    @app.route('/schema/<db_name>')
    def schema_viewer(db_name=None):
        import os
        import glob
        
        # Get all schema files
        schema_files = glob.glob('schema_*.md')
        schemas = {}
        
        for file_path in schema_files:
            base_name = os.path.basename(file_path)
            # Extract db name from filename (schema_primary.md -> primary)
            db = base_name.replace('schema_', '').replace('.md', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    schemas[db] = f.read()
            except Exception as e:
                schemas[db] = f"# Error reading {file_path}\n\nError: {str(e)}"
        
        # If specific database requested, show only that one
        if db_name:
            if db_name in schemas:
                filtered_schemas = {db_name: schemas[db_name]}
                return render_template('schema.html', schemas=filtered_schemas, selected_db=db_name, config=app.config)
            else:
                # Database not found, show 404-like message
                error_content = f"# Database Schema Not Found\n\nThe schema for '{db_name}' database could not be found.\n\nAvailable schemas: {', '.join(schemas.keys())}"
                filtered_schemas = {db_name: error_content}
                return render_template('schema.html', schemas=filtered_schemas, selected_db=db_name, config=app.config)
        
        # Show all schemas
        return render_template('schema.html', schemas=schemas, selected_db=None, config=app.config)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_RUN_PORT', 5003))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
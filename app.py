import os
import logging
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config.base import config
from config.database import DatabaseConfig

db = SQLAlchemy()

def log_request_info():
    """Log connection request info to console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    remote_addr = request.environ.get('REMOTE_ADDR', 'Unknown')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    method = request.method
    url = request.url
    endpoint = request.endpoint or 'Unknown'
    
    # Create log message
    log_message = f"[{timestamp}] {method} {url} - IP: {remote_addr} - Agent: {user_agent} - Endpoint: {endpoint}"
    
    # Print to console
    print(f"REQUEST INFO: {log_message}")
    
    # Write to log file
    log_file = 'requests.log'
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{log_message}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    
    # Add request logging middleware
    @app.before_request
    def before_request():
        log_request_info()
    
    @app.route('/')
    def hello():
        env = os.environ.get('FLASK_ENV', 'development')
        db_url = DatabaseConfig.get_database_url('primary', env)
        return render_template('index.html', env=env, db_url=db_url, config=app.config)

    @app.route('/about')
    def about():
        return render_template('about.html', config=app.config)
    
    @app.route('/db-info')
    def db_info():
        env = os.environ.get('FLASK_ENV', 'development')
        configs = DatabaseConfig.get_database_configs()
        db_configs = {db_name: db_configs[env] for db_name, db_configs in configs.items()}
        return render_template('db_info.html', env=env, db_configs=db_configs, config=app.config)
    
    @app.route('/sonic-switch')
    def sonic_switch():
        return render_template('sonic_switch.html', config=app.config)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
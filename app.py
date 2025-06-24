import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config.base import config
from config.database import DatabaseConfig

db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    
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
import os
from config.database import DatabaseConfig

class Config:
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    
    def __init__(self):
        super().__init__()
        db_config = DatabaseConfig()
        self.SQLALCHEMY_DATABASE_URI = db_config.get_database_url('primary', 'development')

class ProductionConfig(Config):
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        db_config = DatabaseConfig()
        self.SQLALCHEMY_DATABASE_URI = db_config.get_database_url('primary', 'production')

class TestingConfig(Config):
    TESTING = True
    
    def __init__(self):
        super().__init__()
        db_config = DatabaseConfig()
        self.SQLALCHEMY_DATABASE_URI = db_config.get_database_url('primary', 'testing')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
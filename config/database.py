import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    @staticmethod
    def get_database_configs():
        return {
            'primary': {
                'development': os.environ.get('PRIMARY_DEV_DB_URL', 'sqlite:///primary_dev.db'),
                'production': os.environ.get('PRIMARY_PROD_DB_URL', 'sqlite:///primary_prod.db'),
                'testing': os.environ.get('PRIMARY_TEST_DB_URL', 'sqlite:///primary_test.db')
            },
            'analytics': {
                'development': os.environ.get('ANALYTICS_DEV_DB_URL', 'sqlite:///analytics_dev.db'),
                'production': os.environ.get('ANALYTICS_PROD_DB_URL', 'sqlite:///analytics_prod.db'),
                'testing': os.environ.get('ANALYTICS_TEST_DB_URL', 'sqlite:///analytics_test.db')
            },
            'cache': {
                'development': os.environ.get('CACHE_DEV_DB_URL', 'sqlite:///cache_dev.db'),
                'production': os.environ.get('CACHE_PROD_DB_URL', 'sqlite:///cache_prod.db'),
                'testing': os.environ.get('CACHE_TEST_DB_URL', 'sqlite:///cache_test.db')
            }
        }
    
    @staticmethod
    def get_database_url(db_name='primary', environment='development'):
        configs = DatabaseConfig.get_database_configs()
        return configs.get(db_name, {}).get(environment, 'sqlite:///default.db')
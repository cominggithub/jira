import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration and connection management"""
    
    @staticmethod
    def get_database_configs():
        """Get all database configurations for current environment"""
        env = os.environ.get('FLASK_ENV', 'development')
        
        configs = {
            'primary': DatabaseConfig.get_database_url('primary', env),
            'analytics': DatabaseConfig.get_database_url('analytics', env),
            'cache': DatabaseConfig.get_database_url('cache', env)
        }
        
        return configs
    
    @staticmethod
    def get_database_url(db_name, env='development'):
        """Get database URL for specific database and environment"""
        # Map environment names to the short forms used in .env
        env_map = {
            'development': 'DEV',
            'production': 'PROD', 
            'testing': 'TEST'
        }
        env_short = env_map.get(env, env.upper())
        env_var = f"{db_name.upper()}_{env_short}_DB_URL"
        result = os.environ.get(env_var, f"sqlite:///{db_name}_{env}.db")
        return result
    
    @staticmethod
    def test_postgresql_connection(db_url):
        """Test PostgreSQL database connection"""
        try:
            # Parse the database URL
            parsed = urlparse(db_url)
            
            if parsed.scheme not in ['postgresql', 'postgres']:
                return False, f"Not a PostgreSQL URL: {parsed.scheme}"
            
            # Extract connection parameters
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password
            
            # Test connection
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=10
            )
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return True, f"Connected successfully. PostgreSQL version: {version}"
            
        except psycopg2.OperationalError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def probe_database_connections():
        """Probe all database connections and return status"""
        env = os.environ.get('FLASK_ENV', 'development')
        configs = DatabaseConfig.get_database_configs()
        results = {}
        
        for db_name, db_url in configs.items():
            if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
                success, message = DatabaseConfig.test_postgresql_connection(db_url)
                results[db_name] = {
                    'url': db_url,
                    'status': 'connected' if success else 'failed',
                    'message': message,
                    'type': 'postgresql'
                }
            elif db_url.startswith('sqlite://'):
                results[db_name] = {
                    'url': db_url,
                    'status': 'available',
                    'message': 'SQLite database (file-based)',
                    'type': 'sqlite'
                }
            elif db_url.startswith('redis://'):
                results[db_name] = {
                    'url': db_url,
                    'status': 'not_tested',
                    'message': 'Redis connection (not tested)',
                    'type': 'redis'
                }
            else:
                results[db_name] = {
                    'url': db_url,
                    'status': 'unknown',
                    'message': 'Unknown database type',
                    'type': 'unknown'
                }
        
        return results
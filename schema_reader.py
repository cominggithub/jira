#!/usr/bin/env python3
"""
Database Schema Reader - Extract and document database schemas
"""
import os
import psycopg2
import sqlite3
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SchemaReader:
    """Read database schemas and generate documentation"""
    
    def __init__(self):
        self.schemas = {}
    
    def get_database_configs(self):
        """Get all database configurations"""
        env = os.environ.get('FLASK_ENV', 'development')
        env_map = {
            'development': 'DEV',
            'production': 'PROD', 
            'testing': 'TEST'
        }
        env_short = env_map.get(env, env.upper())
        
        configs = {}
        for db_name in ['primary', 'analytics', 'cache']:
            env_var = f"{db_name.upper()}_{env_short}_DB_URL"
            db_url = os.environ.get(env_var, f"sqlite:///{db_name}_{env}.db")
            configs[db_name] = db_url
        
        return configs
    
    def read_postgresql_schema(self, db_url, db_name):
        """Read PostgreSQL database schema"""
        try:
            parsed = urlparse(db_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/'),
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            
            # Get database info
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Get all tables
            cursor.execute("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            schema_info = {
                'database_name': db_name,
                'database_type': 'PostgreSQL',
                'version': version,
                'connection_url': db_url,
                'tables': []
            }
            
            for table_name, table_type in tables:
                # Get columns for each table
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """, (table_name,))
                columns = cursor.fetchall()
                
                # Get primary keys
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.key_column_usage
                    WHERE table_name = %s AND table_schema = 'public'
                    AND constraint_name IN (
                        SELECT constraint_name
                        FROM information_schema.table_constraints
                        WHERE table_name = %s AND constraint_type = 'PRIMARY KEY'
                    );
                """, (table_name, table_name))
                primary_keys = [row[0] for row in cursor.fetchall()]
                
                # Get foreign keys
                cursor.execute("""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = %s
                        AND tc.table_schema = 'public';
                """, (table_name,))
                foreign_keys = cursor.fetchall()
                
                # Get indexes
                cursor.execute("""
                    SELECT
                        i.relname AS index_name,
                        a.attname AS column_name,
                        ix.indisunique AS is_unique
                    FROM pg_class t
                    JOIN pg_index ix ON t.oid = ix.indrelid
                    JOIN pg_class i ON i.oid = ix.indexrelid
                    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                    WHERE t.relname = %s
                    AND t.relkind = 'r'
                    ORDER BY i.relname, a.attname;
                """, (table_name,))
                indexes = cursor.fetchall()
                
                table_info = {
                    'name': table_name,
                    'type': table_type,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2] == 'YES',
                            'default': col[3],
                            'max_length': col[4],
                            'precision': col[5],
                            'scale': col[6],
                            'is_primary_key': col[0] in primary_keys
                        }
                        for col in columns
                    ],
                    'primary_keys': primary_keys,
                    'foreign_keys': [
                        {
                            'column': fk[0],
                            'references_table': fk[1],
                            'references_column': fk[2]
                        }
                        for fk in foreign_keys
                    ],
                    'indexes': [
                        {
                            'name': idx[0],
                            'column': idx[1],
                            'unique': idx[2]
                        }
                        for idx in indexes
                    ]
                }
                
                schema_info['tables'].append(table_info)
            
            cursor.close()
            conn.close()
            
            return schema_info
            
        except Exception as e:
            print(f"Error reading PostgreSQL schema for {db_name}: {e}")
            return None
    
    def read_sqlite_schema(self, db_url, db_name):
        """Read SQLite database schema"""
        try:
            db_path = db_url.replace('sqlite:///', '')
            
            # Check if database exists
            if not os.path.exists(db_path):
                return {
                    'database_name': db_name,
                    'database_type': 'SQLite',
                    'version': 'File not found',
                    'connection_url': db_url,
                    'tables': [],
                    'error': f'Database file {db_path} does not exist'
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get SQLite version
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            
            # Get all tables
            cursor.execute("""
                SELECT name, type FROM sqlite_master 
                WHERE type IN ('table', 'view') 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
            """)
            tables = cursor.fetchall()
            
            schema_info = {
                'database_name': db_name,
                'database_type': 'SQLite',
                'version': f'SQLite {version}',
                'connection_url': db_url,
                'tables': []
            }
            
            for table_name, table_type in tables:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = cursor.fetchall()
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name});")
                indexes = cursor.fetchall()
                
                table_info = {
                    'name': table_name,
                    'type': table_type,
                    'columns': [
                        {
                            'name': col[1],
                            'type': col[2],
                            'nullable': col[3] == 0,
                            'default': col[4],
                            'is_primary_key': col[5] == 1
                        }
                        for col in columns
                    ],
                    'primary_keys': [col[1] for col in columns if col[5] == 1],
                    'foreign_keys': [
                        {
                            'column': fk[3],
                            'references_table': fk[2],
                            'references_column': fk[4]
                        }
                        for fk in foreign_keys
                    ],
                    'indexes': [
                        {
                            'name': idx[1],
                            'unique': idx[2] == 1
                        }
                        for idx in indexes
                    ]
                }
                
                schema_info['tables'].append(table_info)
            
            conn.close()
            return schema_info
            
        except Exception as e:
            print(f"Error reading SQLite schema for {db_name}: {e}")
            return None
    
    def read_all_schemas(self):
        """Read schemas from all configured databases"""
        configs = self.get_database_configs()
        
        for db_name, db_url in configs.items():
            print(f"Reading schema for {db_name}...")
            
            if db_url.startswith(('postgresql://', 'postgres://')):
                schema = self.read_postgresql_schema(db_url, db_name)
            elif db_url.startswith('sqlite:///'):
                schema = self.read_sqlite_schema(db_url, db_name)
            else:
                schema = {
                    'database_name': db_name,
                    'database_type': 'Unknown',
                    'version': 'N/A',
                    'connection_url': db_url,
                    'tables': [],
                    'error': f'Unsupported database type: {db_url.split("://")[0]}'
                }
            
            if schema:
                self.schemas[db_name] = schema
    
    def get_field_description(self, table_name, column_name):
        """Get field description based on domain knowledge"""
        descriptions = {
            # s_feature_map table
            'feature_key': 'Unique identifier for SONiC features (community and Edgecore proprietary)',
            'category': 'Feature category classification',
            'feature_n1': 'Feature name or title',
            'ec_sonic_2111': 'Edgecore SONiC 2111 branch support status (community branch)',
            'ec_sonic_2211': 'Edgecore SONiC 2211 branch support status (community branch)', 
            'ec_202211_fabric': 'Edgecore 202211 fabric implementation support',
            'ec_sonic_2311_x': 'Edgecore SONiC 2311-x branch support status (community branch)',
            'ec_sonic_2311_n': 'Edgecore SONiC 2311-n branch support status (community branch)',
            'vs_202311': 'Virtual Switch 202311 implementation support',
            'vs_202311_fabric': 'Virtual Switch 202311 fabric implementation support',
            'ec_proprietary': 'Edgecore proprietary feature implementation',
            'component': 'JIRA Cloud component associated with this feature',
            
            # s_feature_label table
            'label': 'Classification label or tag for the feature',
            
            # s_test_case table
            'test_case_id': 'Unique identifier for the test case',
            'test_case_name': 'Human-readable name of the test case',
            'description': 'Detailed description of what the test case covers',
            'step': 'Test execution steps and procedures',
            'topology': 'Network topology or test environment configuration',
            'pytest_mark': 'Pytest markers for test categorization and execution',
            'validation': 'Validation criteria and expected results',
            'traffic_pattern': 'Network traffic patterns used in testing',
            'project_customer': 'Associated project or customer information',
            'time': 'Estimated execution time or duration',
            'note': 'Additional notes and comments',
            
            # s_test_case_label table - inherits from above
            
            # Common fields
            'created_at': 'Timestamp when the record was created',
        }
        
        # Try exact match first
        key = f"{table_name}.{column_name}"
        if key in descriptions:
            return descriptions[key]
        
        # Try column name only
        if column_name in descriptions:
            return descriptions[column_name]
        
        # Default description
        return f"Database column: {column_name}"

    def generate_markdown(self, db_name, schema):
        """Generate markdown documentation for a database schema"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md_content = f"""# {schema['database_name'].title()} Database Schema

**Generated:** {timestamp}  
**Database Type:** {schema['database_type']}  
**Version:** {schema['version']}  
**Connection:** `{schema['connection_url']}`

## Overview

This database contains schema for SONiC (Software for Open Networking in the Cloud) feature and test management system. The schema supports tracking of both community SONiC features and Edgecore proprietary implementations across different branches and fabric configurations.

### Key Concepts

- **EC**: Edgecore Networks - hardware vendor
- **Feature Key**: Unique identifier for SONiC features (community and proprietary)
- **Community Branches**: 2111, 2211, 2311 refer to SONiC community release branches
- **Component**: JIRA Cloud component for issue tracking
- **VS**: Virtual Switch implementation
- **Fabric**: Network fabric implementation support

"""
        
        if 'error' in schema:
            md_content += f"""## Error

❌ **{schema['error']}**

"""
            return md_content
        
        if not schema['tables']:
            md_content += """## No Tables Found

This database currently contains no tables.

"""
            return md_content
        
        # Table of Contents
        md_content += "## Table of Contents\n\n"
        for table in schema['tables']:
            md_content += f"- [{table['name']}](#{table['name'].lower().replace('_', '-')})\n"
        md_content += "\n"
        
        # Database Statistics
        md_content += f"""## Database Statistics

- **Total Tables:** {len(schema['tables'])}
- **Total Columns:** {sum(len(table['columns']) for table in schema['tables'])}

"""
        
        # Tables Detail
        md_content += "## Tables\n\n"
        
        for table in schema['tables']:
            md_content += f"### {table['name']}\n\n"
            md_content += f"**Type:** {table['type']}\n\n"
            
            if table['columns']:
                md_content += "#### Columns\n\n"
                md_content += "| Column | Type | Nullable | Default | Primary Key | Description |\n"
                md_content += "|--------|------|----------|-------------|-------------|-------------|\n"
                
                for col in table['columns']:
                    nullable = "✅" if col['nullable'] else "❌"
                    pk = "🔑" if col['is_primary_key'] else ""
                    default = col['default'] if col['default'] else ""
                    description = self.get_field_description(table['name'], col['name'])
                    
                    # Format type with length/precision info
                    col_type = col['type']
                    if col.get('max_length'):
                        col_type += f"({col['max_length']})"
                    elif col.get('precision') and col.get('scale'):
                        col_type += f"({col['precision']},{col['scale']})"
                    elif col.get('precision'):
                        col_type += f"({col['precision']})"
                    
                    md_content += f"| {col['name']} | {col_type} | {nullable} | {default} | {pk} | {description} |\n"
                
                md_content += "\n"
            
            if table['primary_keys']:
                md_content += f"**Primary Keys:** {', '.join(table['primary_keys'])}\n\n"
            
            if table['foreign_keys']:
                md_content += "#### Foreign Keys\n\n"
                md_content += "| Column | References Table | References Column |\n"
                md_content += "|--------|------------------|-------------------|\n"
                for fk in table['foreign_keys']:
                    md_content += f"| {fk['column']} | {fk['references_table']} | {fk['references_column']} |\n"
                md_content += "\n"
            
            if table['indexes']:
                md_content += "#### Indexes\n\n"
                for idx in table['indexes']:
                    unique = " (UNIQUE)" if idx.get('unique') else ""
                    column_info = f" on {idx['column']}" if idx.get('column') else ""
                    md_content += f"- **{idx['name']}**{unique}{column_info}\n"
                md_content += "\n"
            
            md_content += "---\n\n"
        
        return md_content
    
    def save_schemas_to_files(self):
        """Save all schemas to markdown files"""
        for db_name, schema in self.schemas.items():
            markdown_content = self.generate_markdown(db_name, schema)
            filename = f"schema_{db_name}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ Schema saved to {filename}")

def main():
    """Main function to read and document all database schemas"""
    print("🔍 Reading database schemas...")
    
    reader = SchemaReader()
    reader.read_all_schemas()
    reader.save_schemas_to_files()
    
    print(f"\n✅ Generated {len(reader.schemas)} schema documentation files")
    print("📁 Files created:")
    for db_name in reader.schemas.keys():
        print(f"   - schema_{db_name}.md")

if __name__ == "__main__":
    main()
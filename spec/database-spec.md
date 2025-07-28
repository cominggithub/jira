# Database Specification

## Requirements

### Functional Requirements

1. **Multi-Database Architecture**
   - Primary database for core application data
   - Analytics database for reporting and metrics
   - Cache database for performance optimization
   - Support for both PostgreSQL and SQLite

2. **Data Models**
   - SONiC feature management with version support
   - Test case storage and categorization
   - Label and metadata management
   - Audit trails and change tracking

3. **Performance**
   - Efficient queries with proper indexing
   - Connection pooling and resource management
   - Caching layer for frequently accessed data
   - Query optimization and monitoring

4. **Data Integrity**
   - Foreign key constraints and referential integrity
   - Data validation at the model level
   - Transaction management and rollback capabilities
   - Backup and recovery procedures

### Non-Functional Requirements

1. **Scalability**
   - Support for 100,000+ test cases
   - 10,000+ SONiC features across multiple versions
   - Concurrent user access (50+ simultaneous users)
   - Horizontal scaling capabilities

2. **Reliability**
   - 99.9% uptime target
   - Data consistency across all operations
   - Automated backup and recovery
   - Disaster recovery procedures

3. **Security**
   - Encrypted connections (SSL/TLS)
   - User authentication and authorization
   - Data encryption at rest (sensitive fields)
   - Audit logging for all data changes

## Feature Description

### Database Architecture

#### 1. Primary Database (PostgreSQL)
**Purpose**: Core application data storage
**Schema**: `ESTS_Dev`
**Tables**:
- `s_feature_map` - SONiC feature mapping
- `s_feature_label` - Feature labels and categories
- `s_test_case` - Test case definitions
- `s_test_case_label` - Test case labels
- `audit_log` - Change tracking and audit trail

#### 2. Analytics Database (PostgreSQL)
**Purpose**: Reporting, metrics, and analytical queries
**Schema**: `ESTS_Analytics`
**Tables**:
- `feature_metrics` - Feature usage statistics
- `test_execution_history` - Test execution records
- `performance_metrics` - System performance data
- `user_activity` - User interaction tracking

#### 3. Cache Database (SQLite)
**Purpose**: High-performance caching and session storage
**File**: `cache_dev.db`
**Tables**:
- `api_cache` - API response caching
- `session_data` - User session information
- `temp_data` - Temporary processing data

## Configuration

### Database Connection Configuration
```python
# config/database.py
DATABASE_CONFIGS = {
    'primary': {
        'url': 'postgresql://postgres:k8sadmin@10.102.6.16:15432/ESTS_Dev',
        'type': 'postgresql',
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600
    },
    'analytics': {
        'url': 'postgresql://postgres:k8sadmin@10.102.6.16:15432/ESTS_Analytics',
        'type': 'postgresql',
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 3600
    },
    'cache': {
        'url': 'sqlite:///cache_dev.db',
        'type': 'sqlite',
        'timeout': 30
    }
}
```

### SQLAlchemy Configuration
```python
# config/base.py
class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_CONFIGS['primary']['url']
    SQLALCHEMY_BINDS = {
        'analytics': DATABASE_CONFIGS['analytics']['url'],
        'cache': DATABASE_CONFIGS['cache']['url']
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
```

## Test Criteria

### Unit Tests
- [ ] Model definition and validation
- [ ] Database connection establishment
- [ ] CRUD operations for all models
- [ ] Constraint validation and error handling
- [ ] Migration scripts execution

### Integration Tests
- [ ] Multi-database transaction handling
- [ ] Cross-database queries and joins
- [ ] Connection pooling under load
- [ ] Backup and restore procedures
- [ ] Performance under concurrent access

### Data Quality Tests
- [ ] Data integrity constraints
- [ ] Foreign key relationships
- [ ] Data validation rules
- [ ] Duplicate detection and prevention
- [ ] Data migration accuracy

### Performance Tests
- [ ] Query execution time benchmarks
- [ ] Index effectiveness measurement
- [ ] Connection pool optimization
- [ ] Cache hit ratio analysis
- [ ] Concurrent operation handling

## Source Code Structure

```
/
├── models/                         # Database models
│   ├── __init__.py                 # Model exports
│   ├── base.py                     # Base model class
│   └── sonic_feature.py            # SONiC feature models
├── config/
│   ├── database.py                 # Database configuration
│   └── base.py                     # Application configuration
├── migrations/                     # Database migrations
│   ├── alembic.ini                 # Alembic configuration
│   ├── env.py                      # Migration environment
│   └── versions/                   # Migration scripts
├── db_manager.py                   # Database management utilities
├── schema_reader.py                # Schema documentation generator
└── tests/database/                 # Database tests
    ├── test_models.py              # Model tests
    ├── test_connections.py         # Connection tests
    └── test_migrations.py          # Migration tests
```

## Temporary Folders

### Database Working Directories
- `backups/` - Database backup files
- `migrations/versions/` - Migration version files
- `tmp/db/` - Temporary database operations
- `logs/db/` - Database operation logs

### Cache Locations
- `cache_dev.db` - Main cache database file
- `cache/queries/` - Query result cache
- `cache/sessions/` - Session data cache

## Test Files Structure

```
tests/database/
├── test_models.py                  # Model definition tests
├── test_crud_operations.py         # CRUD operation tests
├── test_relationships.py           # Model relationship tests
├── test_constraints.py             # Database constraint tests
├── test_migrations.py              # Migration tests
├── test_performance.py             # Database performance tests
├── fixtures/
│   ├── sample_features.sql         # Sample feature data
│   ├── sample_test_cases.sql       # Sample test case data
│   ├── test_schema.sql             # Test database schema
│   └── migration_data.sql          # Migration test data
├── integration/
│   ├── test_multi_db.py            # Multi-database tests
│   ├── test_transactions.py        # Transaction tests
│   └── test_connection_pool.py     # Connection pooling tests
└── performance/
    ├── test_query_performance.py   # Query performance tests
    ├── test_concurrent_access.py   # Concurrency tests
    └── test_large_datasets.py      # Large dataset tests
```

## Data Models

### SONiC Feature Model
```python
# models/sonic_feature.py
class FeatureMap(db.Model):
    __tablename__ = 's_feature_map'
    
    id = db.Column(db.Integer, primary_key=True)
    feature_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    feature_n1 = db.Column(db.Text)  # Feature description
    ec_sonic_2111 = db.Column(db.String(20))
    ec_sonic_2211 = db.Column(db.String(20))
    ec_sonic_2311_x = db.Column(db.String(20))
    ec_sonic_2311_n = db.Column(db.String(20))
    vs_202311 = db.Column(db.String(20))
    ec_proprietary = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    labels = db.relationship('FeatureLabel', backref='feature', lazy='dynamic')
```

### Feature Label Model
```python
class FeatureLabel(db.Model):
    __tablename__ = 's_feature_label'
    
    id = db.Column(db.Integer, primary_key=True)
    feature_key = db.Column(db.String(100), db.ForeignKey('s_feature_map.feature_key'), nullable=False)
    label = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite index for performance
    __table_args__ = (
        db.Index('idx_feature_label', 'feature_key', 'label'),
    )
```

### Test Case Model
```python
class TestCase(db.Model):
    __tablename__ = 's_test_case'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), index=True)
    feature_key = db.Column(db.String(100), db.ForeignKey('s_feature_map.feature_key'))
    status = db.Column(db.String(20), default='Draft')
    priority = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    labels = db.relationship('TestCaseLabel', backref='test_case', lazy='dynamic')
    feature = db.relationship('FeatureMap', backref='test_cases')
```

## Database Schema

### Primary Database Schema (PostgreSQL)
```sql
-- SONiC Feature Mapping Table
CREATE TABLE s_feature_map (
    id SERIAL PRIMARY KEY,
    feature_key VARCHAR(100) UNIQUE NOT NULL,
    feature_n1 TEXT,
    ec_sonic_2111 VARCHAR(20),
    ec_sonic_2211 VARCHAR(20),
    ec_sonic_2311_x VARCHAR(20),
    ec_sonic_2311_n VARCHAR(20),
    vs_202311 VARCHAR(20),
    ec_proprietary VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feature Labels Table
CREATE TABLE s_feature_label (
    id SERIAL PRIMARY KEY,
    feature_key VARCHAR(100) REFERENCES s_feature_map(feature_key),
    label VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test Cases Table
CREATE TABLE s_test_case (
    id SERIAL PRIMARY KEY,
    test_case_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    feature_key VARCHAR(100) REFERENCES s_feature_map(feature_key),
    status VARCHAR(20) DEFAULT 'Draft',
    priority VARCHAR(20) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test Case Labels Table
CREATE TABLE s_test_case_label (
    id SERIAL PRIMARY KEY,
    test_case_id VARCHAR(50) REFERENCES s_test_case(test_case_id),
    label VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log Table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes for Performance
```sql
-- Feature map indexes
CREATE INDEX idx_feature_key ON s_feature_map(feature_key);
CREATE INDEX idx_feature_proprietary ON s_feature_map(ec_proprietary);
CREATE INDEX idx_feature_created ON s_feature_map(created_at);

-- Feature label indexes
CREATE INDEX idx_feature_label_key ON s_feature_label(feature_key);
CREATE INDEX idx_feature_label_name ON s_feature_label(label);
CREATE INDEX idx_feature_label_composite ON s_feature_label(feature_key, label);

-- Test case indexes
CREATE INDEX idx_test_case_id ON s_test_case(test_case_id);
CREATE INDEX idx_test_case_category ON s_test_case(category);
CREATE INDEX idx_test_case_feature ON s_test_case(feature_key);
CREATE INDEX idx_test_case_status ON s_test_case(status);
CREATE INDEX idx_test_case_created ON s_test_case(created_at);

-- Audit log indexes
CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_record ON audit_log(record_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
```

## Migration Management

### Alembic Configuration
```python
# migrations/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from models.base import db

# Configuration object
config = context.config

# Set up loggers
fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = db.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Migration Commands
```bash
# Initialize migration repository
flask db init

# Generate migration script
flask db migrate -m "Add test case model"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Show current revision
flask db current

# Show migration history
flask db history
```

## Performance Optimization

### Query Optimization
```python
# Use efficient queries with proper indexing
def get_features_by_label(label_name):
    return db.session.query(FeatureMap)\
        .join(FeatureLabel)\
        .filter(FeatureLabel.label == label_name)\
        .options(db.joinedload(FeatureMap.labels))\
        .all()

# Use pagination for large datasets
def get_paginated_features(page=1, per_page=50):
    return FeatureMap.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
```

### Connection Pool Configuration
```python
# Optimized connection pool settings
engine = create_engine(
    database_url,
    pool_size=10,           # Number of connections to maintain
    max_overflow=20,        # Additional connections allowed
    pool_timeout=30,        # Timeout for getting connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Validate connections before use
    echo=False              # Disable SQL logging in production
)
```

### Caching Strategy
```python
# Redis-based caching for expensive queries
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.memoize(timeout=3600)
def get_feature_statistics():
    """Cache expensive aggregation queries"""
    return db.session.query(
        func.count(FeatureMap.id).label('total_features'),
        func.count(case([(FeatureMap.ec_proprietary == 'EC', 1)])).label('ec_features'),
        func.count(case([(FeatureMap.ec_proprietary == 'COMMUNITY', 1)])).label('community_features')
    ).first()
```

## Backup and Recovery

### Backup Strategy
```bash
# Daily automated backup
pg_dump -h 10.102.6.16 -U postgres -d ESTS_Dev > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -h 10.102.6.16 -U postgres -d ESTS_Dev | gzip > backup_$(date +%Y%m%d).sql.gz

# Schema-only backup
pg_dump -h 10.102.6.16 -U postgres -d ESTS_Dev -s > schema_backup.sql
```

### Recovery Procedures
```bash
# Full database restore
psql -h 10.102.6.16 -U postgres -d ESTS_Dev < backup_20240115.sql

# Restore from compressed backup
gunzip -c backup_20240115.sql.gz | psql -h 10.102.6.16 -U postgres -d ESTS_Dev

# Schema-only restore
psql -h 10.102.6.16 -U postgres -d ESTS_Dev < schema_backup.sql
```

## Monitoring and Maintenance

### Database Monitoring
```python
# Monitor database performance
def get_database_stats():
    """Get database performance statistics"""
    stats = db.session.execute(text("""
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
    """)).fetchall()
    return stats
```

### Maintenance Tasks
```sql
-- Regular maintenance queries
VACUUM ANALYZE s_feature_map;
VACUUM ANALYZE s_test_case;
REINDEX TABLE s_feature_map;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('s_feature_map', 's_test_case')
ORDER BY n_distinct DESC;

-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;
```
# SQLAlchemy Setup for SONiC Feature Management

This project now includes SQLAlchemy ORM for database management alongside the existing raw SQL approach.

## Key Components

### 1. Models (`models/`)
- **`models/base.py`** - SQLAlchemy database instance
- **`models/sonic_feature.py`** - FeatureMap and FeatureLabel models
- **`models/__init__.py`** - Model exports

### 2. Database Management (`db_manager.py`)
```bash
# Initialize database tables
python db_manager.py init-db --env development

# Drop all tables
python db_manager.py drop-db --env development

# Reset database (drop + recreate)
python db_manager.py reset-db --env development

# Show statistics
python db_manager.py show-stats --env development

# List features
python db_manager.py list-features --env development --limit 10
```

### 3. SQLAlchemy Feature Importer (`feature_importer_sqlalchemy.py`)
```bash
# Import latest Excel file
python feature_importer_sqlalchemy.py --env development

# Import specific date
python feature_importer_sqlalchemy.py --env development --date 20250627

# Dry run (preview only)
python feature_importer_sqlalchemy.py --env development --dry-run

# Import without clearing existing data
python feature_importer_sqlalchemy.py --env development --no-clear
```

### 4. Updated Routes
- **`routes_sqlalchemy.py`** - SQLAlchemy-based feature list route
- **`app.py`** - Updated to use SQLAlchemy models and routes

## Database Models

### FeatureMap
- **Primary Key**: `feature_key` (String)
- **Fields**: category, feature_n1 (description), branch support columns, ec_proprietary, component
- **Relationships**: One-to-many with FeatureLabel

### FeatureLabel  
- **Primary Key**: Composite (`feature_key`, `label`)
- **Fields**: feature_key (FK), label, created_at
- **Relationships**: Many-to-one with FeatureMap

## Benefits of SQLAlchemy

1. **Type Safety**: Models define schema and relationships
2. **Query Builder**: Pythonic query construction
3. **Relationship Management**: Automatic joins and lazy loading
4. **Migration Support**: Flask-Migrate for schema changes
5. **Maintainability**: Cleaner, more readable code

## Usage Examples

### Query Features with Labels
```python
from models import FeatureMap, FeatureLabel

# Get all features with their labels
features = FeatureMap.query.options(joinedload(FeatureMap.labels)).all()

# Filter by label
community_features = FeatureMap.query.join(FeatureLabel).filter(
    FeatureLabel.label == 'community'
).all()

# Filter by source type
ec_features = FeatureMap.query.filter(
    FeatureMap.ec_proprietary == 'EC'
).all()
```

### Create New Features
```python
from models.base import db
from models import FeatureMap, FeatureLabel

# Create feature
feature = FeatureMap(
    feature_key='new_feature',
    category='L3',
    feature_n1='New feature description',
    ec_sonic_2111='Support',
    ec_proprietary='COMMUNITY'
)
db.session.add(feature)

# Add labels
label1 = FeatureLabel(feature_key='new_feature', label='community')
label2 = FeatureLabel(feature_key='new_feature', label='routing')
db.session.add_all([label1, label2])

db.session.commit()
```

## Migration Path

The SQLAlchemy models are designed to work with the existing database schema:
- No `id` columns (uses natural keys)
- Compatible field names and types
- Preserves existing data structure

Both raw SQL and SQLAlchemy approaches can coexist during the transition period.

## Environment Setup

1. **Install Dependencies**:
   ```bash
   pip install Flask-SQLAlchemy Flask-Migrate
   ```

2. **Initialize Database**:
   ```bash
   python db_manager.py init-db --env development
   ```

3. **Import Data**:
   ```bash
   python feature_importer_sqlalchemy.py --env development
   ```

4. **Verify Setup**:
   ```bash
   python db_manager.py show-stats --env development
   ```

The Feature Support Matrix web interface now uses SQLAlchemy models while maintaining the same functionality and display format.
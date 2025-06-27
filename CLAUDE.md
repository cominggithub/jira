# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Abbreviations and Acronyms

- `ec` stands for Edgecore
- `feature_key` means the key of sonic feature, including sonic community feature and ec proprietary feature
- `2111 2211 2311` means community sonic branch
- `component` is the jira cloud component in ticket
- `ESTS` stands for Edgecore SONiC Test Suite

## File Locations

- There is an EC SONiC feature file located at `data/EC_SONiC_Feature.<data>.xlsx`
- There is ests test case file in `data/ESTS_Test_Case.xlsx`

## Feature Classification

- EC Proprietary is categorized to EC or community:
  - If it is EC, that means EC's proprietary feature
  - If it is community, that means native support from community source
  - Update the feature importer and the feature matrix page properly

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
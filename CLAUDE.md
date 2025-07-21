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

## EC Device Information

### Edgecore Switch Portfolio by Chip Architecture

**Sheet1 - Chip to Platform Mapping**:
- TD2+: AS5812-54X
- TD3: AS4630-54NPE, AS4630-54PE, AS5835-54T, AS5835-54X, AS7326-56X, AS7726-32X
- TD4: AS9726-32D  
- TH: AS7712-32X
- TH2: AS7816-64X
- TH3: AS9716-32D, AS8000
- TH4: AS9736-64D, AS9737-32D
- TH5: AIS800-64D, AIS800-64O, AIS800-32D, AIS800-32O, AS9817-64D, AS9O17-64O
- TF: Wedge100BF-32QS, Wedge100BF-32X, Wedge100BF-65X
- TF2: AS9516-32D

**Product Line Details** (24 platforms total with specifications from product line sheet)

**Naming Convention**: ASwxyz-abc where w indicates line rate (4xxx=1G, 5xxx=10G, 6xxx=40G, 7xxx=100G, 8xxx/9xxx=400G)

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
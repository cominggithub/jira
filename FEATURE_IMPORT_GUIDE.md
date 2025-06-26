# EC SONiC Feature Import Guide

## Overview
The `feature_importer.py` script imports EC SONiC feature data from Excel files into the ESTS_Dev database.

## Features
- ✅ Reads Excel files with pattern `data/EC_SONiC_Feature.YYYYMMDD.xlsx`
- ✅ Maps Excel columns to database fields automatically
- ✅ Splits comma-separated labels and stores in `s_feature_label` table
- ✅ Handles insert/update logic (upsert) for existing features
- ✅ Auto-generates feature keys if missing
- ✅ Comprehensive error handling and validation
- ✅ Dry-run mode for testing
- ✅ Detailed import statistics

## Usage

### Basic Import (Latest File)
```bash
source venv/bin/activate
python feature_importer.py
```

### Import Specific Date
```bash
python feature_importer.py --date 20250626
```

### Import Specific File
```bash
python feature_importer.py --file data/EC_SONiC_Feature.20250626.xlsx
```

### Dry Run (Preview Only)
```bash
python feature_importer.py --dry-run
```

### Import Without Clearing Existing Data
```bash
python feature_importer.py --no-clear
```

## Column Mapping

| Excel Column | Database Field | Description |
|--------------|----------------|-------------|
| `Feature_Key` | `feature_key` | Unique identifier (auto-generated if missing) |
| `Category` | `category` | Feature category (e.g., L2, L3) |
| `Feature N1` | `feature_n1` | Feature name/title |
| `EC_SONiC_2111` | `ec_sonic_2111` | Edgecore SONiC 2111 support status |
| `EC_SONiC_2211` | `ec_sonic_2211` | Edgecore SONiC 2211 support status |
| `EC_202211_Fabric` | `ec_202211_fabric` | Edgecore 202211 fabric support |
| `EC SONiC 2311.X` | `ec_sonic_2311_x` | Edgecore SONiC 2311-X support |
| `EC SONiC 2311.N` | `ec_sonic_2311_n` | Edgecore SONiC 2311-N support |
| `VS_202311` | `vs_202311` | Virtual Switch 202311 support |
| `VS_202311_Fabric` | `vs_202311_fabric` | VS 202311 fabric support |
| `EC Proprietary` | `ec_proprietary` | Edgecore proprietary implementation |
| `Component` | `component` | JIRA component association |
| `Labels` | Split to `s_feature_label` | Comma-separated labels |

## Database Tables

### s_feature_map
- Primary table storing feature information
- Uses `feature_key` as primary key
- Updates existing records, inserts new ones

### s_feature_label  
- Stores feature labels (many-to-many relationship)
- Composite primary key: `(feature_key, label)`
- Clears existing labels before inserting new ones

## Data Clearing Behavior

⚠️ **IMPORTANT**: By default, the script **clears all existing data** before importing new data.

### Default Behavior (Recommended)
- Clears `s_feature_label` table (due to foreign key constraints)
- Clears `s_feature_map` table  
- Imports fresh data from Excel

### Alternative: Append Mode
Use `--no-clear` flag to append data without clearing existing records.

## Data Processing Rules

### Feature Key Generation
If `Feature_Key` is empty, auto-generates from:
```
{Category}_{Feature_N1}
```
Example: `L2_LAG_LACP_Fallback` → `L2_LAG_LACP_FALLBACK`

### Label Processing
- Splits `Labels` column by comma
- Trims whitespace from each label
- Skips empty labels
- Example: `"community, lag, lacp, lacp_fallback"` → 4 separate label records

### Data Cleaning
- Converts `NaN`, `None`, empty strings to `NULL`
- Trims whitespace from all values
- Normalizes data types

### Support Status Value Mapping
Support status fields are automatically mapped from Excel codes to descriptive text:
- **O** → `Support`
- **X** → `Not Support` 
- **D** → `Under Development`

Applied to fields: `ec_sonic_2111`, `ec_sonic_2211`, `ec_202211_fabric`, `ec_sonic_2311_x`, `ec_sonic_2311_n`, `vs_202311`, `vs_202311_fabric`, `ec_proprietary`

## Error Handling
- Validates required columns exist
- Skips rows with missing/invalid feature keys
- Reports all errors in summary
- Commits only successful operations
- Database rollback on critical errors

## Output Example
```
🚀 Starting EC SONiC Feature import process
============================================================
📅 Using file: data/EC_SONiC_Feature.20250626.xlsx (date: 20250626)
✅ Connected to database: 10.102.6.16:15432/ESTS_Dev
📖 Reading Excel file: data/EC_SONiC_Feature.20250626.xlsx
📊 Loaded 149 rows from feature_map sheet

📝 Processing 149 feature rows...
✅ Feature inserted: lacp_fallback
✅ Labels inserted for lacp_fallback: community, lag, lacp, lacp_fallback
✅ Feature inserted: static_lag
✅ Labels inserted for static_lag: ec, lag, static_lag

📊 Import Summary
============================================================
📝 Features processed: 149
➕ Features inserted: 145
🔄 Features updated: 4
🏷️  Labels processed: 587
➕ Labels inserted: 587
❌ Errors: 0

🎉 Import completed successfully!
```

## Requirements
- Python packages: `pandas`, `openpyxl`, `psycopg2-binary`, `python-dotenv`
- Database connection configured in `.env`
- Excel file in `data/` directory with correct naming pattern

## Notes
- Script supports both insert and update operations (upsert)
- Always backs up database before running production imports
- Use `--dry-run` to preview changes before actual import
- Check import summary for errors and statistics
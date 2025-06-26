# ESTS Test Case Import Guide

## Overview
The `testcase_importer.py` script imports ESTS test case data from Excel files into the ESTS_Dev database.

## Features
- ✅ Reads Excel files with test case data from the `data/` directory
- ✅ Auto-detects sheet with test case data (prioritizes "ESTS testcase" sheet)
- ✅ Maps Excel columns to database fields intelligently
- ✅ Splits comma-separated labels and stores in `s_test_case_label` table
- ✅ Handles insert logic for test cases (clears existing data by default)
- ✅ Auto-generates test case IDs if missing
- ✅ Comprehensive error handling and validation
- ✅ Dry-run mode for testing
- ✅ Detailed import statistics

## Usage

### Basic Import (Latest File)
```bash
source venv/bin/activate
python testcase_importer.py
```

### Import Specific Date
```bash
python testcase_importer.py --date 20250626
```

### Import Specific File
```bash
python testcase_importer.py --file data/ESTS_Test_Case.20250626.xlsx
```

### Import Specific Sheet
```bash
python testcase_importer.py --sheet "implenented(&ID)(以 zepher 為主)"
```

### Dry Run (Preview Only)
```bash
python testcase_importer.py --dry-run
```

### Import Without Clearing Existing Data
```bash
python testcase_importer.py --no-clear
```

## Column Mapping

The script intelligently maps Excel columns to database fields:

| Database Field | Possible Excel Columns |
|---------------|------------------------|
| `test_case_id` | Testcase ID, Test ID, ID, TestcaseID, TestID |
| `test_case_name` | Testcase Name, Test Name, Name, TestcaseName, TestName, Testcase |
| `description` | Description, Desc, Brief |
| `step` | Step, Steps, Test Steps, Procedure |
| `topology` | Topology, Topo, Test Topology |
| `pytest_mark` | Pytest Mark, PyTest Mark, Mark, Markers |
| `validation` | Validation, Validate, Expected Result, Result |
| `traffic_pattern` | Traffic Pattern, Traffic, Pattern |
| `project_customer` | Project / Customer, Project/Customer, Project, Customer |
| `time` | Time, Duration, Execution Time |
| `note` | Note, Notes, Comment, Comments |
| `labels` | Features (labels), New Features (labels), Features, Labels, Tags |

## Database Tables

### s_test_case
- Primary table storing test case information
- Uses `test_case_id` as primary key
- Clears existing records before importing new ones

### s_test_case_label  
- Stores test case labels (many-to-many relationship)
- Composite primary key: `(test_case_id, label)`
- Links test cases to classification labels

## Data Processing Rules

### Test Case ID Generation
If `test_case_id` is empty, auto-generates from:
- Test case name (if available): cleaned and lowercased
- Row index: `testcase_0001`, `testcase_0002`, etc.

### Label Processing
- Combines labels from multiple label columns
- Splits by comma and trims whitespace
- Removes duplicates
- Skips empty labels
- Example: `"feature1, feature2, feature3"` → 3 separate label records

### Sheet Detection
The script automatically finds the best sheet to import from:
1. Looks for sheet named "ESTS testcase"
2. Falls back to sheets containing "implenented"
3. Falls back to any sheet with "testcase" or "test" in the name
4. Uses first available sheet as last resort

### Data Cleaning
- Converts `NaN`, `None`, empty strings to `NULL`
- Trims whitespace from all values
- Normalizes data types
- Skips rows without meaningful test case data

## Error Handling
- Validates Excel file exists and is readable
- Handles missing sheets gracefully with fallback logic
- Skips rows with insufficient data
- Reports all errors in summary
- Commits only successful operations
- Database rollback on critical errors

## Output Example
```
🚀 Starting ESTS Test Case import process
============================================================
📅 Using file: data/ESTS_Test_Case.20250626.xlsx (date: 20250626)
✅ Connected to database: 10.102.6.16:15432/ESTS_Dev
📖 Reading Excel file: data/ESTS_Test_Case.20250626.xlsx
📋 Found matching sheet: 'implenented(&ID)(以 zepher 為主)'
📊 Loaded 1324 rows from 'implenented(&ID)(以 zepher 為主)' sheet

🧹 Clearing existing test case data...
   ✅ Cleared 1200 records from s_test_case_label
   ✅ Cleared 500 records from s_test_case
   ✅ Old test case data cleared successfully

📝 Processing 1324 test case rows...
✅ Test case inserted: tool-1
✅ Labels inserted for tool-1: community, tool, config
✅ Test case inserted: tool-2
✅ Labels inserted for tool-2: system, cleanup, maintenance

📊 Import Summary
============================================================
📝 Test cases processed: 1324
➕ Test cases inserted: 1200
🏷️  Labels processed: 3500
➕ Labels inserted: 3500
❌ Errors: 0

🎉 Import completed successfully!
```

## Requirements
- Python packages: `pandas`, `openpyxl`, `psycopg2-binary`, `python-dotenv`
- Database connection configured in `.env`
- Excel file in `data/` directory

## File Naming Pattern
- `ESTS_Test_Case.xlsx` - Basic naming
- `ESTS_Test_Case.YYYYMMDD.xlsx` - With date suffix
- Any file containing "test_case" in the name

## Sheet Requirements
The Excel sheet should contain columns for:
- **Test Case ID** (or will be auto-generated)
- **Test Case Name** 
- **Description**
- **Steps/Procedures**
- **Labels/Features** (comma-separated)

## Notes
- Script clears existing test case data by default (use `--no-clear` to append)
- Always backup database before running production imports
- Use `--dry-run` to preview changes before actual import
- Check import summary for errors and statistics
- The script handles Chinese characters in sheet names properly
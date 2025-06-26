#!/usr/bin/env python3
"""
ESTS Test Case Importer
Reads ESTS Test Case Excel files and imports data to ESTS_Dev database
"""
import os
import sys
import pandas as pd
import psycopg2
import re
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

class TestCaseImporter:
    """Import ESTS test cases from Excel to database"""
    
    def __init__(self):
        self.db_conn = None
        self.stats = {
            'testcases_processed': 0,
            'testcases_inserted': 0,
            'labels_processed': 0,
            'labels_inserted': 0,
            'errors': []
        }
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            # Get database URL
            env = os.environ.get('FLASK_ENV', 'development')
            env_short = 'DEV' if env == 'development' else 'PROD' if env == 'production' else 'TEST'
            db_url = os.environ.get(f'PRIMARY_{env_short}_DB_URL')
            
            if not db_url:
                raise Exception(f"Database URL not found for environment: {env}")
            
            # Parse URL and connect
            parsed = urlparse(db_url)
            self.db_conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/'),
                user=parsed.username,
                password=parsed.password
            )
            
            print(f"✅ Connected to database: {parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        return True
    
    def find_testcase_file(self, specific_date=None):
        """Find ESTS test case file"""
        data_dir = "data"
        
        if not os.path.exists(data_dir):
            print(f"❌ Data directory not found: {data_dir}")
            return None
        
        # Look for test case files
        testcase_files = []
        for filename in os.listdir(data_dir):
            if "test_case" in filename.lower() and filename.endswith(".xlsx"):
                if specific_date:
                    if specific_date in filename:
                        testcase_files.append((filename, specific_date))
                else:
                    # Extract date if present
                    date_match = re.search(r'(\d{8})', filename)
                    if date_match:
                        testcase_files.append((filename, date_match.group(1)))
                    else:
                        testcase_files.append((filename, '00000000'))  # No date found
        
        if not testcase_files:
            print("❌ No ESTS test case files found")
            return None
        
        # Sort by date and get latest
        testcase_files.sort(key=lambda x: x[1], reverse=True)
        latest_file = os.path.join(data_dir, testcase_files[0][0])
        
        print(f"📅 Using file: {latest_file} (date: {testcase_files[0][1]})")
        return latest_file
    
    def read_excel_data(self, filepath, sheet_name="ESTS testcase"):
        """Read and validate Excel data"""
        try:
            print(f"📖 Reading Excel file: {filepath}")
            print(f"📊 Target sheet: '{sheet_name}'")
            
            # Check if sheet exists
            excel_file = pd.ExcelFile(filepath)
            available_sheets = excel_file.sheet_names
            
            # Try to find the correct sheet
            target_sheet = None
            for sheet in available_sheets:
                if sheet_name.lower() in sheet.lower() or "implenented" in sheet.lower():
                    target_sheet = sheet
                    print(f"📋 Found matching sheet: '{target_sheet}'")
                    break
            
            if not target_sheet:
                print(f"❌ Sheet '{sheet_name}' not found. Available sheets: {available_sheets}")
                print("🔍 Trying first sheet with test case data...")
                # Try the first sheet that looks like test cases
                for sheet in available_sheets:
                    if any(keyword in sheet.lower() for keyword in ['implenented', 'testcase', 'test']):
                        target_sheet = sheet
                        print(f"📋 Using sheet: '{target_sheet}'")
                        break
                
                if not target_sheet:
                    target_sheet = available_sheets[0]
                    print(f"⚠️  Using first available sheet: '{target_sheet}'")
            
            # Read the sheet
            df = pd.read_excel(filepath, sheet_name=target_sheet)
            print(f"📊 Loaded {len(df)} rows from '{target_sheet}' sheet")
            
            # Display column information
            print("📋 Available columns:")
            for i, col in enumerate(df.columns):
                print(f"   {i+1:2d}. {col}")
            
            return df, target_sheet
            
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            return None, None
    
    def clean_value(self, value):
        """Clean and normalize cell values"""
        if pd.isna(value):
            return None
        
        # Convert to string and strip whitespace
        cleaned = str(value).strip()
        
        # Return None for empty strings
        if cleaned == '' or cleaned.lower() in ['nan', 'none', 'null']:
            return None
            
        return cleaned
    
    def generate_testcase_id(self, testcase_name, row_index):
        """Generate test case ID if missing"""
        if testcase_name:
            # Create ID from testcase name
            test_id = re.sub(r'[^\w\-]', '_', str(testcase_name))
            test_id = re.sub(r'_+', '_', test_id)  # Replace multiple underscores
            test_id = test_id.strip('_')  # Remove leading/trailing underscores
            return test_id.lower()
        else:
            # Generate from row index
            return f"testcase_{row_index:04d}"
    
    def process_testcase_row(self, row, row_index):
        """Process a single test case row and return normalized data"""
        # Map Excel columns to database fields - try multiple possible column names
        column_mappings = {
            'test_case_id': ['Testcase ID', 'Test ID', 'ID', 'TestcaseID', 'TestID'],
            'test_case_name': ['Testcase Name', 'Test Name', 'Name', 'TestcaseName', 'TestName', 'Testcase'],
            'description': ['Description', 'Desc', 'Brief'],
            'step': ['Step', 'Steps', 'Test Steps', 'Procedure'],
            'topology': ['Topology', 'Topo', 'Test Topology'],
            'pytest_mark': ['Pytest Mark', 'PyTest Mark', 'Mark', 'Markers'],
            'validation': ['Validation', 'Validate', 'Expected Result', 'Result'],
            'traffic_pattern': ['Traffic Pattern', 'Traffic', 'Pattern'],
            'project_customer': ['Project / Customer', 'Project/Customer', 'Project', 'Customer'],
            'time': ['Time', 'Duration', 'Execution Time'],
            'note': ['Note', 'Notes', 'Comment', 'Comments'],
            'labels': ['Features (labels)', 'New Features (labels)', 'Features', 'Labels', 'Tags']
        }
        
        def find_column_value(field_name):
            """Find value from row using multiple possible column names"""
            possible_columns = column_mappings.get(field_name, [field_name])
            for col_name in possible_columns:
                if col_name in row.index:
                    return self.clean_value(row.get(col_name))
            return None
        
        # Get and clean values
        test_case_id = find_column_value('test_case_id')
        test_case_name = find_column_value('test_case_name')
        
        # Generate test_case_id if missing
        if not test_case_id:
            test_case_id = self.generate_testcase_id(test_case_name, row_index)
        
        # Skip if no meaningful data
        if not test_case_id and not test_case_name:
            return None
        
        # Prepare test case data
        testcase_data = {
            'test_case_id': test_case_id,
            'test_case_name': test_case_name,
            'description': find_column_value('description'),
            'step': find_column_value('step'),
            'topology': find_column_value('topology'),
            'pytest_mark': find_column_value('pytest_mark'),
            'validation': find_column_value('validation'),
            'traffic_pattern': find_column_value('traffic_pattern'),
            'project_customer': find_column_value('project_customer'),
            'time': find_column_value('time'),
            'note': find_column_value('note')
        }
        
        # Process labels (try multiple label columns and combine)
        labels = []
        for label_field in ['labels']:
            labels_raw = find_column_value(label_field)
            if labels_raw:
                # Split by comma and clean each label
                for label in str(labels_raw).split(','):
                    cleaned_label = label.strip()
                    if cleaned_label and cleaned_label not in labels:
                        labels.append(cleaned_label)
        
        return testcase_data, labels
    
    def clear_existing_testcase_data(self):
        """Clear existing data from test case tables"""
        try:
            cursor = self.db_conn.cursor()
            
            print("🧹 Clearing existing test case data...")
            
            # Clear s_test_case_label first (due to foreign key constraint)
            cursor.execute("SELECT COUNT(*) FROM s_test_case_label")
            label_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM s_test_case_label")
            print(f"   ✅ Cleared {label_count} records from s_test_case_label")
            
            # Clear s_test_case
            cursor.execute("SELECT COUNT(*) FROM s_test_case")
            testcase_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM s_test_case")
            print(f"   ✅ Cleared {testcase_count} records from s_test_case")
            
            # Commit the deletions
            self.db_conn.commit()
            print("   ✅ Old test case data cleared successfully")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Error clearing test case data: {e}")
            self.db_conn.rollback()
            return False
    
    def insert_testcase(self, testcase_data):
        """Insert test case in s_test_case table"""
        try:
            cursor = self.db_conn.cursor()
            
            # Insert new test case
            insert_sql = """
            INSERT INTO s_test_case (
                test_case_id, test_case_name, description, step, topology,
                pytest_mark, validation, traffic_pattern, project_customer,
                time, note, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            
            cursor.execute(insert_sql, (
                testcase_data['test_case_id'],
                testcase_data['test_case_name'],
                testcase_data['description'],
                testcase_data['step'],
                testcase_data['topology'],
                testcase_data['pytest_mark'],
                testcase_data['validation'],
                testcase_data['traffic_pattern'],
                testcase_data['project_customer'],
                testcase_data['time'],
                testcase_data['note']
            ))
            
            self.stats['testcases_inserted'] += 1
            cursor.close()
            print(f"✅ Test case inserted: {testcase_data['test_case_id']}")
            return True
            
        except Exception as e:
            self.stats['errors'].append(f"Test case {testcase_data['test_case_id']}: {e}")
            print(f"❌ Error inserting test case {testcase_data['test_case_id']}: {e}")
            return False
    
    def insert_testcase_labels(self, test_case_id, test_case_name, labels):
        """Insert test case labels into s_test_case_label table"""
        if not labels:
            return
        
        try:
            cursor = self.db_conn.cursor()
            
            # Insert labels
            for label in labels:
                cursor.execute("""
                    INSERT INTO s_test_case_label (test_case_id, test_case_name, label, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (test_case_id, test_case_name, label))
                
                self.stats['labels_inserted'] += 1
            
            cursor.close()
            print(f"✅ Labels inserted for {test_case_id}: {', '.join(labels)}")
            
        except Exception as e:
            self.stats['errors'].append(f"Labels for {test_case_id}: {e}")
            print(f"❌ Error inserting labels for {test_case_id}: {e}")
    
    def import_testcases(self, filepath, sheet_name="ESTS testcase", clear_data=True):
        """Main import process"""
        print("🚀 Starting ESTS Test Case import process")
        print("="*60)
        
        # Clear existing data first (if requested)
        if clear_data:
            if not self.clear_existing_testcase_data():
                print("❌ Failed to clear existing test case data. Aborting import.")
                return False
        else:
            print("⚠️  Skipping data clearing - will append to existing data")
        
        # Read Excel data
        df, actual_sheet = self.read_excel_data(filepath, sheet_name)
        if df is None:
            return False
        
        # Process each row
        print(f"\n📝 Processing {len(df)} test case rows...")
        
        for index, row in df.iterrows():
            self.stats['testcases_processed'] += 1
            
            # Process the row
            result = self.process_testcase_row(row, index)
            if result is None:
                continue
            
            testcase_data, labels = result
            
            # Skip empty rows
            if not testcase_data['test_case_id']:
                continue
            
            # Insert test case
            if self.insert_testcase(testcase_data):
                # Insert labels
                if labels:
                    self.stats['labels_processed'] += len(labels)
                    self.insert_testcase_labels(
                        testcase_data['test_case_id'], 
                        testcase_data['test_case_name'], 
                        labels
                    )
        
        # Commit all changes
        self.db_conn.commit()
        print("\n✅ All changes committed to database")
        
        return True
    
    def print_summary(self):
        """Print import summary"""
        print("\n📊 Import Summary")
        print("="*60)
        print(f"📝 Test cases processed: {self.stats['testcases_processed']}")
        print(f"➕ Test cases inserted: {self.stats['testcases_inserted']}")
        print(f"🏷️  Labels processed: {self.stats['labels_processed']}")
        print(f"➕ Labels inserted: {self.stats['labels_inserted']}")
        print(f"❌ Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Error Details:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more errors")
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            print("🔌 Database connection closed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import ESTS test cases from Excel to database')
    parser.add_argument('--date', help='Specific date in YYYYMMDD format (e.g., 20250626)')
    parser.add_argument('--file', help='Specific Excel file path')
    parser.add_argument('--sheet', default='ESTS testcase', help='Sheet name to read (default: "ESTS testcase")')
    parser.add_argument('--dry-run', action='store_true', help='Preview data without importing')
    parser.add_argument('--no-clear', action='store_true', help='Do not clear existing data before import')
    
    args = parser.parse_args()
    
    # Create importer
    importer = TestCaseImporter()
    
    try:
        # Connect to database (skip in dry-run mode)
        if not args.dry_run and not importer.connect_database():
            return 1
        
        # Find Excel file
        if args.file:
            excel_file = args.file
        else:
            excel_file = importer.find_testcase_file(args.date)
        
        if not excel_file:
            print("❌ No Excel file found")
            return 1
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No data will be imported")
            df, sheet_name = importer.read_excel_data(excel_file, args.sheet)
            if df is not None:
                print(f"✅ Would process {len(df)} test case rows from sheet '{sheet_name}'")
                
                # Preview first few rows
                print("\n📋 Preview of first 3 rows:")
                for index, row in df.head(3).iterrows():
                    result = importer.process_testcase_row(row, index)
                    if result:
                        testcase_data, labels = result
                        print(f"   Row {index+1}: {testcase_data['test_case_id']} ({len(labels)} labels)")
                        print(f"      Name: {testcase_data['test_case_name']}")
                        print(f"      Description: {testcase_data['description'][:100] if testcase_data['description'] else 'None'}...")
                        if labels:
                            print(f"      Labels: {', '.join(labels)}")
                        print()
            return 0
        else:
            # Import test cases
            clear_data = not args.no_clear
            success = importer.import_testcases(excel_file, args.sheet, clear_data)
            
            if success:
                importer.print_summary()
                print("\n🎉 Import completed successfully!")
                return 0
            else:
                print("\n💥 Import failed!")
                return 1
    
    except KeyboardInterrupt:
        print("\n⏹️  Import cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1
    finally:
        importer.close()

if __name__ == "__main__":
    sys.exit(main())
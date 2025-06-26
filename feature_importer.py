#!/usr/bin/env python3
"""
EC SONiC Feature Importer
Reads EC SONiC Feature Excel files and imports data to ESTS_Dev database
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

class FeatureImporter:
    """Import EC SONiC features from Excel to database"""
    
    def __init__(self):
        self.db_conn = None
        self.stats = {
            'features_processed': 0,
            'features_inserted': 0,
            'features_updated': 0,
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
    
    def find_latest_feature_file(self, specific_date=None):
        """Find the latest or specific EC SONiC feature file"""
        data_dir = "data"
        
        if specific_date:
            # Look for specific date file
            filename = f"EC_SONiC_Feature.{specific_date}.xlsx"
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                return filepath
            else:
                print(f"❌ File not found: {filepath}")
                return None
        
        # Find latest file
        if not os.path.exists(data_dir):
            print(f"❌ Data directory not found: {data_dir}")
            return None
        
        feature_files = []
        for filename in os.listdir(data_dir):
            if filename.startswith("EC_SONiC_Feature.") and filename.endswith(".xlsx"):
                # Extract date from filename
                date_match = re.search(r'EC_SONiC_Feature\.(\d{8})\.xlsx', filename)
                if date_match:
                    feature_files.append((filename, date_match.group(1)))
        
        if not feature_files:
            print("❌ No EC SONiC Feature files found")
            return None
        
        # Sort by date and get latest
        feature_files.sort(key=lambda x: x[1], reverse=True)
        latest_file = os.path.join(data_dir, feature_files[0][0])
        
        print(f"📅 Using file: {latest_file} (date: {feature_files[0][1]})")
        return latest_file
    
    def read_excel_data(self, filepath):
        """Read and validate Excel data"""
        try:
            print(f"📖 Reading Excel file: {filepath}")
            
            # Read the feature_map sheet
            df = pd.read_excel(filepath, sheet_name='feature_map')
            print(f"📊 Loaded {len(df)} rows from feature_map sheet")
            
            # Validate required columns
            required_columns = ['Feature_Key', 'Category', 'Feature N1']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return None
            
            # Show column mapping
            print("📋 Column mapping:")
            column_mapping = {
                'Feature_Key': 'feature_key',
                'Category': 'category', 
                'Feature N1': 'feature_n1',
                'EC_SONiC_2111': 'ec_sonic_2111',
                'EC_SONiC_2211': 'ec_sonic_2211',
                'EC_202211_Fabric': 'ec_202211_fabric',
                'EC SONiC 2311.X': 'ec_sonic_2311_x',
                'EC SONiC 2311.N': 'ec_sonic_2311_n',
                'VS_202311': 'vs_202311',
                'VS_202311_Fabric': 'vs_202311_fabric',
                'EC Proprietary': 'ec_proprietary',
                'Component': 'component',
                'Labels': 'labels'
            }
            
            for excel_col, db_col in column_mapping.items():
                status = "✅" if excel_col in df.columns else "❌"
                print(f"   {status} {excel_col} → {db_col}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            return None
    
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
    
    def map_support_value(self, value):
        """Map O/X/D values to meaningful text"""
        if not value:
            return None
        
        # Clean the value first
        cleaned = str(value).strip().upper()
        
        # Map the values
        value_mapping = {
            'O': 'Support',
            'X': 'Not Support', 
            'D': 'Under Development'
        }
        
        return value_mapping.get(cleaned, cleaned)  # Return original if not in mapping
    
    def generate_feature_key(self, category, feature_name):
        """Generate feature key if missing"""
        if not category or not feature_name:
            return None
        
        # Create key from category and feature name
        key = f"{category}_{feature_name}"
        # Clean up the key - remove special characters, spaces
        key = re.sub(r'[^\w\-]', '_', key)
        key = re.sub(r'_+', '_', key)  # Replace multiple underscores with single
        key = key.strip('_')  # Remove leading/trailing underscores
        
        return key.upper()
    
    def process_feature_row(self, row):
        """Process a single feature row and return normalized data"""
        # Get and clean feature_key
        feature_key = self.clean_value(row.get('Feature_Key'))
        category = self.clean_value(row.get('Category'))
        feature_n1 = self.clean_value(row.get('Feature N1'))
        
        # Generate feature_key if missing
        if not feature_key:
            feature_key = self.generate_feature_key(category, feature_n1)
            if not feature_key:
                print(f"⚠️  Skipping row: Cannot generate feature_key from category='{category}', feature_n1='{feature_n1}'")
                return None
        
        # Prepare feature data (map O/X/D values for support status fields)
        feature_data = {
            'feature_key': feature_key,
            'category': category,
            'feature_n1': feature_n1,
            'ec_sonic_2111': self.map_support_value(row.get('EC_SONiC_2111')),
            'ec_sonic_2211': self.map_support_value(row.get('EC_SONiC_2211')),
            'ec_202211_fabric': self.map_support_value(row.get('EC_202211_Fabric')),
            'ec_sonic_2311_x': self.map_support_value(row.get('EC SONiC 2311.X')),
            'ec_sonic_2311_n': self.map_support_value(row.get('EC SONiC 2311.N')),
            'vs_202311': self.map_support_value(row.get('VS_202311')),
            'vs_202311_fabric': self.map_support_value(row.get('VS_202311_Fabric')),
            'ec_proprietary': self.map_support_value(row.get('EC Proprietary')),
            'component': self.clean_value(row.get('Component'))
        }
        
        # Process labels (comma-separated)
        labels_raw = self.clean_value(row.get('Labels'))
        labels = []
        if labels_raw:
            # Split by comma and clean each label
            for label in labels_raw.split(','):
                cleaned_label = label.strip()
                if cleaned_label:
                    labels.append(cleaned_label)
        
        return feature_data, labels
    
    def insert_feature(self, feature_data):
        """Insert feature in s_feature_map table"""
        try:
            cursor = self.db_conn.cursor()
            
            # Insert new feature (since we cleared all data first)
            insert_sql = """
            INSERT INTO s_feature_map (
                feature_key, category, feature_n1,
                ec_sonic_2111, ec_sonic_2211, ec_202211_fabric,
                ec_sonic_2311_x, ec_sonic_2311_n,
                vs_202311, vs_202311_fabric,
                ec_proprietary, component, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            
            cursor.execute(insert_sql, (
                feature_data['feature_key'],
                feature_data['category'],
                feature_data['feature_n1'],
                feature_data['ec_sonic_2111'],
                feature_data['ec_sonic_2211'],
                feature_data['ec_202211_fabric'],
                feature_data['ec_sonic_2311_x'],
                feature_data['ec_sonic_2311_n'],
                feature_data['vs_202311'],
                feature_data['vs_202311_fabric'],
                feature_data['ec_proprietary'],
                feature_data['component']
            ))
            
            self.stats['features_inserted'] += 1
            cursor.close()
            print(f"✅ Feature inserted: {feature_data['feature_key']}")
            return True
            
        except Exception as e:
            self.stats['errors'].append(f"Feature {feature_data['feature_key']}: {e}")
            print(f"❌ Error inserting feature {feature_data['feature_key']}: {e}")
            return False
    
    def insert_feature_labels(self, feature_key, labels):
        """Insert feature labels into s_feature_label table"""
        if not labels:
            return
        
        try:
            cursor = self.db_conn.cursor()
            
            # Insert labels (no need to delete since we cleared all data first)
            for label in labels:
                cursor.execute("""
                    INSERT INTO s_feature_label (feature_key, label, created_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                """, (feature_key, label))
                
                self.stats['labels_inserted'] += 1
            
            cursor.close()
            print(f"✅ Labels inserted for {feature_key}: {', '.join(labels)}")
            
        except Exception as e:
            self.stats['errors'].append(f"Labels for {feature_key}: {e}")
            print(f"❌ Error inserting labels for {feature_key}: {e}")
    
    def clear_existing_data(self):
        """Clear existing data from feature tables"""
        try:
            cursor = self.db_conn.cursor()
            
            print("🧹 Clearing existing data...")
            
            # Clear s_feature_label first (due to foreign key constraint)
            cursor.execute("SELECT COUNT(*) FROM s_feature_label")
            label_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM s_feature_label")
            print(f"   ✅ Cleared {label_count} records from s_feature_label")
            
            # Clear s_feature_map
            cursor.execute("SELECT COUNT(*) FROM s_feature_map")
            feature_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM s_feature_map")
            print(f"   ✅ Cleared {feature_count} records from s_feature_map")
            
            # Commit the deletions
            self.db_conn.commit()
            print("   ✅ Old data cleared successfully")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Error clearing data: {e}")
            self.db_conn.rollback()
            return False

    def import_features(self, filepath, clear_data=True):
        """Main import process"""
        print("🚀 Starting EC SONiC Feature import process")
        print("="*60)
        
        # Clear existing data first (if requested)
        if clear_data:
            if not self.clear_existing_data():
                print("❌ Failed to clear existing data. Aborting import.")
                return False
        else:
            print("⚠️  Skipping data clearing - will append to existing data")
        
        # Read Excel data
        df = self.read_excel_data(filepath)
        if df is None:
            return False
        
        # Process each row
        print(f"\n📝 Processing {len(df)} feature rows...")
        
        for index, row in df.iterrows():
            self.stats['features_processed'] += 1
            
            # Process the row
            result = self.process_feature_row(row)
            if result is None:
                continue
            
            feature_data, labels = result
            
            # Insert feature
            if self.insert_feature(feature_data):
                # Insert labels
                if labels:
                    self.stats['labels_processed'] += len(labels)
                    self.insert_feature_labels(feature_data['feature_key'], labels)
        
        # Commit all changes
        self.db_conn.commit()
        print("\n✅ All changes committed to database")
        
        return True
    
    def print_summary(self):
        """Print import summary"""
        print("\n📊 Import Summary")
        print("="*60)
        print(f"📝 Features processed: {self.stats['features_processed']}")
        print(f"➕ Features inserted: {self.stats['features_inserted']}")
        print(f"🔄 Features updated: {self.stats['features_updated']}")
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
    
    parser = argparse.ArgumentParser(description='Import EC SONiC features from Excel to database')
    parser.add_argument('--date', help='Specific date in YYYYMMDD format (e.g., 20250626)')
    parser.add_argument('--file', help='Specific Excel file path')
    parser.add_argument('--dry-run', action='store_true', help='Preview data without importing')
    parser.add_argument('--no-clear', action='store_true', help='Do not clear existing data before import')
    
    args = parser.parse_args()
    
    # Create importer
    importer = FeatureImporter()
    
    try:
        # Connect to database (skip in dry-run mode)
        if not args.dry_run and not importer.connect_database():
            return 1
        
        # Find Excel file
        if args.file:
            excel_file = args.file
        else:
            excel_file = importer.find_latest_feature_file(args.date)
        
        if not excel_file:
            print("❌ No Excel file found")
            return 1
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No data will be imported")
            df = importer.read_excel_data(excel_file)
            if df is not None:
                print(f"✅ Would process {len(df)} feature rows")
                
                # Preview first few rows
                print("\n📋 Preview of first 3 rows:")
                for index, row in df.head(3).iterrows():
                    result = importer.process_feature_row(row)
                    if result:
                        feature_data, labels = result
                        print(f"   Row {index+1}: {feature_data['feature_key']} ({len(labels)} labels)")
                        print(f"      Category: {feature_data['category']}")
                        print(f"      Feature: {feature_data['feature_n1']}")
                        print(f"      SONiC 2111: {feature_data['ec_sonic_2111']}")
                        print(f"      SONiC 2211: {feature_data['ec_sonic_2211']}")
                        print(f"      SONiC 2311.X: {feature_data['ec_sonic_2311_x']}")
                        if labels:
                            print(f"      Labels: {', '.join(labels)}")
                        print()
            return 0
        else:
            # Import features
            clear_data = not args.no_clear
            success = importer.import_features(excel_file, clear_data)
            
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
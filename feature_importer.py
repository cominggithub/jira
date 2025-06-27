#!/usr/bin/env python3
"""
SQLAlchemy-based EC SONiC Feature Importer
Reads EC SONiC Feature Excel files and imports data using SQLAlchemy ORM
"""
import os
import sys
import pandas as pd
import re
import click
from datetime import datetime
from dotenv import load_dotenv
from models.base import db
from models import FeatureMap, FeatureLabel
from config.base import config

# Load environment variables
load_dotenv()


class SQLAlchemyFeatureImporter:
    """Import EC SONiC features from Excel using SQLAlchemy ORM"""
    
    def __init__(self, env='development'):
        self.env = env
        self.app = None
        self.stats = {
            'features_processed': 0,
            'features_inserted': 0,
            'features_updated': 0,
            'labels_processed': 0,
            'labels_inserted': 0,
            'errors': []
        }
    
    def create_app(self):
        """Create Flask app for database operations"""
        from flask import Flask
        
        app = Flask(__name__)
        
        # Set configuration
        app.config.from_object(config[self.env])
        
        # Get database URI
        db_config = config[self.env]()
        app.config['SQLALCHEMY_DATABASE_URI'] = db_config.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions
        db.init_app(app)
        
        self.app = app
        return app
    
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
                click.echo(f"❌ File not found: {filepath}")
                return None
        
        # Find latest file
        if not os.path.exists(data_dir):
            click.echo(f"❌ Data directory not found: {data_dir}")
            return None
        
        feature_files = []
        for filename in os.listdir(data_dir):
            if filename.startswith("EC_SONiC_Feature.") and filename.endswith(".xlsx"):
                # Extract date from filename
                date_match = re.search(r'EC_SONiC_Feature\.(\d{8})\.xlsx', filename)
                if date_match:
                    feature_files.append((filename, date_match.group(1)))
        
        if not feature_files:
            click.echo("❌ No EC SONiC Feature files found")
            return None
        
        # Sort by date and get latest
        feature_files.sort(key=lambda x: x[1], reverse=True)
        latest_file = os.path.join(data_dir, feature_files[0][0])
        
        click.echo(f"📅 Using file: {latest_file} (date: {feature_files[0][1]})")
        return latest_file
    
    def read_excel_data(self, filepath):
        """Read and validate Excel data"""
        try:
            click.echo(f"📖 Reading Excel file: {filepath}")
            
            # Read the feature_map sheet
            df = pd.read_excel(filepath, sheet_name='feature_map')
            click.echo(f"📊 Loaded {len(df)} rows from feature_map sheet")
            
            # Validate required columns
            required_columns = ['Feature_Key', 'Category', 'Feature N1']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                click.echo(f"❌ Missing required columns: {missing_columns}")
                return None
            
            return df
            
        except Exception as e:
            click.echo(f"❌ Error reading Excel file: {e}")
            return None
    
    def clean_value(self, value):
        """Clean and normalize cell values"""
        if pd.isna(value):
            return None
        
        # Convert to string and strip whitespace
        cleaned = str(value).strip()
        
        # Return None for empty strings and NAN values
        if cleaned == '' or cleaned.upper() in ['NAN', 'NONE', 'NULL', 'N/A']:
            return None
            
        return cleaned
    
    def map_support_value(self, value):
        """Map O/X/D values to meaningful text"""
        # Clean the value first
        cleaned_value = self.clean_value(value)
        if not cleaned_value:
            return None
        
        # Convert to uppercase for mapping
        upper_value = cleaned_value.upper()
        
        # Map the values
        value_mapping = {
            'O': 'Support',
            'X': 'Not Support', 
            'D': 'Under Development'
        }
        
        return value_mapping.get(upper_value, cleaned_value)
    
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
                click.echo(f"⚠️  Skipping row: Cannot generate feature_key from category='{category}', feature_n1='{feature_n1}'")
                return None
        
        # Prepare feature data
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
            'ec_proprietary': self.clean_value(row.get('EC Proprietary')),
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
    
    def clear_existing_data(self):
        """Clear existing data from feature tables"""
        try:
            click.echo("🧹 Clearing existing data...")
            
            # Get counts before deletion
            label_count = FeatureLabel.query.count()
            feature_count = FeatureMap.query.count()
            
            # Delete all labels first (due to foreign key constraint)
            FeatureLabel.query.delete()
            click.echo(f"   ✅ Cleared {label_count} records from s_feature_label")
            
            # Delete all features
            FeatureMap.query.delete()
            click.echo(f"   ✅ Cleared {feature_count} records from s_feature_map")
            
            # Commit the deletions
            db.session.commit()
            click.echo("   ✅ Old data cleared successfully")
            
            return True
            
        except Exception as e:
            click.echo(f"   ❌ Error clearing data: {e}")
            db.session.rollback()
            return False
    
    def import_features(self, filepath, clear_data=True):
        """Main import process"""
        click.echo("🚀 Starting SQLAlchemy EC SONiC Feature import process")
        click.echo("=" * 60)
        
        # Create app and push context
        app = self.create_app()
        
        with app.app_context():
            # Clear existing data first (if requested)
            if clear_data:
                if not self.clear_existing_data():
                    click.echo("❌ Failed to clear existing data. Aborting import.")
                    return False
            else:
                click.echo("⚠️  Skipping data clearing - will append to existing data")
            
            # Read Excel data
            df = self.read_excel_data(filepath)
            if df is None:
                return False
            
            # Process each row
            click.echo(f"\n📝 Processing {len(df)} feature rows...")
            
            for index, row in df.iterrows():
                self.stats['features_processed'] += 1
                
                # Process the row
                result = self.process_feature_row(row)
                if result is None:
                    continue
                
                feature_data, labels = result
                
                try:
                    # Create feature object
                    feature = FeatureMap(**feature_data)
                    db.session.add(feature)
                    db.session.flush()  # Get the ID
                    
                    self.stats['features_inserted'] += 1
                    
                    # Add labels
                    for label in labels:
                        feature_label = FeatureLabel(
                            feature_key=feature.feature_key,
                            label=label
                        )
                        db.session.add(feature_label)
                        self.stats['labels_inserted'] += 1
                    
                    self.stats['labels_processed'] += len(labels)
                    
                    click.echo(f"✅ Feature processed: {feature.feature_key} ({len(labels)} labels)")
                    
                except Exception as e:
                    self.stats['errors'].append(f"Feature {feature_data['feature_key']}: {e}")
                    click.echo(f"❌ Error processing feature {feature_data['feature_key']}: {e}")
                    db.session.rollback()
                    continue
            
            # Commit all changes
            try:
                db.session.commit()
                click.echo("\n✅ All changes committed to database")
                return True
            except Exception as e:
                click.echo(f"\n❌ Error committing to database: {e}")
                db.session.rollback()
                return False
    
    def print_summary(self):
        """Print import summary"""
        click.echo("\n📊 Import Summary")
        click.echo("=" * 60)
        click.echo(f"📝 Features processed: {self.stats['features_processed']}")
        click.echo(f"➕ Features inserted: {self.stats['features_inserted']}")
        click.echo(f"🔄 Features updated: {self.stats['features_updated']}")
        click.echo(f"🏷️  Labels processed: {self.stats['labels_processed']}")
        click.echo(f"➕ Labels inserted: {self.stats['labels_inserted']}")
        click.echo(f"❌ Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            click.echo(f"\n⚠️  Error Details:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                click.echo(f"   • {error}")
            if len(self.stats['errors']) > 10:
                click.echo(f"   ... and {len(self.stats['errors']) - 10} more errors")


@click.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
@click.option('--date', help='Specific date in YYYYMMDD format (e.g., 20250626)')
@click.option('--file', help='Specific Excel file path')
@click.option('--dry-run', is_flag=True, help='Preview data without importing')
@click.option('--no-clear', is_flag=True, help='Do not clear existing data before import')
def main(env, date, file, dry_run, no_clear):
    """Import EC SONiC features from Excel to database using SQLAlchemy"""
    
    # Create importer
    importer = SQLAlchemyFeatureImporter(env)
    
    try:
        # Find Excel file
        if file:
            excel_file = file
        else:
            excel_file = importer.find_latest_feature_file(date)
        
        if not excel_file:
            click.echo("❌ No Excel file found")
            return 1
        
        if dry_run:
            click.echo("🔍 DRY RUN MODE - No data will be imported")
            df = importer.read_excel_data(excel_file)
            if df is not None:
                click.echo(f"✅ Would process {len(df)} feature rows")
                
                # Preview first few rows
                click.echo("\n📋 Preview of first 3 rows:")
                for index, row in df.head(3).iterrows():
                    result = importer.process_feature_row(row)
                    if result:
                        feature_data, labels = result
                        click.echo(f"   Row {index+1}: {feature_data['feature_key']} ({len(labels)} labels)")
                        click.echo(f"      Category: {feature_data['category']}")
                        click.echo(f"      Feature: {feature_data['feature_n1']}")
                        click.echo(f"      SONiC 2111: {feature_data['ec_sonic_2111']}")
                        click.echo(f"      SONiC 2211: {feature_data['ec_sonic_2211']}")
                        click.echo(f"      SONiC 2311.X: {feature_data['ec_sonic_2311_x']}")
                        if labels:
                            click.echo(f"      Labels: {', '.join(labels)}")
                        click.echo()
            return 0
        else:
            # Import features
            clear_data = not no_clear
            success = importer.import_features(excel_file, clear_data)
            
            if success:
                importer.print_summary()
                click.echo("\n🎉 Import completed successfully!")
                return 0
            else:
                click.echo("\n💥 Import failed!")
                return 1
    
    except KeyboardInterrupt:
        click.echo("\n⏹️  Import cancelled by user")
        return 1
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    main()
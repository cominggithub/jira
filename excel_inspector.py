#!/usr/bin/env python3
"""
Excel File Inspector - Analyze the structure of EC SONiC Feature files
"""
import pandas as pd
import sys
import os
from datetime import datetime

def inspect_excel_file(filepath):
    """Inspect Excel file structure"""
    print(f"📁 Inspecting file: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(filepath)
        print(f"📊 Sheets found: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n🔍 Sheet: '{sheet_name}'")
            
            # Read first few rows to understand structure
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=5)
            print(f"   📏 Shape: {df.shape} (first 5 rows)")
            print(f"   📋 Columns: {list(df.columns)}")
            
            # Show sample data
            print("   📄 Sample data:")
            for i, row in df.iterrows():
                print(f"      Row {i+1}: {dict(row.head(3))}")  # Show first 3 columns
                if i >= 2:  # Show max 3 rows
                    break
            
            print("   " + "="*50)
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def find_latest_feature_file():
    """Find the latest EC SONiC feature file"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return None
    
    feature_files = []
    for filename in os.listdir(data_dir):
        if filename.startswith("EC_SONiC_Feature.") and filename.endswith(".xlsx"):
            feature_files.append(filename)
    
    if not feature_files:
        print("❌ No EC SONiC Feature files found")
        return None
    
    # Sort by date (assuming YYYYMMDD format)
    feature_files.sort(reverse=True)
    latest_file = os.path.join(data_dir, feature_files[0])
    
    print(f"📅 Latest file: {latest_file}")
    print(f"📄 All files found: {feature_files}")
    
    return latest_file

if __name__ == "__main__":
    print("🔍 Excel File Inspector for EC SONiC Feature Files")
    print("="*60)
    
    # Find and inspect the latest file
    latest_file = find_latest_feature_file()
    if latest_file:
        inspect_excel_file(latest_file)
    else:
        print("❌ No files to inspect")
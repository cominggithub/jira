#!/usr/bin/env python3
"""
ESTS Test Case File Inspector - Analyze the structure of ESTS Test Case Excel files
"""
import pandas as pd
import sys
import os
from datetime import datetime

def inspect_testcase_file(filepath):
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
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=10)
            print(f"   📏 Shape: {df.shape} (first 10 rows)")
            print(f"   📋 Columns: {list(df.columns)}")
            
            # Show sample data
            print("   📄 Sample data:")
            for i, row in df.iterrows():
                row_data = {}
                for j, (col, val) in enumerate(row.items()):
                    if j < 5:  # Show first 5 columns
                        row_data[col] = val
                    else:
                        break
                print(f"      Row {i+1}: {row_data}")
                if i >= 3:  # Show max 4 rows
                    break
            
            print("   " + "="*50)
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def find_testcase_files():
    """Find ESTS test case files"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return []
    
    testcase_files = []
    for filename in os.listdir(data_dir):
        if "test_case" in filename.lower() and filename.endswith(".xlsx"):
            testcase_files.append(filename)
    
    if not testcase_files:
        print("❌ No test case files found")
        return []
    
    print(f"📄 Test case files found: {testcase_files}")
    return [os.path.join(data_dir, f) for f in testcase_files]

if __name__ == "__main__":
    print("🔍 ESTS Test Case File Inspector")
    print("="*60)
    
    # Find and inspect test case files
    testcase_files = find_testcase_files()
    for filepath in testcase_files:
        inspect_testcase_file(filepath)
        print("\n" + "="*60)
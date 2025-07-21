#!/usr/bin/env python3
"""
Find and identify feature support tables that contain Category, Feature Name, Sub item columns
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_table_structure(excel_file):
    """Analyze all tables to find feature support tables"""
    try:
        xl_file = pd.ExcelFile(excel_file)
        
        print(f"Analyzing tables in: {excel_file}")
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Skip metadata sheet, process table sheets
        table_sheets = [sheet for sheet in xl_file.sheet_names if sheet.startswith('Table_')]
        
        feature_support_tables = []
        
        for sheet_name in table_sheets:
            print(f"\n{'='*60}")
            print(f"Analyzing {sheet_name}")
            print(f"{'='*60}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Check if this looks like a feature support table
            columns = [str(col).lower() for col in df.columns]
            
            # Look for key indicators of feature support tables
            has_category = any('category' in col for col in columns)
            has_feature = any('feature' in col for col in columns)
            has_subitem = any('sub' in col and 'item' in col for col in columns)
            
            # Also check for device names in columns (AS####-##X pattern)
            import re
            has_device_columns = any(re.search(r'AS\d{4}-\d{2}[A-Z]', str(col)) for col in df.columns)
            
            print(f"Has 'category': {has_category}")
            print(f"Has 'feature': {has_feature}")
            print(f"Has 'sub item': {has_subitem}")
            print(f"Has device columns: {has_device_columns}")
            
            # Show first few rows
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            
            # Determine if this is a feature support table
            is_feature_support = (has_category and has_feature) or has_device_columns
            
            if is_feature_support:
                print(f"\n*** {sheet_name} identified as FEATURE SUPPORT TABLE ***")
                feature_support_tables.append(sheet_name)
            else:
                print(f"\n{sheet_name} is NOT a feature support table")
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: Found {len(feature_support_tables)} feature support tables:")
        for table in feature_support_tables:
            print(f"  - {table}")
        
        return feature_support_tables
        
    except Exception as e:
        print(f"Error analyzing tables: {e}")
        return []

def main():
    excel_file = "output/20250714/SONiC/202111_11_feature_list_tables.xlsx"
    
    if not Path(excel_file).exists():
        print(f"Excel file not found: {excel_file}")
        return
    
    feature_support_tables = analyze_table_structure(excel_file)
    
    if feature_support_tables:
        print(f"\nNext step: Extract and merge these {len(feature_support_tables)} feature support tables")
    else:
        print("\nNo feature support tables found with the expected structure")

if __name__ == "__main__":
    main()
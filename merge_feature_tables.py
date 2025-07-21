#!/usr/bin/env python3
"""
Merge feature support tables from 202111.11 into one big table
Replace column headers with actual device names from the database
"""

import pandas as pd
import sys
import re
from pathlib import Path

def load_device_mapping():
    """Load device mapping from EC switches data"""
    try:
        df = pd.read_excel('data/ec switches.xlsx', sheet_name='product line')
        # Create mapping from platform names to clean device names
        device_mapping = {}
        for _, row in df.iterrows():
            platform = row['Platform']
            # Extract the main device name (before any spaces or additional codes)
            clean_name = platform.split()[0] if pd.notna(platform) else platform
            device_mapping[platform] = clean_name
            
        print(f"Loaded {len(device_mapping)} device mappings")
        return device_mapping
    except Exception as e:
        print(f"Error loading device mapping: {e}")
        return {}

def clean_column_name(col_name, device_mapping):
    """Clean column name and map to device name if possible"""
    if pd.isna(col_name) or col_name == '':
        return col_name
    
    col_str = str(col_name).strip()
    
    # Try to find exact match first
    if col_str in device_mapping:
        return device_mapping[col_str]
    
    # Try partial matches for device names
    for platform, device in device_mapping.items():
        if col_str in platform or platform in col_str:
            return device
    
    # If it looks like a device name pattern (AS####-##X), keep as is
    if re.match(r'^AS\d{4}-\d{2}[A-Z]$', col_str):
        return col_str
    
    return col_str

def merge_feature_tables(excel_file):
    """Merge all feature tables into one big table"""
    try:
        # Load device mapping
        device_mapping = load_device_mapping()
        
        # Read the Excel file
        xl_file = pd.ExcelFile(excel_file)
        
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Skip metadata sheet, process table sheets
        table_sheets = [sheet for sheet in xl_file.sheet_names if sheet.startswith('Table_')]
        
        if not table_sheets:
            print("No table sheets found")
            return None
            
        merged_data = []
        
        for sheet_name in table_sheets:
            print(f"\nProcessing {sheet_name}...")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            print(f"  Original shape: {df.shape}")
            print(f"  Original columns: {list(df.columns)}")
            
            # Clean and rename columns
            new_columns = []
            for col in df.columns:
                clean_col = clean_column_name(col, device_mapping)
                new_columns.append(clean_col)
            
            df.columns = new_columns
            print(f"  Cleaned columns: {list(df.columns)}")
            
            # Add table source information
            df['Source_Table'] = sheet_name
            
            # Append to merged data
            merged_data.append(df)
        
        if not merged_data:
            print("No data to merge")
            return None
            
        # Concatenate all tables
        print(f"\nMerging {len(merged_data)} tables...")
        merged_df = pd.concat(merged_data, ignore_index=True, sort=False)
        
        print(f"Final merged table shape: {merged_df.shape}")
        print(f"Final columns: {list(merged_df.columns)}")
        
        return merged_df
        
    except Exception as e:
        print(f"Error merging tables: {e}")
        return None

def save_merged_table(merged_df, output_file):
    """Save merged table to Excel"""
    try:
        # Create output directory
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            merged_df.to_excel(writer, sheet_name='Merged_Feature_Support', index=False)
            
            # Add summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Rows', 'Total Columns', 'Source Tables', 'Generated At'],
                'Value': [
                    len(merged_df),
                    len(merged_df.columns),
                    len(merged_df['Source_Table'].unique()) if 'Source_Table' in merged_df.columns else 'N/A',
                    pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Merged table saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error saving merged table: {e}")
        return False

def main():
    excel_file = "output/20250714/SONiC/202111_11_feature_list_tables.xlsx"
    output_file = "output/20250714/SONiC/202111_11_merged_feature_support.xlsx"
    
    print("Merging feature support tables from 202111.11...")
    
    merged_df = merge_feature_tables(excel_file)
    
    if merged_df is not None:
        success = save_merged_table(merged_df, output_file)
        if success:
            print("Feature table merging completed successfully!")
            
            # Show sample of the merged data
            print(f"\nSample of merged data (first 5 rows):")
            print(merged_df.head().to_string())
            
        else:
            print("Failed to save merged table")
    else:
        print("Failed to merge tables")

if __name__ == "__main__":
    main()
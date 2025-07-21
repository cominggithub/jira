#!/usr/bin/env python3
"""
Read EC switches Excel file and display device information
"""

import pandas as pd
import sys

def read_ec_switches(file_path):
    """Read and display EC switches data"""
    try:
        # First, let's see what sheets are available
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Read each sheet
        for sheet_name in xl_file.sheet_names:
            print(f"\n{'='*60}")
            print(f"Sheet: {sheet_name}")
            print(f"{'='*60}")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape} (rows, columns)")
            print(f"Columns: {list(df.columns)}")
            
            # Display first few rows
            print("\nFirst 10 rows:")
            print(df.head(10).to_string())
            
            # If there are device/model columns, show unique values
            potential_device_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['device', 'model', 'switch', 'platform', 'name', 'product'])]
            
            if potential_device_cols:
                print(f"\nPotential device columns: {potential_device_cols}")
                for col in potential_device_cols:
                    unique_values = df[col].dropna().unique()
                    print(f"\nUnique values in '{col}' ({len(unique_values)} total):")
                    for val in sorted(unique_values):
                        print(f"  - {val}")
            
            print("\n" + "-"*60)
        
        return True
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

if __name__ == "__main__":
    file_path = "data/ec switches.xlsx"
    read_ec_switches(file_path)
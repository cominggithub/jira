#!/usr/bin/env python3
"""
Quick script to find the URL for a specific version from the Excel file
"""

import pandas as pd
import sys

def find_version_url(excel_file, target_version):
    """Find URL for a specific version in the Excel file"""
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file, sheet_name='SONiC Release Notes')
        
        # Look for the target version
        matching_rows = df[df['Version'] == target_version]
        
        if matching_rows.empty:
            print(f"Version {target_version} not found in the Excel file")
            return None
        
        # Get the first match
        url = matching_rows.iloc[0]['URL']
        title = matching_rows.iloc[0]['Title']
        
        print(f"Found version {target_version}:")
        print(f"Title: {title}")
        print(f"URL: {url}")
        
        return url
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    excel_file = "output/20250714/SONiC/sonic_actual_release_versions.xlsx"
    target_version = "202111.11"
    
    url = find_version_url(excel_file, target_version)
    if url:
        print(f"\nURL for {target_version}: {url}")
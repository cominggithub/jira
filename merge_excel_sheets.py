

import pandas as pd
import sys

def merge_and_verify_sheets(file_path, sheet1_name, sheet2_name, output_sheet_name, key_columns):
    """
    Merges two sheets and verifies the integrity of the merged data.
    """
    try:
        # Read the original sheets
        df1_orig = pd.read_excel(file_path, sheet_name=sheet1_name, header=0)
        df2_orig = pd.read_excel(file_path, sheet_name=sheet2_name, header=0)

        # --- Data Cleaning and Preparation ---
        df1 = df1_orig.copy()
        df2 = df2_orig.copy()

        # Discovered from inspect_headers.py that this rename is not needed.
        # df2.rename(columns={'Sub item': 'Sub Item'}, inplace=True)

        print("Cleaning key columns (stripping whitespace)...")
        for col in key_columns:
            if col in df1.columns:
                df1[col] = df1[col].astype(str).str.strip()
            if col in df2.columns:
                df2[col] = df2[col].astype(str).str.strip()

        # --- Deduplication ---
        df1.drop_duplicates(subset=key_columns, keep='first', inplace=True)
        df2.drop_duplicates(subset=key_columns, keep='first', inplace=True)

        # --- Merge ---
        merged_df = pd.merge(df1, df2, on=key_columns, how='outer')

        # --- Save Merged Sheet ---
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            merged_df.to_excel(writer, sheet_name=output_sheet_name, index=False)

        print(f"Successfully merged sheets into '{output_sheet_name}'.")

        # --- Verification Step ---
        print("\n--- Starting Verification ---")
        verification_passed = True
        mismatches = []

        # Correct column names from inspect_headers.py
        col1 = '202111.11 AS4630-54TE'
        col2 = '202311.3 AS4630-54TE'

        df1_lookup = df1.set_index(key_columns)[col1].to_dict()
        df2_lookup = df2.set_index(key_columns)[col2].to_dict()

        for index, row in merged_df.iterrows():
            key = tuple(row[k] for k in key_columns)

            if key in df1_lookup:
                original_val = df1_lookup[key]
                merged_val = row[col1]
                if str(original_val) != str(merged_val):
                    mismatches.append(f"Row {index+2} (Key: {key}): Mismatch in {col1}. Original: '{original_val}', Merged: '{merged_val}'")
                    verification_passed = False

            if key in df2_lookup:
                original_val = df2_lookup[key]
                merged_val = row[col2]
                if str(original_val) != str(merged_val):
                    mismatches.append(f"Row {index+2} (Key: {key}): Mismatch in {col2}. Original: '{original_val}', Merged: '{merged_val}'")
                    verification_passed = False

        if verification_passed:
            print("✅ Verification successful: All values in checked columns match the original sheets.")
        else:
            print("❌ Verification failed. Mismatches found:")
            for mismatch in mismatches:
                print(f"  - {mismatch}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python merge_excel_sheets.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    sheet1_name = "2111.11"
    sheet2_name = "2311.3"
    output_sheet_name = "c"
    key_columns = ["Category", "Feature Name", "Sub Item"]

    merge_and_verify_sheets(file_path, sheet1_name, sheet2_name, output_sheet_name, key_columns)

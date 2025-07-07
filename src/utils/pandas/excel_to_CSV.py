import os

import pandas as pd

def excel_to_csv(excel_file: str, output_dir: str) -> None:
    """
    Convert an Excel file to CSV format.

    Args:
        excel_file (str): Path to the input Excel file.
        output_dir (str): Directory where the CSV files will be saved.

    Returns:
        None
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read the Excel file
    xls = pd.ExcelFile(excel_file)

    # Iterate through each sheet and save as CSV
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        csv_file_path = os.path.join(output_dir, f"{sheet_name}.csv")
        df.to_csv(csv_file_path, index=False)
        print(f"Converted {sheet_name} to {csv_file_path}")
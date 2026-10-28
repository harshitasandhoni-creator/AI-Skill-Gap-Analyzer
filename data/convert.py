from pathlib import Path

import pandas as pd


# Resolve files relative to this script, so it works from any terminal directory.
data_dir = Path(__file__).resolve().parent
excel_path = data_dir / "main_dataset.xlsx"
csv_path = data_dir / "role_lookup.csv"

excel_file = pd.ExcelFile(excel_path)
print("Available sheets:", excel_file.sheet_names)

df = pd.read_excel(excel_path, sheet_name="Role Lookup")
df.to_csv(csv_path, index=False)

print("CSV created:", csv_path.exists())
print("Rows and columns:", df.shape)
print(df.head())

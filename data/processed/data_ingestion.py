import os
import pandas as pd

# -----------------------------
# Folder Paths
# -----------------------------
data_folder = "data/raw"
report_folder = "reports"

os.makedirs(report_folder, exist_ok=True)

report_file = os.path.join(report_folder, "day1_summary.txt")

# Get all CSV files
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

summary = []

print("=" * 80)
print("DATA INGESTION REPORT")
print("=" * 80)

for file in csv_files:

    file_path = os.path.join(data_folder, file)

    print(f"\nDataset : {file}")

    try:

        df = pd.read_csv(file_path)

        # -----------------------------
        # Basic Information
        # -----------------------------
        print("\nShape")
        print(df.shape)

        print("\nData Types")
        print(df.dtypes)

        print("\nFirst 5 Rows")
        print(df.head())

        # -----------------------------
        # Missing Values
        # -----------------------------
        print("\nMissing Values")

        missing = df.isnull().sum()
        print(missing)

        total_missing = missing.sum()

        # -----------------------------
        # Duplicate Rows
        # -----------------------------
        duplicates = df.duplicated().sum()

        print("\nDuplicate Rows")
        print(duplicates)

        # -----------------------------
        # Data Quality Summary
        # -----------------------------
        summary.append(f"Dataset : {file}")
        summary.append(f"Rows : {df.shape[0]}")
        summary.append(f"Columns : {df.shape[1]}")
        summary.append(f"Total Missing Values : {total_missing}")
        summary.append(f"Duplicate Rows : {duplicates}")
        summary.append("-" * 60)

    except Exception as e:

        print(f"Error reading {file}")
        print(e)

        summary.append(f"{file} : ERROR - {e}")
        summary.append("-" * 60)

print("\n")
print("=" * 80)
print("All datasets loaded successfully.")
print("=" * 80)

# -----------------------------
# Save Report
# -----------------------------
with open(report_file, "w") as f:

    f.write("DAY 1 DATA QUALITY REPORT\n")
    f.write("=" * 80 + "\n\n")

    for line in summary:
        f.write(line + "\n")

print(f"\nReport saved to : {report_file}")
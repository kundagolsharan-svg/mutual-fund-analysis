import os
import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# Create SQLite Database
# ==========================================
engine = create_engine("sqlite:///bluestock_mf.db")

print("=" * 60)
print("Database created successfully.")
print("=" * 60)

# Folder containing cleaned CSV files
processed_folder = "data/processed"

# Get all cleaned CSV files
csv_files = [f for f in os.listdir(processed_folder)
             if f.endswith("_clean.csv")]

# Check if any cleaned files exist
if len(csv_files) == 0:
    print("No cleaned CSV files found!")
    exit()

# Load every cleaned CSV into SQLite
for file in csv_files:

    file_path = os.path.join(processed_folder, file)

    print(f"Loading {file}...")

    df = pd.read_csv(file_path)

    table_name = file.replace("_clean.csv", "").lower()

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    print(f"✓ {table_name} loaded successfully.")

print("\n" + "=" * 60)
print("ALL CLEANED CSV FILES LOADED INTO SQLITE SUCCESSFULLY")
print("=" * 60)
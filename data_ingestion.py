import os
import pandas as pd

# Folder containing CSV files
folder_path = "data/raw"

# Get all CSV files
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

# Read each CSV file
for file in csv_files:
    print("=" * 60)
    print(f"Dataset: {file}")

    file_path = os.path.join(folder_path, file)

    try:
        df = pd.read_csv(file_path)

        print("\nShape:")
        print(df.shape)

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 5 Rows:")
        print(df.head())

    except Exception as e:
        print(f"Error reading {file}: {e}")

print("=" * 60)
print("All datasets loaded successfully.")
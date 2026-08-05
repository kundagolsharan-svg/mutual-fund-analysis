import os
import pandas as pd
import numpy as np

RAW_FOLDER = "data/raw"
PROCESSED_FOLDER = "data/processed"

os.makedirs(PROCESSED_FOLDER, exist_ok=True)

print("="*70)
print("MUTUAL FUND DATA CLEANING")
print("="*70)

summary = []

csv_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]

for file in csv_files:

    print("\nProcessing:", file)

    path = os.path.join(RAW_FOLDER, file)

    try:

        df = pd.read_csv(path)

        original_rows = len(df)

        original_cols = len(df.columns)

        duplicate_rows = df.duplicated().sum()

        missing_before = df.isnull().sum().sum()

        # ----------------------------------------
        # Remove duplicate rows
        # ----------------------------------------

        df = df.drop_duplicates()

        # ----------------------------------------
        # Remove completely empty rows
        # ----------------------------------------

        df = df.dropna(how="all")

        # ----------------------------------------
        # Convert date columns automatically
        # ----------------------------------------

        for col in df.columns:

            col_lower = col.lower()

            if "date" in col_lower:

                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

        # ----------------------------------------
        # Convert numeric columns automatically
        # ----------------------------------------

        for col in df.columns:

            if df[col].dtype == object:

                try:
                    converted = pd.to_numeric(
                        df[col],
                        errors="ignore"
                    )

                    df[col] = converted

                except:
                    pass

        # ----------------------------------------
        # Fill missing numeric values
        # ----------------------------------------

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        for col in numeric_columns:

            df[col] = df[col].fillna(
                df[col].median()
            )

        # ----------------------------------------
        # Fill missing text values
        # ----------------------------------------

        text_columns = df.select_dtypes(
            include="object"
        ).columns

        for col in text_columns:

            df[col] = df[col].fillna("Unknown")

        # ----------------------------------------
        # NAV validation
        # ----------------------------------------

        if "nav" in df.columns:

            df = df[df["nav"] > 0]

        # ----------------------------------------
        # Expense ratio validation
        # ----------------------------------------

        if "expense_ratio" in df.columns:

            df = df[
                (df["expense_ratio"] >= 0.1)
                &
                (df["expense_ratio"] <= 2.5)
            ]

        # ----------------------------------------
        # Standardize transaction type
        # ----------------------------------------

        if "transaction_type" in df.columns:

            df["transaction_type"] = (
                df["transaction_type"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

            replacements = {
                "SIP PURCHASE": "SIP",
                "SYSTEMATIC INVESTMENT": "SIP",
                "PURCHASE": "LUMPSUM",
                "BUY": "LUMPSUM",
                "SELL": "REDEMPTION",
                "REDEEM": "REDEMPTION"
            }

            df["transaction_type"] = (
                df["transaction_type"]
                .replace(replacements)
            )

        # ----------------------------------------
        # Amount validation
        # ----------------------------------------

        if "amount" in df.columns:

            df = df[df["amount"] > 0]

        # ----------------------------------------
        # Sort NAV history
        # ----------------------------------------

        if "amfi_code" in df.columns and "date" in df.columns:

            df = df.sort_values(
                by=["amfi_code", "date"]
            )

            if "nav" in df.columns:

                df["nav"] = (
                    df.groupby("amfi_code")["nav"]
                    .ffill()
                )

        # ----------------------------------------
        # Save cleaned CSV
        # ----------------------------------------

        clean_name = file.replace(
            ".csv",
            "_clean.csv"
        )

        output_path = os.path.join(
            PROCESSED_FOLDER,
            clean_name
        )

        df.to_csv(
            output_path,
            index=False
        )

        summary.append({
            "File": file,
            "Rows Before": original_rows,
            "Rows After": len(df),
            "Columns": original_cols,
            "Duplicates Removed": duplicate_rows,
            "Missing Before": missing_before,
            "Missing After": df.isnull().sum().sum()
        })

        print("✓ Saved:", clean_name)

    except Exception as e:

        print("Error:", e)

# ----------------------------------------
# Summary Report
# ----------------------------------------

summary_df = pd.DataFrame(summary)

summary_file = os.path.join(
    PROCESSED_FOLDER,
    "cleaning_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)

print("\n")
print("="*70)
print("DATA CLEANING COMPLETED")
print("="*70)

print(summary_df)

print("\nCleaning summary saved.")
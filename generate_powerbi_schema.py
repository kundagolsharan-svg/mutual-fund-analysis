import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROC = ROOT / "data" / "processed"
files = sorted(PROC.glob("*_clean.csv"))

if not files:
    raise SystemExit("No cleaned CSV files found in data/processed")

rows = []
for file_path in files:
    df = pd.read_csv(file_path, low_memory=False)
    table_name = file_path.stem
    for col in df.columns:
        dtype = str(df[col].dtype)
        nullable = bool(df[col].isna().any())
        sample = ""
        non_null = df[col].dropna()
        if not non_null.empty:
            sample = str(non_null.iloc[0])
        rows.append({
            "table": table_name,
            "column": col,
            "dtype": dtype,
            "nullable": nullable,
            "sample": sample,
        })

schema_df = pd.DataFrame(rows)
schema_df.to_csv(ROOT / "powerbi_data_model_schema.csv", index=False)

model = {}
for table_name, group in schema_df.groupby("table"):
    model[table_name] = {
        "source_csv": str(PROC / f"{table_name}.csv"),
        "columns": [
            {"name": row[1]["column"], "dtype": row[1]["dtype"], "nullable": row[1]["nullable"]}
            for row in group.iterrows()
        ],
    }

relationships = [
    {
        "from_table": "01_fund_master_clean",
        "from_column": "amfi_code",
        "to_table": "02_nav_history_clean",
        "to_column": "amfi_code",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "01_fund_master_clean",
        "from_column": "amfi_code",
        "to_table": "07_scheme_performance_clean",
        "to_column": "amfi_code",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "01_fund_master_clean",
        "from_column": "amfi_code",
        "to_table": "08_investor_transactions_clean",
        "to_column": "amfi_code",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "01_fund_master_clean",
        "from_column": "amfi_code",
        "to_table": "09_portfolio_holdings_clean",
        "to_column": "amfi_code",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "02_nav_history_clean",
        "to_column": "date",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "10_benchmark_indices_clean",
        "to_column": "date",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "08_investor_transactions_clean",
        "to_column": "transaction_date",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "09_portfolio_holdings_clean",
        "to_column": "portfolio_date",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "03_aum_by_fund_house_clean",
        "to_column": "date",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "04_monthly_sip_inflows_clean",
        "to_column": "month",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "05_category_inflows_clean",
        "to_column": "month",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
    {
        "from_table": "Date",
        "from_column": "Date",
        "to_table": "06_industry_folio_count_clean",
        "to_column": "month",
        "cardinality": "One-to-many",
        "cross_filter_direction": "Single",
    },
]

dataflow = {
    "tables": model,
    "relationships": relationships,
    "notes": [
        "Create a Date table in Power Query or DAX with Date, Year, Quarter, Month, and YearMonth columns.",
        "Do not create fund dimension joins for peer NAV tables because they lack amfi_code.",
        "Use 01_fund_master_clean as the primary fund dimension on amfi_code.",
    ],
}

with open(ROOT / "powerbi_dataflow_schema.json", "w", encoding="utf-8") as f:
    json.dump(dataflow, f, indent=2)

print("Generated powerbi_data_model_schema.csv and powerbi_dataflow_schema.json")

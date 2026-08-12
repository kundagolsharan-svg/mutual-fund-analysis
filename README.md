# Bluestock Mutual Fund Analysis

## Project Overview

This repository contains the Bluestock mutual fund capstone analysis. It includes:
- ETL for mutual fund raw datasets
- Exploratory data analysis (EDA)
- Performance analytics and risk metrics
- A static dashboard artifact
- A final report and presentation deck

The analysis evaluates 40 mutual fund schemes using NAV history, benchmark indices, investor transactions, holdings, SIP inflows, and fund metadata.

## Setup Instructions

1. Create and activate a Python environment.
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   python -m pip install python-pptx reportlab pillow
   ```

## Running the ETL and Analytics Pipeline

From the repository root run:
```bash
python run_pipeline.py
```

This executes:
- `data/processed/data_cleaning.py`
- `data/processed/data_ingestion.py`
- `compute_metrics.py`
- `generate_advanced_analytics_outputs.py`
- `validate_returns.py`
- `generate_eda.py`
- `build_final_report.py`
- `build_presentation.py`

## Generated Deliverables

- `Final_Report.pdf`
- `Bluestock_MF_Presentation.pptx`
- `dashboard/dashboard.html`
- `outputs/plots/` and `outputs/charts/`

## Opening the Dashboard

A static dashboard artifact is available at:
- `dashboard/dashboard.html`

Open this file in a browser to see key charts and summary insight.

## Dataset Descriptions

- `data/raw/01_fund_master.csv`: Fund metadata and scheme details.
- `data/raw/02_nav_history.csv`: Daily NAV values for schemes.
- `data/raw/03_aum_by_fund_house.csv`: AUM by fund house and year.
- `data/raw/04_monthly_sip_inflows.csv`: Monthly SIP inflow amounts.
- `data/raw/05_category_inflows.csv`: Category-level net inflows.
- `data/raw/06_industry_folio_count.csv`: Investor folio counts over time.
- `data/raw/07_scheme_performance.csv`: Scheme performance metrics.
- `data/raw/08_investor_transactions.csv`: Investor-level transaction records.
- `data/raw/09_portfolio_holdings.csv`: Scheme holdings, sector weights, and allocations.
- `data/raw/10_benchmark_indices.csv`: Benchmark index close values (NIFTY50 / NIFTY100).

## Notes

- The pipeline is designed to be repeatable and file-based.
- If a dashboard publishing service is required, export `dashboard/dashboard.html` or upload the visual assets to Power BI or Tableau.

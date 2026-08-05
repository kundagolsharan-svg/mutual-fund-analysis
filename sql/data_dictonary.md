# Data Dictionary

## fact_nav

| Column | Data Type | Description |
|---------|-----------|-------------|
| amfi_code | INTEGER | AMFI Mutual Fund Scheme Code |
| date | DATE | NAV Date |
| nav | REAL | Net Asset Value |

## dim_fund

| Column | Data Type | Description |
|---------|-----------|-------------|
| amfi_code | INTEGER | Unique Scheme Code |
| scheme_name | TEXT | Mutual Fund Name |
| fund_house | TEXT | Fund House |
| category | TEXT | Fund Category |
| sub_category | TEXT | Fund Sub Category |
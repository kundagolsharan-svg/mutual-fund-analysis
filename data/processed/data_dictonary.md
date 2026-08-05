# Mutual Fund Data Dictionary

## fund_master

| Column | Type | Description |
|---------|------|-------------|
| amfi_code | Integer | AMFI Scheme Code |
| scheme_name | Text | Mutual Fund Name |
| fund_house | Text | AMC Name |
| category | Text | Fund Category |
| sub_category | Text | Fund Type |

---

## nav_history

| Column | Type | Description |
|---------|------|-------------|
| amfi_code | Integer | Scheme Code |
| date | Date | NAV Date |
| nav | Float | Net Asset Value |

---

## scheme_performance

| Column | Type | Description |
|---------|------|-------------|
| return_1yr | Float | 1 Year Return |
| return_3yr | Float | 3 Year Return |
| return_5yr | Float | 5 Year Return |
| expense_ratio | Float | Expense Ratio |
from pathlib import Path

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / "data" / "processed"
OUTPUTS_PATH = BASE_PATH / "outputs"
OUTPUTS_PATH.mkdir(exist_ok=True, parents=True)

RETURNS_FILE = BASE_PATH / "daily_returns.csv"
FUND_MASTER_FILE = DATA_PATH / "01_fund_master_clean.csv"
TRANSACTIONS_FILE = DATA_PATH / "08_investor_transactions_clean.csv"
HOLDINGS_FILE = DATA_PATH / "09_portfolio_holdings_clean.csv"

returns = pd.read_csv(RETURNS_FILE, parse_dates=["date"]).set_index("date").sort_index()
returns.columns = returns.columns.astype(str)

fund_master = pd.read_csv(FUND_MASTER_FILE, dtype={"amfi_code": str})
fund_master["amfi_code"] = fund_master["amfi_code"].astype(str)
fund_master["risk_category"] = fund_master["risk_category"].fillna("Unknown")

scheme_names = fund_master.set_index("amfi_code")["scheme_name"].to_dict()
fund_lookup = fund_master.set_index("amfi_code")[['scheme_name', 'risk_category', 'category', 'sub_category']].copy()

# VaR / CVaR
var_level = 0.05
var_results = []
for code in returns.columns:
    series = returns[code].dropna()
    if len(series) < 20:
        continue
    var_value = np.quantile(series, var_level)
    cvar_value = series[series <= var_value].mean()
    var_results.append({
        "amfi_code": code,
        "scheme_name": scheme_names.get(code, "Unknown"),
        "VaR_95": var_value,
        "CVaR_95": cvar_value,
        "observations": len(series),
    })
var_cvar_df = pd.DataFrame(var_results).sort_values("VaR_95")
var_cvar_df.to_csv(OUTPUTS_PATH / "var_cvar_report.csv", index=False)
print(f"Saved {OUTPUTS_PATH / 'var_cvar_report.csv'}")

# Rolling Sharpe
key_funds = [
    "100016",
    "120504",
    "119551",
    "118634",
    "149324",
]
rolling_window = 90
annualization = math.sqrt(252)
rolling_sharpe = returns[key_funds].rolling(rolling_window).mean() / returns[key_funds].rolling(rolling_window).std() * annualization
rolling_sharpe = rolling_sharpe.dropna()

plt.figure(figsize=(14, 7))
for code in key_funds:
    if code in rolling_sharpe:
        label = scheme_names.get(code, code)
        plt.plot(rolling_sharpe.index, rolling_sharpe[code], label=label)
plt.title("Rolling 90-Day Sharpe Ratio for Selected Funds")
plt.xlabel("Date")
plt.ylabel("Rolling 90-Day Sharpe")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUTS_PATH / "rolling_sharpe_chart.png", dpi=200)
plt.close()
print(f"Saved {OUTPUTS_PATH / 'rolling_sharpe_chart.png'}")

# Recommendation table
mean_returns = returns.mean()
std_returns = returns.std()
sharpe_scores = (mean_returns / std_returns) * annualization
sharpe_df = pd.DataFrame({"amfi_code": mean_returns.index.astype(str), "sharpe": sharpe_scores.values})
sharpe_df = sharpe_df.merge(fund_lookup.reset_index(), on="amfi_code", how="left")

risk_map = {
    "Low": ["Low"],
    "Moderate": ["Moderate"],
    "High": ["High", "Very High", "Moderately High"],
}
recommendation_dfs = []
for appetite, categories in risk_map.items():
    mask = sharpe_df["risk_category"].isin(categories)
    top = sharpe_df[mask].sort_values("sharpe", ascending=False).head(3).copy()
    top["risk_appetite"] = appetite
    recommendation_dfs.append(top)
recommendation_table = pd.concat(recommendation_dfs, ignore_index=True)
recommendation_table.to_csv(OUTPUTS_PATH / "recommender_table.csv", index=False)
print(f"Saved {OUTPUTS_PATH / 'recommender_table.csv'}")

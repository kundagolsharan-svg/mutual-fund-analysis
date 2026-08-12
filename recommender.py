from pathlib import Path

import numpy as np
import pandas as pd

BASE_PATH = Path(r"c:\Users\shara\OneDrive\Desktop\mutual fund analysis")
DATA_PATH = BASE_PATH / "data" / "processed"

RETURNS_FILE = BASE_PATH / "daily_returns.csv"
FUND_MASTER_FILE = DATA_PATH / "01_fund_master_clean.csv"


def load_data():
    returns = pd.read_csv(RETURNS_FILE, parse_dates=["date"]).set_index("date").sort_index()
    fund_master = pd.read_csv(FUND_MASTER_FILE, dtype={"amfi_code": str})
    fund_master["amfi_code"] = fund_master["amfi_code"].astype(str)
    fund_master["risk_category"] = fund_master["risk_category"].fillna("Unknown")
    fund_master = fund_master.set_index("amfi_code")
    return returns, fund_master


def compute_sharpe(returns: pd.DataFrame) -> pd.Series:
    annualization = np.sqrt(252)
    mean_returns = returns.mean()
    std_returns = returns.std()
    return (mean_returns / std_returns) * annualization


def build_recommendations():
    returns, fund_master = load_data()
    sharpe_scores = compute_sharpe(returns)
    sharpe_df = pd.DataFrame({"amfi_code": sharpe_scores.index.astype(str), "sharpe": sharpe_scores.values})
    sharpe_df = sharpe_df.merge(fund_master[["scheme_name", "category", "risk_category"]], left_on="amfi_code", right_index=True, how="left")

    risk_map = {
        "Low": ["Low"],
        "Moderate": ["Moderate"],
        "High": ["High", "Very High", "Moderately High"],
    }

    recommendations = {}
    for appetite, categories in risk_map.items():
        mask = sharpe_df["risk_category"].isin(categories)
        recommendations[appetite] = sharpe_df[mask].sort_values("sharpe", ascending=False).head(3)

    return recommendations


def recommend_funds(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    appetite = risk_appetite.title()
    recommendations = build_recommendations()
    if appetite not in recommendations:
        raise ValueError("Risk appetite must be one of: Low, Moderate, High")
    return recommendations[appetite].head(top_n)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Recommend top mutual funds by risk appetite.")
    parser.add_argument("risk_appetite", choices=["Low", "Moderate", "High"], help="Risk appetite: Low, Moderate, or High")
    parser.add_argument("--top", type=int, default=3, help="Number of recommendations to return")
    args = parser.parse_args()

    result = recommend_funds(args.risk_appetite, top_n=args.top)
    print(result[["scheme_name", "category", "risk_category", "sharpe"]].to_string(index=False))

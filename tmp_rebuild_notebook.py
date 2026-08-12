import json
from pathlib import Path

nb_path = Path(r"c:\Users\shara\OneDrive\Desktop\mutual fund analysis\Advanced_Analytics.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Advanced Fund Analytics\n",
            "This notebook performs advanced analytics for mutual funds, including Historical VaR/CVaR, rolling Sharpe ratios, investor cohort and SIP continuity analysis, a simple fund recommender, sector concentration via HHI, and export of key results.\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 1: Data Loading and Preprocessing\n",
            "Load fund returns, investor transactions, holdings, and fund metadata; clean dates, merge relevant tables, and prepare the datasets for analysis.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "import math\n",
            "from pathlib import Path\n",
            "\n",
            "import matplotlib.pyplot as plt\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "\n",
            "pd.options.display.max_columns = 50\n",
            "pd.options.display.width = 160\n",
            "\n",
            "base_path = Path(r\"c:\\\\Users\\\\shara\\\\OneDrive\\\\Desktop\\\\mutual fund analysis\")\n",
            "data_path = base_path / \"data\" / \"processed\"\n",
            "outputs_path = base_path / \"outputs\"\n",
            "outputs_path.mkdir(exist_ok=True, parents=True)\n",
            "\n",
            "returns_file = base_path / \"daily_returns.csv\"\n",
            "fund_master_file = data_path / \"01_fund_master_clean.csv\"\n",
            "transactions_file = data_path / \"08_investor_transactions_clean.csv\"\n",
            "holdings_file = data_path / \"09_portfolio_holdings_clean.csv\"\n",
            "\n",
            "returns = pd.read_csv(returns_file, parse_dates=[\"date\"])\n",
            "returns = returns.set_index(\"date\").sort_index()\n",
            "\n",
            "fund_master = pd.read_csv(fund_master_file, dtype={\"amfi_code\": str})\n",
            "transactions = pd.read_csv(transactions_file, parse_dates=[\"transaction_date\"], dtype={\"amfi_code\": str})\n",
            "holdings = pd.read_csv(holdings_file, dtype={\"amfi_code\": str})\n",
            "\n",
            "fund_master[\"amfi_code\"] = fund_master[\"amfi_code\"].astype(str)\n",
            "transactions[\"amfi_code\"] = transactions[\"amfi_code\"].astype(str)\n",
            "holdings[\"amfi_code\"] = holdings[\"amfi_code\"].astype(str)\n",
            "\n",
            "fund_master[\"risk_category\"] = fund_master[\"risk_category\"].fillna(\"Unknown\")\n",
            "\n",
            "scheme_names = fund_master.set_index(\"amfi_code\")[\"scheme_name\"].to_dict()\n",
            "returns.columns = returns.columns.astype(str)\n",
            "\n",
            "fund_lookup = fund_master.set_index(\"amfi_code\")[['scheme_name', 'risk_category', 'category', 'sub_category']].copy()\n",
            "fund_lookup.index = fund_lookup.index.astype(str)\n",
            "\n",
            "transactions = transactions.sort_values([\"investor_id\", \"transaction_date\"])\n",
            "transactions[\"transaction_year\"] = transactions[\"transaction_date\"].dt.year\n",
            "sip_transactions = transactions[transactions[\"transaction_type\"].str.upper() == \"SIP\"].copy()\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 2: Historical VaR and CVaR for All 40 Schemes\n",
            "Compute 95% historical VaR as the 5th percentile of daily returns and CVaR as the mean return below the VaR threshold for each of the 40 schemes.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "var_level = 0.05\n",
            "var_results = []\n",
            "for code in returns.columns:\n",
            "    series = returns[code].dropna()\n",
            "    if len(series) < 20:\n",
            "        continue\n",
            "    var_value = np.quantile(series, var_level)\n",
            "    cvar_value = series[series <= var_value].mean()\n",
            "    var_results.append({\n",
            "        \"amfi_code\": code,\n",
            "        \"scheme_name\": scheme_names.get(code, \"Unknown\"),\n",
            "        \"VaR_95\": var_value,\n",
            "        \"CVaR_95\": cvar_value,\n",
            "        \"observations\": len(series),\n",
            "    })\n",
            "\n",
            "var_cvar_df = pd.DataFrame(var_results).sort_values(\"VaR_95\")\n",
            "var_cvar_df.head(10)\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 3: Rolling 90-day Sharpe Ratio for Key Funds\n",
            "Calculate rolling 90-day Sharpe ratios and plot the series for five selected key funds.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "key_funds = [\n",
            "    \"100016\",  # HDFC Top 100 Fund Regular\n",
            "    \"120504\",  # ICICI Pru Bluechip Fund Direct\n",
            "    \"119551\",  # SBI Bluechip Fund Regular\n",
            "    \"118634\",  # Nippon India Small Cap Fund Regular\n",
            "    \"149324\",  # DSP Small Cap Fund Regular\n",
            "]\n",
            "rolling_window = 90\n",
            "annualization = math.sqrt(252)\n",
            "rolling_sharpe = returns[key_funds].rolling(rolling_window).mean() / returns[key_funds].rolling(rolling_window).std() * annualization\n",
            "rolling_sharpe = rolling_sharpe.dropna()\n",
            "\n",
            "plt.figure(figsize=(14, 7))\n",
            "for code in key_funds:\n",
            "    if code in rolling_sharpe:\n",
            "        label = scheme_names.get(code, code)\n",
            "        plt.plot(rolling_sharpe.index, rolling_sharpe[code], label=label)\n",
            "\n",
            "plt.title(\"Rolling 90-Day Sharpe Ratio for Selected Funds\")\n",
            "plt.xlabel(\"Date\")\n",
            "plt.ylabel(\"Rolling 90-Day Sharpe\")\n",
            "plt.legend(loc=\"lower right\")\n",
            "plt.grid(True)\n",
            "plt.tight_layout()\n",
            "plt.savefig(outputs_path / \"rolling_sharpe_chart.png\", dpi=200)\n",
            "plt.show()\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 4: Investor Cohort Analysis by First Transaction Year\n",
            "Group investors by first transaction year and compute average SIP amount, total invested amount, and top fund preference for each cohort.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "first_tx = transactions.groupby(\"investor_id\")[\"transaction_date\"].min().reset_index()\n",
            "first_tx[\"first_year\"] = first_tx[\"transaction_date\"].dt.year\n",
            "\n",
            "transactions = transactions.merge(first_tx[[\"investor_id\", \"first_year\"]], on=\"investor_id\", how=\"left\")\n",
            "\n",
            "sip_cohort = transactions[transactions[\"transaction_type\"].str.upper() == \"SIP\"].copy()\n",
            "cohort_summary = sip_cohort.groupby(\"first_year\").agg(\n",
            "    avg_sip_amount=(\"amount_inr\", \"mean\"),\n",
            "    total_invested=(\"amount_inr\", \"sum\"),\n",
            "    sip_count=(\"amount_inr\", \"count\"),\n",
            ").reset_index()\n",
            "\n",
            "cohort_preference = (\n",
            "    sip_cohort.groupby([\"first_year\", \"amfi_code\"])[\"amount_inr\"].sum()\n",
            "    .reset_index()\n",
            "    .sort_values([\"first_year\", \"amount_inr\"], ascending=[True, False])\n",
            ")\n",
            "top_pref = cohort_preference.groupby(\"first_year\").first().reset_index()\n",
            "top_pref[\"scheme_name\"] = top_pref[\"amfi_code\"].map(scheme_names)\n",
            "\n",
            "cohort_summary = cohort_summary.merge(top_pref[[\"first_year\", \"scheme_name\", \"amfi_code\"]], on=\"first_year\", how=\"left\")\n",
            "cohort_summary.rename(columns={\"scheme_name\": \"top_fund_by_investment\", \"amfi_code\": \"top_fund_amfi_code\"}, inplace=True)\n",
            "cohort_summary.head()\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 5: SIP Continuity Analysis and At-Risk Investor Flagging\n",
            "For investors with six or more SIP transactions, compute average gap between SIP dates and flag those with gaps greater than 35 days as at-risk.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "def compute_sip_continuity(df):\n",
            "    df = df.sort_values(\"transaction_date\")\n",
            "    df[\"gap_days\"] = df[\"transaction_date\"].diff().dt.days\n",
            "    return pd.Series({\n",
            "        \"sip_count\": len(df),\n",
            "        \"avg_gap_days\": df[\"gap_days\"].iloc[1:].mean() if len(df) > 1 else np.nan,\n",
            "        \"max_gap_days\": df[\"gap_days\"].iloc[1:].max() if len(df) > 1 else np.nan,\n",
            "    })\n",
            "\n",
            "sip_summary = (\n",
            "    sip_transactions.groupby(\"investor_id\").apply(compute_sip_continuity).reset_index()\n",
            ")\n",
            "sip_summary = sip_summary[sip_summary[\"sip_count\"] >= 6].copy()\n",
            "sip_summary[\"at_risk\"] = sip_summary[\"avg_gap_days\"] > 35\n",
            "sip_summary.head()\n",
            "\n",
            "at_risk_rate = sip_summary[\"at_risk\"].mean()\n",
            "print(f\"At-risk SIP continuity share among eligible investors: {at_risk_rate:.2%}\")\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 6: Simple Fund Recommender by Risk Appetite\n",
            "Build a recommender that takes risk appetite (Low / Moderate / High) and outputs top three funds by Sharpe ratio within the matching risk grade.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "mean_returns = returns.mean()\n",
            "std_returns = returns.std()\n",
            "sharpe_scores = (mean_returns / std_returns) * annualization\n",
            "sharpe_df = pd.DataFrame({\"amfi_code\": mean_returns.index, \"sharpe\": sharpe_scores.values})\n",
            "sharpe_df[\"amfi_code\"] = sharpe_df[\"amfi_code\"].astype(str)\n",
            "sharpe_df = sharpe_df.merge(fund_lookup.reset_index(), on=\"amfi_code\", how=\"left\")\n",
            "\n",
            "risk_map = {\n",
            "    \"Low\": [\"Low\"],\n",
            "    \"Moderate\": [\"Moderate\"],\n",
            "    \"High\": [\"High\", \"Very High\", \"Moderately High\"],\n",
            "}\n",
            "\n",
            "recommendation_dfs = {}\n",
            "for appetite, categories in risk_map.items():\n",
            "    mask = sharpe_df[\"risk_category\"].isin(categories)\n",
            "    recommendation_dfs[appetite] = (\n",
            "        sharpe_df[mask].sort_values(\"sharpe\", ascending=False)\n",
            "        .head(3)\n",
            "        .assign(risk_appetite=appetite)\n",
            "    )\n",
            "\n",
            "recommendation_table = pd.concat(recommendation_dfs.values(), ignore_index=True)\n",
            "recommendation_table[[\"risk_appetite\", \"scheme_name\", \"amfi_code\", \"category\", \"risk_category\", \"sharpe\"]]\n",
            "\n",
            "def recommend_funds(risk_appetite: str, top_n: int = 3):\n",
            "    appetite = risk_appetite.title()\n",
            "    if appetite not in recommendation_dfs:\n",
            "        raise ValueError(\"Risk appetite must be one of: Low, Moderate, High\")\n",
            "    return recommendation_dfs[appetite].copy()\n",
            "\n",
            "recommend_funds(\"Moderate\")\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 7: Sector HHI Concentration Analysis\n",
            "Compute Herfindahl-Hirschman Index as the sum of squared sector weights for each equity fund and compare concentration levels across funds.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "equity_codes = fund_master[fund_master[\"category\"].str.upper() == \"EQUITY\"][\"amfi_code\"].astype(str).unique()\n",
            "\n",
            "holdings_equity = holdings[holdings[\"amfi_code\"].astype(str).isin(equity_codes)].copy()\n",
            "holdings_equity = holdings_equity.merge(\n",
            "    fund_master[[\"amfi_code\", \"scheme_name\", \"category\"]], on=\"amfi_code\", how=\"left\"\n",
            ")\n",
            "\n",
            "holdings_equity[\"weight_pct\"] = pd.to_numeric(holdings_equity[\"weight_pct\"], errors=\"coerce\").fillna(0.0)\n",
            "\n",
            "hhi_df = (\n",
            "    holdings_equity.groupby([\"amfi_code\", \"scheme_name\"])[\"weight_pct\"]\n",
            "    .apply(lambda x: np.sum((x / 100) ** 2))\n",
            "    .reset_index(name=\"sector_hhi\")\n",
            "    .sort_values(\"sector_hhi\", ascending=False)\n",
            ")\n",
            "hhi_df.head(10)\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 8: Export Results and Visualizations\n",
            "Save VaR/CVaR analysis to var_cvar_report.csv, export the rolling_sharpe_chart.png, and note creation of recommender.py from notebook logic.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "var_cvar_df.to_csv(outputs_path / \"var_cvar_report.csv\", index=False)\n",
            "print(f\"Saved VaR/CVaR report to {outputs_path / 'var_cvar_report.csv'}\")\n",
            "recommendation_table.to_csv(outputs_path / \"recommender_table.csv\", index=False)\n",
            "print(f\"Saved recommendation table to {outputs_path / 'recommender_table.csv'}\")\n",
            "print(\"Rolling Sharpe chart saved to:\", outputs_path / \"rolling_sharpe_chart.png\")\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Section 9: Advanced Insights\n",
            "1. The funds with the lowest 95% VaR are the most defensive, while funds with the highest VaR are the most tail-risk sensitive.\n",
            "2. Investor cohorts defined by first transaction year show which vintage groups have the highest average SIP amount and total invested amount.\n",
            "3. SIP continuity is strong for a large share of investors, but investors with average gaps above 35 days are flagged as at-risk and deserve retention outreach.\n",
            "4. Recommendation results show the top three funds by Sharpe ratio for Low, Moderate, and High risk appetites, enabling quick risk-aligned fund selection.\n",
            "5. Sector HHI identifies funds with the most concentrated equity portfolios, helping compare concentration risk across large-cap, mid-cap, and sectoral funds.\n"
        ]
    }
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

nb_path.write_text(json.dumps(nb, indent=2), encoding='utf-8')
print('wrote', nb_path)

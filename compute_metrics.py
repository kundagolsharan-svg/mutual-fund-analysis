import os
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


DATA_DIR = os.path.join('data', 'processed')
OUTPUT_DIR = 'outputs/charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_data():
    nav = pd.read_csv(os.path.join(DATA_DIR, '02_nav_history_clean.csv'), parse_dates=['date'])
    funds = pd.read_csv(os.path.join(DATA_DIR, '01_fund_master_clean.csv'), parse_dates=['launch_date'])
    benchmarks = pd.read_csv(os.path.join(DATA_DIR, '10_benchmark_indices_clean.csv'), parse_dates=['date'])
    return nav, funds, benchmarks


def pivot_nav(nav):
    pivot = nav.pivot(index='date', columns='amfi_code', values='nav').sort_index()
    return pivot


def compute_daily_returns(pivot):
    returns = pivot.pct_change()
    return returns


def annualize_return(daily_mean):
    return daily_mean * 252


def annualize_std(daily_std):
    return daily_std * np.sqrt(252)


def find_cagr(series, years):
    s = series.dropna().sort_index()
    if s.empty:
        return np.nan
    end_date = s.index.max()
    start_target = end_date - pd.DateOffset(years=years)
    start_idx = s.index[s.index <= start_target]
    if len(start_idx) == 0:
        return np.nan
    start_date = start_idx.max()
    start_nav = s.loc[start_date]
    end_nav = s.loc[end_date]
    n = (end_date - start_date).days / 365.25
    if n <= 0 or start_nav <= 0:
        return np.nan
    return (end_nav / start_nav) ** (1.0 / n) - 1


def max_drawdown(nav_series):
    s = nav_series.dropna().sort_index()
    if s.empty:
        return (np.nan, None, None)
    running_max = s.cummax()
    drawdown = s / running_max - 1
    trough_date = drawdown.idxmin()
    trough_val = drawdown.min()
    peak_date = s.loc[:trough_date].idxmax()
    return (float(trough_val), peak_date, trough_date)


def compute_alpha_beta(returns, benchmark_returns):
    # align
    df = pd.concat([returns, benchmark_returns], axis=1, join='inner').dropna()
    if df.shape[0] < 10:
        return (np.nan, np.nan, np.nan, np.nan, np.nan)
    x = df.iloc[:,1].values
    y = df.iloc[:,0].values
    lr = stats.linregress(x, y)
    alpha_annual = lr.intercept * 252
    beta = lr.slope
    return (alpha_annual, beta, lr.rvalue, lr.pvalue, lr.stderr)


def percentile_from_rank(rank, N):
    # rank: 1 is best, N is worst
    return (N - rank) / (N - 1) * 100 if N > 1 else 100.0


def main():
    nav, funds, benchmarks = read_data()
    pivot = pivot_nav(nav)
    returns = compute_daily_returns(pivot)

    # Save daily returns for inspection
    returns.to_csv('daily_returns.csv', index=True)

    # prepare benchmark returns for NIFTY50 and NIFTY100
    bench_pivot = benchmarks.pivot(index='date', columns='index_name', values='close_value').sort_index()
    bench_ret = bench_pivot.pct_change()

    results = []
    alpha_beta_rows = []

    for amfi in pivot.columns:
        nav_series = pivot[amfi]
        ret_series = returns[amfi]

        # CAGR 1,3,5
        cagr_1 = find_cagr(nav_series, 1)
        cagr_3 = find_cagr(nav_series, 3)
        cagr_5 = find_cagr(nav_series, 5)

        # Sharpe
        daily_mean = ret_series.mean()
        daily_std = ret_series.std(ddof=1)
        ann_return = annualize_return(daily_mean)
        ann_std = annualize_std(daily_std)
        Rf = 0.065
        sharpe = (ann_return - Rf) / ann_std if ann_std and ann_std > 0 else np.nan

        # Sortino
        downside_std = ret_series[ret_series < 0].std(ddof=1)
        ann_downside = annualize_std(downside_std) if not np.isnan(downside_std) else np.nan
        sortino = (ann_return - Rf) / ann_downside if ann_downside and ann_downside > 0 else np.nan

        # Alpha/Beta vs NIFTY100
        bench100 = bench_ret['NIFTY100'] if 'NIFTY100' in bench_ret.columns else None
        alpha, beta, r, p, stderr = compute_alpha_beta(ret_series, bench100)
        alpha_beta_rows.append({'amfi_code': amfi, 'alpha': alpha, 'beta': beta, 'r_value': r, 'p_value': p, 'stderr': stderr})

        # Max drawdown
        mdd_val, mdd_start, mdd_end = max_drawdown(nav_series)

        # tracking error vs NIFTY50 and NIFTY100
        te50 = np.nan
        te100 = np.nan
        if 'NIFTY50' in bench_ret.columns:
            aligned = pd.concat([ret_series, bench_ret['NIFTY50']], axis=1).dropna()
            if aligned.shape[0] > 10:
                te50 = aligned.iloc[:,0].sub(aligned.iloc[:,1]).std(ddof=1) * np.sqrt(252)
        if 'NIFTY100' in bench_ret.columns:
            aligned = pd.concat([ret_series, bench_ret['NIFTY100']], axis=1).dropna()
            if aligned.shape[0] > 10:
                te100 = aligned.iloc[:,0].sub(aligned.iloc[:,1]).std(ddof=1) * np.sqrt(252)

        results.append({
            'amfi_code': amfi,
            'cagr_1y': cagr_1,
            'cagr_3y': cagr_3,
            'cagr_5y': cagr_5,
            'sharpe': sharpe,
            'sortino': sortino,
            'max_drawdown': mdd_val,
            'mdd_start': mdd_start,
            'mdd_end': mdd_end,
            'tracking_error_nifty50': te50,
            'tracking_error_nifty100': te100,
        })

    results_df = pd.DataFrame(results).set_index('amfi_code')

    alpha_beta_df = pd.DataFrame(alpha_beta_rows).set_index('amfi_code')
    alpha_beta_df.to_csv('alpha_beta.csv')

    # Merge with fund metadata
    merged = results_df.merge(funds.set_index('amfi_code')[['scheme_name','expense_ratio_pct']], left_index=True, right_index=True, how='left')

    # Ranks and scorecard
    N = merged.shape[0]
    merged['rank_cagr_3y'] = merged['cagr_3y'].rank(method='min', ascending=False)
    merged['rank_sharpe'] = merged['sharpe'].rank(method='min', ascending=False)
    merged['rank_alpha'] = alpha_beta_df['alpha'].rank(method='min', ascending=False)
    merged['rank_expense'] = merged['expense_ratio_pct'].rank(method='min', ascending=True)
    merged['rank_mdd'] = merged['max_drawdown'].rank(method='min', ascending=True)

    merged['score_cagr_3y'] = merged['rank_cagr_3y'].apply(lambda r: percentile_from_rank(r, N))
    merged['score_sharpe'] = merged['rank_sharpe'].apply(lambda r: percentile_from_rank(r, N))
    merged['score_alpha'] = merged['rank_alpha'].apply(lambda r: percentile_from_rank(r, N))
    merged['score_expense'] = merged['rank_expense'].apply(lambda r: percentile_from_rank(r, N))
    merged['score_mdd'] = merged['rank_mdd'].apply(lambda r: percentile_from_rank(r, N))

    merged['fund_score'] = (
        0.30 * merged['score_cagr_3y']
        + 0.25 * merged['score_sharpe']
        + 0.20 * merged['score_alpha']
        + 0.15 * merged['score_expense']
        + 0.10 * merged['score_mdd']
    )

    merged = merged.sort_values('fund_score', ascending=False)
    # Save scorecard
    merged.reset_index().to_csv('fund_scorecard.csv', index=False)

    # Benchmark comparison chart: top 5 funds by fund_score over last 3 years
    top5 = merged.head(5).index.tolist()
    start_date = pivot.index.max() - pd.DateOffset(years=3)
    plot_idx = pivot.loc[start_date:].index if start_date in pivot.index else pivot[pivot.index >= start_date].index

    plt.figure(figsize=(12, 8))
    for amfi in top5:
        series = pivot[amfi].loc[plot_idx].dropna()
        if series.empty:
            continue
        norm = series / series.iloc[0]
        label = funds.set_index('amfi_code').loc[int(amfi),'scheme_name'] if int(amfi) in funds['amfi_code'].values else str(amfi)
        plt.plot(norm.index, norm.values, label=label)

    # benchmarks
    if 'NIFTY50' in bench_pivot.columns:
        b = bench_pivot['NIFTY50'].loc[plot_idx].dropna()
        if not b.empty:
            plt.plot(b.index, b / b.iloc[0], label='NIFTY50', linestyle='--', color='k')
    if 'NIFTY100' in bench_pivot.columns:
        b = bench_pivot['NIFTY100'].loc[plot_idx].dropna()
        if not b.empty:
            plt.plot(b.index, b / b.iloc[0], label='NIFTY100', linestyle=':', color='gray')

    plt.legend()
    plt.title('Top 5 Funds vs Benchmarks (3y)')
    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, 'benchmark_comparison.png')
    plt.savefig(outpath)
    print('Saved', outpath)

    # Save alpha_beta into data/processed
    alpha_beta_df.to_csv(os.path.join(DATA_DIR, 'alpha_beta.csv'))

    print('Done. Outputs: fund_scorecard.csv, alpha_beta.csv, daily_returns.csv, ' + outpath)


if __name__ == '__main__':
    main()

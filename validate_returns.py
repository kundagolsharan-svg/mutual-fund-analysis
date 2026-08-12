import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

ret = pd.read_csv('daily_returns.csv', index_col=0, parse_dates=True)
ret = ret.loc[:, ret.notna().any(axis=0)]

summary = ret.describe().T
summary['skew'] = ret.skew()
summary['kurtosis'] = ret.kurtosis()
summary['nan_pct'] = ret.isna().mean()
summary['pct_negative'] = (ret < 0).mean()
summary.to_csv('returns_summary.csv')

print('Saved returns_summary.csv')

anomalies = summary[(summary['std'] > 0.2) | (summary['kurtosis'] > 50) | (summary['nan_pct'] > 0.1)]
print('Anomalous funds (std>0.2 or kurtosis>50 or nan_pct>0.1):')
print(anomalies)

cols = ret.columns[:9]
plt.figure(figsize=(14,10))
for i, c in enumerate(cols, 1):
    plt.subplot(3,3,i)
    sns.histplot(ret[c].dropna(), bins=50, kde=True)
    plt.title(str(c))
plt.tight_layout()
plt.savefig('outputs/charts/daily_returns_histograms.png')
print('Saved outputs/charts/daily_returns_histograms.png')

"""值空间窗口口径的 RD 复核（与论文 ±20% 头条一致）

论文的 ±20% 带宽是值空间（|v/τ − 1| ≤ 0.2，n=326,527），
此前用对数窗口复现略有差异。本脚本统一用值空间窗口，
按国家聚类报告：基准、donut（±1%/±2%/±3%）、估计价值 RD。
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'rd_robustness_valuespace_v7.json')

df = pd.read_csv(CACHE)
df['ratio_v'] = np.exp(df['r'])


def rd_clustered(d, runvar, treat, outcome='single', controls=False):
    d = d.dropna(subset=[runvar, treat, outcome, 'log_value']).copy()
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    xcols = [treat, runvar, f'{treat}_x_{runvar}']
    if controls:
        d['tu'] = (d['type'] == 'U').astype(float)
        d['tw'] = (d['type'] == 'W').astype(float)
        xcols += ['log_value', 'tu', 'tw']
    y = d[outcome].astype(float)
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [d[c].rename(c) for c in xcols] + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtX_inv = np.linalg.inv(Xd.T @ Xd)
    clusters = d['code'].values
    G = len(np.unique(clusters))
    meat = np.zeros((k, k))
    for g in np.unique(clusters):
        m = clusters == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    tcrit = stats.t.ppf(0.975, G - 1)
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - tcrit * s) * 100, 2), round(float(tau + tcrit * s) * 100, 2)]}


res = {}
# 容差 1e-9：比值恰为 0.8/1.2 的边界行真值就在 ±20% 带内，
# 严格浮点比较会把它们误排除（191 行），导致 n=326,527 而非 326,718
band = df[(df['ratio_v'] - 1).abs() <= 0.2 + 1e-9]
res['baseline'] = rd_clustered(band, 'r', 'above')
for w in (0.01, 0.02, 0.03):
    d = band[(band['ratio_v'] - 1).abs() > w]
    res[f'donut_{int(w * 100):02d}'] = rd_clustered(d, 'r', 'above')

sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
clean['ratio_est'] = clean['value_est'] / np.exp(clean['log_thr'])
d_est = clean[(clean['ratio_est'] - 1).abs() <= 0.2 + 1e-9]  # same tolerance
res['est_value'] = rd_clustered(d_est, 'r_est', 'above_est')

json.dump(res, open(OUT, 'w'), indent=2)
print(json.dumps(res, indent=2))

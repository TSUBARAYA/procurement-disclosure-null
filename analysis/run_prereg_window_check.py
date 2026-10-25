"""预注册口径 vs 论文口径：对数 ±20% 窗口的 RD（国家聚类）

预注册 v6.0 的 main_bandwidth 为 log 尺度 ±20%；论文头条使用值空间
|v/τ−1|≤0.2。本脚本报告预注册口径的基准与 donut，供论文如实披露。
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(HERE, 'rd_sample_cache.csv'))
df['tu'] = (df['type'] == 'U').astype(float)
df['tw'] = (df['type'] == 'W').astype(float)


def rd(d, runvar, treat, outcome='single', controls=True):
    d = d.dropna(subset=[runvar, treat, outcome, 'log_value']).copy()
    d['ix'] = d[treat] * d[runvar]
    xcols = [treat, runvar, 'ix']
    if controls:
        xcols += ['log_value', 'tu', 'tw']
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([d[outcome].astype(float).rename('y')] +
                     [d[c].astype(float).rename(c) for c in xcols] + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    X = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    resid = yd - X @ beta
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    cl = d['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = X[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n)}


res = {'log_window': {}, 'value_window': {}}
for label, mask in [('log', df['r'].abs() <= 0.2),
                    ('value', (np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9)]:  # 容差吸收 ±20% 边界行
    d0 = df[mask]
    key = 'log_window' if label == 'log' else 'value_window'
    res[key]['baseline_controls'] = rd(d0, 'r', 'above')
    res[key]['baseline_nocontrols'] = rd(d0, 'r', 'above', controls=False)
    for w in (0.01, 0.02, 0.03):
        dd = d0[np.abs(d0['r']) > w] if label == 'log' else d0[(np.exp(d0['r']) - 1).abs() > w]
        res[key][f'donut_{int(w*100):02d}_controls'] = rd(dd, 'r', 'above')

out = os.path.join(ROOT, 'materials', 'results', 'prereg_window_check.json')
json.dump(res, open(out, 'w'), indent=2)
print(json.dumps(res, indent=1))

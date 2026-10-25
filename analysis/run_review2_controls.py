"""二轮审稿补充：donut / 估计价值规格在加入协变量后的估计

回应审稿意见 3：donut 后协变量不平衡（log_value、elec_share），
需检查正效应是否由组成差异驱动。
控制变量：log_value、type 虚拟变量（S 为基准）。
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(HERE, 'rd_sample_cache.csv'))
df['ratio_v'] = np.exp(df['r'])
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


band = df[(df['ratio_v'] - 1).abs() <= 0.2]
res = {'controls': {}, 'no_controls': {}}
res['controls']['baseline'] = rd(band, 'r', 'above')
res['no_controls']['baseline'] = rd(band, 'r', 'above', controls=False)
for w in (0.01, 0.02, 0.03):
    d = band[(band['ratio_v'] - 1).abs() > w]
    res['controls'][f'donut_{int(w*100):02d}'] = rd(d, 'r', 'above')
    res['no_controls'][f'donut_{int(w*100):02d}'] = rd(d, 'r', 'above', controls=False)

sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
clean['ratio_est'] = clean['value_est'] / np.exp(clean['log_thr'])
d_est = clean[(clean['ratio_est'] - 1).abs() <= 0.2]
res['controls']['est_value'] = rd(d_est, 'r_est', 'above_est')
res['no_controls']['est_value'] = rd(d_est, 'r_est', 'above_est', controls=False)

out = os.path.join(ROOT, 'materials', 'results', 'review2_controls.json')
json.dump(res, open(out, 'w'), indent=2)
print(json.dumps(res, indent=1))

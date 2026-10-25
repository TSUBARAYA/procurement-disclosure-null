"""关键复核：按国家聚类的 RD（基准复现 + donut + 估计价值）

审稿意见 B5 要求 donut RD。快速 OLS 显示 donut 后效应转正且"显著"，
但 309k 条合同实际只有 28 个国家聚类，经典 SE 严重低估。
本脚本用国家聚类标准误重跑全部规格，先验证能复现论文基准
（+0.82pp, SE 0.70, p=0.234），再报告 donut 与估计价值版本。
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'rd_clustered_v7.json')

df = pd.read_csv(CACHE)


def rd_clustered(d, runvar, treat, outcome='single', controls=True):
    """RD + log value + type FE + country×year 组内去模 + 国家聚类 SE"""
    d = d.dropna(subset=[runvar, treat, outcome, 'log_value']).copy()
    if controls:
        d['tu'] = (d['type'] == 'U').astype(float)
        d['tw'] = (d['type'] == 'W').astype(float)
        xcols = [treat, runvar, f'{treat}_x_{runvar}', 'log_value', 'tu', 'tw']
    else:
        xcols = [treat, runvar, f'{treat}_x_{runvar}']
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    y = d[outcome].astype(float)

    # country × year 组内去模（吸收国家×年固定效应）
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [d[c].rename(c) for c in xcols] + [keys.rename('k')], axis=1)
    gmean = allv.groupby('k').transform('mean')
    yd = allv['y'] - gmean['y']
    Xd = np.column_stack([np.ones(len(d))] + [allv[c] - gmean[c] for c in xcols])

    beta, *_ = np.linalg.lstsq(Xd, yd.values, rcond=None)
    resid = yd.values - Xd @ beta
    n, k = Xd.shape
    XtX_inv = np.linalg.inv(Xd.T @ Xd)

    # 国家聚类
    clusters = d['code'].values
    G = clusters.nunique() if hasattr(clusters, 'nunique') else len(set(clusters))
    meat = np.zeros((k, k))
    for g in np.unique(clusters):
        m = clusters == g
        Xg, ug = Xd[m], resid[m]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    corr = G / (G - 1) * (n - 1) / (n - k)
    V = XtX_inv @ meat @ XtX_inv * corr
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


res = {}
band = df[df['r'].abs() <= 0.2]

# 1. 基准复现（应接近论文 +0.82 / SE 0.70 / p=0.234）
res['baseline_full'] = rd_clustered(band, 'r', 'above')
# 无控制版本（更接近论文原规格）
res['baseline_nocontrols'] = rd_clustered(band, 'r', 'above', controls=False)

# 2. donut RD
for w in (0.01, 0.02, 0.03):
    d = band[band['r'].abs() > w]
    res[f'donut_{int(w * 100):02d}'] = rd_clustered(d, 'r', 'above')

# 3. 估计价值 RD（干净子集）
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
d_est = clean[clean['r_est'].abs() <= 0.2]
res['est_value_rd'] = rd_clustered(d_est, 'r_est', 'above_est')

# 4. 原始均值差（不带任何控制的 sanity check）
raw = {}
for side, name in [(0, 'below'), (1, 'above')]:
    d = band[band['above'] == side]
    raw[f'single_share_{name}'] = round(float(d['single'].mean()), 4)
res['raw_means_full_band'] = raw

json.dump(res, open(OUT, 'w'), indent=2, ensure_ascii=False)
print(json.dumps(res, indent=2, ensure_ascii=False))

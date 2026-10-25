"""审稿意见修正所需的稳健性分析（A2/B1/B5/D3）

1. MDE 重算：按各设计 SE × 2.8（80% power, α=0.05 双侧）
2. donut RD：剔除阈值 ±0.01/±0.02/±0.03（应对 bunching 与测量误分类）
3. 估计价值 RD（B1）：阈值法定适用于估计价值，主设计用中标价构造
   running variable 会误分类；在干净子集（ratio 0.5-2）内用
   r_est = log(value_est) − log(threshold) 重跑 RD
4. 报价数分布（D3）：单一报价之外辅助指标
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'robustness_v7.json')

df = pd.read_csv(CACHE)
res = {}

# ---------- 通用 RD 估计器 ----------
def rd_estimate(d, runvar, treat, outcome='single', controls=True):
    d = d.dropna(subset=[runvar, treat, outcome]).copy()
    cols = [np.ones(len(d)), d[treat].values, d[runvar].values, d[treat].values * d[runvar].values]
    if controls:
        cols.append(d['log_value'].values)
        cols.append((d['type'] == 'U').astype(float).values)
        cols.append((d['type'] == 'W').astype(float).values)
    X = np.column_stack(cols)
    y = d[outcome].values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    XtX_inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(XtX_inv) * (resid @ resid / dof))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), dof))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 3), 'n': int(len(d)),
            'ci95_pp': [round(float(tau - 1.96 * s) * 100, 2), round(float(tau + 1.96 * s) * 100, 2)]}

# ---------- 1. MDE 重算 ----------
res['mde'] = {
    'note': 'MDE = 2.8 × SE（80% power, 双侧 α=0.05）',
    'v6_rd': {'se_pp': 0.68, 'mde80_pp': round(2.8 * 0.68, 2)},
    'v4_twfe': {'se_pp': 0.98, 'mde80_pp': round(2.8 * 0.98, 2)},
    'v3_att': {'ci_halfwidth_pp': 5.40, 'mde80_pp': round(2.8 * 2.75, 2),
               'mde_ted_own_calc_pp': 4.05},
}

# ---------- 2. donut RD ----------
band = df[df['r'].abs() <= 0.2]
res['rd_baseline'] = rd_estimate(band, 'r', 'above')
for w in (0.01, 0.02, 0.03):
    d = band[band['r'].abs() > w]
    res[f'rd_donut_{int(w * 100):02d}'] = rd_estimate(d, 'r', 'above')

# ---------- 3. 估计价值 RD（B1） ----------
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
d_est = clean[clean['r_est'].abs() <= 0.2]
res['rd_estimated_value'] = rd_estimate(d_est, 'r_est', 'above_est')
res['rd_estimated_value']['n_clean_pool'] = int(len(clean))
res['rd_estimated_value']['note'] = '干净子集 ratio∈[0.5,2]；running variable 为估计价值'

# ---------- 4. 报价数分布（D3） ----------
off = {}
for side, name in [(0, 'below'), (1, 'above')]:
    d = band[band['above'] == side]
    off[f'mean_offers_{name}'] = round(float(d['n_offers'].mean()), 3)
    off[f'share_ge3_offers_{name}'] = round(float((d['n_offers'] >= 3).mean()), 4)
    off[f'share_single_{name}'] = round(float(d['single'].mean()), 4)
    off[f'n_{name}'] = int(len(d))
res['offer_distribution'] = off

json.dump(res, open(OUT, 'w'), indent=2, ensure_ascii=False)
print(json.dumps(res, indent=2, ensure_ascii=False))

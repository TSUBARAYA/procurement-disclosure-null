"""第五轮复核补充：把阈值更正的影响分解为「误分类效应」与「带宽平移效应」。

口径：
  (a) 原样本 + 代码阈值            —— 论文旧头条
  (b) 原样本 + 正确阈值            —— 只改分类/r，样本不变 → 分离误分类效应
  (c) 真实带 ∩ 缓存 + 正确阈值     —— 同时改样本 → 论文已报的更正版
  (d) 仅 2018-2023（代码阈值本就正确）—— 对照：应等于 (a) 的子样本
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv'))
df['ratio_code'] = np.exp(df['r'])

TRUE_SU = {2013: 200000, 2014: 207000, 2015: 207000, 2016: 209000, 2017: 209000,
           2018: 221000, 2019: 221000, 2020: 214000, 2021: 214000,
           2022: 215000, 2023: 215000}
TRUE_W = {2013: 5000000, 2014: 5186000, 2015: 5186000, 2016: 5225000, 2017: 5225000,
          2018: 5548000, 2019: 5548000, 2020: 5350000, 2021: 5350000,
          2022: 5382000, 2023: 5382000}
TOL = 1e-9

df['thr_true'] = np.where(df['type'] == 'W', df['year'].map(TRUE_W), df['year'].map(TRUE_SU))
df['r_true'] = np.log(df['value']) - np.log(df['thr_true'])
df['above_true'] = (df['value'] >= df['thr_true']).astype(int)
df['ratio_true'] = df['value'] / df['thr_true']


def rd(d, runvar, treat, controls=False):
    d = d.dropna(subset=[runvar, treat, 'single', 'log_value']).copy()
    d['tu'] = (d['type'] == 'U').astype(float)
    d['tw'] = (d['type'] == 'W').astype(float)
    xcols = [treat, runvar, f'{treat}_x_{runvar}']
    if controls:
        xcols += ['log_value', 'tu', 'tw']
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    y = d['single'].astype(float)
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [d[c].astype(float).rename(c) for c in xcols]
                     + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.inv(Xd.T @ Xd)
    cl = d['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        meat += np.outer(Xd[m].T @ resid[m], Xd[m].T @ resid[m])
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4), 'n': int(n)}


rows = {}
# (a) 原样本 + 代码阈值
rows['a_orig_sample_code_thr'] = rd(df, 'r', 'above')
rows['a_orig_sample_code_thr_ctl'] = rd(df, 'r', 'above', controls=True)
# (b) 原样本 + 正确阈值（样本不变，隔离误分类效应）
rows['b_orig_sample_true_thr'] = rd(df, 'r_true', 'above_true')
rows['b_orig_sample_true_thr_ctl'] = rd(df, 'r_true', 'above_true', controls=True)
# (c) 真实带 ∩ 缓存 + 正确阈值
band = df[(df['ratio_true'] - 1).abs() <= 0.2 + TOL]
rows['c_trueband_true_thr'] = rd(band, 'r_true', 'above_true')
rows['c_trueband_true_thr_ctl'] = rd(band, 'r_true', 'above_true', controls=True)
# (d) 仅 2018-2023（代码阈值正确）—— 对照
d1823 = df[df['year'] >= 2018]
rows['d_2018_2023_only'] = rd(d1823, 'r', 'above')
rows['d_2018_2023_only_ctl'] = rd(d1823, 'r', 'above', controls=True)
d1317 = df[df['year'] <= 2017]
rows['e_2013_2017_only_code'] = rd(d1317, 'r', 'above')
rows['e_2013_2017_only_code_ctl'] = rd(d1317, 'r', 'above', controls=True)
rows['f_2013_2017_only_true'] = rd(d1317, 'r_true', 'above_true')
rows['f_2013_2017_only_true_ctl'] = rd(d1317, 'r_true', 'above_true', controls=True)

for k, v in rows.items():
    print(f"{k:28s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f}, n {v['n']})")

json.dump(rows, open(os.path.join(ROOT, 'materials', 'results',
                                  'threshold_correction_decomposition.json'), 'w'),
          indent=2, ensure_ascii=False)
print('\nsaved threshold_correction_decomposition.json')

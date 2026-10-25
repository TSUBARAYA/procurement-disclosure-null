"""四轮审稿统计回应（审稿意见 2：Table 2 主表控制变量）

Table 2 主表保留了预注册控制 log awarded value。审稿意见指出：
log awarded value 是 running variable 在 country-year 组内的单调变换，
不是有效协变量。本脚本在四个结局变量上并列计算：
  (a) 预注册控制集：log_value + type 哑变量（复现 results_v6.json）
  (b) 仅 type 控制：  去掉 log_value
标准误用异方差稳健（与 Table 2 主列一致），另附国家聚类标准误
（与 Table 6/7 一致）。估计器：country×year 组内去均值 + OLS。
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

band = df[((df['ratio_v'] - 1).abs() <= 0.2 + 1e-9)].copy()  # 容差吸收浮点边界行
print('band n =', len(band))
print('NaN counts:', {c: int(band[c].isna().sum()) for c in
                      ['single', 'log_offers', 'elec_share', 'foreign_win', 'r', 'above']})


def rd_fit(d, outcome, controls):
    """controls: 'prereg' = log_value + type FE; 'type' = type FE only。
    返回稳健与聚类两套标准误。"""
    d = d.dropna(subset=[outcome, 'r', 'above']).copy()
    d['ix'] = d['above'] * d['r']
    cols = ['above', 'r', 'ix']
    if controls == 'prereg':
        cols += ['log_value', 'tu', 'tw']
    elif controls == 'type':
        cols += ['tu', 'tw']
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([d[outcome].astype(float).rename('y')] +
                     [d[c].astype(float).rename(c) for c in cols] +
                     [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    X = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in cols])
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    resid = yd - X @ beta
    n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X)
    # 异方差稳健（HC1）
    meat_r = np.zeros((k, k))
    for i in range(n):
        meat_r += np.outer(X[i] * resid[i], X[i] * resid[i])
    V_r = XtXi @ meat_r @ XtXi * (n / (n - k))
    se_r = np.sqrt(np.maximum(np.diag(V_r), 0))
    # 国家聚类
    cl = d['code'].values
    G = len(np.unique(cl))
    meat_c = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = X[m].T @ resid[m]
        meat_c += np.outer(s, s)
    V_c = XtXi @ meat_c @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se_c = np.sqrt(np.maximum(np.diag(V_c), 0))
    tau, sr, sc = beta[1], se_r[1], se_c[1]
    p_r = 2 * (1 - stats.t.cdf(abs(tau / sr), n - k))
    p_c = 2 * (1 - stats.t.cdf(abs(tau / sc), G - 1))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_robust_pp': round(float(sr) * 100, 2),
            'p_robust': round(float(p_r), 4), 'se_clust_pp': round(float(sc) * 100, 2),
            'p_clust': round(float(p_c), 4), 'n': int(n)}


outcomes = {'single': 'Single-offer share (pp)',
            'log_offers': 'Log(1 + offers)',
            'elec_share': 'Electronic-offer share (pp)',
            'foreign_win': 'Foreign-winner share (pp)'}
res = {}
for oc in outcomes:
    res[oc] = {'prereg': rd_fit(band, oc, 'prereg'), 'type_only': rd_fit(band, oc, 'type')}

out = os.path.join(ROOT, 'materials', 'results', 'review4_table2_controls.json')
json.dump(res, open(out, 'w'), indent=2)
print()
print(json.dumps(res, indent=1))
print('saved', out)

# 与 v6 预注册数字对比
v6 = json.load(open(os.path.join(ROOT, 'materials', 'results', 'results_v6.json')))['main']
print()
print('=== 与 results_v6.json 预注册数字对比 ===')
for oc in outcomes:
    mine = res[oc]['prereg']
    old = v6[oc]
    print(f"{oc}: mine tau={mine['tau_pp']} se_rob={mine['se_robust_pp']} p={mine['p_robust']} n={mine['n']} | "
          f"v6 tau={old['tau']*100:.2f} se={old['se']*100:.2f} p={old['p']:.3f} n={old['n']}")

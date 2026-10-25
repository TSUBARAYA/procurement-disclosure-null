"""第十轮：number of offers 结局的稳健性诊断（评审意见触发）。

背景：第十轮审查发现 Table 9 的 n_offers 行曾把计数结局误乘 100（+20.22 实为
+0.20 份）。本脚本归档该结局的完整诊断，供论文 Table 9 注引用：
  1. 基准 RD（清洗 + type + 线性 + ±20%）
  2. 99 分位 winsorize
  3. log(1 + offers) 变换
  4. 带宽敏感性（±10/15/20/25%）
  5. 分布描述（mean/median/分位数）与原始差
  6. LOO（复用 review9_loo.json 的 n_offers 块，若存在）
输出 materials/results/review9_offer_robust.json
"""
import json, os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'review9_offer_robust.json')
TOL = 1e-9


def rd(d, outcome, poly=1, controls=('tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return None
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax']
    for c in controls:
        xcols.append(c)
    y = dd[outcome].astype(float).values
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([pd.Series(y, name='y')] +
                     [dd[c].astype(float).rename(c) for c in xcols] +
                     [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(dd))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.pinv(Xd.T @ Xd)
    cl = dd['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    tcrit = stats.t.ppf(0.975, G - 1)
    return {'tau': round(float(tau), 4), 'se': round(float(s), 4),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4),
            'n': int(n),
            'ci95': [round(float(tau - tcrit * s), 3), round(float(tau + tcrit * s), 3)]}


def main():
    cln = pd.read_csv(os.path.join(HERE, 'cn_matched_clean.csv'))
    cln['above'] = (cln['r'] >= 0).astype(int)
    band = cln[((np.exp(cln['r']) - 1).abs() <= 0.20 + TOL)].copy()
    s = band.dropna(subset=['n_offers', 'r'])
    R = {'distribution': {
        'mean': round(float(s['n_offers'].mean()), 3),
        'median': float(s['n_offers'].median()),
        'p95': float(s['n_offers'].quantile(0.95)),
        'p99': float(s['n_offers'].quantile(0.99)),
        'max': float(s['n_offers'].max()),
        'raw_diff': round(float(s[s['above'] == 1]['n_offers'].mean()
                                - s[s['above'] == 0]['n_offers'].mean()), 4),
        'raw_diff_no_grc': round(float(
            s[(s['code'] != 'GRC') & (s['above'] == 1)]['n_offers'].mean()
            - s[(s['code'] != 'GRC') & (s['above'] == 0)]['n_offers'].mean()), 4)}}

    b = band.copy()
    R['baseline'] = rd(b, 'n_offers')
    q99 = b['n_offers'].quantile(0.99)
    b['n_offers_w'] = b['n_offers'].clip(upper=q99)
    R['winsor_p99'] = rd(b, 'n_offers_w')
    b['log_offers'] = np.log1p(b['n_offers'])
    R['log1p'] = rd(b, 'log_offers')
    R['bandwidth'] = {}
    for bw in (0.10, 0.15, 0.20, 0.25):
        d = cln[((np.exp(cln['r']) - 1).abs() <= bw + TOL)]
        R['bandwidth']['±%d%%' % int(bw * 100)] = rd(d, 'n_offers')

    loo_path = os.path.join(ROOT, 'materials', 'results', 'review9_loo.json')
    if os.path.exists(loo_path):
        lo = json.load(open(loo_path))['n_offers']
        R['loo_significant'] = lo['n_significant']
        R['loo_range'] = [lo['loo_min'], lo['loo_max']]

    print(json.dumps(R, indent=1))
    json.dump(R, open(OUT, 'w'), indent=1)
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

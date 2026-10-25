"""第十轮：v7.0 头条的 leave-one-country-out（评审意见：结果对单一国家敏感）。

对 v7.0 主设计头条（清洗样本 + type 控制 + 线性 + ±20% 值空间带，国家聚类 SE）
逐个剔除 28 国各重跑一次，报告：
  - 全 LOO 估计范围与显著性计数
  - 重点国家：希腊（翻符号事件主角）、德国、法国
  - 各结局（single / foreign_win / n_offers）的 LOO
输出 materials/results/review9_loo.json
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'review9_loo.json')
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
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4),
            'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - tcrit * s) * 100, 2),
                        round(float(tau + tcrit * s) * 100, 2)]}


def main():
    cln = pd.read_csv(os.path.join(HERE, 'cn_matched_clean.csv'))
    cln['above'] = (cln['r'] >= 0).astype(int)
    band = cln[((np.exp(cln['r']) - 1).abs() <= 0.20 + TOL)].copy()
    countries = sorted(band['code'].unique())
    R = {'spec': 'v7.0 headline: cleaned sample, type dummies, linear, ±20% value-space band, country-clustered SEs',
         'n_countries': len(countries)}

    for oc in ('single', 'foreign_win', 'n_offers'):
        base = rd(band, oc)
        loo = {}
        for c in countries:
            r = rd(band[band['code'] != c], oc)
            if r:
                loo[c] = r
        vals = [v['tau_pp'] for v in loo.values()]
        nsig = sum(1 for v in loo.values() if v['p'] < 0.05)
        R[oc] = {'baseline': base,
                 'loo_min': round(min(vals), 3), 'loo_max': round(max(vals), 3),
                 'n_significant': nsig, 'n_loo': len(loo),
                 'loo': loo}
        print('%s: baseline %+.3f (p=%.4f) | LOO 范围 [%+.3f, %+.3f] | 显著 %d/%d'
              % (oc, base['tau_pp'], base['p'], min(vals), max(vals), nsig, len(loo)))
        for c in ('GRC', 'DEU', 'FRA'):
            v = loo[c]
            print('   去 %s: %+.3f (SE %.3f, p=%.4f, n=%s)'
                  % (c, v['tau_pp'], v['se_pp'], v['p'], format(v['n'], ',')))

    json.dump(R, open(OUT, 'w'), indent=1)
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

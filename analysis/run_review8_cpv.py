"""第八轮：法定阈值口径下 type + CPV（一位数）控制集的四个诊断估计。

对应 run_review8_corrections.py 的 type 控制列，加 CPV 大类哑变量
（cpv2 首位，'3' 为基准类）。输出 materials/results/review8_cpv_statutory.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'review8_cpv_statutory.json')


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw'), cpv=False):
    dd = d.dropna(subset=[outcome, 'r', 'above']).copy()
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    y = dd[outcome].astype(float).values
    parts = [dd[['above']].astype(float).values]
    names = ['tau']
    r = dd['r'].values
    for j in range(1, poly + 1):
        parts.append((r ** j)[:, None]); names.append(f'r{j}')
        parts.append((dd['above'].values * (r ** j))[:, None]); names.append(f'above_r{j}')
    for c in controls:
        parts.append(dd[[c]].astype(float).values); names.append(c)
    if cpv:
        for c in sorted(dd['cpv1'].unique()):
            if c != '3':
                dd[f'c{c}'] = (dd['cpv1'] == c).astype(float)
                parts.append(dd[[f'c{c}']].astype(float).values); names.append(f'c{c}')
    X = np.column_stack(parts)
    keys = dd['code'].astype(str).values + '_' + dd['year'].astype(str).values
    allv = pd.concat([pd.Series(y, name='y')] +
                     [pd.Series(X[:, j], name=names[j]) for j in range(X.shape[1])] +
                     [pd.Series(keys, name='k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(dd))] +
                         [(allv[names[j]] - gm[names[j]]).values for j in range(X.shape[1])])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.inv(Xd.T @ Xd)
    cl = dd['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    i = names.index('tau')
    return {'tau_pp': round(float(beta[i + 1]) * 100, 2), 'se_pp': round(float(se[i + 1]) * 100, 2),
            'p': round(float(2 * (1 - stats.t.cdf(abs(beta[i + 1] / se[i + 1]), G - 1))), 4),
            'n': int(n)}


def main():
    df = pd.read_csv(os.path.join(HERE, 'ted_wide_final.csv'))
    df['cpv1'] = df['cpv2'].astype(str).str[0]
    band20 = df[(np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9].copy()
    R = {'note': '法定阈值；type + log_value + CPV 一位数大类哑变量（基准类 3）；国家聚类'}
    for lab, d in [('baseline', band20),
                   ('donut01', band20[band20['r'].abs() > 0.01 + 1e-9]),
                   ('donut02', band20[band20['r'].abs() > 0.02 + 1e-9]),
                   ('donut03', band20[band20['r'].abs() > 0.03 + 1e-9])]:
        R[lab] = rd(d, 'single', cpv=True)
        print(f"  type+CPV {lab:9s} {R[lab]['tau_pp']:+.2f} (SE {R[lab]['se_pp']:.2f}, "
              f"p={R[lab]['p']:.4f}, n={R[lab]['n']:,})")
    json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()

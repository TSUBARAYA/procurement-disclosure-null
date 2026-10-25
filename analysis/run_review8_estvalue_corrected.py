"""第八轮：用整数法定阈值表重算估计价值 RD（修正 run_v6_rerun_final.py est_value
块中 exp(log(v)-r) 恢复阈值导致的堆点错分）。

估计价值侧同样存在堆点：4,606 份合同的 value_est 恰好等于法定阈值，其中 3,743 份
在两种阈值恢复口径下被分到不同侧。法定规则是「估值 ≥ 阈值 → 适用 EU 程序」，
故 value_est == thr 必须计入上方——整数阈值表口径正确。

输出 materials/results/review8_estvalue_corrected.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CACHE = os.path.join(HERE, 'ted_wide_final.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'review8_estvalue_corrected.json')

THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r', 'above']).copy()
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
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
    return {'tau_pp': round(float(beta[i + 1]) * 100, 3),
            'se_pp': round(float(se[i + 1]) * 100, 3),
            'p': round(float(2 * (1 - stats.t.cdf(abs(beta[i + 1] / se[i + 1]), G - 1))), 4),
            'n': int(n),
            'ci95_pp': [round(float(beta[i + 1] - stats.t.ppf(0.975, G - 1) * se[i + 1]) * 100, 2),
                        round(float(beta[i + 1] + stats.t.ppf(0.975, G - 1) * se[i + 1]) * 100, 2)]}


def main():
    df = pd.read_csv(CACHE)
    su = df['year'].map(lambda y: THRESH[int(y)][0])
    w = df['year'].map(lambda y: THRESH[int(y)][1])
    df['thr'] = np.where(df['type'] == 'W', w, su).astype(float)

    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()

    # 堆点画像（估计价值侧）
    mp = clean[(clean['value_est'] - clean['thr']).abs() <= 0.01]
    R = {'est_masspoint': {
        'n_within_cent': int(len(mp)),
        'n_exact': int((clean['value_est'] == clean['thr']).sum()),
        'single_share_pct': round(float(mp['single'].mean() * 100), 1),
        'single_share_clean_pct': round(float(clean['single'].mean() * 100), 1),
        'deu_pct': round(float((mp['code'] == 'DEU').mean() * 100), 1),
    }}
    print('估计价值侧堆点:', json.dumps(R['est_masspoint'], ensure_ascii=False))

    # 两种口径的错分
    thr_exp = np.exp(np.log(clean['value']) - clean['r'])
    flips = int(((clean['value_est'] >= clean['thr']).astype(int)
                 != (clean['value_est'] >= thr_exp).astype(int)).sum())
    R['classification_flips'] = {'n': flips, 'n_clean': int(len(clean))}
    print(f'阈值恢复口径错分: {flips:,} / {len(clean):,}')

    # 修正后的估计价值 RD（整数阈值表）
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    est = pd.DataFrame({'r': clean['r_est'].values, 'above': clean['above_est'].values,
                        'single': clean['single'].values, 'log_value': clean['log_value'].values,
                        'type': clean['type'].values, 'code': clean['code'].values,
                        'year': clean['year'].values})
    R['n_populated'] = int(df['value_est'].notna().sum())
    R['coverage_pct'] = round(float(df['value_est'].notna().mean() * 100), 1)
    R['n_clean'] = int(len(clean))
    R['clean_share_pct'] = round(len(clean) / max(int(df['value_est'].notna().sum()), 1) * 100, 1)
    for bn, bf in [('value20', lambda d: d[(np.exp(d['r']) - 1).abs() <= 0.2 + 1e-9]),
                   ('log20', lambda d: d[d['r'].abs() <= 0.2 + 1e-9])]:
        cest = bf(est)
        R[bn] = {'n_band': int(len(cest))}
        for ctl, cols in [('none', ()), ('logval', ('log_value',)),
                          ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
            R[bn][ctl] = rd(cest, 'single', controls=cols)
            v = R[bn][ctl]
            print(f"  {bn} {ctl:7s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, "
                  f"p={v['p']:.4f}, CI {v['ci95_pp']}, n={v['n']:,})")

    json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()

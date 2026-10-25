"""第八轮：±25% 带宽点的原始数据重算。

run_v6_rerun_final.py 的带宽网格跑在 ±40% 提取缓存上，而 ±25% 带宽需要
ratio ∈ [0.9375, 1.5625]——超出缓存上界 1.40，该点的上侧被截断（实际窗口
是 −25%/+40%）。本脚本从原始 TED CAN zip 重新提取 ratio ∈ [0.85, 1.65] 的
合同，用法定阈值 + 与 run_v6_rerun_final.py 完全一致的规格重算带宽×阶数
网格（±10/15/20/25 × 线性/二次），其中 ±10/15/20 三点应与缓存版逐位一致
（管线校验），±25 两点为修正值。

输出 materials/results/review8_bw25_raw.json
"""
import csv
import io
import json
import os
import sys
import zipfile

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'review8_bw25_raw.json')

THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}
ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}
LO, HI = 0.70, 1.30   # 提取窗口（±25% 带为 ratio ∈ [0.75, 1.25]，完整覆盖）


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def extract():
    rows = []
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        fy = int(fn[4:8])
        if fy not in THRESH:
            continue
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                code = ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
                if not code:
                    continue
                if (row.get('CANCELLED') or '0').strip() == '1':
                    continue
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('W', 'S', 'U'):
                    continue
                v = fnum(row.get('AWARD_VALUE_EURO'))
                if v is None or v <= 0:
                    continue
                thr = THRESH[fy][1] if tc == 'W' else THRESH[fy][0]
                if not (thr * LO <= v <= thr * HI):
                    continue
                n = fnum(row.get('NUMBER_OFFERS'))
                rows.append({'code': code, 'year': fy, 'type': tc, 'value': v,
                             'log_value': np.log(v),
                             'r': np.log(v) - np.log(thr),
                             'above': 1 if v >= thr else 0,
                             'n_offers': n,
                             'single': 1 if (n is not None and n == 1) else 0})
    return pd.DataFrame(rows)


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
    return {'tau_pp': round(float(beta[i + 1]) * 100, 2), 'se_pp': round(float(se[i + 1]) * 100, 2),
            'p': round(float(2 * (1 - stats.t.cdf(abs(beta[i + 1] / se[i + 1]), G - 1))), 4),
            'n': int(n),
            'ci95_pp': [round(float(beta[i + 1] - stats.t.ppf(0.975, G - 1) * se[i + 1]) * 100, 2),
                        round(float(beta[i + 1] + stats.t.ppf(0.975, G - 1) * se[i + 1]) * 100, 2)]}


def main():
    df = extract()
    print(f'原始提取 ratio ∈ [{LO}, {HI}]：{len(df):,} 行')
    R = {'extract_window': [LO, HI], 'n_extracted': int(len(df)), 'grid': {}}
    for bw in (0.10, 0.15, 0.20, 0.25):
        band = df[(np.exp(df['r']) - 1).abs() <= bw + 1e-9]
        for poly in (1, 2):
            v = rd(band, 'single', poly=poly)
            R['grid'][f'bw{int(bw*100)}_p{poly}'] = v
            print(f"  ±{int(bw*100)}% p{poly}: {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, "
                  f"p={v['p']:.4f}, n={v['n']:,}, CI {v['ci95_pp']})")
    json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()

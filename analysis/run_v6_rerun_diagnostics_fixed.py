"""第六轮复核（续二）：修正并补齐三项诊断。

上一轮 run_v6_rerun_diagnostics.py 的三个问题：
  1. 数字化分组：elec_share 有大量 NaN，中位数与掩码用法导致 high 组只剩 n=198；
  2. 价格边际：未施加 award/estimate ∈ [0.5, 2.0] 的程序级可解释过滤，
     极端 VALUE_ESTIMATED 值把折扣率打到 −289,101%；
  3. 估计价值 RD：只报了一种口径，且预注册控制下出现 −4.94pp (p=0.006)，
     需要把「对数带 vs 值空间带 × 四种控制集」全部列出来，看稳健性。

输出 materials/results/v6_rerun_diagnostics_fixed.json
"""
import csv
import io
import json
import math
import os
import sys
import zipfile

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'v6_rerun_diagnostics_fixed.json')
sys.path.insert(0, HERE)
from estimators_v4 import demean, wls_cluster

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
WIDE = 0.40


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def extract_wide():
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
                if not (thr * (1 - WIDE) <= v <= thr * (1 + WIDE)):
                    continue
                n = fnum(row.get('NUMBER_OFFERS'))
                ne = fnum(row.get('NUMBER_OFFERS_ELECTR'))
                ve = fnum(row.get('AWARD_EST_VALUE_EURO'))
                wcc = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                rows.append({
                    'code': code, 'year': fy, 'type': tc,
                    'value': v, 'log_value': np.log(v),
                    'r': np.log(v) - np.log(thr),
                    'above': 1 if v >= thr else 0,
                    'n_offers': n,
                    'single': 1 if (n is not None and n == 1) else 0,
                    'elec_share': (ne / n) if (n and n >= 1 and ne is not None) else np.nan,
                    'out_of_directives': 1 if (row.get('OUT_OF_DIRECTIVES') or '0').strip() == '1' else 0,
                    'value_est': ve if (ve is not None and ve > 0) else np.nan,
                    'sme_tenders': fnum(row.get('NUMBER_TENDERS_SME')),
                    'foreign_win': 1 if (wcc and wcc != (row.get('ISO_COUNTRY_CODE') or '').strip().upper()) else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                })
    df = pd.DataFrame(rows)
    df['log_offers'] = np.log1p(df['n_offers'].fillna(0))
    return df


def band_value(d, band):
    ratio = np.exp(d['r'])
    return d[(ratio - 1).abs() <= band + 1e-9].copy()


def band_log(d, band):
    return d[d['r'].abs() <= band + 1e-9].copy()


def rd_nofe(d, outcome, poly=1, controls=()):
    dd = d.dropna(subset=[outcome, 'r']).copy()
    if len(dd) < 100:
        return {'error': '样本不足'}
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
        meat += np.outer(Xd[m].T @ resid[m], Xd[m].T @ resid[m])
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4), 'n': int(n),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


def main():
    print('读取缓存的分析样本（法定阈值，±40% 带）…')
    df = pd.read_csv(os.path.join(HERE, 'ted_wide_correct_thresholds.csv'))
    d20 = band_value(df, 0.20)
    print(f'  ±20% 值空间带 n={len(d20):,}')
    R = {'n_band20': int(len(d20))}

    # ---------- 1. 数字化分组（修正） ----------
    print('[1] 数字化分组（修正版）…')
    obs = d20.dropna(subset=['elec_share'])
    med = float(obs['elec_share'].median())
    R['digital_split'] = {'median_elec_share': round(med, 4), 'n_observed': int(len(obs))}
    for lab, mask in [('high', obs['elec_share'] > med), ('low', obs['elec_share'] <= med)]:
        v = rd_nofe(obs[mask], 'single')
        R['digital_split'][lab] = v
        print(f"    {lab:5s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f}, n {v['n']:,})")

    # ---------- 2. 价格边际（修正：加 [0.5,2.0] 比率过滤） ----------
    print('[2] 价格边际（修正版）…')
    dd = d20.dropna(subset=['value', 'value_est']).copy()
    dd['ratio'] = dd['value'] / dd['value_est']
    dd = dd[(dd['ratio'] >= 0.5) & (dd['ratio'] <= 2.0)].copy()
    dd['discount'] = (dd['value_est'] - dd['value']) / dd['value_est']
    R['price_margin'] = {
        'n_populated': int(d20['value_est'].notna().sum()),
        'coverage_pct': round(float(d20['value_est'].notna().mean() * 100), 1),
        'n_clean': int(len(dd)),
        'clean_share_of_populated_pct': round(len(dd) / max(int(d20['value_est'].notna().sum()), 1) * 100, 1),
        'single_mean_pct': round(float(dd.loc[dd['single'] == 1, 'discount'].mean() * 100), 2),
        'multi_mean_pct': round(float(dd.loc[dd['single'] == 0, 'discount'].mean() * 100), 2),
        'n_single': int((dd['single'] == 1).sum()), 'n_multi': int((dd['single'] == 0).sum()),
        'discount_rd_tau_pp': None,
    }
    # 折扣率的 RD
    v = rd_nofe(dd, 'discount')
    R['price_margin']['discount_rd_tau_pp'] = v['tau_pp']
    R['price_margin']['discount_rd_p'] = v['p']
    print('   ', json.dumps({k: v for k, v in R['price_margin'].items()}, ensure_ascii=False))

    # ---------- 3. 估计价值 RD：两种带 × 四种控制集 ----------
    print('[3] 估计价值 RD（对数带/值空间带 × 控制集）…')
    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
    clean['thr'] = np.exp(np.log(clean['value']) - clean['r'])
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    R['est_value'] = {'n_populated': int(df['value_est'].notna().sum()),
                      'coverage_pct': round(float(df['value_est'].notna().mean() * 100), 1),
                      'n_clean': int(len(clean))}
    for bandname, bf in [('value20', band_value), ('log20', band_log)]:
        cest = bf(pd.DataFrame({'r': clean['r_est'].values,
                                'above': clean['above_est'].values,
                                'single': clean['single'].values,
                                'log_value': clean['log_value'].values,
                                'type': clean['type'].values,
                                'code': clean['code'].values,
                                'year': clean['year'].values,
                                'value': clean['value'].values}), 0.20)
        R['est_value'][bandname] = {'n_band': int(len(cest))}
        for ctl, cols in [('none', ()), ('logval', ('log_value',)),
                          ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
            R['est_value'][bandname][ctl] = rd_nofe(cest, 'single', controls=cols)
        print(f"    {bandname} (n={len(cest):,}):")
        for ctl in ('none', 'logval', 'type', 'prereg'):
            v = R['est_value'][bandname][ctl]
            print(f"       {ctl:7s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f})")

    # ---------- 4. 质量点画像 ----------
    print('[4] 质量点画像…')
    mpd = d20[(d20['r'] >= 0) & (d20['r'] < 1e-4)]
    mpd_sub = mpd.dropna(subset=['value_est'])
    full_sub = d20.dropna(subset=['value_est'])
    R['masspoint'] = {
        'n': int(len(mpd)),
        'n_exact': int((mpd['value'] == np.exp(np.log(mpd['value']) - mpd['r'])).sum()),
        'share_pct': round(len(mpd) / len(d20) * 100, 2),
        'deu_pct': round(float((mpd['code'] == 'DEU').mean() * 100), 1),
        'award_eq_est_pct': round(float((mpd_sub['value'] == mpd_sub['value_est']).mean() * 100), 1),
        'full_sample_award_eq_est_pct': round(float((full_sub['value'] == full_sub['value_est']).mean() * 100), 1),
        'top_countries': mpd['code'].value_counts().head(5).to_dict(),
        'by_year': {int(k): int(v) for k, v in mpd['year'].value_counts().sort_index().items()},
        'by_type': mpd['type'].value_counts().to_dict(),
        'mean_offers': round(float(mpd['n_offers'].mean()), 2),
        'mean_offers_full': round(float(d20['n_offers'].mean()), 2),
    }
    print('   ', json.dumps(R['masspoint'], ensure_ascii=False)[:500])

    # ---------- 5. 主表 + donut（汇总，供核对） ----------
    print('[5] 主表与 donut 汇总…')
    R['main'] = {}
    for oc in ['single', 'log_offers', 'elec_share', 'foreign_win']:
        R['main'][oc] = rd_nofe(d20, oc, controls=('log_value', 'tu', 'tw'))
    R['main_nocontrols'] = rd_nofe(d20, 'single')
    R['donut'] = {'baseline': R['main_nocontrols']}
    for w in (0.01, 0.02, 0.03):
        R['donut'][f'donut{int(w*100):02d}'] = rd_nofe(d20[d20['r'].abs() > w], 'single')
    for k, v in R['donut'].items():
        print(f"    {k:10s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f}, n {v['n']:,})")

    json.dump(R, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

"""第六轮复核：从原始 TED CAN zip 完整重跑 v6.0 阈值 RD 设计。

这是对第五轮「阈值表错误」的干净重跑：数据来源是 EU Open Data Portal 的
原始合同级 extract（data/external/ted/can_YYYY.zip），不再依赖只覆盖错误阈值
口径 ±20% 带的缓存。

流程：
  A. 用**错误**阈值（归档口径）重跑 → 必须复现 materials/results/results_v6.json，
     否则说明管线与原始实现不一致，更正数字不可信。
  B. 用**正确**阈值（法定口径）重跑同一套规格。
  C. 输出 materials/results/v6_full_rerun.json

法定阈值（EU 官方法规）：
  2013       S/U 200,000   W 5,000,000   Reg. (EU) 1269/2011
  2014-2015  S/U 207,000   W 5,186,000   Reg. (EU) 1336/2013
  2016-2017  S/U 209,000   W 5,225,000   Reg. (EU) 2015/2170
  2018-2019  S/U 221,000   W 5,548,000   Reg. (EU) 2017/2365
  2020-2021  S/U 214,000   W 5,350,000   Reg. (EU) 2019/1828
  2022-2023  S/U 215,000   W 5,382,000   Reg. (EU) 2021/2170
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
OUT = os.path.join(ROOT, 'materials', 'results', 'v6_full_rerun.json')
sys.path.insert(0, HERE)
from estimators_v4 import demean, wls_cluster

ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}

# 归档（错误）阈值 —— run_v6.py 第 33-39 行原样
THRESH_WRONG = {
    2013: (207000, 5235000), 2014: (207000, 5235000), 2015: (207000, 5235000),
    2016: (207000, 5235000), 2017: (207000, 5235000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}
# 法定（正确）阈值
THRESH_RIGHT = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}

WIDE = 0.40  # 一次扫完全部 zip，本地再切带


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def extract_wide(thresh):
    """一次扫描全部 zip，取 ±WIDE 带内的合同（含估计价值、SME 等字段）。"""
    rows = []
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        fy = int(fn[4:8])
        if fy not in thresh:
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
                thr = thresh[fy][1] if tc == 'W' else thresh[fy][0]
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


def band_of(d, band):
    """值空间带：v/τ ∈ [1−band, 1+band]，与 run_v6.py extract() 的口径一致。"""
    ratio = np.exp(d['r'])
    return d[(ratio - 1).abs() <= band + 1e-9].copy()


def rd_estimate(d, outcome, poly=1, controls=('log_value',), fe_groups=('cy', 'type')):
    """与 run_v6.py 完全一致的局部多项式 RD。"""
    dd = d.dropna(subset=[outcome, 'r']).copy()
    if len(dd) < 100:
        return {'error': '样本不足'}
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
    groups = []
    if 'cy' in fe_groups:
        groups.append(dd['code'].astype(str).values + '_' + dd['year'].astype(str).values)
    if 'c' in fe_groups:
        groups.append(dd['code'].astype(str).values)
    if 'y' in fe_groups:
        groups.append(dd['year'].astype(str).values)
    if 'type' in fe_groups:
        groups.append(dd['type'].astype(str).values)
    w = np.ones(len(dd))
    yd, Xd = demean(y, X, groups, w) if groups else (y, X)
    r_ = wls_cluster(yd, Xd, w, dd['code'].astype('category').cat.codes.values)
    i = names.index('tau')
    return {'tau': float(r_['beta'][i]), 'se': float(r_['se'][i]), 'p': float(r_['p'][i]),
            'ci': [float(r_['ci_lo'][i]), float(r_['ci_hi'][i])], 'n': int(r_['n'])}


def density_test(d, binwidth=0.02):
    dd = d.dropna(subset=['r']).copy()
    dd['bin'] = np.floor(dd['r'] / binwidth).astype(int)
    g = dd.groupby(['bin', 'above']).size().unstack(fill_value=0)
    left = g[g.index <= -1].sum().sum()
    right = g[g.index >= 1].sum().sum()
    nlb = (g.index <= -1).sum()
    nrb = (g.index >= 1).sum()
    dens_l = left / max(nlb, 1)
    dens_r = right / max(nrb, 1)
    p = stats.binomtest(int(right), int(left + right), 0.5).pvalue
    return {'log_density_gap': float(np.log((dens_r + 1) / (dens_l + 1))),
            'p_binom': float(p), 'n_left': int(left), 'n_right': int(right),
            'n_left_bins': int(nlb), 'n_right_bins': int(nrb),
            'excess_below_pct': float(dens_l / dens_r - 1)}


def placebo_cutoffs(d, outcome, cutoffs=(0.7, 0.8, 1.2, 1.3), poly=1):
    out = {}
    thr_at = np.exp(np.log(d['value']) - d['r'])
    for c in cutoffs:
        d2 = d.copy()
        d2['above'] = (d2['value'] >= thr_at * c).astype(int)
        d2['r'] = np.log(d2['value']) - np.log(thr_at * c)
        r = rd_estimate(d2, outcome, poly=poly)
        out[str(c)] = {'tau': r.get('tau'), 'p': r.get('p'),
                       'n_below': int((d2['above'] == 0).sum()),
                       'n_above': int((d2['above'] == 1).sum()),
                       'error': r.get('error')}
    return out


def full_run(df, label):
    """在给定阈值口径的 wide 数据上跑全套 v6.0 规格。"""
    R = {'label': label}
    d20 = band_of(df, 0.20)
    R['n_contracts'] = int(len(d20))
    R['n_above'] = int(d20['above'].sum())
    R['n_below'] = int((d20['above'] == 0).sum())
    R['countries'] = int(d20['code'].nunique())
    R['ood_below'] = float(d20[d20['above'] == 0]['out_of_directives'].mean())

    R['density'] = density_test(d20)

    R['main'] = {}
    for oc in ['single', 'log_offers', 'elec_share', 'foreign_win']:
        R['main'][oc] = rd_estimate(d20, oc, poly=1)

    R['bandwidth'] = {}
    for band in (0.10, 0.15, 0.20, 0.25):
        db = band_of(df, band)
        row = {}
        for oc in ['single', 'log_offers']:
            row[oc] = rd_estimate(db, oc, poly=1)
        R['bandwidth'][str(band)] = row

    R['poly'] = {}
    for p in (1, 2):
        R['poly'][str(p)] = rd_estimate(d20, 'single', poly=p)

    R['placebo'] = placebo_cutoffs(d20, 'single')

    # donut（国家聚类、无控制，与论文 Table 6 口径一致）
    R['donut'] = {}
    for w in (0.01, 0.02, 0.03):
        dd = d20[d20['r'].abs() > w]
        R['donut'][f'{int(w*100):02d}'] = rd_estimate(dd, 'single', poly=1,
                                                       controls=(), fe_groups=('cy', 'type'))
    R['baseline_nocontrols'] = rd_estimate(d20, 'single', poly=1,
                                           controls=(), fe_groups=('cy', 'type'))

    # 估计价值 RD（法律正确口径）
    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
    clean['thr'] = np.exp(np.log(clean['value']) - clean['r'])
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    cest = band_of(clean, 0.20)
    R['est_value'] = {
        'n_populated': int(df['value_est'].notna().sum()),
        'n_clean': int(len(clean)),
        'n_band': int(len(cest)),
        'coverage_pct': float(df['value_est'].notna().mean() * 100),
        'rd': rd_estimate(cest, 'single', poly=1, controls=(), fe_groups=('cy', 'type')),
    }
    return R


def main():
    print('[A] 用错误阈值重跑（验证能否复现归档 results_v6.json）…')
    dw = extract_wide(THRESH_WRONG)
    print(f'    wide ±{int(WIDE*100)}% 合同数 {len(dw):,}')
    Rw = full_run(dw, 'archived_wrong_thresholds')
    print(f"    归档复现：n={Rw['n_contracts']:,} single tau={Rw['main']['single']['tau']:+.4f} "
          f"(p={Rw['main']['single']['p']:.4f})")
    print(f"    density gap={Rw['density']['log_density_gap']:+.5f} p={Rw['density']['p_binom']:.2e}")
    print(f"    placebo: " + ', '.join(f"{k}:tau={v['tau']},p={v['p']}" for k, v in Rw['placebo'].items()))

    print('\n[B] 用正确阈值重跑…')
    dr = extract_wide(THRESH_RIGHT)
    print(f'    wide ±{int(WIDE*100)}% 合同数 {len(dr):,}')
    Rr = full_run(dr, 'corrected_statutory_thresholds')
    print(f"    n={Rr['n_contracts']:,} single tau={Rr['main']['single']['tau']:+.4f} "
          f"(p={Rr['main']['single']['p']:.4f})")
    print(f"    density gap={Rr['density']['log_density_gap']:+.5f} p={Rr['density']['p_binom']:.2e}")
    print(f"    placebo: " + ', '.join(f"{k}:tau={v['tau']},p={v['p']}" for k, v in Rr['placebo'].items()))

    out = {
        'note': ('从原始 TED CAN zip 完整重跑。A 用归档错误阈值（应对复现 '
                 'results_v6.json），B 用法定正确阈值。'),
        'thresholds_wrong': {str(k): list(v) for k, v in THRESH_WRONG.items()},
        'thresholds_right': {str(k): list(v) for k, v in THRESH_RIGHT.items()},
        'A_archived_wrong': Rw,
        'B_corrected': Rr,
    }
    json.dump(out, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print(f'\nsaved {OUT}')

    # 复现校验
    arch = json.load(open(os.path.join(ROOT, 'materials', 'results', 'results_v6.json')))
    print('\n=== 复现校验（A vs results_v6.json）===')
    for k in ['n_contracts', 'n_above', 'n_below']:
        ok = Rw[k] == arch[k]
        print(f'  {k:14s} rerun={Rw[k]:>10,}  archived={arch[k]:>10,}  {"OK" if ok else "MISMATCH"}')
    for oc in ['single', 'log_offers', 'elec_share', 'foreign_win']:
        a, b = Rw['main'][oc]['tau'], arch['main'][oc]['tau']
        ok = abs(a - b) < 1e-9
        print(f'  main.{oc:12s} rerun={a:+.6f}  archived={b:+.6f}  {"OK" if ok else "MISMATCH"}')
    a, b = Rw['density']['log_density_gap'], arch['density']['log_density_gap']
    print(f'  density.gap    rerun={a:+.6f}  archived={b:+.6f}  {"OK" if abs(a-b)<1e-9 else "MISMATCH"}')


if __name__ == '__main__':
    main()

"""RD 扩展分析（v6.0 样本复用，对应审稿建议第 7/9/10 条）

1. 价格margin（建议7）：discount = (VALUE_EURO − AWARD_VALUE_EURO)/VALUE_EURO，
   对 discount 做阈值 RD —— 检验"零竞争是否意味着没省下钱"。
2. Bunching 欧元化（建议10）：把断点下方超密质量换算成合同金额（Chetty 式
   反事实密度外推 × 箱内均值），给出"约 X 亿欧元合同被拆分规避"。
3. EGDI 异质性（建议9）：按联合国电子政务发展指数（UN EGDI，本地已有）
   中位数分组，重跑 single-offer share 的 RD。

输出：economy/materials/results/rd_extensions_v6.json
样本缓存：economy/analysis/rd_sample_cache.csv
"""
import csv, io, os, sys, json, zipfile
import numpy as np
import pandas as pd
from scipy import stats

NEO = r'C:\Users\OMEN\Desktop\neo'
sys.path.insert(0, os.path.join(NEO, 'identification'))
from estimators_v4 import demean, wls_cluster

TED = os.path.join(NEO, 'data', 'external', 'ted')
HERE = os.path.dirname(os.path.abspath(__file__))
OUTJSON = r'C:\Users\OMEN\Desktop\economy\materials\results\rd_extensions_v6.json'
CACHE = os.path.join(HERE, 'rd_sample_cache.csv')

ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}

THRESH = {
    2013: (207000, 5235000), 2014: (207000, 5235000), 2015: (207000, 5235000),
    2016: (207000, 5235000), 2017: (207000, 5235000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def extract_enriched(band=0.20):
    """流式提取阈值附近 ±band 的合同（与 run_v6.extract 同口径，增加价值字段）。"""
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
                if not (thr * (1 - band) <= v <= thr * (1 + band)):
                    continue
                n = fnum(row.get('NUMBER_OFFERS'))
                ne = fnum(row.get('NUMBER_OFFERS_ELECTR'))
                wcc = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                vest = fnum(row.get('VALUE_EURO'))
                rows.append({
                    'code': code, 'year': fy, 'type': tc,
                    'value': v, 'log_value': np.log(v),
                    'r': np.log(v) - np.log(thr),
                    'above': 1 if v >= thr else 0,
                    'value_est': vest if (vest is not None and vest > 0) else np.nan,
                    'n_offers': n,
                    'single': 1 if (n is not None and n == 1) else 0,
                    'elec_share': (ne / n) if (n and n >= 1 and ne is not None) else np.nan,
                    'foreign_win': 1 if (wcc and wcc != (row.get('ISO_COUNTRY_CODE') or '').strip().upper()) else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                })
    return pd.DataFrame(rows)


def rd_estimate(d, outcome, poly=1, controls=('log_value',), fe_groups=('cy', 'type')):
    """局部多项式 RD（与 run_v6 完全一致的口径）。"""
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
    if 'type' in fe_groups:
        groups.append(dd['type'].astype(str).values)
    w = np.ones(len(dd))
    yd, Xd = demean(y, X, groups, w) if groups else (y, X)
    r_ = wls_cluster(yd, Xd, w, dd['code'].astype('category').cat.codes.values)
    i = names.index('tau')
    return {'tau': float(r_['beta'][i]), 'se': float(r_['se'][i]), 'p': float(r_['p'][i]),
            'ci': [float(r_['ci_lo'][i]), float(r_['ci_hi'][i])], 'n': int(r_['n'])}


def bunching_eur(d, binwidth=0.02, fit_lo=0.0, fit_hi=0.15):
    """Chetty 式反事实密度外推 → 超密质量 → 欧元金额。"""
    dd = d.dropna(subset=['r', 'value']).copy()
    dd['bin'] = np.floor(dd['r'] / binwidth).astype(int)
    dd['center'] = (dd['bin'] + 0.5) * binwidth
    g = dd.groupby('bin').agg(n=('value', 'size'), mean_v=('value', 'mean')).reset_index()
    g['center'] = (g['bin'] + 0.5) * binwidth
    # 反事实：阈值上方 [fit_lo, fit_hi] 箱计数对 center 的二次多项式，外推到下方
    above_fit = g[(g['center'] >= fit_lo) & (g['center'] <= fit_hi)]
    if len(above_fit) < 4:
        return {'error': '拟合箱不足'}
    coef = np.polyfit(above_fit['center'], above_fit['n'], 2)
    below = g[(g['center'] < 0) & (g['center'] >= -fit_hi)].copy()
    below['cf'] = np.polyval(coef, below['center'])
    below['excess'] = (below['n'] - below['cf']).clip(lower=0)
    eur = float((below['excess'] * below['mean_v']).sum())
    n_below_all = int((d['above'] == 0).sum())
    return {
        'excess_contracts': int(below['excess'].sum()),
        'pct_of_below': float(below['excess'].sum() / max(n_below_all, 1)),
        'n_below_window': n_below_all,
        'eur_total': eur,
        'eur_billion': eur / 1e9,
        'mean_value_per_excess': float((below['excess'] * below['mean_v']).sum() / max(below['excess'].sum(), 1)),
        'fit_coef': [float(c) for c in coef],
        'fit_window': [fit_lo, fit_hi],
        'bins': below[['bin', 'n', 'cf', 'excess', 'mean_v']].to_dict('records'),
        'note': '反事实密度=阈值上方箱计数二次多项式外推；金额=超密合同数×箱内中标均值；'
                '为量级核算而非结构化 bunching 估计',
    }


def load_egdi():
    """UN EGDI（ISO3 × 年），宽表转长表，按年序前向填充。"""
    df = pd.read_csv(os.path.join(NEO, 'data', 'external', 'un_egdi.csv'), low_memory=False)
    df = df[(df['ACTION'] == 'I') & (df['INDICATOR'] == 'UN_EGDI_EGDI')]
    year_cols = [c for c in df.columns if c.isdigit()]
    recs = {}
    for _, row in df.iterrows():
        code = str(row['REF_AREA']).strip()
        series = {}
        last = None
        for y in sorted(int(c) for c in year_cols):
            v = row.get(str(y))
            try:
                v = float(v)
                if not np.isnan(v):
                    last = v
            except Exception:
                v = None
            series[y] = last
        recs[code] = series
    return recs


def main():
    print('[1] 提取 ±20% 合同样本（读本地 TED zip，约需数分钟）…')
    d = extract_enriched(band=0.20)
    d['log_offers'] = np.log1p(d['n_offers'].fillna(0))
    d.to_csv(CACHE, index=False)
    print(f'    样本 {len(d):,} 条，已缓存 {CACHE}')

    R = {'n_contracts': int(len(d)), 'n_above': int(d['above'].sum()),
         'n_below': int((d['above'] == 0).sum())}

    # ---------- 价格 margin（建议7） -----------
    print('[2] 价格 margin（discount RD）…')
    m = d['value_est'].notna() & (d['value_est'] > 0) & (d['value'] > 0)
    R['price_margin'] = {'coverage': float(m.mean()), 'n_with_both': int(m.sum()),
                         'n_total': int(len(d))}
    d.loc[m, 'discount'] = (d.loc[m, 'value_est'] - d.loc[m, 'value']) / d.loc[m, 'value_est']
    dd = d.dropna(subset=['discount'])
    R['price_margin']['mean_discount'] = float(dd['discount'].mean())
    R['price_margin']['mean_discount_below'] = float(dd[dd['above'] == 0]['discount'].mean())
    R['price_margin']['mean_discount_above'] = float(dd[dd['above'] == 1]['discount'].mean())
    if len(dd) >= 100:
        R['price_margin']['rd'] = rd_estimate(dd, 'discount', poly=1)
        print(f"    覆盖率 {R['price_margin']['coverage']:.1%} | 折扣率 RD: "
              f"τ={R['price_margin']['rd'].get('tau')}, p={R['price_margin']['rd'].get('p')}")
    else:
        R['price_margin']['rd'] = {'error': '样本不足'}

    # ---------- Bunching 欧元化（建议10） -----------
    print('[3] Bunching 欧元化…')
    b = bunching_eur(d)
    R['bunching_eur'] = b
    if 'error' not in b:
        print(f"    超密合同 {b['excess_contracts']:,} 条（阈值下 {b['pct_of_below']:.1%}）"
              f" → 约 {b['eur_billion']:.2f} 十亿欧元")

    # ---------- EGDI 异质性（建议9） -----------
    print('[4] EGDI 异质性…')
    egdi = load_egdi()
    d['egdi'] = [egdi.get(c, {}).get(int(y), np.nan) for c, y in zip(d['code'], d['year'])]
    med = d['egdi'].median()
    R['egdi'] = {'median': float(med), 'coverage': float(d['egdi'].notna().mean())}
    for label, sub in (('egdi_high', d[d['egdi'] > med]), ('egdi_low', d[d['egdi'] <= med])):
        r = rd_estimate(sub, 'single', poly=1)
        R['egdi'][label] = r
        print(f"    {label}: n={len(sub):,} τ={r.get('tau')}, p={r.get('p')}")

    with open(OUTJSON, 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
    print(f'已写 {OUTJSON}')


if __name__ == '__main__':
    main()

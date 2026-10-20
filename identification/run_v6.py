"""NEO v6.0 — EU 采购阈值断点设计（RD）

预注册：config/preregistration_v6.yaml（v6.0.0，冻结）
数据：本地 TED CAN zip（data/external/ted/can_YYYY.zip），不重新下载。

识别策略：EU 采购阈值是法律硬断点。阈值上方的合同必须走 EU 全范围公开
程序（TED 公告、电子提交、更长公告期），下方只需国内程序。断点两侧合同
基本面连续 → 断点跳跃 = 更严格的电子披露程序的边际效应。识别来自法律
断点，不依赖国家处理变异。

用法：python identification/run_v6.py
"""
import csv, io, os, sys, json, zipfile
import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'identification'))
from estimators_v4 import demean, wls_cluster

TED = os.path.join(BASE, 'data', 'external', 'ted')

ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}

# EU 阈值（EUR，excl. VAT）：sub-central 货物/服务 + 工程
# 来源：Directive 2014/24/EU Art.4；Delegated Regulations (EU) 2017/2365,
# 2019/1828, 2021/2170；2013 用 Directive 2004/18/EC
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


def extract(band=0.20):
    """流式提取阈值附近 ±band 的合同（仅读本地 zip）。"""
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
                rows.append({
                    'code': code, 'year': fy, 'type': tc,
                    'value': v, 'log_value': np.log(v),
                    'r': np.log(v) - np.log(thr),
                    'above': 1 if v >= thr else 0,
                    'n_offers': n,
                    'single': 1 if (n is not None and n == 1) else 0,
                    'elec_share': (ne / n) if (n and n >= 1 and ne is not None) else np.nan,
                    'out_of_directives': 1 if (row.get('OUT_OF_DIRECTIVES') or '0').strip() == '1' else 0,
                    'eu_funds': 1 if (row.get('B_EU_FUNDS') or '0').strip() == '1' else 0,
                    'elec_auction': 1 if (row.get('B_ELECTRONIC_AUCTION') or '0').strip() == '1' else 0,
                    'foreign_win': 1 if (wcc and wcc != (row.get('ISO_COUNTRY_CODE') or '').strip().upper()) else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                })
    return pd.DataFrame(rows)


def rd_estimate(d, outcome, poly=1, controls=('log_value',), fe_groups=('cy', 'type')):
    """局部多项式 RD：Y ~ above + poly(r) + above×poly(r) + controls + FE。"""
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
            'ci': [float(r_['ci_lo'][i]), float(r_['ci_hi'][i])], 'n': r_['n']}


def density_test(d, binwidth=0.02):
    """McCrary 式密度检验：断点两侧 log 密度差 + 二项检验。"""
    dd = d.dropna(subset=['r']).copy()
    dd['bin'] = np.floor(dd['r'] / binwidth).astype(int)
    g = dd.groupby(['bin', 'above']).size().unstack(fill_value=0)
    left = g[g.index <= -1].sum().sum()
    right = g[g.index >= 1].sum().sum()
    n_left_bins = (g.index <= -1).sum()
    n_right_bins = (g.index >= 1).sum()
    dens_l = left / max(n_left_bins, 1)
    dens_r = right / max(n_right_bins, 1)
    p = stats.binomtest(int(right), int(left + right), 0.5).pvalue
    return {'log_density_gap': float(np.log((dens_r + 1) / (dens_l + 1))),
            'p_binom': float(p), 'n_left': int(left), 'n_right': int(right),
            'note': '断点两侧密度若显著不等 → 操纵/选择证据'}


def placebo_cutoffs(d, outcome, cutoffs=(0.7, 0.8, 1.2, 1.3), poly=1):
    """安慰剂断点：在真实阈值 ×cutoff 处放假断点，应无跳跃。"""
    out = {}
    thr_at = np.exp(np.log(d['value']) - d['r'])   # 该国年型真实阈值
    for c in cutoffs:
        d2 = d.copy()
        d2['above'] = (d2['value'] >= thr_at * c).astype(int)
        d2['r'] = np.log(d2['value']) - np.log(thr_at * c)
        r = rd_estimate(d2, outcome, poly=poly)
        out[str(c)] = {'tau': r.get('tau'), 'p': r.get('p')}
    return out


def main():
    OUT = os.path.join(BASE, 'report')
    os.makedirs(OUT, exist_ok=True)
    R = {'design': 'EU procurement threshold sharp RD',
         'thresholds': {str(k): list(v) for k, v in THRESH.items()},
         'threshold_source': 'Directive 2014/24/EU Art.4; Commission Delegated '
                             'Regulations (EU) 2017/2365, 2019/1828, 2021/2170; '
                             '2013: Directive 2004/18/EC'}

    # ---------- 1. 提取（±20% 主带宽）----------
    print('[1] 提取阈值附近合同（±20%）…')
    d = extract(band=0.20)
    d['log_offers'] = np.log1p(d['n_offers'].fillna(0))
    R['n_contracts'] = int(len(d))
    R['n_above'] = int(d['above'].sum())
    R['n_below'] = int((d['above'] == 0).sum())
    R['countries'] = int(d['code'].nunique())
    R['ood_below'] = float(d[d['above'] == 0]['out_of_directives'].mean())
    print(f"    合同 {len(d):,} | 上 {d['above'].sum():,} | 下 {(d['above']==0).sum():,} "
          f"| 国 {d['code'].nunique()}")
    print(f"    阈值下 OUT_OF_DIRECTIVES=1 占比: {R['ood_below']:.3f}（自愿公告程度）")

    # ---------- 2. 密度检验 ----------
    print('[2] 断点密度检验…')
    dens = density_test(d)
    R['density'] = dens
    print(f"    log 密度差 {dens['log_density_gap']:+.4f}, 二项 p={dens['p_binom']:.4f}")

    # ---------- 3. 主 RD 估计 ----------
    print('[3] 主 RD（局部线性，country×year + type FE，聚类国家）…')
    R['main'] = {}
    for oc in ['single', 'log_offers', 'elec_share', 'foreign_win']:
        r = rd_estimate(d, oc, poly=1)
        R['main'][oc] = r
        if 'error' not in r:
            print(f"    {oc:14s}: τ={r['tau']:+.4f} (p={r['p']:.3f}, "
                  f"CI [{r['ci'][0]:.4f}, {r['ci'][1]:.4f}], n={r['n']})")
        else:
            print(f'    {oc}: {r["error"]}')

    # ---------- 4. 带宽敏感性 ----------
    print('[4] 带宽敏感性…')
    R['bandwidth'] = {}
    for band in (0.10, 0.15, 0.20, 0.25):
        db = extract(band=band)
        db['log_offers'] = np.log1p(db['n_offers'].fillna(0))
        row = {}
        for oc in ['single', 'log_offers']:
            r = rd_estimate(db, oc, poly=1)
            row[oc] = {'tau': r.get('tau'), 'p': r.get('p'), 'n': r.get('n')}
        R['bandwidth'][str(band)] = row
        print(f"    ±{int(band*100)}%: single τ={row['single']['tau']:+.4f} "
              f"(p={row['single']['p']:.3f}) | log_offers τ={row['log_offers']['tau']:+.4f} "
              f"(p={row['log_offers']['p']:.3f}) | n={row['single']['n']}")

    # ---------- 5. 多项式阶数 ----------
    print('[5] 多项式阶数…')
    R['poly'] = {}
    for p in (1, 2):
        r = rd_estimate(d, 'single', poly=p)
        R['poly'][str(p)] = {'tau': r.get('tau'), 'p': r.get('p')}
        print(f"    p={p}: single τ={r['tau']:+.4f} (p={r['p']:.3f})")

    # ---------- 6. 安慰剂断点 ----------
    print('[6] 安慰剂断点（0.7/0.8/1.2/1.3 × 阈值）…')
    pl = placebo_cutoffs(d, 'single')
    R['placebo'] = pl
    print('    ', {k: (round(v['tau'], 4) if v['tau'] is not None else None,
                       round(v['p'], 3) if v['p'] is not None else None)
                 for k, v in pl.items()})

    # ---------- 7. 判定 ----------
    v = {}
    for oc, r in R['main'].items():
        if 'error' in r:
            v[oc] = 'uncertain'
        elif r['ci'][0] > 0 or r['ci'][1] < 0:
            v[oc] = ('significant_negative' if r['tau'] < 0 else 'significant_positive')
        else:
            v[oc] = 'null'
    if dens['p_binom'] < 0.05:
        v['density_alarm'] = '断点处密度显著异常 → 全部结论降级'
    R['verdict'] = v
    print('[7] 判定:', v)

    with open(os.path.join(OUT, 'results_v6.json'), 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
    print(f'已写 {os.path.join(OUT, "results_v6.json")}')


if __name__ == '__main__':
    main()

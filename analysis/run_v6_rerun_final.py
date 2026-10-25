"""第六轮复核（最终版）：从原始 TED CAN 数据 + 法定阈值 + 正确的估值字段，完整重跑 v6.0。

关键修正（相对前几轮）：
  1. 阈值用法定值（2013 €200,000/€5,000,000；2014-15 €207,000/€5,186,000；
     2016-17 €209,000/€5,225,000；2018-23 原值即正确）。
  2. 估值字段用 VALUE_EURO（公告级总估值，覆盖率 95.4%）——经比对确认这才是
     原分析缓存 rd_sample_cache.csv 中 value_est 的实际来源；
     AWARD_EST_VALUE_EURO 覆盖率仅 49.6%，是另一个字段。
  3. 带口径用值空间 |v/τ−1| ≤ 0.2，与 run_v6.py extract() 一致（对数带另报）。

用法：python analysis/run_v6_rerun_final.py
输出：materials/results/v6_rerun_final.json
      analysis/ted_wide_final.csv（提取缓存）
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
OUT = os.path.join(ROOT, 'materials', 'results', 'v6_rerun_final.json')
CACHE = os.path.join(HERE, 'ted_wide_final.csv')
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


def extract():
    if os.path.exists(CACHE):
        print(f'读取缓存 {CACHE}')
        return pd.read_csv(CACHE)
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
                ve = fnum(row.get('VALUE_EURO'))          # 公告级总估值（原分析所用字段）
                ve2 = fnum(row.get('AWARD_EST_VALUE_EURO'))  # 授标估值（另一个字段）
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
                    'value_est_award': ve2 if (ve2 is not None and ve2 > 0) else np.nan,
                    'sme_tenders': fnum(row.get('NUMBER_TENDERS_SME')),
                    'foreign_win': 1 if (wcc and wcc != (row.get('ISO_COUNTRY_CODE') or '').strip().upper()) else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                })
    df = pd.DataFrame(rows)
    df['log_offers'] = np.log1p(df['n_offers'].fillna(0))
    df.to_csv(CACHE, index=False)
    print(f'已提取并缓存 {len(df):,} 行 -> {CACHE}')
    return df


def band_value(d, band):
    return d[(np.exp(d['r']) - 1).abs() <= band + 1e-9].copy()


def band_log(d, band):
    return d[d['r'].abs() <= band + 1e-9].copy()


def rd(d, outcome, poly=1, controls=('log_value', 'tu', 'tw'), bandkind='value'):
    """country×year 去模 + 国家聚类；controls ∈ () / ('log_value',) / ('tu','tw') / 全。"""
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
    df = extract()
    d20 = band_value(df, 0.20)
    R = {'thresholds': {str(k): list(v) for k, v in THRESH.items()},
         'n_band20_value': int(len(d20)),
         'n_band20_log': int(len(band_log(df, 0.20))),
         'value_est_field': 'VALUE_EURO (notice-level total estimated value)'}
    print(f"±20% 值空间带 n={len(d20):,} | 对数带 n={R['n_band20_log']:,}")

    # ---------- 主表 ----------
    print('[1] 主表…')
    R['main'] = {}
    for oc in ['single', 'log_offers', 'elec_share', 'foreign_win']:
        R['main'][oc] = {'prereg': rd(d20, oc),
                         'type_only': rd(d20, oc, controls=('tu', 'tw')),
                         'none': rd(d20, oc, controls=())}
        v = R['main'][oc]
        print(f"   {oc:12s} prereg {v['prereg']['tau_pp']:+.2f}(p{v['prereg']['p']:.3f}) "
              f"type {v['type_only']['tau_pp']:+.2f}(p{v['type_only']['p']:.3f}) "
              f"none {v['none']['tau_pp']:+.2f}(p{v['none']['p']:.3f})")

    # ---------- donut ----------
    print('[2] donut（无控制）…')
    R['donut'] = {'baseline': rd(d20, 'single', controls=())}
    for w in (0.01, 0.02, 0.03):
        R['donut'][f'donut{int(w*100):02d}'] = rd(d20[d20['r'].abs() > w], 'single', controls=())
    for k, v in R['donut'].items():
        print(f"   {k:10s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f}, n {v['n']:,})")

    # ---------- 控制集网格 ----------
    print('[3] 控制集网格…')
    R['grid'] = {}
    for ctl, cols in [('none', ()), ('logval', ('log_value',)),
                      ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
        g = {'baseline': rd(d20, 'single', controls=cols)}
        for w in (0.01, 0.02, 0.03):
            g[f'donut{int(w*100):02d}'] = rd(d20[d20['r'].abs() > w], 'single', controls=cols)
        R['grid'][ctl] = g
        print(f"   {ctl:7s} " + ' | '.join(f"{k}={v['tau_pp']:+.2f}(p{v['p']:.3f})" for k, v in g.items()))

    # ---------- 带宽 × 阶数 ----------
    print('[4] 带宽 × 阶数（type 控制）…')
    R['bw_poly'] = {}
    for bw in (0.10, 0.15, 0.20, 0.25):
        db = band_value(df, bw)
        R['bw_poly'][f'bw{int(bw*100)}_lin'] = rd(db, 'single', controls=('tu', 'tw'))
        R['bw_poly'][f'bw{int(bw*100)}_quad'] = rd(db, 'single', poly=2, controls=('tu', 'tw'))
        print(f"   ±{int(bw*100):2d}%  lin {R['bw_poly'][f'bw{int(bw*100)}_lin']['tau_pp']:+.2f}"
              f"(p{R['bw_poly'][f'bw{int(bw*100)}_lin']['p']:.3f})"
              f"  quad {R['bw_poly'][f'bw{int(bw*100)}_quad']['tau_pp']:+.2f}"
              f"(p{R['bw_poly'][f'bw{int(bw*100)}_quad']['p']:.3f})"
              f"  n={R['bw_poly'][f'bw{int(bw*100)}_lin']['n']:,}")

    # ---------- 密度审计 ----------
    print('[5] 密度审计…')
    r = d20['r'].values
    BW = 0.02
    bins = np.arange(-12, 10)
    b = np.floor(r / BW).astype(int)
    cnt = pd.Series(b).value_counts()
    n = np.array([cnt.get(k, 0) for k in bins], dtype=float)
    L = n[bins <= -1].sum(); Rr = n[bins >= 1].sum()
    gap = math.log((Rr / 9 + 1) / (L / 12 + 1))
    fL = (-0.22 - math.log(0.8)) / BW
    fR = (math.log(1.2) - 0.18) / BW
    fullL = n[(bins <= -1) & (bins >= -11)]
    fullR = n[(bins >= 0) & (bins <= 8)]
    dnull = (fullL.sum() + fullR.sum()) / (len(fullL) + len(fullR))
    gap_null = math.log(((8 + fR) * dnull / 9 + 1) / ((11 + fL) * dnull / 12 + 1))
    ratio_null = ((11 + fL) / 12) / ((8 + fR) / 9)
    mL, mR = fullL.mean(), fullR.mean()
    sL, sR = fullL.std(ddof=1), fullR.std(ddof=1)
    se = math.sqrt(sL**2 / len(fullL) + sR**2 / len(fullR))
    t = (mR - mL) / se
    mp = int(((r >= 0) & (r < 1e-4)).sum())
    mpb = int(((r < 0) & (r >= -1e-4)).sum())
    n_ex = n.copy(); n_ex[bins == 0] -= mp; n_ex[bins == -1] -= mpb
    mL_ex = n_ex[(bins <= -1) & (bins >= -11)].mean()
    mR_ex = n_ex[(bins >= 0) & (bins <= 8)].mean()
    centers = (bins + 0.5) * BW
    cl_ = centers[(bins >= -11) & (bins <= -1)]
    cr_ = centers[(bins >= 0) & (bins <= 8)]

    def lin(cx, cy):
        A = np.vstack([cx, np.ones_like(cx)]).T
        co, *_ = np.linalg.lstsq(A, np.log(cy), rcond=None)
        return co
    bl = lin(cl_, fullL); br = lin(cr_, fullR)
    pl = math.exp(bl[0] * (-0.01) + bl[1])
    pr = math.exp(br[0] * (0.01) + br[1])
    cell = (d20['code'].astype(str) + '_' + d20['year'].astype(str) + '_' + d20['type'].astype(str)).values
    cells = pd.unique(cell)
    ci = {c: np.where(cell == c)[0] for c in cells}
    rng = np.random.default_rng(42)
    gaps, shares = [], []
    for _ in range(2000):
        pick = rng.choice(cells, size=len(cells), replace=True)
        idx = np.concatenate([ci[c] for c in pick])
        bb = np.floor(r[idx] / BW).astype(int)
        c2 = pd.Series(bb).value_counts()
        nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
        Lx = nn[bins <= -1].sum(); Rx = nn[bins >= 1].sum()
        gaps.append(math.log((Rx / 9 + 1) / (Lx / 12 + 1)))
        shares.append(Lx / (Lx + Rx))
    gaps = np.array(gaps); shares = np.array(shares)
    z_gap = (gap - gap_null) / gaps.std()
    z_sh = (L / (L + Rr) - 12 / 21) / shares.std()
    mpd = d20[(d20['r'] >= 0) & (d20['r'] < 1e-4)]
    thr_mp = np.exp(np.log(mpd['value']) - mpd['r'])
    mpd_sub = mpd.dropna(subset=['value_est'])
    full_sub = d20.dropna(subset=['value_est'])
    R['density'] = {
        'left_contracts': int(L), 'right_contracts': int(Rr),
        'log_density_gap': round(gap, 5),
        'excess_below_pct': round(L / 12 / (Rr / 9) - 1, 5),
        'mechanical_log_gap': round(gap_null, 5),
        'bias_corrected_excess_below_pct': round((L / 12 / (Rr / 9)) / ratio_null - 1, 5),
        'symmetric_full_bins': {'below_mean': round(float(mL), 1), 'above_mean': round(float(mR), 1),
                                't_stat': round(float(t), 3),
                                'p_value': round(float(2 * stats.t.sf(abs(t), 18)), 4)},
        'mccrary_ratio': round(pl / pr, 4),
        'ex_masspoint': {'below_mean': round(float(mL_ex), 1), 'above_mean': round(float(mR_ex), 1),
                         'above_over_below': round(mR_ex / mL_ex, 4)},
        'binom_p_correct_null': round(float(2 * stats.norm.sf(abs(z_sh))), 4),
        'p_loggap_vs_mechanical': round(float(2 * stats.norm.sf(abs(z_gap))), 4),
        'bin_minus1': int(n[bins == -1][0]), 'bin_0': int(n[bins == 0][0]),
        'masspoint': mp, 'masspoint_exact': int((mpd['value'].round(0) == thr_mp.round(0)).sum()),
        'masspoint_share_pct': round(mp / len(d20) * 100, 2),
        'masspoint_deu_pct': round(float((mpd['code'] == 'DEU').mean() * 100), 1),
        'masspoint_award_eq_est_pct': round(float((mpd_sub['value'] == mpd_sub['value_est']).mean() * 100), 1),
        'full_award_eq_est_pct': round(float((full_sub['value'] == full_sub['value_est']).mean() * 100), 1),
        'n_cells': int(len(cells)),
    }
    print('   ', json.dumps(R['density'], ensure_ascii=False)[:520])

    # ---------- 估计价值 RD（VALUE_EURO） ----------
    print('[6] 估计价值 RD（VALUE_EURO，两种带 × 控制集）…')
    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
    clean['thr'] = np.exp(np.log(clean['value']) - clean['r'])
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    est = pd.DataFrame({'r': clean['r_est'].values, 'above': clean['above_est'].values,
                        'single': clean['single'].values, 'log_value': clean['log_value'].values,
                        'type': clean['type'].values, 'code': clean['code'].values,
                        'year': clean['year'].values, 'value': clean['value'].values})
    R['est_value'] = {
        'n_populated': int(df['value_est'].notna().sum()),
        'coverage_pct': round(float(df['value_est'].notna().mean() * 100), 1),
        'n_clean': int(len(clean)),
        'clean_share_pct': round(len(clean) / max(int(df['value_est'].notna().sum()), 1) * 100, 1),
    }
    for bn, bf in [('value20', band_value), ('log20', band_log)]:
        cest = bf(est, 0.20)
        R['est_value'][bn] = {'n_band': int(len(cest))}
        for ctl, cols in [('none', ()), ('logval', ('log_value',)),
                          ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
            R['est_value'][bn][ctl] = rd(cest, 'single', controls=cols)
        print(f"   {bn} (n={len(cest):,}): " +
              ' | '.join(f"{c}={R['est_value'][bn][c]['tau_pp']:+.2f}(p{R['est_value'][bn][c]['p']:.3f})"
                         for c in ('none', 'logval', 'type', 'prereg')))

    # ---------- 数字化分组 ----------
    print('[7] 数字化分组…')
    obs = d20.dropna(subset=['elec_share'])
    med = float(obs['elec_share'].median())
    R['digital_split'] = {'median_elec_share': round(med, 4), 'n_observed': int(len(obs)),
                          'note': '合同级电子报价份额中位数；>1.0 的 198 条为 NUMBER_OFFERS_ELECTR>NUMBER_OFFERS 的数据异常'}
    for lab, mask in [('high', obs['elec_share'] > med), ('low', obs['elec_share'] <= med)]:
        R['digital_split'][lab] = rd(obs[mask], 'single')
        print(f"   {lab:5s} {R['digital_split'][lab]['tau_pp']:+.2f} "
              f"(p {R['digital_split'][lab]['p']:.3f}, n {R['digital_split'][lab]['n']:,})")

    # ---------- 价格边际 ----------
    print('[8] 价格边际…')
    dd = d20.dropna(subset=['value', 'value_est']).copy()
    dd = dd[(dd['value'] / dd['value_est'] >= 0.5) & (dd['value'] / dd['value_est'] <= 2.0)].copy()
    dd['discount'] = (dd['value_est'] - dd['value']) / dd['value_est']
    R['price_margin'] = {
        'n_populated': int(d20['value_est'].notna().sum()),
        'coverage_pct': round(float(d20['value_est'].notna().mean() * 100), 1),
        'n_clean': int(len(dd)),
        'clean_share_pct': round(len(dd) / max(int(d20['value_est'].notna().sum()), 1) * 100, 1),
        'single_mean_pct': round(float(dd.loc[dd['single'] == 1, 'discount'].mean() * 100), 2),
        'multi_mean_pct': round(float(dd.loc[dd['single'] == 0, 'discount'].mean() * 100), 2),
        'n_single': int((dd['single'] == 1).sum()), 'n_multi': int((dd['single'] == 0).sum()),
    }
    v = rd(dd, 'discount')
    R['price_margin']['discount_rd'] = v
    print('   ', json.dumps(R['price_margin'], ensure_ascii=False))

    # ---------- placebo 诊断 ----------
    print('[9] placebo 断点诊断…')
    thr_at = np.exp(np.log(d20['value']) - d20['r'])
    R['placebo'] = {}
    for c in (0.7, 0.8, 1.2, 1.3):
        nb = int((d20['value'] < thr_at * c).sum())
        na = int((d20['value'] >= thr_at * c).sum())
        R['placebo'][str(c)] = {'n_below': nb, 'n_above': na,
                                'minority_share_pct': round(min(nb, na) / (nb + na) * 100, 4)}
        print(f"   {c}: below={nb:,} above={na:,} 少数侧={R['placebo'][str(c)]['minority_share_pct']}%")

    # ---------- 样本构成 ----------
    R['composition'] = {
        'n_above': int(d20['above'].sum()), 'n_below': int((d20['above'] == 0).sum()),
        'countries': int(d20['code'].nunique()),
        'ood_below': round(float(d20[d20['above'] == 0]['out_of_directives'].mean()), 4),
        'mean_offers_below': round(float(d20.loc[d20['above'] == 0, 'n_offers'].mean()), 2),
        'mean_offers_above': round(float(d20.loc[d20['above'] == 1, 'n_offers'].mean()), 2),
        'share_ge3_below': round(float((d20.loc[d20['above'] == 0, 'n_offers'].fillna(0) >= 3).mean() * 100), 1),
        'share_ge3_above': round(float((d20.loc[d20['above'] == 1, 'n_offers'].fillna(0) >= 3).mean() * 100), 1),
    }
    print('   ', json.dumps(R['composition'], ensure_ascii=False))

    json.dump(R, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

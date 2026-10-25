"""第六轮复核（续）：用原始 TED 数据 + 法定阈值，补齐 v6.0 其余诊断。

run_v6_full_rerun.py 已给出主表/带宽/阶数/placebo。本脚本补齐：
  1. 密度审计（机械零值、对称满箱、McCrary 外推、质量点、cluster bootstrap）
  2. donut（论文 Table 6 口径：无 type FE，country×year 去模，国家聚类）
  3. 控制集网格（none / logval / type / type+cpv）×（baseline + donut + est-value）
  4. Figure 4 网格（带宽 × 阶数，type 控制）
  5. 数字化分组
  6. 价格边际
  7.  placebo 断点的少数侧构成（证明结构性退化）
输出 materials/results/v6_full_rerun_diagnostics.json
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
OUT = os.path.join(ROOT, 'materials', 'results', 'v6_full_rerun_diagnostics.json')
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


def band_of(d, band):
    ratio = np.exp(d['r'])
    return d[(ratio - 1).abs() <= band + 1e-9].copy()


def rd_nofe(d, outcome, poly=1, controls=(), cluster='code'):
    """论文 Table 6 口径：country×year 去模（不含 type FE）+ 国家聚类。"""
    dd = d.dropna(subset=[outcome, 'r']).copy()
    if len(dd) < 100:
        return {'error': '样本不足'}
    # 先建类型虚拟列，再统一进 controls 循环
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
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


def main():
    print('提取原始数据（法定阈值，±40% 带）…')
    df = extract_wide()
    d20 = band_of(df, 0.20)
    print(f'  ±20% 带 n={len(d20):,}')

    R = {'thresholds': {str(k): list(v) for k, v in THRESH.items()},
         'n_band20': int(len(d20))}

    # ---------- 1. 密度审计 ----------
    print('[1] 密度审计…')
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
    gaps = []
    for _ in range(2000):
        pick = rng.choice(cells, size=len(cells), replace=True)
        idx = np.concatenate([ci[c] for c in pick])
        bb = np.floor(r[idx] / BW).astype(int)
        c2 = pd.Series(bb).value_counts()
        nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
        Lx = nn[bins <= -1].sum(); Rx = nn[bins >= 1].sum()
        gaps.append(math.log((Rx / 9 + 1) / (Lx / 12 + 1)))
    gaps = np.array(gaps)
    z_gap = (gap - gap_null) / gaps.std()
    obs_share = L / (L + Rr)
    shares = []
    for _ in range(2000):
        pick = rng.choice(cells, size=len(cells), replace=True)
        idx = np.concatenate([ci[c] for c in pick])
        bb = np.floor(r[idx] / BW).astype(int)
        c2 = pd.Series(bb).value_counts()
        nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
        Lx = nn[bins <= -1].sum(); Rx = nn[bins >= 1].sum()
        shares.append(Lx / (Lx + Rx))
    shares = np.array(shares)
    z_sh = (obs_share - 12 / 21) / shares.std()
    mpd = d20[(d20['r'] >= 0) & (d20['r'] < 1e-4)]
    sub = mpd.dropna(subset=['value_est'])
    R['density_audit'] = {
        'n_band': int(len(d20)),
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
        'masspoint': mp, 'masspoint_exact': int((d20['value'] == np.exp(d20['r'] * 0 + np.log(d20['value']) - d20['r'])).sum()),
        'masspoint_share_pct': round(mp / len(d20) * 100, 2),
        'masspoint_deu_pct': round(float((mpd['code'] == 'DEU').mean() * 100), 1) if len(mpd) else None,
        'masspoint_award_eq_est_pct': round(float((sub['value'] == sub['value_est']).mean() * 100), 1) if len(sub) else None,
        'n_cells': int(len(cells)),
    }
    print('   ', json.dumps({k: v for k, v in R['density_audit'].items()
                             if k not in ('masspoint_exact',)}, ensure_ascii=False)[:600])

    # ---------- 2. donut（Table 6 口径） ----------
    print('[2] donut（无 type FE，国家聚类）…')
    R['donut_table6'] = {'baseline': rd_nofe(d20, 'single')}
    for w in (0.01, 0.02, 0.03):
        dd = d20[d20['r'].abs() > w]
        R['donut_table6'][f'donut{int(w*100):02d}'] = rd_nofe(dd, 'single')
    for k, v in R['donut_table6'].items():
        print(f"    {k:10s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p {v['p']:.3f}, n {v['n']:,})")

    # ---------- 3. 控制集网格 ----------
    print('[3] 控制集网格…')
    grid = {}
    for ctl, cols in [('none', ()), ('logval', ('log_value',)),
                      ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
        g = {'baseline': rd_nofe(d20, 'single', controls=cols)}
        for w in (0.01, 0.02, 0.03):
            dd = d20[d20['r'].abs() > w]
            g[f'donut{int(w*100):02d}'] = rd_nofe(dd, 'single', controls=cols)
        grid[ctl] = g
    # 估计价值
    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
    clean['thr'] = np.exp(np.log(clean['value']) - clean['r'])
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    cest = band_of(clean, 0.20)
    for ctl, cols in [('none', ()), ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
        grid[ctl]['est_value'] = rd_nofe(cest.assign(r= cest['r_est'], above=cest['above_est']),
                                         'single', controls=cols)
    R['control_grid'] = grid
    R['est_value_meta'] = {'n_populated': int(df['value_est'].notna().sum()),
                           'coverage_pct': round(float(df['value_est'].notna().mean() * 100), 1),
                           'n_clean': int(len(clean)), 'n_band': int(len(cest))}
    for ctl, g in grid.items():
        print(f"    {ctl:7s} " + ' | '.join(f"{k}={v['tau_pp']:+.2f}(p{v['p']:.3f})" for k, v in g.items()))

    # ---------- 4. Figure 4 网格 ----------
    print('[4] 带宽 × 阶数（type 控制）…')
    bw_poly = {}
    for bw in (0.10, 0.15, 0.20, 0.25):
        db = band_of(df, bw)
        bw_poly[f'bw{int(bw*100)}_lin'] = rd_nofe(db, 'single', controls=('tu', 'tw'))
        dd = db.dropna(subset=['single', 'r']).copy()
        dd['tu'] = (dd['type'] == 'U').astype(float)
        dd['tw'] = (dd['type'] == 'W').astype(float)
        y = dd['single'].astype(float).values
        parts = [dd[['above']].astype(float).values]
        names = ['tau']
        rv = dd['r'].values
        for j in (1, 2):
            parts.append((rv ** j)[:, None]); names.append(f'r{j}')
            parts.append((dd['above'].values * (rv ** j))[:, None]); names.append(f'above_r{j}')
        parts.append(dd[['tu']].astype(float).values); names.append('tu')
        parts.append(dd[['tw']].astype(float).values); names.append('tw')
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
        nn, kk = Xd.shape
        XtXi = np.linalg.inv(Xd.T @ Xd)
        cl = dd['code'].values
        G = len(np.unique(cl))
        meat = np.zeros((kk, kk))
        for g in np.unique(cl):
            m = cl == g
            meat += np.outer(Xd[m].T @ resid[m], Xd[m].T @ resid[m])
        V = XtXi @ meat @ XtXi * (G / (G - 1) * (nn - 1) / (nn - kk))
        se2 = np.sqrt(np.diag(V))
        tau2, s2 = beta[1], se2[1]
        bw_poly[f'bw{int(bw*100)}_quad'] = {
            'tau_pp': round(float(tau2) * 100, 2), 'se_pp': round(float(s2) * 100, 2),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau2 / s2), G - 1))), 4), 'n': int(nn)}
    R['bandwidth_poly_type'] = bw_poly
    for k, v in bw_poly.items():
        print(f"    {k:12s} {v['tau_pp']:+.2f} (p {v['p']:.3f}, n {v['n']:,})")

    # ---------- 5. 数字化分组 ----------
    print('[5] 数字化分组…')
    med = d20['elec_share'].median()
    R['digital_split'] = {}
    for lab, mask in [('high', d20['elec_share'] > med), ('low', d20['elec_share'] <= med)]:
        R['digital_split'][lab] = rd_nofe(d20[mask], 'single')
        print(f"    {lab:5s} {R['digital_split'][lab]['tau_pp']:+.2f} "
              f"(p {R['digital_split'][lab]['p']:.3f}, n {R['digital_split'][lab]['n']:,})")

    # ---------- 6. 价格边际 ----------
    print('[6] 价格边际…')
    dd = d20.dropna(subset=['value', 'value_est']).copy()
    dd['discount'] = (dd['value_est'] - dd['value']) / dd['value_est']
    R['price_margin'] = {
        'n_with_both': int(len(dd)),
        'coverage_pct': round(len(dd) / len(d20) * 100, 1),
        'single_mean': round(float(dd.loc[dd['single'] == 1, 'discount'].mean() * 100), 2),
        'multi_mean': round(float(dd.loc[dd['single'] == 0, 'discount'].mean() * 100), 2),
        'n_single': int((dd['single'] == 1).sum()), 'n_multi': int((dd['single'] == 0).sum()),
    }
    print('   ', R['price_margin'])

    # ---------- 7. placebo 少数侧构成 ----------
    print('[7] placebo 少数侧构成…')
    thr_at = np.exp(np.log(d20['value']) - d20['r'])
    R['placebo_minority'] = {}
    for c in (0.7, 0.8, 1.2, 1.3):
        nb = int((d20['value'] < thr_at * c).sum())
        na = int((d20['value'] >= thr_at * c).sum())
        R['placebo_minority'][str(c)] = {'n_below': nb, 'n_above': na,
                                         'minority_share_pct': round(min(nb, na) / (nb + na) * 100, 4)}
        print(f"    {c}: below={nb:,} above={na:,} 少数侧={R['placebo_minority'][str(c)]['minority_share_pct']}%")

    json.dump(R, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

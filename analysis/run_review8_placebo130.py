"""第八轮：130% placebo 异常的完整诊断。

审稿意见 1：130% 安慰剂断点估计 −1.15pp（p=0.004，过 Bonferroni）。
需要：(a) binscatter 看 1.3τ 附近分布形态；
(b) 样本构成（类型/国家/年份）分解；
(c) 带宽 × 函数形式 × donut × 留一国网格；
(d) 若异常仍在，如实写"主 RD 因果识别可信度不足"。
"""
import csv, io, json, os, sys, zipfile
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

THRESH = {2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
          2016: (209000, 5225000), 2017: (209000, 5225000), 2018: (221000, 5548000),
          2019: (221000, 5548000), 2020: (214000, 5350000), 2021: (214000, 5350000),
          2022: (215000, 5382000), 2023: (215000, 5382000)}
ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}
WIDE = 0.40
TOL = 1e-9


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def extract_wide():
    """从原始 TED CAN 提取 ±40% 带（法定阈值）。"""
    TED = os.path.join(ROOT, 'data', 'external', 'ted')
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
                wcc = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                iso = (row.get('ISO_COUNTRY_CODE') or '').strip().upper()
                rows.append({
                    'code': code, 'year': fy, 'type': tc, 'value': v,
                    'log_value': np.log(v), 'r': np.log(v) - np.log(thr),
                    'above': 1 if v >= thr else 0,
                    'n_offers': n,
                    'single': 1 if (n is not None and n == 1) else 0,
                    'elec_share': (ne / n) if (n and n >= 1 and ne is not None) else np.nan,
                    'value_est': fnum(row.get('VALUE_EURO')),
                    'sme_tenders': fnum(row.get('NUMBER_TENDERS_SME')),
                    'foreign_win': 1 if (wcc and wcc != iso) else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                })
    df = pd.DataFrame(rows)
    df['log_offers'] = np.log1p(df['n_offers'].fillna(0))
    return df


def load():
    cache = os.path.join(HERE, 'ted_wide_final.csv')
    if os.path.exists(cache):
        return pd.read_csv(cache)
    df = extract_wide()
    df.to_csv(cache, index=False)
    return df


def band_around(d, center, bw, metric='ratio'):
    """以 center × 阈值为断点、±bw 的带。center=1.3 即 130% placebo。"""
    if metric == 'ratio':
        return d[((np.exp(d['r']) / center) - 1).abs() <= bw + TOL].copy()
    return d[((d['r'] - np.log(center))).abs() <= bw + TOL].copy()


def rd_est(d, outcome='single', poly=1, controls=(), cluster='code', cutoff=None):
    """局部线性/多项式 RD，国家×年份去模，国家聚类 SE。

    cutoff=None 时用真实阈值（r=0）；否则以 r - log(cutoff) 为 running var。
    """
    dd = d.dropna(subset=[outcome, 'r']).copy()
    if len(dd) < 50:
        return {'error': '样本不足', 'n': int(len(dd))}
    if cutoff is not None:
        dd['r'] = dd['r'] - np.log(cutoff)
    dd['above'] = (dd['r'] >= 0).astype(int)
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax1'] = dd['above'] * dd['r']
    xcols = ['above', 'r']
    for j in range(2, poly + 1):
        dd[f'r{j}'] = dd['r'] ** j
        dd[f'ax{j}'] = dd['above'] * dd['r'] ** j
        xcols += [f'r{j}', f'ax{j}']
    for c in ('log_value', 'tu', 'tw'):
        if c in controls:
            xcols.append(c)
    y = dd[outcome].astype(float).values
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([pd.Series(y, index=dd.index).rename('y')] +
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
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(p), 4), 'n': int(n),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


def main():
    df = load()
    out = {}

    # ---------- 1. 130% 附近的 binscatter ----------
    b13 = band_around(df, 1.3, 0.25)
    BW = 0.02
    edges = np.arange(-0.25, 0.2501, BW)
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (b13['r'] >= lo + np.log(1.3) - 1e-9) & (b13['r'] < hi + np.log(1.3))
        if m.sum() > 0:
            bins.append({'center': round(float((lo + hi) / 2 + np.log(1.3)), 4),
                         'ratio_to_true_thr': round(float(np.exp((lo + hi) / 2 + np.log(1.3))), 4),
                         'n': int(m.sum()), 'single_share': round(float(b13.loc[m, 'single'].mean()), 5)})
    out['binscatter_130'] = bins

    # ---------- 2. 样本构成 ----------
    comp = {}
    for tag, d in [('full40', df), ('band130_20', band_around(df, 1.3, 0.20))]:
        below = d[d['r'] < np.log(1.3) - 1e-9]
        above = d[d['r'] >= np.log(1.3) - 1e-9]
        def side(x):
            tot = len(x)
            if tot == 0:
                return {}
            return {
                'n': int(tot),
                'type_S': round(float((x['type'] == 'S').mean()), 4),
                'type_U': round(float((x['type'] == 'U').mean()), 4),
                'type_W': round(float((x['type'] == 'W').mean()), 4),
                'share_2013_17': round(float((x['year'] <= 2017).mean()), 4),
                'share_DEU': round(float((x['code'] == 'DEU').mean()), 4),
                'top5_countries': [f'{c}:{round(float(v),3)}' for c, v in
                                   (x['code'].value_counts() / tot).head(5).items()],
                'mean_log_value': round(float(x['log_value'].mean()), 4),
                'median_value': float(x['value'].median()),
                'mean_n_offers': round(float(x['n_offers'].mean()), 3),
            }
        comp[tag] = {'below': side(below), 'above': side(above)}
    out['composition'] = comp

    # ---------- 3. 带宽 × 函数形式 × 控制集 ----------
    grid = {}
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        d = band_around(df, 1.3, bw)
        for poly in (1, 2, 3):
            for ctl, cname in [((), 'none'), (('log_value', 'tu', 'tw'), 'prereg')]:
                grid[f'bw{int(bw*100)}_p{poly}_{cname}'] = rd_est(
                    d, 'single', poly=poly, controls=ctl, cutoff=1.3)
    out['bandwidth_poly_controls'] = grid

    # ---------- 4. donut ----------
    donut = {}
    d20 = band_around(df, 1.3, 0.20)
    for w in (0.01, 0.02, 0.03, 0.05):
        dd = d20[((np.exp(dd_r := d20['r']) / 1.3) - 1).abs() > w + TOL] if False else \
             d20[(d20['r'] - np.log(1.3)).abs() > w + TOL]
        donut[f'donut{int(w*100):02d}'] = rd_est(dd, 'single', poly=1,
                                                  controls=('log_value', 'tu', 'tw'), cutoff=1.3)
    out['donut'] = donut

    # ---------- 5. 留一国 ----------
    loo = {}
    d20p = band_around(df, 1.3, 0.20)
    for c in sorted(d20p['code'].unique()):
        loo[c] = rd_est(d20p[d20p['code'] != c], 'single', poly=1,
                        controls=('log_value', 'tu', 'tw'), cutoff=1.3)
    out['leave_one_out'] = loo

    # ---------- 6. 逐年 × 类型 ----------
    by_yt = {}
    for y in sorted(d20p['year'].unique()):
        for t in ('S', 'U', 'W'):
            sub = d20p[(d20p['year'] == y) & (d20p['type'] == t)]
            if len(sub) >= 100:
                r = rd_est(sub, 'single', poly=1, controls=('log_value', 'tu', 'tw'), cutoff=1.3)
                by_yt[f'{y}_{t}'] = r
    out['by_year_type'] = by_yt

    # ---------- 7. 对照：真实阈值与其余三个 placebo 的同规格 ----------
    ctrl = {}
    for tag, cutoff in [('true_1.0', 1.0), ('placebo_0.7', 0.7), ('placebo_0.8', 0.8),
                        ('placebo_1.2', 1.2), ('placebo_1.3', 1.3)]:
        ctrl[tag] = {f'bw{int(bw*100)}_p{poly}': rd_est(band_around(df, cutoff, bw), 'single',
                                                        poly=poly, controls=('log_value', 'tu', 'tw'),
                                                        cutoff=cutoff)
                     for bw in (0.10, 0.20) for poly in (1, 2)}
    out['all_cutoffs_same_spec'] = ctrl

    json.dump(out, open(os.path.join(ROOT, 'materials', 'results', 'review8_placebo130.json'), 'w'),
              indent=1)

    # ---------- 摘要 ----------
    print('=== binscatter（1.3τ 断点附近，比值为对真实阈值）===')
    for b in bins:
        if 1.22 <= b['ratio_to_true_thr'] <= 1.38:
            print(f"  ratio {b['ratio_to_true_thr']:.3f}  n={b['n']:6d}  single={b['single_share']*100:.2f}%")
    print('\n=== 130% ±20% 带两侧构成 ===')
    for side in ('below', 'above'):
        c = comp['band130_20'][side]
        print(f"  {side}: n={c['n']} S/U/W={c['type_S']}/{c['type_U']}/{c['type_W']} "
              f"2013-17={c['share_2013_17']} DEU={c['share_DEU']} "
              f"meanlogval={c['mean_log_value']} medval={c['median_value']:,.0f} "
              f"meanoffers={c['mean_n_offers']}")
    print('\n=== 带宽 × 阶数 × 控制（130% 断点，主规格控制集）===')
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        row = []
        for poly in (1, 2, 3):
            r = grid[f'bw{int(bw*100)}_p{poly}_prereg']
            row.append(f"p{poly}={r['tau_pp']:+.2f}(p={r['p']:.3f},n={r['n']:,})")
        print(f"  ±{int(bw*100)}%: " + '  '.join(row))
    print('\n=== 无控制对照 ===')
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        row = [f"p{p}={grid[f'bw{int(bw*100)}_p{p}_none']['tau_pp']:+.2f}"
               f"(p={grid[f'bw{int(bw*100)}_p{p}_none']['p']:.3f})" for p in (1, 2, 3)]
        print(f"  ±{int(bw*100)}%: " + '  '.join(row))
    print('\n=== donut（130% ±20%，预注册控制）===')
    for k, v in donut.items():
        print(f"  {k}: {v['tau_pp']:+.2f} (p={v['p']:.4f}, n={v['n']:,})")
    print('\n=== 留一国（130% ±20%，预注册控制）===')
    vals = [(c, v['tau_pp'], v['p']) for c, v in loo.items() if 'tau_pp' in v]
    for c, t, p in sorted(vals, key=lambda x: x[1]):
        print(f"  drop {c}: {t:+.2f} (p={p:.3f})")
    print('\n=== 逐年 × 类型（前 12 个有效单元）===')
    for k, v in list(by_yt.items())[:12]:
        print(f"  {k}: {v['tau_pp']:+.2f} (p={v['p']:.3f}, n={v['n']:,})")
    print('\n=== 五个断点同规格对照（±20%, 线性, 预注册控制）===')
    for tag in ('true_1.0', 'placebo_0.7', 'placebo_0.8', 'placebo_1.2', 'placebo_1.3'):
        r = ctrl[tag]['bw20_p1']
        print(f"  {tag}: {r['tau_pp']:+.2f} (SE {r['se_pp']:.2f}, p={r['p']:.4f}, n={r['n']:,})")


if __name__ == '__main__':
    main()

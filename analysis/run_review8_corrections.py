"""第八轮补算：论文切换法定阈值口径后需要的新统计量。

1. 诊断家族的多重检验校正（法定阈值）：±1/2/3% donut + 估计价值 running
   variable，type 控制与无控制两档；Bonferroni + Holm（闭式）+ Romano-Wolf
   （国家聚类 bootstrap，复刻 run_review3.py 的 centered stepdown 方法）。
   估计价值用**值空间**窗口（与头条窗口口径一致）。
2. ±1% donut 的留一国家法（LOO，无控制，法定阈值）。
3. 对数窗口基线（法定阈值，四种控制集）——窗口口径 departure 的当前数据版。
4. 窗口分段（2013-2021 vs 2022-2023，法定阈值）。
5. 构成统计：2022-23 占比、报价数字段覆盖率。
6. 价格描述：阈值附近 S/U 合同的平均成交价 vs 平均程序估值。

输出 materials/results/review8_corrections.json
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
from estimators_v4 import demean, wls_cluster  # noqa

CACHE = os.path.join(HERE, 'ted_wide_final.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'review8_corrections.json')

THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def load():
    df = pd.read_csv(CACHE)
    su = df['year'].map(lambda y: THRESH[int(y)][0])
    w = df['year'].map(lambda y: THRESH[int(y)][1])
    df['thr'] = np.where(df['type'] == 'W', w, su).astype(float)
    df['tu'] = (df['type'] == 'U').astype(float)
    df['tw'] = (df['type'] == 'W').astype(float)
    return df


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw')):
    """cy 去均值 + tu/tw 哑变量 + 国家聚类（小样本修正）——与 run_v6_rerun_final 一致。"""
    dd = d.dropna(subset=[outcome, 'r', 'above']).copy()
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
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
            'n': int(n)}


def main():
    df = load()
    R = {}
    band20 = df[(np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9].copy()
    print(f'值空间 ±20% 带 n={len(band20):,}')

    # ---------- 1. 诊断家族（值空间 est_value） ----------
    print('\n[1] 诊断家族（法定阈值）…')
    est = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    est['ratio'] = est['value'] / est['value_est']
    clean = est[(est['ratio'] >= 0.5) & (est['ratio'] <= 2.0)].copy()
    clean['above_est'] = (clean['value_est'] >= clean['thr']).astype(int)
    clean['r_est'] = np.log(clean['value_est']) - np.log(clean['thr'])
    clean20 = clean[(np.exp(clean['r_est']) - 1).abs() <= 0.2 + 1e-9].copy()

    def sample(name):
        if name == 'est_value':
            d = clean20.drop(columns=['r', 'above'], errors='ignore').rename(
                columns={'above_est': 'above', 'r_est': 'r'})
            return d[['single', 'r', 'above', 'log_value', 'tu', 'tw', 'code', 'year']]
        w = float(name[-1]) / 100
        return band20[band20['r'].abs() > w + 1e-9][
            ['single', 'r', 'above', 'log_value', 'tu', 'tw', 'code', 'year']]

    fam = ['donut01', 'donut02', 'donut03', 'est_value']
    R['family'] = {}
    for ctl, cols in [('none', ()), ('type', ('tu', 'tw'))]:
        R['family'][ctl] = {}
        for name in fam:
            R['family'][ctl][name] = rd(sample(name), 'single', controls=cols)
            v = R['family'][ctl][name]
            print(f"  {ctl:5s} {name:9s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, "
                  f"p={v['p']:.4f}, n={v['n']:,})")

    # Bonferroni + Holm（闭式）
    R['corrections'] = {}
    for ctl in ('none', 'type'):
        ps = {n: R['family'][ctl][n]['p'] for n in fam}
        bonf = {n: round(min(1.0, p * len(fam)), 4) for n, p in ps.items()}
        order = sorted(fam, key=lambda n: ps[n])
        holm, prev = {}, 0.0
        for rank, n in enumerate(order):
            prev = max(prev, min(1.0, ps[n] * (len(fam) - rank)))
            holm[n] = round(prev, 4)
        R['corrections'][ctl] = {'bonferroni': bonf, 'holm': holm}
        print(f"  {ctl}: Bonferroni {bonf} | Holm {holm}")

    # ---------- 2. Romano-Wolf（国家聚类 bootstrap，centered stepdown） ----------
    print('\n[2] Romano-Wolf（1000 次国家聚类 bootstrap）…')

    def cluster_stats(d, controls):
        dd = d.dropna(subset=['single', 'r', 'above']).reset_index(drop=True).copy()
        cols = ['above', 'r']
        dd['axr'] = dd['above'] * dd['r']
        cols.append('axr')
        cl = list(controls)
        cols += cl
        y = dd['single'].astype(float).values
        X = np.column_stack([dd[c].astype(float).values for c in cols])
        keys = dd['code'].astype(str).values + '_' + dd['year'].astype(str).values
        allv = pd.concat([pd.Series(y, name='y')] +
                         [pd.Series(X[:, j], name=cols[j]) for j in range(len(cols))] +
                         [pd.Series(keys, name='k')], axis=1)
        gm = allv.groupby('k').transform('mean')
        yd = (allv['y'] - gm['y']).values
        Xd = np.column_stack([np.ones(len(dd))] +
                             [(allv[c] - gm[c]).values for c in cols])
        out = {}
        for g, idx in dd.groupby('code').groups.items():
            out[g] = (Xd[idx], yd[idx])
        return out, len(Xd[0])

    def boot_est(stats_g, weights, G, beta_obs):
        XtX = sum(weights[i] * (Xg.T @ Xg) for i, (Xg, _) in enumerate(stats_g.values()))
        Xty = sum(weights[i] * (Xg.T @ yg) for i, (Xg, yg) in enumerate(stats_g.values()))
        XtXi = np.linalg.pinv(XtX)
        beta = XtXi @ Xty
        meat = np.zeros((XtXi.shape[0], XtXi.shape[0]))
        for i, (Xg, yg) in enumerate(stats_g.values()):
            s = weights[i] * (Xg.T @ (yg - Xg @ beta))
            meat += np.outer(s, s)
        V = XtXi @ meat @ XtXi * (G / (G - 1))
        se = np.sqrt(max(np.diag(V)[1], 1e-12))
        if beta_obs is None:
            return beta[1], beta[1] / se
        return (beta[1] - beta_obs) / se

    rng = np.random.default_rng(20261022)
    B = 1000
    for ctl, cols in [('none', []), ('type', ['tu', 'tw'])]:
        per_spec = {n: cluster_stats(sample(n), cols)[0] for n in fam}
        clusters = sorted(set().union(*[set(s) for s in per_spec.values()]))
        G = len(clusters)
        t_obs = {n: abs(R['family'][ctl][n]['tau_pp'] / R['family'][ctl][n]['se_pp'])
                 for n in fam}
        tau_obs = {n: R['family'][ctl][n]['tau_pp'] / 100 for n in fam}
        t_boot = {n: np.zeros(B) for n in fam}
        for b in range(B):
            w = rng.multinomial(G, [1 / G] * G)
            wmap = dict(zip(clusters, w))
            for n in fam:
                s = per_spec[n]
                ws = np.array([wmap.get(g, 0) for g in s])
                try:
                    t_boot[n][b] = abs(boot_est(s, ws, G, beta_obs=tau_obs[n]))
                except Exception:
                    t_boot[n][b] = 0.0
        adj = {}
        max_t = np.maximum.reduce([t_boot[n] for n in fam])
        prev = 0.0
        for step, n in enumerate(sorted(fam, key=lambda n: -t_obs[n])):
            p_n = float((max_t >= t_obs[n]).mean())
            prev = max(prev, p_n)
            adj[n] = round(min(1.0, prev), 4)
            remaining = sorted(fam, key=lambda n: -t_obs[n])[step + 1:]
            max_t = (np.maximum.reduce([t_boot[o] for o in remaining])
                     if remaining else np.zeros(B))
        R['corrections'][ctl]['romano_wolf'] = adj
        R['corrections'][ctl]['romano_wolf_t_obs'] = {n: round(t_obs[n], 3) for n in fam}
        print(f"  RW {ctl}: {adj}")

    # ---------- 3. ±1% donut LOO（无控制） ----------
    print('\n[3] ±1% donut 留一国家（无控制）…')
    d1 = band20[band20['r'].abs() > 0.01 + 1e-9]
    loo = {}
    for c in sorted(d1['code'].unique()):
        v = rd(d1[d1['code'] != c], 'single', controls=())
        loo[c] = v
    taus = [v['tau_pp'] for v in loo.values()]
    R['loo_donut01_none'] = {'estimates': loo,
                             'min': round(min(taus), 2), 'max': round(max(taus), 2),
                             'all_positive': bool(min(taus) > 0)}
    print(f"  LOO 范围 [{min(taus):+.2f}, {max(taus):+.2f}]，全正={min(taus) > 0}")

    # ---------- 4. 对数窗口基线（法定阈值） ----------
    print('\n[4] 对数窗口基线（|r| ≤ 0.2）…')
    band_log = df[df['r'].abs() <= 0.2 + 1e-9].copy()
    R['log_window'] = {'n': int(len(band_log))}
    for lab, cols in [('none', ()), ('logval', ('log_value',)),
                      ('type', ('tu', 'tw')), ('prereg', ('log_value', 'tu', 'tw'))]:
        R['log_window'][lab] = rd(band_log, 'single', controls=cols)
        v = R['log_window'][lab]
        print(f"  {lab:7s} {v['tau_pp']:+.2f} (SE {v['se_pp']:.2f}, p={v['p']:.4f})")

    # ---------- 5. 窗口分段 ----------
    print('\n[5] 窗口分段（2013-2021 vs 2022-2023）…')
    R['window_split'] = {}
    for lab, yrs in [('2013_2021', range(2013, 2022)), ('2022_2023', range(2022, 2024))]:
        d = band20[band20['year'].isin(yrs)]
        R['window_split'][lab] = {'n': int(len(d)),
                                  'prereg': rd(d, 'single'),
                                  'none': rd(d, 'single', controls=())}
        v = R['window_split'][lab]
        print(f"  {lab}: n={v['n']:,} prereg {v['prereg']['tau_pp']:+.2f} "
              f"(p={v['prereg']['p']:.3f}) | none {v['none']['tau_pp']:+.2f} (p={v['none']['p']:.3f})")

    # ---------- 6. 构成统计 ----------
    print('\n[6] 构成统计…')
    R['composition'] = {
        'share_2022_23_pct': round(float((band20['year'] >= 2022).mean() * 100), 1),
        'n_2022_23': int((band20['year'] >= 2022).sum()),
        'n_band': int(len(band20)),
        'offer_field_coverage_pct': round(float(band20['n_offers'].notna().mean() * 100), 1),
        'n_offer_reported': int(band20['n_offers'].notna().sum()),
        'mean_offers_below': round(float(band20.loc[band20['above'] == 0, 'n_offers'].mean()), 2),
        'mean_offers_above': round(float(band20.loc[band20['above'] == 1, 'n_offers'].mean()), 2),
        'share_ge3_below_pct': round(float((band20.loc[band20['above'] == 0, 'n_offers'] >= 3).mean() * 100), 1),
        'share_ge3_above_pct': round(float((band20.loc[band20['above'] == 1, 'n_offers'] >= 3).mean() * 100), 1),
    }
    print(' ', json.dumps(R['composition'], ensure_ascii=False))

    # ---------- 7. 价格描述（S/U 近阈值） ----------
    print('\n[7] 价格描述（S/U，|r| ≤ 0.05）…')
    su = band20[(band20['type'] != 'W') & (band20['r'].abs() <= 0.05) & band20['value_est'].notna()]
    R['price_descriptive'] = {
        'n': int(len(su)),
        'mean_award': round(float(su['value'].mean()), 0),
        'mean_est': round(float(su['value_est'].mean()), 0),
        'median_est': round(float(su['value_est'].median()), 0),
    }
    print(' ', json.dumps(R['price_descriptive'], ensure_ascii=False))

    json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

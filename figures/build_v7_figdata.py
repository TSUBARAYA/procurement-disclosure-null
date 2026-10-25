# -*- coding: utf-8 -*-
"""为 v7.0 主设计生成图数据，并重绘图 1-4。

上轮发现：图 1/2/3/4 仍基于归档的授予价值口径（v6.0），而论文主设计已是
v7.0（开标前法定估计价值）。本脚本从 cn_matched_clean.csv 生成 v7.0 的：
  - rd_binscatter_v7.json / rd_fitlines_v7.json   （图 1）
  - density_v7.json                               （图 3）
  - fig4_grid_v7.json                             （图 4）
图 2（forest plot）与图 5（SME dose-response）在 redraw_figures.py 中更新取值。

【第九轮修订】本脚本已被 analysis/run_review9_figures_v7.py 取代：后者在希腊
映射 bug 修复后从 28 国缓存重建同一批 JSON，并修正了两处本脚本的缺陷——
带宽网格的 ±25% 格实为 ±20%（`band` 已限 ±20%，子集等于自身），以及拟合线
未使用论文规格（cy 去均值 + type 哑变量）的斜率。保留本文件作历史记录。
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
RES = os.path.join(ROOT, 'materials', 'results')
TOL = 1e-9
BW = 0.02


def rd(d, outcome, poly=1):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return None
    dd['above'] = (dd['r'] >= 0).astype(int)
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax', 'tu', 'tw']
    for j in range(2, poly + 1):
        dd['r%d' % j] = dd['r'] ** j
        dd['ax%d' % j] = dd['above'] * dd['r'] ** j
        xcols += ['r%d' % j, 'ax%d' % j]
    y = dd[outcome].astype(float).values
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([pd.Series(y, name='y')] +
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
    df = pd.read_csv(os.path.join(ROOT, 'analysis', 'cn_matched_clean.csv'))
    df['above'] = (df['r'] >= 0).astype(int)
    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    print('v7.0 ±20%% 带: %s' % format(len(band), ','))

    # ---------- 图 1：binscatter + 局部线性拟合 ----------
    bins = np.arange(-15, 16)
    cnt = pd.Series(np.floor(band['r'].values / BW).astype(int)).value_counts()
    centers, share, counts = [], [], []
    for k in bins:
        m = (band['r'] >= k * BW - 1e-12) & (band['r'] < (k + 1) * BW)
        if m.sum() >= 30 and band.loc[m, 'single'].notna().any():
            centers.append(round(float((k + 0.5) * BW), 4))
            share.append(round(float(band.loc[m, 'single'].mean()), 6))
            counts.append(int(m.sum()))
    json.dump({'centers': centers, 'share': share, 'counts': counts, 'binwidth': BW,
               'n': int(band['single'].notna().sum()),
               'note': 'v7.0 主设计：CN 法定估计价值作 running variable，清洗后样本'},
              open(os.path.join(FIG, 'rd_binscatter_v7.json'), 'w'), indent=1)

    def linfit(lo, hi):
        m = (band['r'] >= lo) & (band['r'] < hi) & band['single'].notna()
        x = band.loc[m, 'r'].values
        y = band.loc[m, 'single'].values
        A = np.vstack([x, np.ones_like(x)]).T
        co, *_ = np.linalg.lstsq(A, y, rcond=None)
        xs = np.linspace(lo, hi, 60)
        return {'x': [round(float(v), 4) for v in xs],
                'y': [round(float(v), 6) for v in (co[0] * xs + co[1])]}
    json.dump({'left': linfit(-0.15, 0.0), 'right': linfit(0.0, 0.15)},
              open(os.path.join(FIG, 'rd_fitlines_v7.json'), 'w'), indent=1)
    print('图1 数据: %d 箱，单投标份额范围 %.1f%%-%.1f%%'
          % (len(centers), min(share) * 100, max(share) * 100))

    # ---------- 图 3：密度直方图 ----------
    n = np.array([cnt.get(k, 0) for k in bins], dtype=int)
    json.dump({'centers': [round(float((k + 0.5) * BW), 4) for k in bins],
               'counts': [int(c) for c in n], 'n': int(len(band)),
               'note': 'v7.0 主设计：CN 法定估计价值密度，清洗后样本'},
              open(os.path.join(FIG, 'density_v7.json'), 'w'), indent=1)
    mp = int(((band['r'] >= 0) & (band['r'] < 1e-4)).sum())
    print('图3 数据: %d 箱，堆点 %s' % (len(bins), format(mp, ',')))

    # ---------- 图 4：带宽 × 阶数网格 ----------
    grid = {'bandwidth': {}, 'poly': {}, 'note': 'v7.0 主设计，type FE 控制，国家聚类 SE'}
    for b in (10, 15, 20, 25):
        d = band[((np.exp(band['r']) - 1).abs() <= b / 100 + TOL)]
        r = rd(d, 'single', poly=1)
        if r:
            grid['bandwidth'][str(b / 100)] = {'tau_pp': r['tau_pp'], 'p': r['p']}
    for p in (1, 2):
        d = band[((np.exp(band['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(d, 'single', poly=p)
        if r:
            grid['poly'][str(p)] = {'tau_pp': r['tau_pp'], 'p': r['p']}
    json.dump(grid, open(os.path.join(FIG, 'fig4_grid_v7.json'), 'w'), indent=1)
    print('图4 数据:', json.dumps(grid['bandwidth']), json.dumps(grid['poly']))

    # ---------- 汇总：供图 2 使用的主设计与辅助设计估计 ----------
    main_est = rd(band, 'single')
    fw_est = rd(band, 'foreign_win')
    summ = {'v7_single': main_est, 'v7_foreign_win': fw_est,
            'n_band': int(len(band)),
            'note': 'v7.0 主设计 + 外国中标份额，供 forest plot 使用'}
    json.dump(summ, open(os.path.join(FIG, 'fig2_estimates_v7.json'), 'w'), indent=1)
    print('图2 数据: v7.0 single %s ; foreign_win %s'
          % (main_est, fw_est))


if __name__ == '__main__':
    main()

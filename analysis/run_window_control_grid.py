"""第四轮复核：窗口口径 × 控制集 的完整网格。

审稿意见（第 4 轮）指出两处需要可核对数字的表述：
  1. "the choice of window metric is immaterial" —— 此前对比混用了不同控制集
     （对数窗用预注册双控制，值空间窗只用 type FE），不是同口径比较。
  2. "log awarded value accounts for none of the gap" —— 此前是间接推断，
     需要直接报告"只加 log value"的规格。

本脚本对  window ∈ {log, value}  ×  controls ∈ {none, logval_only, type_only, prereg}
跑 baseline + donut ±1/2/3% + estimated-value running variable，
全部用国家聚类标准误（28 clusters）。
输出 economy/materials/results/window_control_grid.json
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'window_control_grid.json')

df = pd.read_csv(CACHE)
df['ratio_v'] = np.exp(df['r'])


def rd(d, runvar, treat, outcome='single', controls='none'):
    """country×year 组内去模 + 国家聚类 SE。controls ∈ none/logval_only/type_only/prereg"""
    d = d.dropna(subset=[runvar, treat, outcome, 'log_value']).copy()
    tu = (d['type'] == 'U').astype(float)
    tw = (d['type'] == 'W').astype(float)
    base = [treat, runvar, f'{treat}_x_{runvar}']
    if controls == 'none':
        extra = []
    elif controls == 'logval_only':
        extra = ['log_value']
    elif controls == 'type_only':
        extra = ['tu', 'tw']
    elif controls == 'prereg':
        extra = ['log_value', 'tu', 'tw']
    else:
        raise ValueError(controls)
    xcols = base + extra
    for c in ('tu', 'tw'):
        d[c] = tu if c == 'tu' else tw
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    y = d[outcome].astype(float)

    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [d[c].astype(float).rename(c) for c in xcols]
                     + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in xcols])

    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.inv(Xd.T @ Xd)
    clusters = d['code'].values
    G = len(np.unique(clusters))
    meat = np.zeros((k, k))
    for g in np.unique(clusters):
        m = clusters == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


# 估计价值子样本（两种窗口共用同一套契约筛选）
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
clean['ratio_est'] = clean['value_est'] / np.exp(clean['log_thr'])

SPECS = ['baseline', 'donut01', 'donut02', 'donut03', 'est_value']
CTRLS = ['none', 'logval_only', 'type_only', 'prereg']
grid = {w: {c: {} for c in CTRLS} for w in ('log', 'value')}

TOL = 1e-9  # 与 run_rd_valuespace.py 一致：比值恰为 0.8/1.2 的边界行真值在带内

for win in ('log', 'value'):
    band = df[df['r'].abs() <= 0.2] if win == 'log' \
        else df[(df['ratio_v'] - 1).abs() <= 0.2 + TOL]
    cest = clean[clean['r_est'].abs() <= 0.2] if win == 'log' else \
        clean[(clean['ratio_est'] - 1).abs() <= 0.2 + TOL]
    for ctl in CTRLS:
        g = grid[win][ctl]
        g['baseline'] = rd(band, 'r', 'above', controls=ctl)
        for w in (0.01, 0.02, 0.03):
            d = band[band['r'].abs() > w] if win == 'log' else \
                band[(band['ratio_v'] - 1).abs() > w]
            g[f'donut{int(w * 100):02d}'] = rd(d, 'r', 'above', controls=ctl)
        g['est_value'] = rd(cest, 'r_est', 'above_est', controls=ctl)

out = {
    'note': ('窗口口径（对数 |r|<=0.2 vs 值空间 |v/tau-1|<=0.2）× 控制集 '
             '(none / 仅 log_value / 仅 type FE / 预注册双控制) 的完整网格，'
             '全部为国家聚类标准误（28 clusters）。'),
    'grid': grid,
    'spec_order': SPECS,
}
json.dump(out, open(OUT, 'w'), indent=2, ensure_ascii=False)

# 摘要打印
for win in ('log', 'value'):
    print(f'--- window = {win} ---')
    for ctl in CTRLS:
        g = grid[win][ctl]
        print('  ' + ctl.ljust(11),
              ' | '.join(f"{s}={g[s]['tau_pp']:+.2f}({g[s]['p']:.3f},n={g[s]['n']})" for s in SPECS))

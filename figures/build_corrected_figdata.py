"""第五轮复核：用正确阈值重算 Figure 1 与 Figure 4 的数据。

Figure 1（binscatter + 局部线性拟合）与 Figure 4（带宽 × 阶数网格）
原先都跑在错误的 2013-2017 阈值上。本脚本用正确阈值在
「缓存带 ∩ 真实带」上重算，输出：
  figures/rd_binscatter_corr.json
  figures/rd_fitlines_corr.json
  figures/fig4_grid_corr.json
"""
import json
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv'))

TRUE_SU = {2013: 200000, 2014: 207000, 2015: 207000, 2016: 209000, 2017: 209000,
           2018: 221000, 2019: 221000, 2020: 214000, 2021: 214000,
           2022: 215000, 2023: 215000}
TRUE_W = {2013: 5000000, 2014: 5186000, 2015: 5186000, 2016: 5225000, 2017: 5225000,
          2018: 5548000, 2019: 5548000, 2020: 5350000, 2021: 5350000,
          2022: 5382000, 2023: 5382000}
TOL = 1e-9

df['thr_true'] = np.where(df['type'] == 'W', df['year'].map(TRUE_W), df['year'].map(TRUE_SU))
df['r_true'] = np.log(df['value']) - np.log(df['thr_true'])
df['above_true'] = (df['value'] >= df['thr_true']).astype(int)
df['ratio_true'] = df['value'] / df['thr_true']
band = df[(df['ratio_true'] - 1).abs() <= 0.2 + TOL].copy()

# ---- Figure 1: binscatter ----
BW = 0.02
edges = np.arange(-0.30, 0.3001, BW)
cnt, _ = np.histogram(band['r_true'].values, bins=edges)
centers = (edges[:-1] + edges[1:]) / 2
share = []
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (band['r_true'] >= lo) & (band['r_true'] < hi)
    share.append(float(band.loc[m, 'single'].mean()) if m.sum() > 0 else np.nan)
bs = {'centers': [round(float(c), 4) for c in centers],
      'share': [round(float(s), 6) for s in share],
      'counts': [int(c) for c in cnt],
      'binwidth': BW,
      'n': int(len(band)),
      'note': '正确阈值口径（Section 7.4），缓存带 ∩ 真实带'}
json.dump(bs, open(os.path.join(HERE, 'rd_binscatter_corr.json'), 'w'), indent=1)

# ---- Figure 1: 局部线性拟合（±0.15） ----
def linfit(lo, hi):
    m = (band['r_true'] >= lo) & (band['r_true'] < hi)
    x = band.loc[m, 'r_true'].values
    y = band.loc[m, 'single'].values
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    xs = np.linspace(lo, hi, 60)
    return {'x': [round(float(v), 4) for v in xs],
            'y': [round(float(v), 6) for v in (coef[0] * xs + coef[1])]}

fl = {'left': linfit(-0.15, 0.0), 'right': linfit(0.0, 0.15)}
json.dump(fl, open(os.path.join(HERE, 'rd_fitlines_corr.json'), 'w'), indent=1)

# ---- Figure 4: 带宽 × 阶数（type 控制）----
tc = json.load(open(os.path.join(ROOT, 'materials', 'results',
                                 'threshold_correction.json')))
bp = tc['corrected_bandwidth_poly']
grid = {'bandwidth': {}, 'poly': {}}
for bw in (10, 15, 20, 25):
    grid['bandwidth'][str(bw / 100)] = {'tau_pp': bp[f'bw{bw}_lin']['tau_pp'],
                                        'p': bp[f'bw{bw}_lin']['p']}
grid['poly'] = {'1': {'tau_pp': bp['bw20_lin']['tau_pp'], 'p': bp['bw20_lin']['p']},
                '2': {'tau_pp': bp['bw20_quad']['tau_pp'], 'p': bp['bw20_quad']['p']}}
grid['note'] = '正确阈值口径（Section 7.4），type 控制'
json.dump(grid, open(os.path.join(HERE, 'fig4_grid_corr.json'), 'w'), indent=1)

print('binscatter n =', bs['n'], 'bin counts sum =', sum(cnt))
print('left fit  at -0.15: %.4f  at 0: %.4f' % (fl['left']['y'][0], fl['left']['y'][-1]))
print('right fit at  0:    %.4f  at 0.15: %.4f' % (fl['right']['y'][0], fl['right']['y'][-1]))
print('grid:', json.dumps(grid, indent=1))

"""第九轮：从 28 国（含希腊）缓存重建 v7.0 全部图数据。

背景：figures/*_v7.json 生成于希腊 bug 修复之前（27 国），图 1/2/3/4 全部
过期；且图 3 的堆点注释错误套用了授标价值样本的故事（5,314 份 / 74% 德国）。
本脚本从 cn_matched.csv / cn_matched_clean.csv 重建：
  rd_binscatter_v7.json  图1 binscatter（0.02 箱单投标份额 + 箱计数）
  rd_fitlines_v7.json    图1 两侧局部线性拟合（cy 去均值 + type 哑变量）
  density_v7.json        图3 密度直方图
  fig2_estimates_v7.json 图2 forest plot 的 v7.0 两行
  fig4_grid_v7.json      图4 带宽 × 阶数网格（清洗 + type 控制）
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(ROOT, 'figures')
TOL = 1e-9
BW = 0.02


def rd(d, outcome, poly=1, controls=('tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax']
    for j in range(2, poly + 1):
        dd['r%d' % j] = dd['r'] ** j
        dd['ax%d' % j] = dd['above'] * dd['r'] ** j
        xcols += ['r%d' % j, 'ax%d' % j]
    for c in controls:
        xcols.append(c)
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
    tcrit = stats.t.ppf(0.975, G - 1)
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4),
            'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - tcrit * s) * 100, 2),
                        round(float(tau + tcrit * s) * 100, 2)]}


def main():
    raw = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    raw['above'] = (raw['r'] >= 0).astype(int)
    cln = pd.read_csv(os.path.join(HERE, 'cn_matched_clean.csv'))
    cln['above'] = (cln['r'] >= 0).astype(int)
    band_raw = raw[((np.exp(raw['r']) - 1).abs() <= 0.20 + TOL)].copy()
    band_cln = cln[((np.exp(cln['r']) - 1).abs() <= 0.20 + TOL)].copy()

    # ---------- 1/2. 图1：binscatter + 拟合线 ----------
    print('=== 图1 binscatter（28 国）===')
    kk = np.floor(band_raw['r'].values / BW).astype(int)
    band_raw = band_raw.assign(k=kk)
    ks = sorted(band_raw['k'].unique())
    centers, share, counts = [], [], []
    for k in ks:
        sub = band_raw[band_raw['k'] == k]
        s = sub['single'].dropna()
        centers.append(round(float((k + 0.5) * BW), 4))
        counts.append(int(len(sub)))
        share.append(round(float(s.mean()), 5) if len(s) else None)
    n_off = int(band_raw['single'].notna().sum())
    json.dump({'centers': centers, 'share': share, 'counts': counts,
               'binwidth': BW, 'n': n_off,
               'note': 'v7.0 主设计（28 国，含希腊）：CN 法定估计价值，0.02 箱单投标份额；'
                       'counts 为箱内公告数，share 为有报价数合同的单投标均值'},
              open(os.path.join(FIGDIR, 'rd_binscatter_v7.json'), 'w'), indent=1)
    print('  bins %d，n(有报价) %s，箱计数合计 %s' % (
        len(centers), format(n_off, ','), format(sum(counts), ',')))

    # 拟合线：两侧 ±0.15。斜率用 cy 去均值 + type 哑变量（与论文规格一致），
    # 水平锚定在该侧原始均值上，使线与箱均值（≈0.30）同尺度。
    fits = {}
    for side, sel in [('left', band_cln['r'] < 0), ('right', band_cln['r'] >= 0)]:
        d = band_cln[sel & (band_cln['r'].abs() <= 0.15 + TOL)].dropna(
            subset=['single', 'r']).reset_index(drop=True).copy()
        d['tu'] = (d['type'] == 'U').astype(float)
        d['tw'] = (d['type'] == 'W').astype(float)
        y = d['single'].astype(float).values
        keys = d['code'].astype(str) + '_' + d['year'].astype(str)
        allv = pd.concat([pd.Series(y, name='y'), pd.Series(d['r'].values, name='r'),
                          pd.Series(d['tu'].values, name='tu'),
                          pd.Series(d['tw'].values, name='tw'),
                          keys.rename('k')], axis=1)
        gm = allv.groupby('k').transform('mean')
        yd = (allv['y'] - gm['y']).values
        Xd = np.column_stack([(allv[c] - gm[c]).values for c in ('r', 'tu', 'tw')])
        beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
        slope = float(beta[0])
        m_side = float(y.mean())
        xbar = float(d['r'].mean())
        xs = np.linspace(-0.15, 0, 60) if side == 'left' else np.linspace(0, 0.15, 60)
        fits[side] = {'x': [round(float(v), 4) for v in xs],
                      'y': [round(float(m_side + slope * (v - xbar)), 5) for v in xs]}
    json.dump(fits, open(os.path.join(FIGDIR, 'rd_fitlines_v7.json'), 'w'), indent=1)
    print('  拟合线: 左截距 %.4f 斜率 %+.4f | 右截距 %.4f 斜率 %+.4f → 隐含跳变 %+.2f pp'
          % (fits['left']['y'][0], (fits['left']['y'][-1] - fits['left']['y'][0]) / 0.15,
             fits['right']['y'][0], (fits['right']['y'][-1] - fits['right']['y'][0]) / 0.15,
             (fits['right']['y'][0] - fits['left']['y'][0]) * 100))

    # ---------- 3. 图3：密度直方图 ----------
    print('=== 图3 密度（28 国）===')
    kk = np.floor(band_raw['r'].values / BW).astype(int)
    band_raw = band_raw.assign(k=kk)
    cnt = band_raw['k'].value_counts()
    ks = sorted(cnt.index)
    centers = [round(float((k + 0.5) * BW), 4) for k in ks]
    counts = [int(cnt[k]) for k in ks]
    below = sum(counts[i] for i, c in enumerate(centers) if c < 0)
    above = sum(counts[i] for i, c in enumerate(centers) if c >= 0)
    assert sum(counts) == len(band_raw), (sum(counts), len(band_raw))
    json.dump({'centers': centers, 'counts': counts, 'n': int(len(band_raw)),
               'n_below': below, 'n_above': above,
               'note': 'v7.0 主设计（28 国）：CN 法定估计价值密度，floor 分箱，清洗前样本'},
              open(os.path.join(FIGDIR, 'density_v7.json'), 'w'), indent=1)
    print('  n=%s（下 %s / 上 %s）' % (format(len(band_raw), ','),
                                      format(below, ','), format(above, ',')))

    # ---------- 4. 图2：forest plot 两行 ----------
    print('=== 图2 forest（28 国）===')
    hs = rd(band_cln, 'single')
    hf = rd(band_cln, 'foreign_win')
    json.dump({'v7_single': hs, 'v7_foreign_win': hf,
               'n_band': int(len(band_cln)),
               'note': 'v7.0 主设计 + 外国中标份额（28 国，清洗 + type 控制）'},
              open(os.path.join(FIGDIR, 'fig2_estimates_v7.json'), 'w'), indent=1)
    print('  single', hs)
    print('  foreign_win', hf)

    # ---------- 5. 图4：带宽 × 阶数网格 ----------
    print('=== 图4 网格（28 国，清洗 + type）===')
    bw = {}
    for b in (0.10, 0.15, 0.20, 0.25):
        d = cln[((np.exp(cln['r']) - 1).abs() <= b + TOL)]
        r = rd(d, 'single', poly=1)
        bw['%.2f' % b] = {'tau_pp': r['tau_pp'], 'p': r['p'], 'n': r['n'],
                          'se_pp': r['se_pp']}
        print('  ±%d%% p1: %+.3f (SE %.3f, p=%.4f, n=%s)'
              % (int(b * 100), r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ',')))
    poly = {}
    for p_ in (1, 2):
        d = cln[((np.exp(cln['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(d, 'single', poly=p_)
        poly[str(p_)] = {'tau_pp': r['tau_pp'], 'p': r['p'], 'n': r['n'],
                         'se_pp': r['se_pp']}
        print('  ±20%% p%d: %+.3f (SE %.3f, p=%.4f, n=%s)'
              % (p_, r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ',')))
    json.dump({'bandwidth': bw, 'poly': poly,
               'note': 'v7.0 主设计（28 国），清洗样本 + type 控制，国家聚类 SE'},
              open(os.path.join(FIGDIR, 'fig4_grid_v7.json'), 'w'), indent=1)
    print('-> figures/*_v7.json 全部重建')


if __name__ == '__main__':
    main()

"""第十一轮：v7.0 密度 slope 诊断（外部评审：below side 的 slope 是否威胁 continuity）。

评审意见：论文报告 below side 从 1,736 升至 16,274 的 slope 并归因于 visibility
selection，但未估计 cutoff 附近的局部斜率，也未讨论其对 local linear fit 截距
的影响——若 slope 在 cutoff 附近仍显著，continuity 假设就是 threat 而非
qualification。

本脚本做三个诊断：
 1. ±5% 值空间窗内逐 0.02 bin 的计数（6 个紧邻箱）
 2. 两侧 log 密度对 r 的局部线性斜率（below / above 各自）+ 外推到 cutoff 的密度比
 3. 相邻箱比（1-bin / 2-bin）与外推比的对照——若两者方向相反，即 slope 驱动
输出 materials/results/review9_density_slope.json
"""
import json, math, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'review9_density_slope.json')
TOL = 1e-9
BW = 0.02


def main():
    df = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    band['k'] = np.floor(band['r'].values / BW).astype(int)
    cnt = band['k'].value_counts()
    R = {}

    # ---------- 1. ±5% 窗内逐箱计数 ----------
    lo_k = math.floor(math.log(0.95) / BW)
    hi_k = math.floor(math.log(1.05) / BW)
    bins = {}
    for k in range(lo_k - 1, hi_k + 2):
        bins[k] = int(cnt.get(k, 0))
    R['bins_±5pct'] = {str(k): v for k, v in bins.items()}
    print('±5% 窗内箱计数（k=bin 序号，每箱宽 0.02 in r）:')
    for k, v in bins.items():
        print('  k=%+d [%.3f, %.3f): %s' % (k, k * BW, (k + 1) * BW, format(v, ',')))

    # ---------- 2. 两侧 log 密度局部线性斜率（0.02 箱，紧邻 cutoff 各三箱） ----------
    # below 侧 k=-3,-2,-1（r ∈ [-0.06, 0)，值空间约 ±6% 内紧贴线下三箱）；
    # above 侧 k=0,1,2（r ∈ [0, 0.06)）。刻意不含更远箱，避免窗内斜率被远箱拉偏。
    def slope_at(k_lo, k_hi):
        """k_lo..k_hi（含）区间的 log(count) ~ bin center 回归，外推到 r=0。"""
        ks = [k for k in range(k_lo, k_hi + 1) if bins.get(k, 0) > 0]
        if len(ks) < 3:
            return None
        xs = np.array([(k + 0.5) * BW for k in ks])
        ys = np.log(np.array([bins[k] for k in ks], dtype=float))
        A = np.vstack([xs, np.ones(len(xs))]).T
        b, *_ = np.linalg.lstsq(A, ys, rcond=None)
        resid = ys - A @ b
        s2 = (resid ** 2).sum() / max(len(xs) - 2, 1)
        XtXi = np.linalg.pinv(A.T @ A)
        se_b = np.sqrt(np.diag(XtXi) * s2)
        dens0 = math.exp(b[1])
        t_slope = b[0] / se_b[0] if se_b[0] > 0 else float('nan')
        return {'k_range': [k_lo, k_hi], 'n_bins': len(ks),
                'counts': [bins[k] for k in ks],
                'slope_per_r': round(float(b[0]), 4),
                'slope_se': round(float(se_b[0]), 4), 'slope_t': round(float(t_slope), 2),
                'log_dens_at_0': round(float(b[1]), 4),
                'dens_at_0_per_unit_r': round(dens0, 1)}

    below = slope_at(-3, -1)
    above = slope_at(0, 2)
    R['local_logdens_below'] = below
    R['local_logdens_above'] = above
    if below and above:
        ratio_extrap = below['dens_at_0_per_unit_r'] / above['dens_at_0_per_unit_r']
        R['extrapolated_ratio_below_over_above'] = round(ratio_extrap, 4)
        print('\n局部线性（0.01 箱、±5% 窗）外推到 cutoff：')
        print('  below: 斜率 %+.4f/log-r (t=%.2f)，外推密度 %.1f'
              % (below['slope_per_r'], below['slope_t'], below['dens_at_0_per_unit_r']))
        print('  above: 斜率 %+.4f/log-r (t=%.2f)，外推密度 %.1f'
              % (above['slope_per_r'], above['slope_t'], above['dens_at_0_per_unit_r']))
        print('  外推比 below/above = %.3f' % ratio_extrap)

    # ---------- 3. 相邻箱比 ----------
    m1 = bins.get(-1, 0), bins.get(0, 0)
    m2 = bins.get(-2, 0) + bins.get(-1, 0), bins.get(0, 0) + bins.get(1, 0)
    R['adjacent_1bin'] = {'below': m1[0], 'above': m1[1],
                          'ratio': round(m1[0] / m1[1], 4) if m1[1] else None}
    R['adjacent_2bin'] = {'below': m2[0], 'above': m2[1],
                          'ratio': round(m2[0] / m2[1], 4) if m2[1] else None}
    print('\n相邻箱比: 1 箱 %.3f（%s vs %s）；2 箱 %.3f（%s vs %s）'
          % (R['adjacent_1bin']['ratio'], format(m1[0], ','), format(m1[1], ','),
             R['adjacent_2bin']['ratio'], format(m2[0], ','), format(m2[1], ',')))
    print('→ 相邻箱比 <1（下方稀）而外推比 %s：方向%s，slope 驱动局部外推'
          % ('>1（下方密）' if ratio_extrap > 1 else '<1',
             '相反' if (ratio_extrap > 1) != (R['adjacent_1bin']['ratio'] < 1) else '一致'))

    json.dump(R, open(OUT, 'w'), indent=1)
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

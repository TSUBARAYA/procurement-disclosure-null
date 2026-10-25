"""第九轮：重建 v7.0 局部密度检验（仓库缺失脚本，review9 补写）。

对 CN 估计价值样本做紧邻断点的箱计数比较：
  - 1 箱检验：bin −1（紧贴下方）vs bin 0（紧贴上方）
  - 2 箱检验：(bin −2, −1) vs (bin 0, +1)
标准误与 p 值用按国家聚类的 bootstrap（重抽 28 国，B=1000）。
输出 materials/results/v7_density_test.json（与旧版同结构，便于对照）
"""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_density_test.json')
TOL = 1e-9
BW = 0.02
B = 1000


def main():
    df = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    df['above'] = (df['r'] >= 0).astype(int)
    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    k = np.floor(band['r'].values / BW).astype(int)
    band['k'] = k
    codes = band['code'].values
    clusters = sorted(band['code'].unique())
    rng = np.random.default_rng(20261024)
    R = {'n_band': int(len(band)), 'G': len(clusters), 'B': B}

    def counts(mask_lo, mask_hi):
        return int((band['k'] == mask_lo).sum()), int((band['k'] == mask_hi).sum())

    def boot_ratio(ksel, csel, lo_keys, hi_keys):
        """国家聚类 bootstrap：重抽国家（有放回，含重复），重算 (下箱计数/上箱计数)。"""
        out = []
        G = len(clusters)
        # 预聚合为国家×箱计数矩阵，bootstrap 在矩阵行上重抽（真正的聚类重抽）
        cc = (pd.DataFrame({'code': csel, 'k': ksel})
              .groupby(['code', 'k']).size().unstack(fill_value=0))
        cc = cc.reindex(columns=lo_keys + hi_keys, fill_value=0)
        mat = cc.values.astype(float)
        nlo = len(lo_keys)
        for _ in range(B):
            idx = rng.integers(0, G, G)
            c = mat[idx].sum(axis=0)
            lo, hi = c[:nlo].sum(), c[nlo:].sum()
            if hi > 0 and lo > 0:
                out.append(lo / hi)
        return np.array(out)

    from scipy import stats as st
    for lab, lo_keys, hi_keys in [('1bin', [-1], [0]),
                                  ('2bin', [-2, -1], [0, 1])]:
        lo, hi = counts(lo_keys[0], hi_keys[0]) if lab == '1bin' else (
            int(band['k'].isin(lo_keys).sum()), int(band['k'].isin(hi_keys).sum()))
        ratio = lo / hi
        boots = boot_ratio(band['k'].values, codes, lo_keys, hi_keys)
        se = float(boots.std(ddof=1))
        z = abs(ratio - 1.0) / se
        p = float(2 * (1 - st.t.cdf(z, len(clusters) - 1)))
        R['density_ratio_%s' % lab] = round(ratio, 4)
        R['p_%s' % lab] = round(p, 4)
        R['se_%s' % lab] = round(se, 4)
        R['n_%s' % lab] = {'below': lo, 'above': hi}
        print('%s: 下 %s vs 上 %s → 比率 %.4f（bootstrap SE %.4f, p=%.4f）'
              % (lab, format(lo, ','), format(hi, ','), ratio, se, p))

    # 箱计数明细（与 v7_density_robust.json 同口径）
    cnt = band['k'].value_counts()
    R['bin_counts'] = {str(int(kk)): int(cnt.get(kk, 0)) for kk in range(-13, 11)}
    # 对称满箱（各 9 箱）
    L9 = int(band['k'].between(-9, -1).sum())
    R9 = int(band['k'].between(1, 9).sum())
    R['symmetric_9bin'] = {'below': L9, 'above': R9,
                           'per_bin_below': round(L9 / 9, 1), 'per_bin_above': round(R9 / 9, 1),
                           'excess_below_pct': round((L9 / 9) / (R9 / 9) * 100 - 100, 2)}
    print('对称 9 箱: 下 %s（每箱 %.0f）vs 上 %s（每箱 %.0f）→ 下方 %+.1f%%'
          % (format(L9, ','), L9 / 9, format(R9, ','), R9 / 9, (L9 / 9) / (R9 / 9) * 100 - 100))
    # 冻结构造（12 箱 vs 9 箱，与 run_v7_estimate_rd.py 同口径）
    L12 = int(band['k'].between(-12, -1).sum())
    R9f = int(band['k'].between(1, 9).sum())
    import math
    gap = math.log((R9f / 9 + 1) / (L12 / 12 + 1))
    R['frozen_12v9'] = {'below': L12, 'above': R9f, 'log_gap': round(gap, 5),
                        'excess_below_pct': round((L12 / 12) / (R9f / 9) * 100 - 100, 3)}
    print('冻结 12v9: 下 %s（每箱 %.0f）vs 上 %s（每箱 %.0f）→ log gap %+.4f（下方 %+.1f%%）'
          % (format(L12, ','), L12 / 12, format(R9f, ','), R9f / 9, gap,
             (L12 / 12) / (R9f / 9) * 100 - 100))
    json.dump(R, open(OUT, 'w'), indent=1)
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

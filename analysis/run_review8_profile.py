"""第八轮续：130% placebo 的决定性诊断 —— 断点剖面 + 预注册规格（type FE）网格。

判据：若 RD 估计随断点位置平滑移动（1.0→1.4），说明是合同金额的平滑梯度被
局部线性当成水平跳变；若只有 1.3 一处异常，则更可能是该处数据特征。
同时用 type FE（预注册规格，与 v7 placebo 一致）重跑带宽×阶数×donut 网格。

缓存为 ±40% 提取（ratio ∈ [0.60, 1.40]）：cutoff ∈ [0.75, 1.167] 的 ±20%
邻域完整；之外的点单侧被缓存边界截断，逐点标记 full_band=False。
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from estimators_v4 import demean, wls_cluster  # noqa

TOL = 1e-9
CACHE_LO, CACHE_HI = 0.60, 1.40   # ted_wide_final.csv 的 ratio 覆盖范围

# 法定阈值（EUR, excl. VAT）：2013 Reg.1269/2011；2014-15 Reg.1336/2013；
# 2016-17 Dir. 2014/24/EU 经 Reg. (EU) 2015/2170 修正；2018+ 各两年期法规
THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def add_cutoff(df, cutoff):
    """按法定阈值整数表直接重构断点，避免 exp(log(v)-r) 的浮点恢复误差
    （该误差会把约 4,246 份 value==threshold 的堆点合同错分到下方）。"""
    d = df.copy()
    su = d['year'].map(lambda y: THRESH[int(y)][0])
    w = d['year'].map(lambda y: THRESH[int(y)][1])
    d['thr'] = np.where(d['type'] == 'W', w, su).astype(float)
    d['thr_pl'] = d['thr'] * cutoff
    d['r'] = np.log(d['value']) - np.log(d['thr_pl'])
    d['above'] = (d['value'] >= d['thr_pl']).astype(int)
    return d


def rd_typefe(d, outcome='single', poly=1, controls=('log_value',)):
    """预注册规格：country×year + type FE（交替投影去均值），国家聚类 SE。"""
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
    groups = [dd['code'].astype(str).values + '_' + dd['year'].astype(str).values,
              dd['type'].astype(str).values]
    w = np.ones(len(dd))
    yd, Xd = demean(y, X, groups, w)
    res = wls_cluster(yd, Xd, w, dd['code'].astype('category').cat.codes.values)
    i = names.index('tau')
    return {'tau_pp': round(float(res['beta'][i]) * 100, 3),
            'se_pp': round(float(res['se'][i]) * 100, 3),
            'p': round(float(res['p'][i]), 4), 'n': int(res['n']),
            'ci95_pp': [round(float(res['ci_lo'][i]) * 100, 2),
                        round(float(res['ci_hi'][i]) * 100, 2)],
            'n_below': int((dd['above'] == 0).sum()),
            'n_above': int((dd['above'] == 1).sum())}


def main():
    df = pd.read_csv(os.path.join(HERE, 'ted_wide_final.csv'))
    ratio_all = df['value'] / np.exp(np.log(df['value']) - df['r'])
    print(f'±40% 提取缓存 {len(df):,} 行（ratio ∈ [{ratio_all.min():.3f}, {ratio_all.max():.3f}]）')
    out = {'cache_ratio_range': [round(float(ratio_all.min()), 4), round(float(ratio_all.max()), 4)]}

    def at(cutoff, bw=0.20, poly=1, controls=('log_value',)):
        d = add_cutoff(df, cutoff)
        band = d[(np.exp(d['r']) - 1).abs() <= bw + TOL]
        v = rd_typefe(band, 'single', poly=poly, controls=controls)
        v['full_band'] = bool(cutoff * (1 - bw) >= CACHE_LO - 1e-9
                              and cutoff * (1 + bw) <= CACHE_HI + 1e-9)
        v['n_band'] = int(len(band))
        return v

    # ---------- 1. 断点剖面（±20% 邻域，线性 + 二次，预注册控制） ----------
    print('\n[1] 断点剖面：cutoff ∈ [0.70, 1.45]，每点自己的 ±20% 邻域')
    prof, prof2 = {}, {}
    for c in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15,
              1.20, 1.25, 1.30, 1.35, 1.40, 1.45]:
        r = at(c)
        r2 = at(c, poly=2)
        prof[f'{c:.2f}'] = r
        prof2[f'{c:.2f}'] = r2
        flag = '' if r['full_band'] else '  [截断]'
        print(f"  cutoff {c:.2f}τ: p1 {r['tau_pp']:+.2f}pp (SE {r['se_pp']:.2f}, "
              f"p={r['p']:.4f}, n={r['n']:,}){flag} | p2 {r2['tau_pp']:+.2f}pp (p={r2['p']:.4f})")
    out['cutoff_profile_linear'] = prof
    out['cutoff_profile_quadratic'] = prof2

    # ---------- 1b. 剖面形状判据：1.3 相对局部趋势是不是离群 ----------
    print('\n[1b] 剖面形状：1.30τ 相对其余各点的离群程度')
    keys = [k for k in prof if prof[k]['full_band']]
    xs = np.array([float(k) for k in keys])
    ys = np.array([prof[k]['tau_pp'] for k in keys])
    # 只用 1.30 以外的完整带点拟合局部线性趋势，再看 1.3（截断点也参与对照）
    mask = xs != 1.30
    sl, ic = np.polyfit(xs[mask], ys[mask], 1)
    pred13 = sl * 1.30 + ic
    obs13 = prof['1.30']['tau_pp']
    others = ys[mask]
    resid_sd = float(np.std(ys[mask] - (sl * xs[mask] + ic), ddof=2))
    z13 = (obs13 - pred13) / resid_sd if resid_sd > 0 else float('nan')
    out['profile_shape'] = {
        'trend_slope_pp_per_cutoff': round(float(sl), 4),
        'trend_intercept': round(float(ic), 4),
        'pred_at_1.30': round(float(pred13), 3),
        'obs_at_1.30': round(float(obs13), 3),
        'resid_sd_full_band': round(resid_sd, 3),
        'z_1.30_vs_trend': round(float(z13), 3),
        'note': '局部线性趋势仅用完整带切点拟合（不含 1.30）；残差 sd 为去趋势后离散度'}
    print(f"  趋势斜率 {sl:+.3f} pp / cutoff；1.30τ 预测 {pred13:+.2f} vs 观测 {obs13:+.2f}；"
          f"z = {z13:.2f}（去趋势残差 sd {resid_sd:.2f}）")

    # ---------- 2. 130% 的带宽×阶数×donut（type FE 预注册规格） ----------
    print('\n[2] 130% 断点：带宽 × 阶数（type FE）')
    g13 = {}
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        for poly in (1, 2, 3):
            r = at(1.3, bw=bw, poly=poly)
            g13[f'bw{int(bw*100)}_p{poly}'] = r
            print(f"  ±{int(bw*100)}% p{poly}: {r['tau_pp']:+.2f}pp "
                  f"(SE {r['se_pp']:.2f}, p={r['p']:.4f}, n={r['n']:,})")
    out['grid_130_typefe'] = g13

    print('\n[3] 130% 断点：donut（type FE，±20%）')
    d13 = {}
    d = add_cutoff(df, 1.3)
    b20 = d[(np.exp(d['r']) - 1).abs() <= 0.20 + TOL]
    for w in (0.005, 0.01, 0.02, 0.03, 0.05):
        dd = b20[(b20['r']).abs() > w + TOL]
        r = rd_typefe(dd, 'single', poly=1)
        d13[f'donut{int(w*1000):04d}'] = r
        print(f"  donut ±{w*100:.1f}%: {r['tau_pp']:+.2f}pp (p={r['p']:.4f}, n={r['n']:,})")
    out['donut_130_typefe'] = d13

    # ---------- 4. 130% 附近的 binscatter（0.01 箱） ----------
    print('\n[4] 130% 附近 binscatter（0.01 箱，比值对真实阈值）')
    bs = []
    for k in range(-8, 9):
        lo, hi = np.log(1.3) + k * 0.01, np.log(1.3) + (k + 1) * 0.01
        m = (d['r'] >= lo - 1e-12) & (d['r'] < hi)
        if m.sum() > 0:
            bs.append({'k': k, 'ratio': round(float(np.exp((lo + hi) / 2)), 4),
                       'n': int(m.sum()), 'single': round(float(d.loc[m, 'single'].mean()), 5)})
            if -3 <= k <= 3:
                print(f"  k={k:+d} ratio={np.exp((lo+hi)/2):.4f} n={m.sum():6d} "
                      f"single={d.loc[m,'single'].mean()*100:.2f}%")
    out['binscatter_130_fine'] = bs

    # ---------- 5. 四个 placebo + 真实断点：Bonferroni 家族 ----------
    print('\n[5] 四个 placebo + 真实断点：Bonferroni 家族（阈值 0.05/5 = 0.01）')
    fam = {}
    for c in (0.7, 0.8, 1.2, 1.3, 1.0):
        r = prof[f'{c:.2f}']
        fam[f'{c:.2f}'] = {'tau_pp': r['tau_pp'], 'se_pp': r['se_pp'],
                           'p': r['p'], 'n': r['n'], 'full_band': r['full_band']}
        sig = '显著' if r['p'] < 0.01 else '不显著'
        print(f"  {c:.2f}τ: {r['tau_pp']:+.2f}pp p={r['p']:.4f} → {sig}"
              f"{'' if r['full_band'] else ' [截断]'}")
    out['bonferroni_family'] = fam

    # Holm 校正
    ps = sorted([(v['p'], k) for k, v in fam.items()])
    holm = {}
    print('  Holm 校正：')
    for rank, (p, k) in enumerate(ps):
        adj = min(1.0, p * (len(ps) - rank))
        holm[k] = round(adj, 4)
        print(f"    {k}: 原始 p={p:.4f} → Holm p={adj:.4f} {'显著' if adj < 0.05 else '不显著'}")
    out['holm'] = holm

    json.dump(out, open(os.path.join(ROOT, 'materials', 'results',
                                     'review8_placebo130_profile.json'), 'w'),
              indent=1)
    print('\n→ materials/results/review8_placebo130_profile.json')


if __name__ == '__main__':
    main()

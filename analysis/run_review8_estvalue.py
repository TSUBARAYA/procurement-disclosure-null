"""第九轮续：法律上正确的阈值 RD —— 以估计价值（VALUE_EURO）为 running variable。

归档的"est_value"规格做了 award/estimate 比率 0.5–2.0 过滤，把样本砍到 41%。
本脚本去掉该过滤，直接用公告级估计价值（覆盖率 95.4%）作 running variable
—— 法定阈值本就适用于估计价值，这才是法律正确的规格。
同时报告比率分布、donut、带宽×阶数网格与 placebo 剖面。
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from estimators_v4 import demean, wls_cluster  # noqa

TOL = 1e-9


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw'), fe='cy_type'):
    dd = d.dropna(subset=[outcome, 'r']).copy()
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
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
    groups = [dd['code'].astype(str).values + '_' + dd['year'].astype(str).values,
              dd['type'].astype(str).values] if fe == 'cy_type' else \
             [dd['code'].astype(str).values + '_' + dd['year'].astype(str).values]
    w = np.ones(len(dd))
    yd, Xd = demean(y, X, groups, w)
    res = wls_cluster(yd, Xd, w, dd['code'].astype('category').cat.codes.values)
    i = names.index('tau')
    return {'tau_pp': round(float(res['beta'][i]) * 100, 3),
            'se_pp': round(float(res['se'][i]) * 100, 3),
            'p': round(float(res['p'][i]), 4), 'n': int(res['n']),
            'ci95_pp': [round(float(res['ci_lo'][i]) * 100, 2),
                        round(float(res['ci_hi'][i]) * 100, 2)]}


def main():
    df = pd.read_csv(os.path.join(HERE, 'ted_wide_final.csv'))
    R = {}
    print(f'±40% 缓存 {len(df):,} 行')
    print(f"VALUE_EURO 覆盖率: {df.value_est.notna().mean()*100:.1f}%")

    # 比率分布
    ratio = (df['value'] / df['value_est']).replace([np.inf, -np.inf], np.nan).dropna()
    for lo, hi in [(0.5, 2.0), (0.8, 1.25), (0.9, 1.11)]:
        R[f'ratio_share_{lo}_{hi}'] = round(float(((ratio >= lo) & (ratio <= hi)).mean()), 4)
    print('award/estimate 比率分布:')
    print(f"  中位 {ratio.median():.3f}, 10% {ratio.quantile(.1):.3f}, 90% {ratio.quantile(.9):.3f}")
    print(f"  [0.5,2.0] 内 {R['ratio_share_0.5_2.0']*100:.1f}%  "
          f"[0.8,1.25] 内 {R['ratio_share_0.8_1.25']*100:.1f}%")

    # ---------- 估计价值 RD（无比率过滤） ----------
    sub = df[df['value_est'].notna() & (df['value_est'] > 0)].copy()
    sub['thr'] = np.exp(np.log(sub['value']) - sub['r'])
    sub['r_est'] = np.log(sub['value_est']) - np.log(sub['thr'])
    sub['above_est'] = (sub['value_est'] >= sub['thr']).astype(int)
    print(f"\n估计价值 RD 可用样本: {len(sub):,} ({len(sub)/len(df)*100:.1f}% of ±40%)")

    print('\n[估计价值 RD] 带宽 × 阶数（值空间 ±20%，type FE + 控制）')
    g = {}
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        d = sub[((np.exp(sub['r_est']) - 1).abs() <= bw + TOL)]
        for poly in (1, 2):
            r = rd(d, 'single', poly=poly)
            g[f'bw{int(bw*100)}_p{poly}'] = r
            print(f"  ±{int(bw*100)}% p{poly}: {r['tau_pp']:+.2f}pp (SE {r['se_pp']:.2f}, "
                  f"p={r['p']:.4f}, n={r['n']:,})")
    R['est_value_rd'] = g

    # donut
    d20 = sub[((np.exp(sub['r_est']) - 1).abs() <= 0.20 + TOL)]
    print('\n[估计价值 RD] donut（±20%）')
    R['est_value_donut'] = {}
    for w in (0.01, 0.02, 0.03):
        dd = d20[d20['r_est'].abs() > w + TOL]
        r = rd(dd, 'single', poly=1)
        R['est_value_donut'][f'donut{int(w*100):02d}'] = r
        print(f"  donut ±{w*100:.0f}%: {r['tau_pp']:+.2f}pp (p={r['p']:.4f}, n={r['n']:,})")

    # ---------- placebo 剖面（估计价值 running variable） ----------
    print('\n[估计价值 RD] 断点剖面（±20% 邻域，线性）')
    prof = {}
    for c in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
        d = sub.copy()
        d['thr_pl'] = d['thr'] * c
        d['r'] = np.log(d['value_est']) - np.log(d['thr_pl'])
        d['above'] = (d['value_est'] >= d['thr_pl']).astype(int)
        band = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(band, 'single', poly=1)
        prof[f'{c:.2f}'] = r
        flag = ' ← 显著' if r['p'] < 0.05 else ''
        print(f"  {c:.2f}τ: {r['tau_pp']:+.2f}pp (SE {r['se_pp']:.2f}, p={r['p']:.4f}, "
              f"n={r['n']:,}){flag}")
    R['est_value_profile'] = prof

    # ---------- 对照：授予价值 RD 的同一剖面（已知） ----------
    print('\n[授予价值 RD] 断点剖面（±20% 邻域，线性）——对照')
    prof2 = {}
    for c in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
        d = df.copy()
        d['thr_pl'] = np.exp(np.log(d['value']) - d['r']) * c
        d['r'] = np.log(d['value']) - np.log(d['thr_pl'])
        d['above'] = (d['value'] >= d['thr_pl']).astype(int)
        band = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(band, 'single', poly=1)
        prof2[f'{c:.2f}'] = r
        flag = ' ← 显著' if r['p'] < 0.05 else ''
        print(f"  {c:.2f}τ: {r['tau_pp']:+.2f}pp (SE {r['se_pp']:.2f}, p={r['p']:.4f}, "
              f"n={r['n']:,}){flag}")
    R['awarded_profile'] = prof2

    # ---------- 第一阶段：估计价值与授予价值的错分 ----------
    print('\n[第一阶段] 授予值在阈值下方但估计值在上方（错分）')
    sub2 = sub.copy()
    sub2['thr'] = np.exp(np.log(sub2['value']) - sub2['r'])
    below_award = sub2[sub2['value'] < sub2['thr']]
    above_est = below_award[below_award['value_est'] >= below_award['thr']]
    print(f"  授予值 < 阈值: {len(below_award):,}; 其中估计值 ≥ 阈值: {len(above_est):,} "
          f"({len(above_est)/max(len(below_award),1)*100:.2f}%)")
    above_award = sub2[sub2['value'] >= sub2['thr']]
    below_est = above_award[above_award['value_est'] < above_award['thr']]
    print(f"  授予值 ≥ 阈值: {len(above_award):,}; 其中估计值 < 阈值: {len(below_est):,} "
          f"({len(below_est)/max(len(above_award),1)*100:.2f}%)")
    R['misclassification'] = {
        'n_below_award': int(len(below_award)), 'n_below_award_but_above_est': int(len(above_est)),
        'n_above_award': int(len(above_award)), 'n_above_award_but_below_est': int(len(below_est)),
        'share_up': round(float(len(above_est) / max(len(below_award), 1)), 4),
        'share_down': round(float(len(below_est) / max(len(above_award), 1)), 4)}

    json.dump(R, open(os.path.join(ROOT, 'materials', 'results', 'review8_estvalue_rd.json'), 'w'),
              indent=1)
    print('\n→ materials/results/review8_estvalue_rd.json')


if __name__ == '__main__':
    main()

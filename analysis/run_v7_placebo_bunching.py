"""第七轮复核（续）：placebo battery（±40% 带）+ bunching 估计器重建与可复现性核查。

1. placebo battery：预注册断点在 0.7/0.8/1.2/1.3 × 法定阈值。上一轮证明在 ±20%
   分析带上它们不可执行；本轮用 ±40% 提取缓存，在每个安慰剂断点自己的 ±20% 邻域内
   重跑 RD，看预注册的 placebo_alarm 规则到底会给出什么。
2. bunching 重建：用法定阈值重建 22 箱直方图，跑归档脚本同款 Chetty 估计器
   （5 阶多项式、剔除 ±0.02 bunching 区），并做窗口×阶数敏感性网格；
   同时核查归档的 3,262 / 2,257 / 11,062 三个口径能否复现。
输出 materials/results/v7_placebo_bunching.json
"""
import json
import math
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
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_placebo_bunching.json')

THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r', 'above']).copy()
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
              dd['type'].astype(str).values]
    w = np.ones(len(dd))
    yd, Xd = demean(y, X, groups, w)
    r_ = wls_cluster(yd, Xd, w, dd['code'].astype('category').cat.codes.values)
    i = names.index('tau')
    return {'tau': float(r_['beta'][i]), 'se': float(r_['se'][i]),
            'p': float(r_['p'][i]), 'n': int(r_['n']),
            'ci': [float(r_['ci_lo'][i]), float(r_['ci_hi'][i])],
            'n_below': int((dd['above'] == 0).sum()), 'n_above': int((dd['above'] == 1).sum())}


def main():
    df = pd.read_csv(CACHE)
    print(f'±40% 提取缓存 {len(df):,} 行')
    R = {'n_wide': int(len(df))}

    # ================= 1. placebo battery =================
    print('\n[1] placebo battery（每个断点自己的 ±20% 邻域）…')

    def add_cutoff(cutoff):
        """按法定阈值整数表直接重构断点：exp(log(v)-r) 的浮点恢复会把
        value 恰好等于 c×threshold 的整数金额合同错分，必须用整数阈值表。"""
        d = df.copy()
        su = d['year'].map(lambda y: THRESH[int(y)][0])
        w = d['year'].map(lambda y: THRESH[int(y)][1])
        d['thr'] = np.where(d['type'] == 'W', w, su).astype(float)
        d['thr_pl'] = d['thr'] * cutoff
        d['r'] = np.log(d['value']) - np.log(d['thr_pl'])
        d['above'] = (d['value'] >= d['thr_pl']).astype(int)
        return d

    R['placebo'] = {}
    for c in (0.7, 0.8, 1.2, 1.3):
        d = add_cutoff(c)
        band = d[(np.exp(d['r']) - 1).abs() <= 0.2 + 1e-9]
        v = rd(band)
        v['n_band'] = int(len(band))
        R['placebo'][str(c)] = v
        print(f"   {c}: n={v.get('n', 0):,} (below {v.get('n_below', 0):,} / above {v.get('n_above', 0):,}) "
              f"τ={v.get('tau')} p={v.get('p')} CI={v.get('ci')}")
    # 对照：真实阈值在同一 ±20% 邻域的定义下
    d0 = df.copy()
    band0 = d0[(np.exp(d0['r']) - 1).abs() <= 0.2 + 1e-9]
    R['placebo']['true_1.0'] = rd(band0)
    R['placebo']['true_1.0']['n_band'] = int(len(band0))
    print(f"   1.0（真实阈值）: n={R['placebo']['true_1.0'].get('n'):,} "
          f"τ={R['placebo']['true_1.0'].get('tau'):+.4f} p={R['placebo']['true_1.0'].get('p'):.4f}")

    # ================= 2. bunching 重建 =================
    print('\n[2] bunching 重建（法定阈值）…')
    d20 = df[(np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9].copy()
    r = d20['r'].values
    BW = 0.02
    bins = np.arange(-12, 10)
    cnt = pd.Series(np.floor(r / BW).astype(int)).value_counts()
    n = np.array([cnt.get(k, 0) for k in bins], dtype=float)
    centers = (bins + 0.5) * BW

    def chetty(window, order, exclude=0.02):
        mfit = (np.abs(centers) > exclude) & (np.abs(centers) <= window)
        coef = np.polyfit(centers[mfit], np.log(np.maximum(n[mfit], 1)), order)
        cf = np.exp(np.polyval(coef, centers))
        bm = (centers < 0) & (centers >= -exclude)
        return float((n - cf)[bm].sum()), coef, cf

    # 归档脚本同款：5 阶、剔除 ±0.02、全窗口拟合
    ex5, _, _ = chetty(0.30, 5)
    near = d20[d20['r'].abs() <= 0.05]
    R['bunching'] = {
        'n_band': int(len(d20)),
        'bin_counts': {int(k): int(v) for k, v in zip(bins, n)},
        'archived_script_replica': {
            'spec': '5 阶多项式，剔除 ±0.02，窗口 ±0.30（归档 run_price_bunching.py 同款）',
            'excess_contracts': round(ex5, 1),
            'excess_pct_of_below': round(ex5 / n[centers < 0].sum() * 100, 2),
            'mean_value_near': round(float(near['value'].mean())),
            'mean_value_near_SU': round(float(near.loc[near['type'].isin(['S', 'U']), 'value'].mean())),
            'excess_value_eur_all_type': round(ex5 * float(near['value'].mean())),
            'excess_value_eur_SU': round(ex5 * float(near.loc[near['type'].isin(['S', 'U']), 'value'].mean())),
        },
    }
    print(f"   归档同款规格: 超额 {ex5:,.0f} 份，"
          f"占阈值以下 {ex5/n[centers<0].sum()*100:.2f}%")

    # 敏感性网格：窗口 × 阶数
    grid = {}
    for window in (0.08, 0.10, 0.15, 0.20, 0.25, 0.30):
        row = {}
        for order in (3, 5, 7):
            e, _, _ = chetty(window, order)
            row[f'p{order}'] = round(e, 0)
        grid[f'w{int(window*100):02d}'] = row
    R['bunching']['sensitivity_grid'] = grid
    print('   敏感性网格（窗口 × 阶数，超额合同数）:')
    for w, row in grid.items():
        print(f"     ±{int(w[1:]):02d}  " + '  '.join(f'p{k[1:]}={v:>9,.0f}' for k, v in row.items()))

    # bootstrap CI（对首选规格）
    rng = np.random.default_rng(42)
    cell = (d20['code'].astype(str) + '_' + d20['year'].astype(str) + '_' + d20['type'].astype(str)).values
    cells = pd.unique(cell)
    ci = {c: np.where(cell == c)[0] for c in cells}
    draws = []
    for _ in range(1000):
        pick = rng.choice(cells, size=len(cells), replace=True)
        idx = np.concatenate([ci[c] for c in pick])
        bb = np.floor(r[idx] / BW).astype(int)
        c2 = pd.Series(bb).value_counts()
        nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
        mfit = (np.abs(centers) > 0.02) & (np.abs(centers) <= 0.30)
        try:
            coef = np.polyfit(centers[mfit], np.log(np.maximum(nn[mfit], 1)), 5)
            cf = np.exp(np.polyval(coef, centers))
            bm = (centers < 0) & (centers >= -0.02)
            draws.append(float((nn - cf)[bm].sum()))
        except Exception:
            pass
    draws = np.array(draws)
    R['bunching']['bootstrap'] = {
        'n_replicates': int(len(draws)), 'mean': round(float(draws.mean()), 0),
        'sd': round(float(draws.std()), 0),
        'ci95': [round(float(np.percentile(draws, 2.5)), 0),
                 round(float(np.percentile(draws, 97.5)), 0)],
        'share_negative': round(float((draws < 0).mean()), 3),
    }
    print(f"   bootstrap 1000 次: 均值 {draws.mean():,.0f}, sd {draws.std():,.0f}, "
          f"CI95 [{np.percentile(draws,2.5):,.0f}, {np.percentile(draws,97.5):,.0f}], "
          f"负值占比 {(draws<0).mean()*100:.1f}%")

    # 归档三口径核查
    R['bunching']['archived_three_implementations'] = {
        'note': '归档论文引用三个互相差 5 倍的口径；仓库内只有一个脚本（run_price_bunching.py）',
        'values': [3262, 2257, 11062],
        'repo_scripts_producing_bunching': 1,
        'verdict': '两个口径无脚本可追溯 → 不可复现；本重建给出第四个独立口径',
    }
    json.dump(R, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

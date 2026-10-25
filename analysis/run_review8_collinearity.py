"""第八轮：log_value 与 running variable 的机械共线性量化。

用户假设：log_value 与 r 在 country×year 单元内机械共线，系数对数值处理敏感。
本脚本量化：
  A. 单元内相关：corr(log_value, r | cy)、corr(log_value, r | cy×type)；
     log_value 对 r 的单元内回归 R²（应当接近 1——两者只差单元内常数）。
  B. 主回归中 log_value 的偏 R² / VIF（对 tau 的挤压）。
  C. 控制集敏感度：none / logval / type / prereg 四档的 tau（法定阈值口径）。
  D. 阈值恢复口径的影响：缓存 above vs 整数阈值表重构 above 的错分数。

输出 materials/results/review8_logvalue_collinearity.json
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

CACHE = os.path.join(HERE, 'ted_wide_final.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'review8_logvalue_collinearity.json')

THRESH = {
    2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
    2016: (209000, 5225000), 2017: (209000, 5225000),
    2018: (221000, 5548000), 2019: (221000, 5548000),
    2020: (214000, 5350000), 2021: (214000, 5350000),
    2022: (215000, 5382000), 2023: (215000, 5382000),
}


def rd(d, outcome='single', poly=1, controls=('log_value', 'tu', 'tw')):
    """与 run_v6_rerun_final.py 完全一致的规格：cy 去均值 + 国家聚类（小样本修正）。"""
    dd = d.dropna(subset=[outcome, 'r', 'above']).copy()
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
    from scipy import stats
    i = names.index('tau')
    return {'tau_pp': round(float(beta[i + 1]) * 100, 3),
            'se_pp': round(float(se[i + 1]) * 100, 3),
            'p': round(float(2 * (1 - stats.t.cdf(abs(beta[i + 1] / se[i + 1]), G - 1))), 4),
            'n': int(n)}


def main():
    df = pd.read_csv(CACHE)
    R = {}

    # ---------- A. 单元内共线 ----------
    band = df[(np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9].copy()
    band['lv'] = band['log_value']
    g = band.groupby(band['code'].astype(str) + '_' + band['year'].astype(str))
    lv_dm = g['lv'].transform(lambda s: s - s.mean())
    r_dm = g['r'].transform(lambda s: s - s.mean())
    c_cy = float(np.corrcoef(lv_dm, r_dm)[0, 1])
    g2 = band.groupby(band['code'].astype(str) + '_' + band['year'].astype(str) + '_' + band['type'].astype(str))
    lv_dm2 = g2['lv'].transform(lambda s: s - s.mean())
    r_dm2 = g2['r'].transform(lambda s: s - s.mean())
    c_cyt = float(np.corrcoef(lv_dm2, r_dm2)[0, 1])
    # 单元内回归 R²：lv_dm ~ r_dm（cy 内）
    b = np.polyfit(r_dm, lv_dm, 1)
    ss_res = float(((lv_dm - np.polyval(b, r_dm)) ** 2).sum())
    ss_tot = float((lv_dm ** 2).sum())
    r2_cy = 1 - ss_res / ss_tot
    R['within_cell_collinearity'] = {
        'corr_logvalue_r_within_cy': round(c_cy, 6),
        'corr_logvalue_r_within_cy_type': round(c_cyt, 6),
        'r2_logvalue_on_r_within_cy': round(float(r2_cy), 6),
        'note': '阈值在 (国家,年,类型) 单元内为常数，log_value = r + log(τ) + log 修正，'
                '故单元内相关应为 1（cy 内因类型阈值不同而略小于 1）'}

    # ---------- B. 主回归中 log_value 的 VIF（对 tau 系数的挤压） ----------
    dd = band.dropna(subset=['single', 'r', 'above']).copy()
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    y = dd['single'].astype(float).values
    X = np.column_stack([dd[['above']].astype(float).values, dd['r'].values,
                         (dd['above'].values * dd['r'].values),
                         dd['log_value'].astype(float).values,
                         dd[['tu']].values, dd[['tw']].values])
    keys = dd['code'].astype(str).values + '_' + dd['year'].astype(str).values
    allv = pd.concat([pd.Series(y, name='y')] +
                     [pd.Series(X[:, j], name=['above', 'r', 'ar', 'lv', 'tu', 'tw'][j])
                      for j in range(6)] + [pd.Series(keys, name='k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    cols = ['above', 'r', 'ar', 'lv', 'tu', 'tw']
    Z = np.column_stack([(allv[c] - gm[c]).values for c in cols])
    # VIF: lv 对其余去均值变量回归
    others = [c for c in cols if c != 'lv']
    Zo = np.column_stack([(allv[c] - gm[c]).values for c in others])
    bta, *_ = np.linalg.lstsq(Zo, (allv['lv'] - gm['lv']).values, rcond=None)
    resid = (allv['lv'] - gm['lv']).values - Zo @ bta
    r2_lv = 1 - (resid ** 2).sum() / ((allv['lv'] - gm['lv']).values ** 2).sum()
    R['vif_logvalue'] = {'r2_logvalue_on_other_regressors': round(float(r2_lv), 4),
                         'vif': round(float(1 / (1 - r2_lv)), 2)}

    # ---------- C. 控制集敏感度（法定阈值口径） ----------
    R['control_sets'] = {}
    for lab, ctl in [('none', ()), ('logval', ('log_value',)), ('type', ('tu', 'tw')),
                     ('prereg', ('log_value', 'tu', 'tw'))]:
        R['control_sets'][lab] = rd(band, 'single', controls=ctl)
        print(f"  {lab:7s} tau={R['control_sets'][lab]['tau_pp']:+.2f} "
              f"(SE {R['control_sets'][lab]['se_pp']:.2f}, p={R['control_sets'][lab]['p']:.4f})")

    # ---------- D. 阈值恢复口径错分 ----------
    su = df['year'].map(lambda y: THRESH[int(y)][0])
    w = df['year'].map(lambda y: THRESH[int(y)][1])
    df['thr'] = np.where(df['type'] == 'W', w, su).astype(float)
    thr_rec = np.exp(np.log(df['value']) - df['r'])
    df['above_rec'] = (df['value'] >= thr_rec).astype(int)
    df['above_exact'] = (df['value'] >= df['thr']).astype(int)
    flip_all = int((df['above_rec'] != df['above_exact']).sum())
    flip_band = int(((df['above_rec'] != df['above_exact']) &
                     ((np.exp(df['r']) - 1).abs() <= 0.2 + 1e-9)).sum())
    R['threshold_recovery'] = {
        'flips_full_cache': flip_all, 'flips_in_band': flip_band,
        'note': 'exp(log(v)-r) 恢复阈值存在 ~1e-16 相对误差，使 value 恰好等于'
                '阈值的堆点合同被错分到下方；整数阈值表重构可避免'}

    json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'\nsaved {OUT}')


if __name__ == '__main__':
    main()

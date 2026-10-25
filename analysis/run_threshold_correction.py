"""第五轮复核：法定阈值错误的量化与重算。

背景：论文 Table 1 与代码把 2013-2017 的阈值一律写成 S/U €207,000、W €5,235,000。
欧盟官方法规的正确序列为：
  2013        S/U 200,000   W 5,000,000   （Reg. (EU) 1269/2011, 适用自 2012-01-01）
  2014-2015   S/U 207,000   W 5,186,000   （Reg. (EU) 1336/2013）
  2016-2017   S/U 209,000   W 5,225,000   （Reg. (EU) 2015/2170）
  2018-2019   S/U 221,000   W 5,548,000   （Reg. (EU) 2017/2365）  ← 代码正确
  2020-2021   S/U 214,000   W 5,350,000   （Reg. (EU) 2019/1828）  ← 代码正确
  2022-2023   S/U 215,000   W 5,382,000   （Reg. (EU) 2021/2170）  ← 代码正确

本脚本：
  A. 统计缓存样本中被误分类的合同（按年×类型）；
  B. 估计真实 ±20% 带内、但不在缓存中的合同数（缓存只覆盖代码口径的带）；
  C. 用正确阈值在「缓存带 ∩ 真实带」上重跑主回归、donut、估计价值 RD、
     密度检验、带宽×阶数网格、控制集网格；
  D. 输出 materials/results/threshold_correction.json
"""
import json
import math
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'threshold_correction.json')

# ---------------- 正确阈值 ----------------
TRUE_SU = {2013: 200000, 2014: 207000, 2015: 207000, 2016: 209000, 2017: 209000,
           2018: 221000, 2019: 221000, 2020: 214000, 2021: 214000,
           2022: 215000, 2023: 215000}
TRUE_W = {2013: 5000000, 2014: 5186000, 2015: 5186000, 2016: 5225000, 2017: 5225000,
          2018: 5548000, 2019: 5548000, 2020: 5350000, 2021: 5350000,
          2022: 5382000, 2023: 5382000}
# 代码实际使用的（错误）阈值
CODE_SU = {y: (207000 if y <= 2017 else v) for y, v in TRUE_SU.items()}
CODE_W = {y: (5235000 if y <= 2017 else v) for y, v in TRUE_W.items()}

TOL = 1e-9
BW = 0.2

df = pd.read_csv(CACHE)
df['ratio_code'] = np.exp(df['r'])


def true_thr(row):
    return TRUE_W[row['year']] if row['type'] == 'W' else TRUE_SU[row['year']]


df['thr_true'] = df.apply(true_thr, axis=1)
df['thr_code'] = np.where(df['type'] == 'W',
                          df['year'].map(CODE_W), df['year'].map(CODE_SU))
df['r_true'] = np.log(df['value']) - np.log(df['thr_true'])
df['above_true'] = (df['value'] >= df['thr_true']).astype(int)
df['ratio_true'] = df['value'] / df['thr_true']

out = {'true_thresholds': {'SU': TRUE_SU, 'W': TRUE_W},
       'code_thresholds': {'SU': CODE_SU, 'W': CODE_W}}

# ---------------- A. 误分类统计 ----------------
mis = df[df['above_true'] != df['above']]
by_yt = (mis.groupby(['year', 'type'])
         .agg(n_mis=('above', 'size'))
         .reset_index())
tot_by_yt = df.groupby(['year', 'type']).size().reset_index(name='n_band')
by_yt = by_yt.merge(tot_by_yt, on=['year', 'type'], how='right').fillna({'n_mis': 0})
by_yt['share_pct'] = (by_yt['n_mis'] / by_yt['n_band'] * 100).round(2)
out['misclassified'] = {
    'total': int(len(mis)),
    'share_of_band_pct': round(len(mis) / len(df) * 100, 2),
    'by_year_type': by_yt.to_dict('records'),
    'detail': {
        'coded_below_truly_above': int(((mis['above'] == 0) & (mis['above_true'] == 1)).sum()),
        'coded_above_truly_below': int(((mis['above'] == 1) & (mis['above_true'] == 0)).sum()),
    },
}
print('A. 误分类合同', len(mis), f'({len(mis)/len(df)*100:.2f}% of band)',
      out['misclassified']['detail'])
print(by_yt[by_yt.n_mis > 0].to_string(index=False))

# ---------------- B. 真实带内缺失合同估计 ----------------
# 缓存带 = |v/τ_code - 1| <= 0.2；真实带 = |v/τ_true - 1| <= 0.2
# 缺失 = 真实带 \ 缓存带。用相邻缓存密度外推估计。
missing = []
for y in sorted(df['year'].unique()):
    for t in ('S', 'U', 'W'):
        sub = df[(df['year'] == y) & (df['type'] == t)]
        if len(sub) == 0:
            continue
        tc = CODE_W[y] if t == 'W' else CODE_SU[y]
        tt = TRUE_W[y] if t == 'W' else TRUE_SU[y]
        lo_t, hi_t = 0.8 * tt, 1.2 * tt
        lo_c, hi_c = 0.8 * tc, 1.2 * tc
        gap_lo, gap_hi = [], []
        if lo_t < lo_c - 1:      # 真实带左端超出缓存带
            gap_lo = [lo_t, lo_c]
        if hi_t > hi_c + 1:      # 真实带右端超出缓存带
            gap_hi = [hi_c, hi_t]
        if not gap_lo and not gap_hi:
            continue
        # 用缓存内最靠近缺口的价格密度（每欧元合同数）外推
        v = sub['value'].values
        dens = len(sub) / (hi_c - lo_c)
        est = 0.0
        if gap_lo:
            est += dens * (gap_lo[1] - gap_lo[0])
        if gap_hi:
            est += dens * (gap_hi[1] - gap_hi[0])
        missing.append({'year': int(y), 'type': t, 'n_cached': int(len(sub)),
                        'gap_below_eur': [round(gap_lo[0]), round(gap_lo[1])] if gap_lo else None,
                        'gap_above_eur': [round(gap_hi[0]), round(gap_hi[1])] if gap_hi else None,
                        'est_missing': int(round(est))})
out['missing_from_cache'] = {
    'note': ('缓存只含代码口径 ±20% 带。真实带与缓存带之差用缓存内均价密度外推估计，'
             '为量级估计而非精确计数；精确重跑需要完整 TED 提取。'),
    'by_year_type': missing,
    'est_total_missing': int(sum(m['est_missing'] for m in missing)),
}
print('\nB. 真实带内估计缺失', out['missing_from_cache']['est_total_missing'])
for m in missing:
    print('   ', m)

# ---------------- RD 估计器（国家聚类） ----------------
def rd(d, runvar, treat, outcome='single', controls='none'):
    d = d.dropna(subset=[runvar, treat, outcome, 'log_value']).copy()
    tu = (d['type'] == 'U').astype(float)
    tw = (d['type'] == 'W').astype(float)
    base = [treat, runvar, f'{treat}_x_{runvar}']
    extra = {'none': [], 'type': ['tu', 'tw'], 'logval': ['log_value'],
             'prereg': ['log_value', 'tu', 'tw']}[controls]
    for c in ('tu', 'tw'):
        d[c] = tu if c == 'tu' else tw
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    xcols = base + extra
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
    cl = d['code'].values
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
    return {'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
            'p': round(float(p), 4), 'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


# ---------------- C. 重算（缓存带 ∩ 真实带） ----------------
band = df[(df['ratio_true'] - 1).abs() <= BW + TOL].copy()   # 真实 ±20% 带（缓存内部分）
res_corrected = {}
for ctl in ('none', 'type', 'prereg'):
    res_corrected[ctl] = {'baseline': rd(band, 'r_true', 'above_true', controls=ctl)}
    for w in (0.01, 0.02, 0.03):
        d = band[band['r_true'].abs() > w]
        res_corrected[ctl][f'donut{int(w*100):02d}'] = rd(d, 'r_true', 'above_true', controls=ctl)

# 估计价值 RD（阈值错误同样影响 log_thr）
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = np.log(clean['thr_true'])
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= clean['thr_true']).astype(int)
clean['ratio_est'] = clean['value_est'] / clean['thr_true']
cest = clean[(clean['ratio_est'] - 1).abs() <= BW + TOL]
for ctl in ('none', 'type', 'prereg'):
    res_corrected[ctl]['est_value'] = rd(cest, 'r_est', 'above_est', controls=ctl)

# 带宽 × 阶数（type 控制）
bw_poly = {}
for bw in (0.10, 0.15, 0.20, 0.25):
    d = band[(band['r_true']).abs() <= bw + TOL]
    bw_poly[f'bw{int(bw*100)}_lin'] = rd(d, 'r_true', 'above_true', controls='type')
    dd = d.dropna(subset=['r_true', 'above_true', 'single', 'log_value']).copy()
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['r2'] = dd['r_true'] ** 2
    dd['above_x_r2'] = dd['above_true'] * dd['r2']
    xcols = ['above_true', 'r_true', 'r2', 'above_x_r2', 'tu', 'tw']
    y = dd['single'].astype(float)
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [dd[c].astype(float).rename(c) for c in xcols]
                     + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(dd))] + [(allv[c] - gm[c]).values for c in xcols])
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
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    bw_poly[f'bw{int(bw*100)}_quad'] = {
        'tau_pp': round(float(tau) * 100, 2), 'se_pp': round(float(s) * 100, 2),
        'p': round(float(p), 4), 'n': int(n)}

out['corrected_estimates'] = res_corrected
out['corrected_bandwidth_poly'] = bw_poly

# ---------------- 密度检验（正确阈值） ----------------
r = band['r_true'].values
b = np.floor(r / 0.02).astype(int)
cnt = pd.Series(b).value_counts()
bins = np.arange(-12, 10)
n = np.array([cnt.get(k, 0) for k in bins], dtype=float)
L = n[bins <= -1].sum(); R = n[bins >= 1].sum()
dens_l, dens_r = L / 12, R / 9
gap_frozen = math.log((dens_r + 1) / (dens_l + 1))
fL = (-0.22 - math.log(0.8)) / 0.02
fR = (math.log(1.2) - 0.18) / 0.02
fullL = n[(bins <= -1) & (bins >= -11)]
fullR = n[(bins >= 0) & (bins <= 8)]
dnull = (fullL.sum() + fullR.sum()) / (len(fullL) + len(fullR))
gap_null = math.log(((8 + fR) * dnull / 9 + 1) / ((11 + fL) * dnull / 12 + 1))
ratio_null = ((11 + fL) / 12) / ((8 + fR) / 9)
mL, mR = fullL.mean(), fullR.mean()
sL, sR = fullL.std(ddof=1), fullR.std(ddof=1)
se = math.sqrt(sL**2 / len(fullL) + sR**2 / len(fullR))
t = (mR - mL) / se
cell = (band['code'].astype(str) + '_' + band['year'].astype(str) + '_' + band['type'].astype(str)).values
cells = pd.unique(cell)
ci = {c: np.where(cell == c)[0] for c in cells}
rng = np.random.default_rng(42)
gaps = []
for _ in range(2000):
    pick = rng.choice(cells, size=len(cells), replace=True)
    idx = np.concatenate([ci[c] for c in pick])
    bb = np.floor(r[idx] / 0.02).astype(int)
    c2 = pd.Series(bb).value_counts()
    nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
    Lx = nn[bins <= -1].sum(); Rx = nn[bins >= 1].sum()
    gaps.append(math.log((Rx / 9 + 1) / (Lx / 12 + 1)))
gaps = np.array(gaps)
z_gap = (gap_frozen - gap_null) / gaps.std()
out['corrected_density'] = {
    'left_contracts': int(L), 'right_contracts': int(R),
    'log_density_gap': round(gap_frozen, 5),
    'excess_below_pct': round(dens_l / dens_r - 1, 5),
    'mechanical_log_gap': round(gap_null, 5),
    'bias_corrected_excess_below_pct': round((dens_l / dens_r) / ratio_null - 1, 5),
    'symmetric_full_bins': {'below_mean': round(float(mL), 1), 'above_mean': round(float(mR), 1),
                            't_stat': round(float(t), 3),
                            'p_value': round(float(2 * stats.t.sf(abs(t), 18)), 4)},
    'p_loggap_vs_mechanical_null': round(float(2 * stats.norm.sf(abs(z_gap))), 4),
    'n_band': int(len(band)),
}
print('\n密度检验（正确阈值）:', json.dumps(out['corrected_density'], indent=1))

# ---------------- 与旧结果对比 ----------------
old = json.load(open(os.path.join(ROOT, 'materials', 'results', 'rd_robustness_valuespace_v7.json')))
keymap = {'baseline': 'baseline', 'donut_01': 'donut01', 'donut_02': 'donut02',
          'donut_03': 'donut03', 'est_value': 'est_value'}
cmp_rows = []
for k, nk in keymap.items():
    o = old[k]
    c = res_corrected['none'][nk]
    cmp_rows.append({'spec': k, 'old_tau': o['tau_pp'], 'new_tau': c['tau_pp'],
                     'old_p': o['p'], 'new_p': c['p'], 'old_n': o['n'], 'new_n': c['n']})
out['old_vs_corrected_no_controls'] = cmp_rows
print('\nC. 旧（错阈值，无控制） vs 新（正确阈值，无控制）:')
for r_ in cmp_rows:
    print(f"   {r_['spec']:10s} {r_['old_tau']:+.2f}(p={r_['old_p']:.3f},n={r_['old_n']})"
          f"  ->  {r_['new_tau']:+.2f}(p={r_['new_p']:.3f},n={r_['new_n']})")

json.dump(out, open(OUT, 'w'), indent=2, ensure_ascii=False)
print('\nsaved', OUT)

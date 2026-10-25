"""二轮审稿补充分析 v2：修正版

1. 协变量平衡：阈值 ±0.05 带内 above/below 均值差，国家聚类 SE
   （审稿意见 3：donut 后协变量平衡）
2. donut × 带宽网格（缓存仅含 ±20% 带，±25% 无法用缓存检验，注明）
3. 估计价值子样本 ratio 带敏感性（审稿意见 2）
4. bunching：局部窗口反事实 + (窗口×阶数) 敏感性网格 + bootstrap CI
   （审稿意见 7；全局 ±0.3 多项式外推病态，作为敏感性报告）
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
OUT = os.path.join(ROOT, 'materials', 'results', 'review2_robustness.json')

df = pd.read_csv(CACHE)
df['ratio_v'] = np.exp(df['r'])
res = {}


def diff_means_clustered(d, outcome, treat='above', cluster='code'):
    """简单 above/below 均值差 + 国家聚类 SE"""
    d = d.dropna(subset=[outcome, treat])
    a = d[d[treat] == 1][outcome].astype(float)
    b = d[d[treat] == 0][outcome].astype(float)
    diff = a.mean() - b.mean()
    # 聚类 SE：按国家计算组内 (mean_a - mean_b) 的方差
    dd = d.copy()
    dd['y'] = dd[outcome].astype(float)
    dd['t'] = dd[treat].astype(float)
    g = dd.groupby(cluster).apply(lambda x: x.loc[x['t'] == 1, 'y'].mean() - x.loc[x['t'] == 0, 'y'].mean(),
                                 include_groups=False)
    n_g = len(g)
    se = float(np.sqrt(((g - diff) ** 2).sum() / (n_g * (n_g - 1))))
    t = diff / se if se > 0 else np.nan
    p = 2 * (1 - stats.t.cdf(abs(t), n_g - 1)) if se > 0 else np.nan
    return {'diff': round(float(diff), 4), 'se': round(se, 4), 'p': round(float(p), 3) if se > 0 else None,
            'mean_above': round(float(a.mean()), 4), 'mean_below': round(float(b.mean()), 4),
            'n_above': int(len(a)), 'n_below': int(len(b))}


# ---------- 1. 协变量平衡 ----------
band05 = df[(df['ratio_v'] - 1).abs() <= 0.05]
band05_donut = band05[(band05['ratio_v'] - 1).abs() > 0.01]
balance = {'baseline_pm05': {}, 'donut01_pm05': {}}
for v in ['log_value', 'elec_share']:
    balance['baseline_pm05'][v] = diff_means_clustered(band05, v)
    balance['donut01_pm05'][v] = diff_means_clustered(band05_donut, v)
for t in ['U', 'W']:
    band05[f'is_{t}'] = (band05['type'] == t).astype(float)
    band05_donut[f'is_{t}'] = (band05_donut['type'] == t).astype(float)
    balance['baseline_pm05'][f'share_{t}'] = diff_means_clustered(band05, f'is_{t}')
    balance['donut01_pm05'][f'share_{t}'] = diff_means_clustered(band05_donut, f'is_{t}')
res['covariate_balance'] = balance


# ---------- 2. donut × 带宽网格 ----------
def rd_tau(d, runvar, treat, outcome):
    d = d.dropna(subset=[runvar, treat, outcome]).copy()
    d['ix'] = d[treat] * d[runvar]
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([d[outcome].astype(float).rename('y'), d[treat].astype(float).rename('a'),
                      d[runvar].rename('r'), d['ix'].rename('ar'), keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    X = np.column_stack([np.ones(len(d)), (allv['a'] - gm['a']).values,
                         (allv['r'] - gm['r']).values, (allv['ar'] - gm['ar']).values])
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    resid = yd - X @ beta
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    cl = d['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = X[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    return beta[1] * 100, se[1] * 100, 2 * (1 - stats.t.cdf(abs(beta[1] / se[1]), G - 1))


# 容差 1e-9：比值真值 0.8/1.2 的边界行必须包含在 ±20% 带内
band20 = df[(df['ratio_v'] - 1).abs() <= 0.2 + 1e-9]
grid = {}
for bw in (0.10, 0.15, 0.20):
    for dn in (0.0, 0.01, 0.02):
        # dn=0 表示无 donut；若套用 > 0.0 会误删恰在阈值上的合同
        d = band20 if dn == 0 else band20[(band20['ratio_v'] - 1).abs() > dn]
        d = d[(d['ratio_v'] - 1).abs() <= bw + 1e-9]  # same tolerance
        tau, se, p = rd_tau(d, 'r', 'above', 'single')
        grid[f'bw{int(bw*100)}_donut{int(dn*100):02d}'] = {'tau_pp': round(float(tau), 2),
                                                           'se_pp': round(float(se), 2), 'p': round(float(p), 3)}
res['donut_bandwidth_grid'] = grid
res['donut_bandwidth_note'] = '缓存仅含 ±20% 阈值带（v6 预注册样本），±25% 带宽无法用缓存复现；论文图4的 ±25% 来自 archived v6 运行（全量数据）'

# ---------- 3. 估计价值 ratio 敏感性 ----------
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['log_thr'] = clean['log_value'] - clean['r']
clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
clean['ratio_est'] = clean['value_est'] / np.exp(clean['log_thr'])
sens = {}
for lo, hi in [(0.5, 2.0), (0.67, 1.5), (0.8, 1.25)]:
    c = clean[(clean['ratio'] >= lo) & (clean['ratio'] <= hi)]
    d = c[(c['ratio_est'] - 1).abs() <= 0.2 + 1e-9]
    tau, se, p = rd_tau(d, 'r_est', 'above_est', 'single')
    sens[f'ratio_{lo}_{hi}'] = {'tau_pp': round(float(tau), 2), 'se_pp': round(float(se), 2),
                                'p': round(float(p), 3), 'n': int(len(d))}
res['estvalue_ratio_sensitivity'] = sens

# ---------- 4. bunching：局部窗口 + 敏感性 + bootstrap ----------
r_vals = df['r'].values
mean_val_su = df[(df['r'].abs() <= 0.05) & (df['type'].isin(['S', 'U']))]['value'].mean()


def hist_counts(vals, width=0.02, half=0.30):
    edges = np.arange(-half, half + 1e-9, width)
    cnt, _ = np.histogram(vals, bins=edges)
    centers = (edges[:-1] + edges[1:]) / 2
    return centers, cnt


def excess(centers, cnt, fit_half, window, order):
    mfit = (np.abs(centers) > window) & (np.abs(centers) <= fit_half)
    coef = np.polyfit(centers[mfit], np.log(np.maximum(cnt[mfit], 1)), order)
    cf = np.exp(np.polyval(coef, centers))
    bm = (centers < 0) & (centers >= -window)
    return float((cnt - cf)[bm].sum())


centers, cnt = hist_counts(r_vals)

# 复现原始估计（density.json 口径：±0.23 范围, poly5）
repro = excess(centers, cnt, fit_half=0.23, window=0.02, order=5)

# 敏感性网格
grid_b = {}
for fh in (0.08, 0.10, 0.15, 0.20, 0.23, 0.30):
    for order in (3, 5, 7):
        grid_b[f'fit{fh}_o{order}'] = round(excess(centers, cnt, fit_half=fh, window=0.02, order=order))

# bootstrap CI（复现口径）
rng = np.random.default_rng(20261021)
boots = []
for _ in range(400):
    samp = rng.choice(r_vals, size=len(r_vals), replace=True)
    c2, n2 = hist_counts(samp)
    boots.append(excess(c2, n2, fit_half=0.23, window=0.02, order=5))
boots = np.array(boots)

res['bunching'] = {
    'excess_repro_poly5_fit023': round(repro),
    'excess_boot_ci': [round(float(np.percentile(boots, 2.5))), round(float(np.percentile(boots, 97.5)))],
    'eur_millions_repro': round(repro * mean_val_su / 1e6, 1),
    'eur_boot_ci_millions': [round(float(np.percentile(boots, 2.5)) * mean_val_su / 1e6, 1),
                             round(float(np.percentile(boots, 97.5)) * mean_val_su / 1e6, 1)],
    'sensitivity_grid_window_x_order': grid_b,
    'note': '反事实为对数密度多项式；窗口内仅 −0.01 一个 bin；全局 ±0.30 拟合外推病态（cf 超过所有邻近 bin）',
}
json.dump(res, open(OUT, 'w'), indent=2)
print(json.dumps(res['covariate_balance'], indent=1))
print(json.dumps(res['donut_bandwidth_grid'], indent=1))
print(json.dumps(res['estvalue_ratio_sensitivity'], indent=1))
print(json.dumps(res['bunching'], indent=1))

"""建议7（价格边际）+ 建议10（Chetty bunching 折金额）分析

建议7：从 rd_sample_cache.csv 提取预估价值，算折扣率。
  口径甄别结论：value_est 为程序级（多 lot 合计）预估价值，
  单合同均值 21 万 vs est 均值 525 万（S 类）。
  干净子集：value/value_est ∈ [0.5, 2]（单 lot 或录入约定 est=award 的通知），
  在该子集内比较 单报价 vs 多报价、阈值上 vs 下 的折扣率差异。

建议10：Chetty et al. (2011) bunching 估算——
  多项式拟合反事实密度，超额质量换算成合同数与欧元金额。
"""
import json
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))          # economy/figures
ROOT = os.path.dirname(HERE)                                # economy/

CACHE = os.path.join(ROOT, 'analysis', 'rd_sample_cache.csv')
FIGDIR = HERE
OUT = os.path.join(ROOT, 'materials', 'results')

df = pd.read_csv(CACHE)

# ============================================================
# 建议 10：Bunching 估算（Chetty 2011 简化版）
# ============================================================
dn = json.load(open(f'{FIGDIR}/density.json'))
centers = np.array(dn['centers'])
counts = np.array(dn['counts'])

# 1. 反事实密度：剔除 bunching 窗口 ±0.02，用 5 阶多项式拟合 log(count)
mask_fit = np.abs(centers) > 0.02
coef = np.polyfit(centers[mask_fit], np.log(counts[mask_fit]), 5)
counterfactual = np.exp(np.polyval(coef, centers))

# 2. 超额质量：bunching 窗口内 observed - counterfactual（只在阈值以下堆积）
bunch_mask = (centers < 0) & (centers >= -0.02)
excess = counts[bunch_mask] - counterfactual[bunch_mask]
excess_contracts = float(excess.sum())

# 3. 换算欧元金额：用阈值附近（|r|<=0.05）合同的均值签约价值，按 type 分组
near = df[df['r'].abs() <= 0.05]
mean_val_by_type = near.groupby('type')['value'].mean()
mean_val_overall = near['value'].mean()

# 阈值附近总签约金额（年度化口径：全样本 11 年）
near_total = near['value'].sum()

bunch = {
    'excess_contracts_below_threshold': round(excess_contracts, 1),
    'excess_pct_of_below_binmass': round(
        excess_contracts / counts[centers < 0].sum() * 100, 2),
    'mean_value_near_threshold_by_type': {k: round(float(v)) for k, v in mean_val_by_type.items()},
    'mean_value_near_threshold_overall': round(float(mean_val_overall)),
    'near_threshold_total_value_eur': round(float(near_total)),
    'excess_value_eur_overall': round(excess_contracts * float(mean_val_overall)),
    'excess_value_eur_supply_service': round(
        excess_contracts * float(near[near['type'].isin(['S', 'U'])]['value'].mean())),
    'n_near': int(len(near)),
}
json.dump(bunch, open(f'{OUT}/bunching_eur_v6.json', 'w'), indent=2)
print('=== 建议10 Bunching 估算 ===')
print(f"阈值以下 0.02 带宽内超额合同数: {bunch['excess_contracts_below_threshold']:,.0f}")
print(f"占阈值以下总合同比例: {bunch['excess_pct_of_below_binmass']}%")
print(f"阈值附近均值合同价值: S/U {bunch['mean_value_near_threshold_by_type'].get('S'):,.0f} / "
      f"W {bunch['mean_value_near_threshold_by_type'].get('W'):,.0f} EUR")
print(f"超额合同对应签约金额(全类型均值): EUR {bunch['excess_value_eur_overall']:,.0f}")
print(f"超额合同对应签约金额(仅S/U): EUR {bunch['excess_value_eur_supply_service']:,.0f}")

# ============================================================
# 建议 7：价格边际（折扣率）
# ============================================================
sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
sub['ratio'] = sub['value'] / sub['value_est']
clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
clean['discount'] = 1 - clean['ratio']  # 折扣率：est 高于 award 的部分

price = {
    'n_total': int(len(df)),
    'n_est_populated': int((df['value_est'] > 0).sum()),
    'coverage_pct': round((df['value_est'] > 0).mean() * 100, 1),
    'n_clean': int(len(clean)),
    'clean_share_of_populated_pct': round(len(clean) / max((df['value_est'] > 0).sum(), 1) * 100, 1),
}

# 1) 单报价 vs 多报价（干净子集）
g_single = clean.groupby('single')['discount'].agg(['mean', 'median', 'count'])
price['discount_by_single_offer'] = {
    'single': {'mean': round(float(g_single.loc[1, 'mean']), 4),
               'median': round(float(g_single.loc[1, 'median']), 4),
               'n': int(g_single.loc[1, 'count'])},
    'multi': {'mean': round(float(g_single.loc[0, 'mean']), 4),
              'median': round(float(g_single.loc[0, 'median']), 4),
              'n': int(g_single.loc[0, 'count'])},
}

# 2) 阈值上 vs 下（干净子集）
g_above = clean.groupby('above')['discount'].agg(['mean', 'median', 'count'])
price['discount_by_above'] = {
    'below': {'mean': round(float(g_above.loc[0, 'mean']), 4),
              'median': round(float(g_above.loc[0, 'median']), 4),
              'n': int(g_above.loc[0, 'count'])},
    'above': {'mean': round(float(g_above.loc[1, 'mean']), 4),
              'median': round(float(g_above.loc[1, 'median']), 4),
              'n': int(g_above.loc[1, 'count'])},
}

# 3) RD 估计：discount ~ above，±20% 带宽，线性，控制 log value + type
rd_band = clean[clean['r'].abs() <= 0.2].copy()
rd_band['lv'] = rd_band['log_value']
X = np.column_stack([
    np.ones(len(rd_band)),
    rd_band['above'],
    rd_band['r'],
    rd_band['above'] * rd_band['r'],
    rd_band['lv'],
])
# type 固定效应
for t in ['U', 'W']:
    X = np.column_stack([X, (rd_band['type'] == t).astype(float)])
y = rd_band['discount'].values
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
resid = y - X @ beta
# 按国家聚类标准误（country 未在缓存中，用 type×year 近似聚类的保守下界）
dof = len(y) - X.shape[1]
sigma2 = resid @ resid / dof
XtX_inv = np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(XtX_inv) * sigma2)
tau, se_tau = beta[1], se[1]
tstat = tau / se_tau
from scipy import stats
pval = 2 * (1 - stats.t.cdf(abs(tstat), dof))
ci = (tau - 1.96 * se_tau, tau + 1.96 * se_tau)
price['rd_discount'] = {
    'tau': round(float(tau), 4), 'se': round(float(se_tau), 4),
    't': round(float(tstat), 3), 'p': round(float(pval), 4),
    'ci95': [round(float(ci[0]), 4), round(float(ci[1]), 4)],
    'n': int(len(rd_band)),
}

# 4) 单报价 × 阈值 四分格（干净子集）
clean['cell'] = clean['single'].map({1: 'single', 0: 'multi'}) + '_' + clean['above'].map({1: 'above', 0: 'below'})
g_cell = clean.groupby('cell')['discount'].agg(['mean', 'count'])
price['discount_by_cell'] = {k: {'mean': round(float(v['mean']), 4), 'n': int(v['count'])}
                             for k, v in g_cell.iterrows()}

json.dump(price, open(f'{OUT}/price_margin_v6.json', 'w'), indent=2)
print()
print('=== 建议7 价格边际 ===')
print(f"预估价值覆盖率: {price['coverage_pct']}% ({price['n_est_populated']:,}/{price['n_total']:,})")
print(f"干净子集(ratio 0.5-2): {price['n_clean']:,} ({price['clean_share_of_populated_pct']}% of populated)")
print(f"单报价折扣率: mean {price['discount_by_single_offer']['single']['mean']:.4f} | "
      f"多报价: {price['discount_by_single_offer']['multi']['mean']:.4f}")
print(f"阈值下折扣率: {price['discount_by_above']['below']['mean']:.4f} | "
      f"阈值上: {price['discount_by_above']['above']['mean']:.4f}")
print(f"RD(折扣率~above): tau={price['rd_discount']['tau']:+.4f} "
      f"(SE {price['rd_discount']['se']:.4f}, p={price['rd_discount']['p']:.4f}, "
      f"CI [{price['rd_discount']['ci95'][0]:+.4f}, {price['rd_discount']['ci95'][1]:+.4f}], n={price['rd_discount']['n']:,})")
print('四分格:', {k: v['mean'] for k, v in price['discount_by_cell'].items()})

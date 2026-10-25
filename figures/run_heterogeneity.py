"""论文 7.2 异质性分析：按合同类型 + 按 CPI 分组的 TWFE（v4 口径）"""
import os, sys, json
import numpy as np
import pandas as pd
from scipy import stats

BASE = r'C:\Users\OMEN\Desktop\neo'
sys.path.insert(0, os.path.join(BASE, 'identification'))
from estimators_v4 import contract_regression

micro = pd.read_csv(os.path.join(BASE, 'data', 'interim', 'ted_micro.csv'))
# 构建 treated_post（与 run_v4.prep 相同口径）
import csv as _csv
cohorts = {}
with open(os.path.join(BASE, 'data', 'external', 'eu_transposition_2014_24.csv'), encoding='utf-8-sig') as f:
    for r in _csv.DictReader(f):
        cohorts[r['code']] = int(r['event_year']) if r['event_year'] else None
micro['event_year'] = micro['code'].map(cohorts)
micro['treated'] = micro['event_year'].notna().astype(int)
micro['post'] = np.where(micro['treated'] == 1,
                         (micro['year'] >= micro['event_year']).astype(float), 0.0)
micro['treated_post'] = micro['treated'] * micro['post']
cpi = pd.read_csv(os.path.join(BASE, 'data', 'raw', 'expanded_corruption_cpi.csv'))
print('micro:', micro.shape, '| cpi 列:', list(cpi.columns))

R = {}

# ---- 1. 按合同类型分组 ----
print('\n=== 按合同类型（TWFE, share_single_offer）===')
for tc, name in [('S', 'Supply'), ('U', 'Service'), ('W', 'Works')]:
    sub = micro[micro['type'] == tc]
    try:
        res = contract_regression(sub, 'share_single_offer', 'treated_post', ['log_mean_value', 'mean_lots', 'mean_n_awards'])
        b = res['treated_post']
        R[f'type_{tc}'] = {'beta': b['beta'], 'se': b['se'], 'p': b['p'], 'ci': b['ci'], 'n': res['n']}
        print(f"  {name:8s}: beta={b['beta']:+.4f} (se {b['se']:.4f}, p={b['p']:.3f}, "
              f"CI [{b['ci'][0]:.4f}, {b['ci'][1]:.4f}], n={res['n']})")
    except Exception as e:
        print(f'  {name}: 失败 {e}')

# ---- 2. 按 CPI 分组（国家 CPI 中位数）----
print('\n=== 按 CPI 分组（国家腐败感知） ===')
# cpi 列名探测
cc = [c for c in cpi.columns if c not in ('code', 'year')]
print('  cpi 值列:', cc[:3])
if 'cpi' in cpi.columns:
    vcol = 'cpi'
else:
    vcol = cc[0]
cpi2 = cpi[['code', 'year', vcol]].rename(columns={vcol: 'cpi'})
m2 = micro.merge(cpi2, on=['code', 'year'], how='left')
med = m2['cpi'].median()
print(f'  CPI 中位数: {med:.1f} | 有 CPI 的箱: {m2["cpi"].notna().sum()}/{len(m2)}')
for lab, mask in [('High CPI (cleaner)', m2['cpi'] > med), ('Low CPI (more corrupt)', m2['cpi'] <= med)]:
    sub = m2[mask].dropna(subset=['cpi'])
    if len(sub) < 500:
        print(f'  {lab}: 样本不足 ({len(sub)})')
        continue
    try:
        res = contract_regression(sub, 'share_single_offer', 'treated_post', ['log_mean_value', 'mean_lots', 'mean_n_awards'])
        b = res['treated_post']
        R[f'cpi_{lab.split()[0].lower()}'] = {'beta': b['beta'], 'se': b['se'], 'p': b['p'],
                                              'ci': b['ci'], 'n': res['n']}
        print(f"  {lab:24s}: beta={b['beta']:+.4f} (se {b['se']:.4f}, p={b['p']:.3f}, "
              f"CI [{b['ci'][0]:.4f}, {b['ci'][1]:.4f}], n={res['n']})")
    except Exception as e:
        print(f'  {lab}: 失败 {e}')

# ---- 3. 全样本基准 ----
res = contract_regression(micro, 'share_single_offer', 'treated_post', ['log_mean_value', 'mean_lots', 'mean_n_awards'])
b = res['treated_post']
R['baseline'] = {'beta': b['beta'], 'se': b['se'], 'p': b['p'], 'ci': b['ci'], 'n': res['n']}
print(f"\n  基准（全样本）: beta={b['beta']:+.4f} (p={b['p']:.3f})")

out = r'C:\Users\OMEN\Desktop\economy\materials\results\heterogeneity_v6.json'
json.dump(R, open(out, 'w'), indent=1)
print(f'\n已写 {out}')

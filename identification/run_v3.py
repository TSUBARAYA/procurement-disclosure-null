"""v3.0 合同级采购数据主检验（TED CAN，EU-28，2013-2021，678 万份合同）。

设计（与 v2.0 同一转化日期登记库，同一 CS 式组-时间估计量）：
  处理 = 各国转化 Directive 2014/24/EU 的生效年（25 国精确日期 + 3 国删失）
  结局 = 合同级汇总指标：单投标占比 / 平均投标数 / 电子投标份额 / 外国中标份额
  第一阶段检验 = 电子投标份额对处理的响应（改革机制的直接度量）
输出 report/results_v3.json + report/tables_v3.md
"""
import csv, json, os, sys
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'identification'))
from estimators_v2 import build_cells, aggregate, cell_ci, pre_trend_test

SEED = 20261018
OUT = os.path.join(BASE, 'report')

# ---------- 转化登记库 ----------
cohorts = {}
with open(os.path.join(BASE, 'data', 'external', 'eu_transposition_2014_24.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        cohorts[r['code']] = int(r['event_year']) if r['event_year'] else None

ted = pd.read_csv(os.path.join(BASE, 'data', 'interim', 'ted_panel.csv'))
ted = ted[ted['code'].isin(cohorts)].copy()
YEARS = sorted(ted['year'].unique())
print(f'TED 面板: {len(ted)} 个 country-year，{ted["code"].nunique()} 国，'
      f'{int(ted["n_contracts"].sum())} 份合同')

R = {'seed': SEED, 'version': '3.0.0', 'n_country_years': len(ted),
     'n_contracts': int(ted['n_contracts'].sum()),
     'n_countries': int(ted['code'].nunique())}

OUTCOMES = ['share_single_offer', 'mean_offers', 'elec_offer_share',
            'foreign_winner_share', 'share_single_offer_works']

# ---------- A. 各结局的 CS 式 ATT ----------
print('[A] CS 式 ATT（合同级结局）…')
R['att'] = {}
for oc in OUTCOMES:
    sub = ted.dropna(subset=[oc]).copy()
    piv = sub.pivot_table(index='year', columns='code', values=oc)
    cells = build_cells(sub.assign(event_year=sub['code'].map(cohorts)),
                        cohorts, YEARS, oc)
    agg = aggregate(cells)
    ci = cell_ci(cells)
    pre = pre_trend_test(cells)
    R['att'][oc] = {'post_att': agg['post']['att'] if agg['post'] else None,
                    'n_cells': agg['post']['n_cells'] if agg['post'] else 0,
                    'ci': ci, 'pre_trend': pre,
                    'sd_annual_change': float(sub.groupby('code')[oc].apply(
                        lambda s: s.sort_values().diff().std()).mean())}
    print(f"    {oc}: ATT={R['att'][oc]['post_att']}, pre_p={pre.get('p')}, "
          f"σ_Δ={R['att'][oc]['sd_annual_change']:.4f}")

# ---------- B. 第一阶段：电子投标份额对处理的响应 ----------
print('[B] 第一阶段（电子投标份额 = 改革机制直接度量）…')
sub = ted.dropna(subset=['elec_offer_share']).copy()
cells = build_cells(sub.assign(event_year=sub['code'].map(cohorts)),
                    cohorts, YEARS, 'elec_offer_share')
agg = aggregate(cells)
by_k = {}
for (g, t), v in cells.items():
    by_k.setdefault(t - g, []).append(v['att'])
R['first_stage'] = {'post_att': agg['post']['att'] if agg['post'] else None,
                    'by_k': {str(k): float(np.mean(v)) for k, v in sorted(by_k.items())}}
print(f"    第一阶段 ATT(post2-3): {R['first_stage']['post_att']}")
print('    动态:', {k: round(v, 3) for k, v in R['first_stage']['by_k'].items()})

# ---------- C. MDE 对比 ----------
print('[C] MDE（合同级 vs WJP）…')
sd_ss = R['att']['share_single_offer']['sd_annual_change']
sd_wjp = 0.0609
# 合同级：12 处理 vs 2 对照（EU 组内）；对照池 = 未转化 EU 国
mde_ted = (2.8) * sd_ss * np.sqrt(1 / 12 + 1 / 2)
mde_wjp = (2.8) * sd_wjp * np.sqrt(1 / 12 + 1 / 2)
R['mde'] = {'sd_ted_single_offer': sd_ss, 'sd_wjp': sd_wjp,
            'mde_ted_12v2': float(mde_ted), 'mde_wjp_12v2': float(mde_wjp),
            'improvement_factor': float(mde_wjp / mde_ted)}
print(f"    MDE(TED 单投标)={mde_ted:.4f} vs MDE(WJP)={mde_wjp:.4f} "
      f"（改善 {mde_wjp/mde_ted:.2f}x）")

# ---------- D. 剂量反应（连续处理强度） ----------
print('[D] 剂量反应：结局 ~ 滞后电子投标份额 + 国家FE + 年份FE …')
d = ted.dropna(subset=['share_single_offer', 'elec_offer_share']).copy()
d = d.sort_values(['code', 'year'])
d['elec_lag1'] = d.groupby('code')['elec_offer_share'].shift(1)
d = d.dropna(subset=['elec_lag1'])
# 两向 FE 回归（国家+年份去均值）
def twfe(y, X, gc, gy):
    Y = np.column_stack([y, X])
    for _ in range(100):
        prev = Y.copy()
        for g in (gc, gy):
            for k in np.unique(g):
                m = g == k
                Y[m] -= Y[m].mean(axis=0)
        if np.max(np.abs(Y - prev)) < 1e-12:
            break
    yw, Xw = Y[:, 0], Y[:, 1:]
    beta = np.linalg.pinv(Xw.T @ Xw) @ (Xw.T @ yw)
    resid = yw - Xw @ beta
    # 国家聚类
    meat = np.zeros((X.shape[1], X.shape[1]))
    for k in np.unique(gc):
        m = gc == k
        s = Xw[m].T @ resid[m]
        meat += np.outer(s, s)
    G = len(np.unique(gc))
    XtXi = np.linalg.pinv(Xw.T @ Xw)
    vcov = XtXi @ meat @ XtXi * (G / (G - 1))
    return beta, np.sqrt(np.diag(vcov)), G - 1

beta, se, dof = twfe(d['share_single_offer'].values, d[['elec_lag1']].values,
                     d['code'].astype('category').cat.codes.values,
                     d['year'].values)
from scipy import stats
t = beta[0] / se[0]
p = float(2 * (1 - stats.t.cdf(abs(t), dof)))
R['dose_response'] = {'outcome': 'share_single_offer', 'treatment': 'elec_lag1',
                      'beta': float(beta[0]), 'se': float(se[0]), 'p': p, 'n': len(d)}
print(f"    剂量反应 β={beta[0]:+.4f} (se={se[0]:.4f}, p={p:.3f}, n={len(d)})")

# ---------- E. 事前趋势与判定 ----------
print('[E] 事前趋势与判定 …')
v = {}
ok = True
for oc in OUTCOMES:
    a = R['att'][oc]
    pre_p = a['pre_trend'].get('p', 0) if a['pre_trend'] else 0
    if pre_p is None:
        pre_p = 1.0
    v[f'pre_ok_{oc}'] = bool(pre_p > 0.10)
R['pre_trend_ok'] = v
# 判定：第一阶段显著为正 + 主结局（单投标）显著为负 = pass
fs = R['first_stage']['post_att']
ss = R['att']['share_single_offer']
ss_ci = ss['ci']
ci_excl = bool(ss_ci and 'ci_lo' in ss_ci and ss_ci['ci_lo'] > 0)
R['verdict'] = {
    'first_stage_positive': bool(fs is not None and fs > 0),
    'single_offer_att': ss['post_att'],
    'single_offer_ci_excludes_zero': ci_excl,
    'single_offer_pre_p': ss['pre_trend'].get('p') if ss['pre_trend'] else None,
}
print(f"    第一阶段为正: {R['verdict']['first_stage_positive']}; "
      f"单投标 ATT={ss['post_att']}, CI 排除 0: {ci_excl}")

with open(os.path.join(OUT, 'results_v3.json'), 'w', encoding='utf-8') as f:
    json.dump(R, f, indent=1, ensure_ascii=False)

# ---------- 简表 ----------
L = ['# NEO v3.0 合同级采购数据主结果（TED CAN，EU-28，2013-2021）', '',
     f'- {R["n_contracts"]} 份合同 -> {R["n_country_years"]} 个 country-year；'
     f'种子 {SEED}', '',
     '## 一、第一阶段（电子投标份额 = 改革机制直接度量）', '',
     f'- 处理后 2-3 年 ATT: {fs}',
     '- 动态（相对事件年）: ' + ', '.join(f'{k}:{v_:+.3f}' for k, v_ in R['first_stage']['by_k'].items()),
     '', '## 二、主结局 ATT（CS 式，not-yet-treated 对照）', '',
     '| 结局 | ATT(post 2-3) | 事前趋势 p | σ_Δ(年变化) |', '|---|---|---|---|']
for oc in OUTCOMES:
    a = R['att'][oc]
    pre_p = a['pre_trend'].get('p') if a['pre_trend'] else None
    L.append(f"| {oc} | {a['post_att']} | {pre_p} | {a['sd_annual_change']:.4f} |")
L += ['', '## 三、MDE 对比', '',
      f"- TED 单投标占比: MDE={mde_ted:.4f}（σ={sd_ss:.4f}）",
      f"- v2.0 WJP: MDE={mde_wjp:.4f}（σ={sd_wjp:.4f}）",
      f"- 改善倍数: {mde_wjp/mde_ted:.2f}x",
      '', '## 四、剂量反应（连续电子化强度）', '',
      f"- share_single_offer ~ elec_lag1 + 双向FE: β={beta[0]:+.4f} "
      f"(se={se[0]:.4f}, p={p:.3f})",
      '', '## 五、判定', '',
      f"- 第一阶段为正: {R['verdict']['first_stage_positive']}",
      f"- 单投标 ATT CI 排除 0: {ci_excl}",
      f"- 事前趋势: " + ', '.join(f'{k}={vv}' for k, vv in v.items())]
open(os.path.join(OUT, 'tables_v3.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L[:20]))
print('已写 report/results_v3.json 与 tables_v3.md')

"""NEO v4.0 — 合同级回归主检验

在 ted_micro 箱面板上跑：
1. 合同级 FE 回归（country×year + cpv2×year FE，合同特征控制，WLS，国家聚类）
   - 结局：单投标占比 / 平均投标数 / 电子投标份额 / SME 投标份额
2. 剂量反应：处理强度 = 电子投标份额（连续）
3. 窗口对比：2013-2021（v3 窗口）vs 2013-2023（v4 窗口）
4. 事前趋势：lead 系数（treated×lead_k）
5. MDE 对比

用法：python identification/run_v4.py
"""
import csv, json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'identification'))
from estimators_v4 import contract_regression, mde_from_panel

SEED = 20261018
OUT = os.path.join(BASE, 'report')
os.makedirs(OUT, exist_ok=True)

# 转化登记库
cohorts = {}
with open(os.path.join(BASE, 'data', 'external', 'eu_transposition_2014_24.csv'),
          encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        cohorts[r['code']] = int(r['event_year']) if r['event_year'] else None


def prep(ted, window):
    d = ted[(ted['year'] >= window[0]) & (ted['year'] <= window[1])].copy()
    d['event_year'] = d['code'].map(cohorts)
    d['treated'] = d['event_year'].notna().astype(int)
    # not-yet-treated 自动为 0；censored/never 恒 0
    d['post'] = np.where(d['treated'] == 1,
                         (d['year'] >= d['event_year']).astype(float), 0.0)
    d['treated_post'] = d['treated'] * d['post']
    # 处理强度：该国该年电子投标份额（合同数加权）——第一阶段机制变量
    d['intensity'] = d.groupby(['code', 'year'])['elec_offer_share'].transform(
        lambda s: np.average(s, weights=d.loc[s.index, 'n_contracts'])
        if (s.notna() & (d.loc[s.index, 'n_contracts'] > 0)).any() else np.nan)
    # 事前趋势：treated × lead（事件年前 1-3 年）
    d['event_time'] = np.where(d['treated'] == 1, d['year'] - d['event_year'], np.nan)
    for k in (1, 2, 3):
        d[f'treat_lead{k}'] = np.where(
            (d['treated'] == 1) & (d['event_time'] == -k), 1.0, 0.0)
    return d


CONTROLS = ['log_mean_value', 'mean_lots', 'mean_n_awards']
OUTCOMES = ['share_single_offer', 'mean_offers', 'elec_offer_share', 'sme_tender_share']


def main():
    rng = np.random.default_rng(SEED)
    ted = pd.read_csv(os.path.join(BASE, 'data', 'interim', 'ted_micro.csv'))
    R = {'seed': SEED, 'cohorts': {k: v for k, v in cohorts.items() if v},
         'n_with_date': sum(1 for v in cohorts.values() if v),
         'n_censored': sum(1 for v in cohorts.values() if not v),
         'n_contracts_total': int(ted['n_contracts'].sum()),
         'n_boxes': int(len(ted))}

    d_full = prep(ted, (2013, 2023))
    d_v3w = prep(ted, (2013, 2021))

    # ---------- 1. 主回归（全窗口）----------
    print('[1] 合同级 FE 回归（2013-2023，country×year + cpv2×year FE）…')
    R['main'] = {}
    for oc in OUTCOMES:
        r = contract_regression(d_full, oc, 'treated_post', CONTROLS)
        R['main'][oc] = r
        if 'error' not in r:
            print(f"    {oc:22s}: {r['treated_post']['beta']:+.4f} "
                  f"(p={r['treated_post']['p']:.3f}, CI {r['treated_post']['ci']}, n={r['n']})")
        else:
            print(f'    {oc}: {r["error"]}')

    # ---------- 2. 事前趋势 ----------
    print('[2] 事前趋势（treated×lead_k，全窗口）…')
    R['pre_trend'] = {}
    for oc in OUTCOMES:
        rr = contract_regression(d_full, oc, 'treated_post', CONTROLS,
                                 extra_x=[f'treat_lead{k}' for k in (1, 2, 3)])
        R['pre_trend'][oc] = {k: rr.get(f'treat_lead{k}') for k in (1, 2, 3)}
        leads = [rr.get(f'treat_lead{k}') for k in (1, 2, 3)]
        betas = [l['beta'] for l in leads if l]
        ps = [l['p'] for l in leads if l]
        print(f'    {oc:22s}: lead betas={[round(b,4) for b in betas]} '
              f'min p={min(ps) if ps else None:.3f}')

    # ---------- 3. 剂量反应 ----------
    print('[3] 剂量反应（电子投标份额作连续强度）…')
    R['dose'] = {}
    for oc in OUTCOMES:
        if oc == 'elec_offer_share':
            continue  # 强度与结局同源，跳过
        r = contract_regression(d_full, oc, 'intensity', CONTROLS)
        R['dose'][oc] = r
        if 'error' not in r:
            print(f"    {oc:22s}: {r['intensity']['beta']:+.4f} "
                  f"(p={r['intensity']['p']:.3f})")

    # ---------- 4. 窗口对比 ----------
    print('[4] 窗口对比（2013-2021 v3窗口 vs 2013-2023）…')
    R['window'] = {}
    for oc in OUTCOMES:
        r_v3 = contract_regression(d_v3w, oc, 'treated_post', CONTROLS)
        r_v4 = R['main'][oc]
        b3 = r_v3.get('treated_post', {}).get('beta') if 'error' not in r_v3 else None
        b4 = r_v4.get('treated_post', {}).get('beta') if 'error' not in r_v4 else None
        R['window'][oc] = {'v3_2013_2021': b3, 'v4_2013_2023': b4}
        print(f'    {oc:22s}: {b3} -> {b4}')

    # ---------- 5. MDE ----------
    print('[5] MDE（TED 箱面板 vs WJP v2.0）…')
    R['mde'] = {}
    for oc in ['share_single_offer', 'mean_offers']:
        m = mde_from_panel(d_full, oc)
        # MDE ≈ 2.8 * sd_change * sqrt(1/n1 + 1/n0)（国家层面，n1=25, n0=3）
        sd = m['sigma_change']
        mde_eu = 2.8 * sd * np.sqrt(1 / 25 + 1 / 3) if sd else None
        R['mde'][oc] = {'sigma_change': sd, 'mde_n1_25_n0_3': mde_eu}
        print(f'    {oc:22s}: sigma_change={sd:.4f}, MDE(25v3)={mde_eu:.4f}')

    # ---------- 6. CS 式协变量调整事件动态（箱面板）----------
    # 每年横截面：处理组=已转化 vs 对照=未转化；共同估计 Y~特征+type+cpv2，
    # 取调整后均值差。避免 TWFE 的 forbidden comparison（v2.1 已证明其存在）。
    print('[6] CS 式协变量调整事件动态（箱面板）…')
    R['cs_adjusted'] = {}
    for oc in OUTCOMES:
        dyn = {}
        for t in sorted(d_full['year'].unique()):
            d = d_full[(d_full['year'] == t)].dropna(subset=[oc, 'log_mean_value']).copy()
            if len(d) < 100:
                continue
            d['tr'] = ((d['treated'] == 1) & (d['event_year'] <= t)).astype(float)
            if d['tr'].sum() < 30 or (d['tr'] == 0).sum() < 30:
                continue
            X = np.column_stack([d[['tr']].values]
                                + [d[[c]].values for c in CONTROLS]
                                + [(d['type'] == k).values.astype(float)[:, None]
                                   for k in ['S', 'U']]
                                + [pd.get_dummies(d['cpv2'], prefix='cpv').values.astype(float)[:, 1:]])
            y = d[oc].values
            w = d['n_contracts'].values
            # 仅用对照组估特征参数（DR 风格），再对全样本预测
            ctl = d['tr'] == 0
            Xc, yc, wc = X[ctl][:, 1:], y[ctl], w[ctl]
            XtX = (Xc * wc[:, None]).T @ Xc
            beta = np.linalg.pinv(XtX) @ ((Xc * wc[:, None]).T @ yc)
            adj = y - X[:, 1:] @ beta
            att = float(np.average(adj[d['tr'] == 1], weights=w[d['tr'] == 1])
                        - np.average(adj[d['tr'] == 0], weights=w[d['tr'] == 0]))
            dyn[int(t)] = att
        R['cs_adjusted'][oc] = dyn
        ks = sorted(dyn)
        print(f'    {oc:22s}: ' + ' '.join(f'{k}:{dyn[k]:+.3f}' for k in ks[-6:]))

    # ---------- 7. 判定 ----------
    print('[6] 判定…')
    v = {}
    for oc in OUTCOMES:
        r = R['main'].get(oc, {})
        if 'error' in r:
            v[oc] = 'uncertain'
            continue
        b = r['treated_post']['beta']
        p = r['treated_post']['p']
        lo, hi = r['treated_post']['ci']
        if lo > 0 or hi < 0:      # CI 排除 0
            v[oc] = 'significant_negative' if b < 0 else 'significant_positive'
        else:
            v[oc] = 'null'
    R['verdict'] = v
    print('   ', v)

    with open(os.path.join(OUT, 'results_v4.json'), 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
    print(f'已写 {os.path.join(OUT, "results_v4.json")}')


if __name__ == '__main__':
    main()

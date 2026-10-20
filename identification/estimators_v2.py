"""v2.0 估计量：CS 式（Callaway-Sant'Anna 精神）队列 ATT + 事前趋势 + 特异性。

单元定义：ATT(g,t) = [Ȳ_g,t − Ȳ_g,g−1] − [Ȳ_C(g,t),t − Ȳ_C(g,t),g−1]
  C(g,t) = t 时尚未转化的 EU 国（censored 三国永久留在对照池——保守处理）
  t 可取 g 前后（t<g−1 的单元即"前导系数"，用于事前趋势检验）
汇总：post 窗口 [2,3] 与前导窗口 [−3,−1] 分别按队列规模加权平均。
与 v1.0 的区别：不用全样本 TWFE 事件研究（交错采用下会产生负权重）。
"""
import numpy as np


def build_cells(panel, cohorts, years, outcome, min_control=2, min_treated=1):
    """panel: DataFrame[code,year,outcome]；cohorts: dict code->event_year（None=删失）。
    返回 {(g,t): {...}}，含 t<g−1 的前导单元。"""
    piv = panel.pivot_table(index='year', columns='code', values=outcome)
    cells = {}
    cohort_years = sorted({y for y in cohorts.values() if y is not None})
    for g in cohort_years:
        g_codes = [c for c, y in cohorts.items() if y == g and c in piv.columns]
        if len(g_codes) < min_treated:
            continue
        b = g - 1
        if b not in piv.index:
            continue
        for t in years:
            if t == b or t not in piv.index:
                continue
            ctrl = [c for c, y in cohorts.items()
                    if (y is None or y > t) and c in piv.columns]
            if len(ctrl) < min_control:
                continue
            y_t = piv.loc[t, g_codes].dropna()
            y_b = piv.loc[b, g_codes].dropna()
            common_t = y_t.index.intersection(y_b.index)
            if len(common_t) < min_treated:
                continue
            y_ct = piv.loc[t, ctrl].dropna()
            y_cb = piv.loc[b, ctrl].dropna()
            common_c = y_ct.index.intersection(y_cb.index)
            if len(common_c) < min_control:
                continue
            att = (y_t[common_t].mean() - y_b[common_t].mean()) - \
                  (y_ct[common_c].mean() - y_cb[common_c].mean())
            cells[(g, t)] = {'att': float(att), 'n_treated': len(common_t),
                             'n_control': len(common_c),
                             'treated': list(common_t), 'control': list(common_c)}
    return cells


def _wagg(items):
    if not items:
        return None
    ws = np.array([c['n_treated'] for c in items], float)
    atts = np.array([c['att'] for c in items], float)
    return {'att': float(np.average(atts, weights=ws)), 'n_cells': len(items),
            'cells': [(c['n_treated'], c['n_control'], round(c['att'], 5)) for c in items]}


def aggregate(cells, window=(2, 3), pre_window=(-3, -1)):
    post = [v for (g, t), v in cells.items() if window[0] <= t - g <= window[1]]
    pre = [v for (g, t), v in cells.items() if pre_window[0] <= t - g <= pre_window[1]]
    return {'post': _wagg(post), 'pre': _wagg(pre)}


def cell_ci(cells, window=(2, 3)):
    """汇总 ATT 区间：跨 (g,t) 单元经验分位（保守，含单元间离散）。"""
    atts = [v['att'] for (g, t), v in cells.items() if window[0] <= t - g <= window[1]]
    if len(atts) < 3:
        return {'n_cells': len(atts), 'note': '单元不足3，不报分位区间'}
    a = np.array(atts)
    return {'mean': float(a.mean()), 'ci_lo': float(np.percentile(a, 2.5)),
            'ci_hi': float(np.percentile(a, 97.5)), 'n_cells': len(a),
            'share_negative': float(np.mean(a < 0))}


def pre_trend_test(cells, pre_window=(-3, -1)):
    """事前趋势：前导单元 ATT 是否联合偏离 0（t 检验 + 规模加权均值）。"""
    from scipy import stats
    items = [v for (g, t), v in cells.items() if pre_window[0] <= t - g <= pre_window[1]]
    if len(items) < 4:
        return {'error': '前导单元不足', 'n': len(items)}
    ws = np.array([c['n_treated'] for c in items], float)
    a = np.array([c['att'] for c in items])
    wmean = float(np.average(a, weights=ws))
    tstat, p = stats.ttest_1samp(a, 0.0)
    return {'weighted_mean_pre_att': wmean, 'equal_mean': float(a.mean()),
            't': float(tstat), 'p': float(p), 'n_cells': len(a),
            'share_negative': float(np.mean(a < 0))}


def placebo_timing(panel, cohorts, years, outcome, n_perm=500, seed=0, min_control=2):
    """安慰剂时点：EU 内随机打乱转化队列，重算汇总 ATT 分布。"""
    rng = np.random.default_rng(seed)
    codes = list(cohorts.keys())
    real_years = [y for y in cohorts.values() if y is not None]
    obs = []
    for _ in range(n_perm):
        fake = {c: (cohorts[c] if cohorts[c] is None else int(rng.choice(real_years)))
                for c in codes}
        panel2 = panel.copy()
        panel2['event_year'] = panel2['code'].map(fake)
        cells = build_cells(panel2, fake, years, outcome, min_control=min_control)
        agg = aggregate(cells)
        if agg['post']:
            obs.append(agg['post']['att'])
    if len(obs) < 30:
        return {'error': 'placebo 运行不足', 'n': len(obs)}
    a = np.array(obs)
    from scipy import stats
    tstat, p = stats.ttest_1samp(a, 0.0)
    return {'mean': float(a.mean()), 'sd': float(a.std()),
            'ci_lo': float(np.percentile(a, 2.5)), 'ci_hi': float(np.percentile(a, 97.5)),
            't': float(tstat), 'p': float(p), 'n': len(a)}

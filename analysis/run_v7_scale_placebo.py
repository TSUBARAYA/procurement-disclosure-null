"""B 轮续：外国中标份额的规模效应检验 + 清洗后安慰剂复核 + 真实覆盖率。

上一轮脚本在 log_award 控制处崩溃（award_value 含 NaN 导致 SVD 不收敛），
且覆盖率误在清洗后测量。本脚本用已保存的清洗后数据补做：
  1. 真实覆盖率（清洗前，按年份与国家）
  2. 外国中标份额 -1.25pp 是否为合同规模效应（分层 + 类型 + 控制）
  3. 清洗后安慰剂剖面复核
输出 materials/results/v7_scale_placebo.json
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_scale_placebo.json')
TOL = 1e-9


def rd(d, outcome, poly=1, controls=('tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if 'log_award' in controls:
        dd = dd[dd['award_value'].notna() & (dd['award_value'] > 0)].copy().reset_index(drop=True)
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax']
    for j in range(2, poly + 1):
        dd['r%d' % j] = dd['r'] ** j
        dd['ax%d' % j] = dd['above'] * dd['r'] ** j
        xcols += ['r%d' % j, 'ax%d' % j]
    for c in controls:
        if c == 'log_award':
            dd[c] = np.log(dd['award_value'])
        xcols.append(c)
    y = dd[outcome].astype(float).values
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([pd.Series(y, name='y')] +
                     [dd[c].astype(float).rename(c) for c in xcols] +
                     [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(dd))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.pinv(Xd.T @ Xd)
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
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(p), 4), 'n': int(n),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


def main():
    raw = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    d = pd.read_csv(os.path.join(HERE, 'cn_matched_clean.csv'))
    d['above'] = (d['r'] >= 0).astype(int)
    band = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)].copy()
    R = {}

    # ---------- 1. 真实覆盖率（清洗前） ----------
    print('=== 真实覆盖率（清洗前，按年份）===')
    cov = {}
    for y in sorted(raw['year'].unique()):
        s = raw[raw['year'] == y]
        row = {'n': int(len(s)),
               'est_nonnull': round(float(s['value_est'].notna().mean()), 3),
               'est_valid': round(float(s['value_est'].between(1000, 1e9).mean()), 3),
               'tp_valid': round(float(s['tender_period'].between(1, 365).mean()), 3),
               'has_can': round(float(s['has_can'].mean()), 3),
               'offers_valid': round(float(s['n_offers'].between(1, 998).mean()), 3)}
        cov[str(y)] = row
        print('  %d n=%9s  est非空=%.2f est有效=%.2f  tp=%.2f  can=%.2f  offers=%.2f'
              % (y, format(row['n'], ','), row['est_nonnull'], row['est_valid'],
                 row['tp_valid'], row['has_can'], row['offers_valid']))
    R['coverage_by_year'] = cov

    print('\n=== 有效估计价值覆盖率最低/最高国家 ===')
    cc = {}
    for c in sorted(raw['code'].unique()):
        s = raw[raw['code'] == c]
        cc[c] = {'n': int(len(s)),
                 'est_valid': round(float(s['value_est'].between(1000, 1e9).mean()), 3)}
    lo = sorted(cc.items(), key=lambda kv: kv[1]['est_valid'])[:8]
    hi = sorted(cc.items(), key=lambda kv: -kv[1]['est_valid'])[:5]
    print('  最低 8:', ' '.join('%s=%.2f' % (k, v['est_valid']) for k, v in lo))
    print('  最高 5:', ' '.join('%s=%.2f' % (k, v['est_valid']) for k, v in hi))
    R['coverage_by_country'] = cc

    # ---------- 2. 外国中标份额：规模效应 ----------
    print('\n=== 外国中标份额：规格 ===')
    fw = {}
    for lab, ctl in [('type only', ('tu', 'tw')),
                     ('type + log award value', ('tu', 'tw', 'log_award'))]:
        r = rd(band, 'foreign_win', controls=ctl)
        fw[lab] = r
        print('  %-26s %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))

    print('\n=== 外国中标份额：按阈值比分层（每层各自 RD）===')
    band['ratio'] = np.exp(band['r'])
    layers = {}
    for lo_, hi_ in [(0.80, 0.90), (0.90, 1.00), (1.00, 1.10), (1.10, 1.20)]:
        s = band[(band.ratio >= lo_) & (band.ratio < hi_)]
        if len(s) < 1000:
            continue
        r = rd(s, 'foreign_win')
        layers['%.2f-%.2f' % (lo_, hi_)] = r
        print('  ratio %.2f-%.2f: %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (lo_, hi_, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    fw['layers'] = layers

    print('\n=== 外国中标份额：按合同类型 ===')
    by_type = {}
    for t in ('S', 'U', 'W'):
        s = band[band.type == t]
        r = rd(s, 'foreign_win')
        by_type[t] = r
        print('  type %s: %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (t, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    fw['by_type'] = by_type

    print('\n=== 外国中标份额：分时期 ===')
    by_period = {}
    for lab, yrs in [('2013-2016', (2013, 2016)), ('2017-2019', (2017, 2019)),
                     ('2020-2023', (2020, 2023))]:
        s = band[(band.year >= yrs[0]) & (band.year <= yrs[1])]
        r = rd(s, 'foreign_win')
        by_period[lab] = r
        print('  %-10s %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    fw['by_period'] = by_period
    R['foreign_win'] = fw

    # ---------- 3. 清洗后安慰剂 ----------
    print('\n=== 清洗后安慰剂剖面 ===')
    plc = {}
    nsig = 0
    for c in [0.70, 0.80, 0.90, 1.10, 1.20, 1.30, 1.40]:
        dd = d.copy()
        dd['thr_pl'] = np.exp(np.log(dd['value_est']) - dd['r']) * c
        dd['r'] = np.log(dd['value_est']) - np.log(dd['thr_pl'])
        dd['above'] = (dd['value_est'] >= dd['thr_pl']).astype(int)
        b = dd[((np.exp(dd['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(b, 'single')
        plc['%.2f' % c] = r
        if r.get('p', 1) < 0.05:
            nsig += 1
        print('  %.2fτ: %+7.2fpp (SE %.2f, p=%.4f, n=%s)%s'
              % (c, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ','), ' <- SIG' if r.get('p', 1) < 0.05 else ''))
    R['placebo_clean'] = {'estimates': plc, 'n_sig': nsig, 'n_total': len(plc)}
    print('  显著断点: %d / %d' % (nsig, len(plc)))

    # ---------- 4. 主结果（清洗后，含 donut） ----------
    print('\n=== 清洗后主结果与 donut ===')
    main_res = {'baseline': rd(band, 'single')}
    print('  baseline: %+.3fpp (SE %.3f, p=%.4f, n=%s, CI %s)'
          % (main_res['baseline']['tau_pp'], main_res['baseline']['se_pp'],
             main_res['baseline']['p'], format(main_res['baseline']['n'], ','),
             main_res['baseline']['ci95_pp']))
    for w in (0.01, 0.02, 0.03):
        s = band[band['r'].abs() > w + TOL]
        r = rd(s, 'single')
        main_res['donut%d' % int(w * 100)] = r
        print('  donut ±%d%%: %+.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (int(w * 100), r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ',')))
    R['main_clean'] = main_res

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()

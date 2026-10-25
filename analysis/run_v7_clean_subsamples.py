"""B 轮：数据清洗 + 覆盖率 + 子样本分解 + 规模效应检验。

上一步发现 CN-CAN 匹配样本有多处数据质量问题：
  value_est   max 5.4e15（荒谬）；41,868 条 < €1,000；5,065 条 > €1e9
  award_value max 9,999,999,999,999（哨兵值）
  n_offers    max 999（上限哨兵）；425 条 < 1
  elec_share  max 499.5（NUMBER_OFFERS_ELECTR > NUMBER_OFFERS）
  lots        max 2,604；25,092 条 > 1,000
  tender_period 404 条 > 365 天

本脚本：
  1. 建立并记录清洗规则，输出清洗前后对比
  2. 覆盖率：按国家×年份检查各字段缺失模式
  3. 子样本分解：时期 × 类型 × 批次结构（解释 2013-16 的 -3.22pp 显著异常）
  4. 规模效应：外国中标份额 -1.25pp 是否为合同规模效应

输出 materials/results/v7_clean_subsamples.json
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_clean_subsamples.json')
CLEAN = os.path.join(HERE, 'cn_matched_clean.csv')
TOL = 1e-9

# ---------------- 清洗规则 ----------------
RULES = {
    'value_est': '保留 [1000, 1e9]；超出记为缺失（荒谬值/哨兵）',
    'award_value': '丢弃 0 与 9,999,999,999,999 哨兵值',
    'n_offers': '丢弃 <1 与 >=999（999 为上报上限）',
    'elec_share': '保留 [0,1]；超出记为缺失',
    'lots': '>1000 记为缺失（数据错误）',
    'tender_period': '保留 [1,365] 天',
    'single': '仅在 n_offers 有效时有值',
}


def clean(df):
    n0 = len(df)
    log = {'n_before': int(n0)}
    d = df.copy()
    # value_est
    bad_ve = ~d['value_est'].between(1000, 1e9)
    log['value_est_out_of_range'] = int(bad_ve.sum())
    d.loc[bad_ve, 'value_est'] = np.nan
    # award_value 哨兵
    bad_av = (d['award_value'] <= 0) | (d['award_value'] >= 9e12)
    log['award_value_sentinel'] = int(bad_av.sum())
    d.loc[bad_av, 'award_value'] = np.nan
    # n_offers
    bad_no = (d['n_offers'] < 1) | (d['n_offers'] >= 999)
    log['n_offers_invalid'] = int(bad_no.sum())
    d.loc[bad_no, 'n_offers'] = np.nan
    d.loc[d['n_offers'].isna(), 'single'] = np.nan
    # elec_share
    bad_es = ~d['elec_share'].between(0, 1)
    log['elec_share_out_of_range'] = int(bad_es.sum())
    d.loc[bad_es, 'elec_share'] = np.nan
    # lots
    bad_lots = d['lots'] > 1000
    log['lots_absurd'] = int(bad_lots.sum())
    d.loc[bad_lots, 'lots'] = np.nan
    # tender_period
    bad_tp = ~d['tender_period'].between(1, 365)
    log['tender_period_out_of_range'] = int(bad_tp.sum())
    d.loc[bad_tp, 'tender_period'] = np.nan

    d['above'] = (d['r'] >= 0).astype(int)
    # running variable 必须有效
    ok = d['value_est'].notna()
    log['n_after_value_est_valid'] = int(ok.sum())
    log['n_dropped_value_est'] = int((~ok).sum())
    d = d[ok].copy().reset_index(drop=True)
    log['n_final'] = int(len(d))
    log['rules'] = RULES
    return d, log


def rd(d, outcome, poly=1, controls=('tu', 'tw'), cluster='code'):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
    if 'log_award' in controls:
        # award_value 含 NaN（哨兵/未匹配），对数控制前先剔除，否则 SVD 不收敛
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
        if c in ('tu', 'tw', 'log_value_est', 'log_award'):
            if c == 'log_value_est':
                dd[c] = np.log(dd['value_est'])
            elif c == 'log_award':
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
    d, log = clean(raw)
    d.to_csv(CLEAN, index=False)
    R = {'cleaning': log}
    print('=== 清洗 ===')
    for k, v in log.items():
        if k != 'rules':
            print('  %-28s %s' % (k, format(v, ',') if isinstance(v, int) else v))

    band = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)].copy()
    print('\n清洗后 ±20%% 带: %s（下 %s / 上 %s）'
          % (format(len(band), ','), format(int((band.above == 0).sum()), ','),
             format(int((band.above == 1).sum()), ',')))
    R['n_band20_clean'] = int(len(band))

    # ---------------- 覆盖率 ----------------
    print('\n=== 覆盖率：按年份 ===')
    cov_y = {}
    for y in sorted(d['year'].unique()):
        s = d[d['year'] == y]
        row = {'n': int(len(s)),
               'value_est': round(float(s['value_est'].notna().mean()), 3),
               'tender_period': round(float(s['tender_period'].notna().mean()), 3),
               'has_can': round(float(s['has_can'].mean()), 3),
               'n_offers': round(float(s['n_offers'].notna().mean()), 3),
               'award_value': round(float(s['award_value'].notna().mean()), 3),
               'elec_share': round(float(s['elec_share'].notna().mean()), 3)}
        cov_y[str(y)] = row
        print('  %d n=%9s  est=%.2f  tp=%.2f  can=%.2f  offers=%.2f  award=%.2f  elec=%.2f'
              % (y, format(row['n'], ','), row['value_est'], row['tender_period'],
                 row['has_can'], row['n_offers'], row['award_value'], row['elec_share']))
    R['coverage_by_year'] = cov_y

    print('\n=== 覆盖率：按国家（估计价值，全期）===')
    cov_c = {}
    for c in sorted(d['code'].unique()):
        s = d[d['code'] == c]
        cov_c[c] = {'n': int(len(s)),
                    'value_est': round(float(s['value_est'].notna().mean()), 3),
                    'n_offers': round(float(s['n_offers'].notna().mean()), 3)}
    lo = sorted(cov_c.items(), key=lambda kv: kv[1]['value_est'])[:8]
    hi = sorted(cov_c.items(), key=lambda kv: -kv[1]['value_est'])[:5]
    print('  最低 8 国:', ' '.join('%s=%.2f' % (k, v['value_est']) for k, v in lo))
    print('  最高 5 国:', ' '.join('%s=%.2f' % (k, v['value_est']) for k, v in hi))
    R['coverage_by_country'] = cov_c

    # ---------------- 主估计（清洗后） ----------------
    print('\n=== 清洗后主估计（±20%，线性）===')
    main_res = {}
    for oc in ('single', 'n_offers', 'foreign_win', 'elec_share', 'tender_period'):
        r = rd(band, oc)
        main_res[oc] = r
        print('  %-16s %+9.3f (SE %.3f, p=%.4f, n=%s)'
              % (oc, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    R['main_clean'] = main_res

    # ---------------- 子样本分解 ----------------
    print('\n=== 子样本分解：单投标份额 ===')
    sub = {}
    for lab, sel in [
        ('2013-2016', band.year <= 2016),
        ('2017-2019', (band.year >= 2017) & (band.year <= 2019)),
        ('2020-2023', band.year >= 2020),
        ('type S', band.type == 'S'), ('type U', band.type == 'U'), ('type W', band.type == 'W'),
        ('single lot', band.lots.fillna(1) <= 1),
        ('multi lot', band.lots.fillna(0) > 1),
        ('2013-2016 S', (band.year <= 2016) & (band.type == 'S')),
        ('2013-2016 U', (band.year <= 2016) & (band.type == 'U')),
        ('2013-2016 W', (band.year <= 2016) & (band.type == 'W')),
    ]:
        s = band[sel]
        r = rd(s, 'single')
        sub[lab] = r
        print('  %-14s %+8.2fpp (SE %.2f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    R['single_subsamples'] = sub

    print('\n=== 子样本分解：报价数 ===')
    sub2 = {}
    for lab, sel in [('2013-2016', band.year <= 2016),
                     ('2017-2019', (band.year >= 2017) & (band.year <= 2019)),
                     ('2020-2023', band.year >= 2023 - 3)]:
        s = band[sel]
        r = rd(s, 'n_offers')
        sub2[lab] = r
        print('  %-14s %+9.3f (SE %.3f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    R['n_offers_subsamples'] = sub2

    # ---------------- 规模效应检验 ----------------
    print('\n=== 外国中标份额：规模效应检验 ===')
    fw = {}
    for lab, ctl in [('type only', ('tu', 'tw')),
                     ('type + log est value', ('tu', 'tw', 'log_value_est')),
                     ('type + log award value', ('tu', 'tw', 'log_award'))]:
        r = rd(band, 'foreign_win', controls=ctl)
        fw[lab] = r
        print('  %-24s %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    # 按估计价值分层
    print('  按估计价值分层（阈值比）：')
    fw_layers = {}
    band['ratio'] = np.exp(band['r'])
    for lo_, hi_ in [(0.8, 0.9), (0.9, 1.0), (1.0, 1.1), (1.1, 1.2)]:
        s = band[(band.ratio >= lo_) & (band.ratio < hi_)]
        if len(s) < 500:
            continue
        r = rd(s, 'foreign_win')
        fw_layers['%.1f-%.1f' % (lo_, hi_)] = r
        print('    ratio %.1f-%.1f: %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (lo_, hi_, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    fw['layers'] = fw_layers
    # 按类型
    print('  按类型：')
    fw_types = {}
    for t in ('S', 'U', 'W'):
        s = band[band.type == t]
        r = rd(s, 'foreign_win')
        fw_types[t] = r
        print('    type %s: %+8.3fpp (SE %.3f, p=%.4f, n=%s)'
              % (t, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    fw['by_type'] = fw_types
    R['foreign_win_scale_test'] = fw

    # ---------------- 安慰剂（清洗后复核） ----------------
    print('\n=== 清洗后安慰剂复核 ===')
    plc = {}
    nsig = 0
    for c in [0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4]:
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

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()

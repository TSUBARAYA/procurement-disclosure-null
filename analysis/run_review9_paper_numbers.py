"""第九轮：论文定稿所需的全部补算（希腊修正后口径）。

一次算清：
 1. CN 估计价值堆点（0.01% 内 / 精确相等 / 德国占比）——图3 题注用
 2. ±5% 带计数与构成平衡（28 国 vs 27 国）——5.1 平衡段用
 3. 清洗样本 + type 控制的第一阶段 bw5/10/20（含 CI）——5.1 与表9 统一口径
 4. 头条 MDE（80% power, G=28）
 5. 哨兵/NUMBER_OFFERS 精确分解（7.6 清洗段用）
 6. elec > offers 行数（7.6 电子份额不可用声明用）
 7. 外国中标头条的原始（未清洗）28 国估计（7.6 清洗对比句用）
 8. n_offers / tender_period 头条 CI（表9 用）
 9. 27 国 vs 28 国 lots 平衡差异来源（希腊驱动？）
输出 materials/results/review9_paper_numbers.json
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'review9_paper_numbers.json')
TOL = 1e-9
THRESH = {2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
          2016: (209000, 5225000), 2017: (209000, 5225000), 2018: (221000, 5548000),
          2019: (221000, 5548000), 2020: (214000, 5350000), 2021: (214000, 5350000),
          2022: (215000, 5382000), 2023: (215000, 5382000)}
R = {}


def rd(d, outcome, poly=1, controls=('tu', 'tw')):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax']
    for c in controls:
        if c == 'log_value_est':
            dd[c] = np.log(dd['value_est'])
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
    tcrit = stats.t.ppf(0.975, G - 1)
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(2 * (1 - stats.t.cdf(abs(tau / s), G - 1))), 4),
            'n': int(n), 'G': int(G),
            'ci95_pp': [round(float(tau - tcrit * s) * 100, 2),
                        round(float(tau + tcrit * s) * 100, 2)]}


def main():
    raw = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    raw['above'] = (raw['r'] >= 0).astype(int)
    raw['thr'] = np.exp(np.log(raw['value_est']) - raw['r'])
    band = raw[((np.exp(raw['r']) - 1).abs() <= 0.20 + TOL)].copy()

    # ---------- 1. 堆点（估计价值侧） ----------
    print('=== 堆点（CN 估计价值，±20% 带）===')
    for tol, lab in [(1e-4, '0.01% 内'), (0.0, '精确相等')]:
        if tol:
            m = (band['value_est'] - band['thr']).abs() / band['thr'] <= tol
        else:
            m = band['value_est'] == band['thr']
        sub = band[m]
        deu = (sub['code'] == 'DEU').mean() * 100 if len(sub) else float('nan')
        print('  %-8s %7s 份（%.2f%% of band）| 德国 %.1f%%' % (
            lab, format(int(m.sum()), ','), m.mean() * 100, deu))
        R['masspoint_%s' % lab] = {'n': int(m.sum()),
                                   'pct_of_band': round(float(m.mean()) * 100, 3),
                                   'deu_share': round(float(deu), 1)}
    # 堆点合同的 award=est 一致率（与 7.1 授标价值侧对照）
    mp = band[(band['value_est'] - band['thr']).abs() / band['thr'] <= 1e-4]
    sub = mp.dropna(subset=['award_value'])
    if len(sub):
        agree = (sub['award_value'] == sub['value_est']).mean() * 100
        print('  堆点合同中 award==est: %.1f%%（全样本 %.1f%%）' % (
            agree, (band.dropna(subset=['award_value']).pipe(
                lambda x: (x['award_value'] == x['value_est']).mean()) * 100)))
        R['masspoint_award_eq_est'] = round(float(agree), 1)
    # 变体：四舍五入到欧元后相等（|ve−thr|<=0.5）与 ±1€
    for tol, lab in [(0.5, 'round 到欧元相等'), (1.0, '±1€')]:
        m = (band['value_est'] - band['thr']).abs() <= tol
        sub = band[m]
        deu = (sub['code'] == 'DEU').mean() * 100 if len(sub) else float('nan')
        print('  %-14s %7s 份 | 德国 %.1f%%' % (lab, format(int(m.sum()), ','), deu))
        R['masspoint_%s' % lab] = {'n': int(m.sum()), 'deu_share': round(float(deu), 1)}

    # ---------- 2. ±5% 平衡 ----------
    print('\n=== ±5% 平衡（28 国 / 27 国）===')
    b05 = band[((np.exp(band['r']) - 1).abs() <= 0.05 + TOL)]
    b05_ng = b05[b05['code'] != 'GRC']
    b10 = band[((np.exp(band['r']) - 1).abs() <= 0.10 + TOL)]
    R['n_bw5_28'], R['n_bw5_27'] = int(len(b05)), int(len(b05_ng))
    R['n_bw10_28'], R['n_bw10_27'] = int(len(b10)), int(len(b10[b10['code'] != 'GRC']))
    print('  ±5%%: 28国 %s / 27国 %s；±10%%: 28国 %s / 27国 %s' % (
        format(len(b05), ','), format(len(b05_ng), ','),
        format(len(b10), ','), format(len(b10[b10['code'] != 'GRC']), ',')))
    bal = {}
    for col in ('lots', 'elec_auction', 'gpa', 'tender_period'):
        lo, hi = b05[b05.above == 0][col].dropna(), b05[b05.above == 1][col].dropna()
        lo27, hi27 = (b05_ng[b05_ng.above == 0][col].dropna(),
                      b05_ng[b05_ng.above == 1][col].dropna())
        bal[col] = {'below_28': round(float(lo.mean()), 3), 'above_28': round(float(hi.mean()), 3),
                    'diff_28': round(float(hi.mean() - lo.mean()), 3),
                    'diff_27': round(float(hi27.mean() - lo27.mean()), 3),
                    'n_28': int(len(lo) + len(hi))}
        print('  %-14s 28国 下 %8.3f 上 %8.3f 差 %+7.3f | 27国差 %+7.3f' % (
            col, lo.mean(), hi.mean(), hi.mean() - lo.mean(),
            hi27.mean() - lo27.mean()))
    t, p = stats.ttest_ind(b05[b05.above == 1]['tender_period'].dropna(),
                           b05[b05.above == 0]['tender_period'].dropna(), equal_var=False)
    bal['tender_period_t'] = {'t': round(float(t), 3), 'p': float(p)}
    print('    投标期 t=%.3f p=%.2e；均值 %.2f 天' % (
        t, p, b05['tender_period'].dropna().mean()))
    R['balance_bw5'] = bal
    R['tender_mean_bw5'] = round(float(b05['tender_period'].dropna().mean()), 2)

    # ---------- 3. 第一阶段（清洗 + type 控制） ----------
    print('\n=== 第一阶段（清洗 + type 控制，bw5/10/20）===')
    cln = pd.read_csv(os.path.join(HERE, 'cn_matched_clean.csv'))
    cln['above'] = (cln['r'] >= 0).astype(int)
    cband = cln[((np.exp(cln['r']) - 1).abs() <= 0.20 + TOL)].copy()
    fs = {}
    for bw in (0.05, 0.10, 0.20):
        d = cband[((np.exp(cband['r']) - 1).abs() <= bw + TOL)]
        r = rd(d, 'tender_period')
        fs['bw%d' % int(bw * 100)] = r
        print('  ±%d%%: %+.2f 天 (SE %.2f, p=%.4f, n=%s, CI %s)' % (
            int(bw * 100), r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ','), r['ci95_pp']))
    R['first_stage_clean_type'] = fs

    # ---------- 4. 头条与 MDE ----------
    print('\n=== 头条（清洗 + type）与 MDE ===')
    head = rd(cband, 'single')
    print('  single:', head)
    R['headline'] = head
    G = head['G']
    mde = (stats.t.ppf(0.975, G - 1) + stats.t.ppf(0.80, G - 1)) * head['se_pp'] / 100 * 100
    R['mde_pp'] = round(float(mde), 2)
    print('  MDE(80%%): %.2f pp (G=%d)' % (mde, G))
    for oc in ('n_offers', 'tender_period', 'elec_share'):
        r = rd(cband, oc)
        R['main_' + oc] = r
        print('  %-14s %+9.3f (SE %.3f, p=%.4f, n=%s, CI %s)' % (
            oc, r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ','), r['ci95_pp']))

    # ---------- 5/6. 清洗计数精确分解 ----------
    print('\n=== 清洗计数分解（28 国原始缓存）===')
    av = raw['award_value']
    sentinel = (av >= 9e12).sum()
    nonpos = (av <= 0).sum()
    no = raw['n_offers']
    n_lt1 = (no < 1).sum()
    n_ge999 = (no >= 999).sum()
    es = raw['elec_share']
    elec_gt = (es > 1).sum()
    es_obs = es.notna().sum()
    print('  award 哨兵(>=9e12): %s | 非正: %s | 合计 %s' % (
        format(int(sentinel), ','), format(int(nonpos), ','), format(int(sentinel + nonpos), ',')))
    print('  n_offers <1: %s | >=999: %s | 合计 %s' % (
        format(int(n_lt1), ','), format(int(n_ge999), ','), format(int(n_lt1 + n_ge999), ',')))
    print('  elec_share>1（%s 行有值中）: %s (%.1f%%)' % (
        format(int(es_obs), ','), format(int(elec_gt), ','), elec_gt / es_obs * 100))
    R['clean_counts'] = {'award_sentinel_exact': int(sentinel),
                         'award_nonpos': int(nonpos),
                         'award_total': int(sentinel + nonpos),
                         'n_offers_lt1': int(n_lt1), 'n_offers_ge999': int(n_ge999),
                         'n_offers_total': int(n_lt1 + n_ge999),
                         'elec_gt_offers': int(elec_gt),
                         'elec_observed': int(es_obs),
                         'elec_gt_pct_of_observed': round(float(elec_gt / es_obs * 100), 1)}

    # ---------- 7. 外国中标：原始 vs 清洗 ----------
    print('\n=== 外国中标：原始（未清洗）28 国 + type ===')
    rband = band.copy()
    r = rd(rband, 'foreign_win')
    print('  raw:', r)
    R['foreign_win_raw_type'] = r
    # 原始无控制（曾产出 +0.40 的规格）
    r0 = rd(rband, 'single', controls=())
    print('  single raw no-controls:', r0)
    R['single_raw_nocontrols'] = r0

    # ---------- 8. donut（清洗 + type，表9 用） ----------
    print('\n=== donut（清洗 + type）===')
    for w in (0.01, 0.02, 0.03):
        s = cband[cband['r'].abs() > w + TOL]
        r = rd(s, 'single')
        R['donut%d' % int(w * 100)] = r
        print('  ±%d%%: %+.3f (SE %.3f, p=%.4f, n=%s, CI %s)' % (
            int(w * 100), r['tau_pp'], r['se_pp'], r['p'], format(r['n'], ','), r['ci95_pp']))

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()

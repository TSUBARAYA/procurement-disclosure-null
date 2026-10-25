"""第九轮（四）：决定性检验 —— 事前趋势是 TWFE 伪影还是真趋势？

合同级事件研究（country + year FE + log value + type）显示 single 的事前系数
显著（e=-4 +8.62 p=0.033, e=-3 +5.42 p=0.009, e=-2 +4.54 p=0.006）。
但 not-yet-treated 对照组让 2016 cohort（16 国）既当处理又当对照，
这是 Goodman-Bacon 的 forbidden comparison：若 2016 cohort 在 2013-15 有
下降趋势，就会在 2017/2018 cohort 的事前系数上制造伪趋势。

本脚本用三种对照组重跑：
  A. not_yet（标准 CS，已做）
  B. never（仅 SWE/PRT/LUX 三国）
  C. not_yet 但排除 2016 cohort 的对照贡献
若 B/C 下事前趋势消失 -> 伪影，设计干净，ATT 可作因果解释。

输出 materials/results/transposition_never_control.json
"""
import csv, json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'transposition_never_control.json')
sys.path.insert(0, HERE)
from estimators_v4 import demean, wls_cluster  # noqa

COHORT = {}
with open(os.path.join(ROOT, 'data', 'external', 'eu_transposition_2014_24.csv'),
          encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        COHORT[r['code']] = int(r['event_year']) if r['event_year'] else None
NEVER = [c for c, g in COHORT.items() if g is None]


def ev(d, outcome, cohorts, rel=(-4, 4), controls=('log_value', 'tu', 'tw'),
       mode='not_yet', drop_codes=(), drop_control_cohorts=()):
    """mode: not_yet | never。drop_control_cohorts: 从对照组中剔除这些 cohort 的国家。"""
    dd = d.dropna(subset=[outcome, 'log_value']).copy()
    if drop_codes:
        dd = dd[~dd['code'].isin(drop_codes)].copy()
    dd['g'] = dd['code'].map(cohorts)
    if mode == 'never':
        dd = dd[(dd['g'].notna()) | (dd['code'].isin(NEVER))].copy()
    else:
        dd = dd[(dd['g'].notna()) | (dd['code'].isin(NEVER))].copy()
    dd['event'] = dd['year'] - dd['g']
    dd = dd[(dd['event'] >= rel[0]) & (dd['event'] <= rel[1])].copy().reset_index(drop=True)
    # 对照组过滤
    if drop_control_cohorts:
        bad = [c for c, g in cohorts.items() if g in drop_control_cohorts]
        is_ctrl = dd['g'].isna() | dd['code'].isin(NEVER)
        dd = dd[~((dd['code'].isin(bad)) & (is_ctrl))].copy().reset_index(drop=True)
    if len(dd) < 1000:
        return None
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    for e in range(rel[0], rel[1] + 1):
        if e == -1:
            continue
        dd['e%d' % e] = (dd['event'] == e).astype(float)
    xcols = ['e%d' % e for e in range(rel[0], rel[1] + 1) if e != -1]
    for c in controls:
        if c in ('log_value', 'tu', 'tw'):
            xcols.append(c)
    y = dd[outcome].astype(float).values
    groups = [dd['code'].astype(str).values, dd['year'].astype(str).values]
    X = np.column_stack([dd[c].astype(float).values for c in xcols])
    yd, Xd = demean(y, X, groups, np.ones(len(dd)))
    res = wls_cluster(yd, Xd, np.ones(len(dd)), dd['code'].astype('category').cat.codes.values)
    beta, se, pvals = res['beta'], res['se'], res['p']
    out = {}
    for i, c in enumerate(xcols):
        if not c.startswith('e'):
            continue
        e = int(c[1:])
        out[e] = {'coef_pp': round(float(beta[i]) * 100, 3),
                  'se_pp': round(float(se[i]) * 100, 3), 'p': round(float(pvals[i]), 4)}
    post = [out[e] for e in out if e >= 0]
    att = None
    if post:
        wts = np.array([(dd['e%d' % e] == 1).sum() for e in out if e >= 0], float)
        vals = np.array([out[e]['coef_pp'] for e in out if e >= 0])
        att = float((wts * vals).sum() / wts.sum())
    nctrl = int(dd['g'].isna().sum() + dd['code'].isin(NEVER).sum() - dd['code'].isin(NEVER).sum())
    nctrl = int(dd['g'].isna().sum())
    return {'coefs': out, 'att_pp': round(att, 3) if att is not None else None,
            'n': int(len(dd)), 'G': int(dd['code'].nunique()),
            'n_never_control_rows': nctrl}


def show(tag, r, R):
    print('  ===== %s =====' % tag)
    if not r:
        print('    insufficient sample')
        return
    for e in sorted(r['coefs']):
        v = r['coefs'][e]
        mark = ' <- PRE' if e < 0 else ''
        print('    e=%+d: %+7.2f (SE %.2f, p=%.3f)%s' % (e, v['coef_pp'], v['se_pp'], v['p'], mark))
    print('    ATT: %+.2fpp  (n=%s, G=%d, never-control rows=%s)'
          % (r['att_pp'], format(r['n'], ','), r['G'], format(r['n_never_control_rows'], ',')))
    pre = [r['coefs'][e]['coef_pp'] for e in r['coefs'] if e < 0]
    R[tag] = {'coefs': {str(k): v for k, v in r['coefs'].items()}, 'att_pp': r['att_pp'],
              'n': r['n'], 'G': r['G'],
              'pre_max_abs_pp': round(float(max(abs(x) for x in pre)), 3) if pre else None,
              'pre_all_insignificant': bool(all(r['coefs'][e]['p'] > 0.05
                                                for e in r['coefs'] if e < 0))}


def main():
    df = pd.read_csv(os.path.join(HERE, 'micro_exact.csv'))
    print('contract-level cache: %s rows' % format(len(df), ','))
    R = {}

    for oc in ('single', 'foreign_win'):
        print()
        show('%s_notyet' % oc, ev(df, oc, COHORT, rel=(-4, 4), mode='not_yet'), R)
        print()
        show('%s_never' % oc, ev(df, oc, COHORT, rel=(-4, 4), mode='never'), R)
        print()
        show('%s_noHUN' % oc, ev(df, oc, COHORT, rel=(-4, 4), drop_codes=('HUN',)), R)
        print()
        show('%s_no2016ctrl' % oc,
             ev(df, oc, COHORT, rel=(-4, 4), drop_control_cohorts=(2016,)), R)
        print()
        show('%s_noHUN_no2016ctrl' % oc,
             ev(df, oc, COHORT, rel=(-4, 4), drop_codes=('HUN',),
                drop_control_cohorts=(2016,)), R)

    json.dump(R, open(OUT, 'w'), indent=1)
    print()
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

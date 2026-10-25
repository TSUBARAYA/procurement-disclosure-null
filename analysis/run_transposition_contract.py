"""第九轮（三）：合同级转化事件研究 —— 含排除匈牙利的稳健性。

背景：国家年层面 share_single_offer 有事前趋势（e=-4 +6.25, e=-1 +2.46）。
匈牙利是 2015 cohort 唯一国家，事前单投标份额 33% vs 对照 18%（差 15pp），
可能独力造成事前趋势。本脚本在合同级（country + year 双向 FE + log value +
type，可选 cpv2 x year FE）上检验：
  1. 全样本事件研究（single / foreign_win / elec_share）
  2. 排除 HUN 后的 single / foreign_win
  3. 只用 2016-2018 cohort
若排除 HUN 后事前趋势消失 -> 设计干净，可报因果结论。

输出 materials/results/transposition_contract_level.json
"""
import csv, io, json, os, sys, zipfile
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'transposition_contract_level.json')
CACHE = os.path.join(HERE, 'micro_exact.csv')

ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}
EU28 = set(ISO2TO3.values())

COHORT = {}
with open(os.path.join(ROOT, 'data', 'external', 'eu_transposition_2014_24.csv'),
          encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        COHORT[r['code']] = int(r['event_year']) if r['event_year'] else None


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fint(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def extract():
    if os.path.exists(CACHE):
        return pd.read_csv(CACHE)
    cols = ['code', 'year', 'type', 'value', 'n_offers', 'single', 'elec_share',
            'foreign_win', 'cpv2']
    rows = {c: [] for c in cols}
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        file_year = int(fn[4:8])
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                code = ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
                if code not in EU28:
                    continue
                if (row.get('CANCELLED') or '0').strip() == '1':
                    continue
                dt = (row.get('DT_AWARD') or '').strip()
                year = file_year
                if dt and len(dt) >= 4 and dt[-4:].isdigit():
                    y = int(dt[-4:])
                    if 2005 <= y <= 2023:
                        year = y
                n = fint(row.get('NUMBER_OFFERS'))
                if n is None or n < 1:
                    continue
                ne = fint(row.get('NUMBER_OFFERS_ELECTR'))
                v = fnum(row.get('AWARD_VALUE_EURO'))
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('S', 'U', 'W'):
                    continue
                if v is None or v <= 0:
                    continue
                win = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                win3 = ISO2TO3.get(win, win if len(win) == 3 else None)
                cpv = (row.get('CPV') or '').strip()
                rows['code'].append(code)
                rows['year'].append(year)
                rows['type'].append(tc)
                rows['value'].append(v)
                rows['n_offers'].append(n)
                rows['single'].append(1 if n == 1 else 0)
                rows['elec_share'].append(ne / n if ne is not None else np.nan)
                rows['foreign_win'].append(1 if (win3 and win3 != code) else 0)
                rows['cpv2'].append(cpv[:2] if cpv[:2].isdigit() else 'NA')
    df = pd.DataFrame(rows)
    df['log_value'] = np.log(df['value'])
    df.to_csv(CACHE, index=False)
    return df


def ev_study(d, outcome, cohorts, rel=(-4, 4), controls=('log_value', 'tu', 'tw'),
             cpv=False, drop_codes=()):
    """合同级事件研究：country + year 双向 FE（必须分离！country x year 会吸收
    处理变量）+ 合同特征控制 + 相对年份哑变量，国家聚类 SE。"""
    from estimators_v4 import demean, wls_cluster
    dd = d.dropna(subset=[outcome, 'log_value']).copy()
    if drop_codes:
        dd = dd[~dd['code'].isin(drop_codes)].copy()
    dd['g'] = dd['code'].map(cohorts)
    dd = dd[(dd['g'].notna()) | (dd['code'].isin(['SWE', 'PRT', 'LUX']))].copy()
    dd['event'] = dd['year'] - dd['g']
    dd = dd[(dd['event'] >= rel[0]) & (dd['event'] <= rel[1])].copy().reset_index(drop=True)
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
    if cpv:
        cpvs = [c for c in sorted(dd['cpv2'].unique()) if (dd['cpv2'] == c).mean() > 0.001]
        for c in cpvs[1:]:
            dd['cpv_%s' % c] = (dd['cpv2'] == c).astype(float)
            xcols.append('cpv_%s' % c)
    y = dd[outcome].astype(float).values
    groups = [dd['code'].astype(str).values, dd['year'].astype(str).values]
    if cpv:
        groups.append((dd['cpv2'].astype(str) + '_' + dd['year'].astype(str)).values)
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
    return {'coefs': out, 'att_pp': round(att, 3) if att is not None else None,
            'n': int(len(dd)), 'G': int(dd['code'].nunique()), 'baseline_event': -1}


def show(tag, r, R):
    print('  ===== %s =====' % tag)
    if not r:
        print('    insufficient sample')
        return
    for e in sorted(r['coefs']):
        v = r['coefs'][e]
        mark = ' <- pre' if e < 0 else ''
        print('    e=%+d: %+7.2f (SE %.2f, p=%.3f)%s' % (e, v['coef_pp'], v['se_pp'], v['p'], mark))
    print('    ATT: %+.2fpp  (n=%s, G=%d)' % (r['att_pp'], format(r['n'], ','), r['G']))
    pre = [r['coefs'][e]['coef_pp'] for e in r['coefs'] if e < 0]
    R[tag] = {'coefs': {str(k): v for k, v in r['coefs'].items()},
              'att_pp': r['att_pp'], 'n': r['n'], 'G': r['G'],
              'pre_max_abs_pp': round(float(max(abs(x) for x in pre)), 3) if pre else None,
              'pre_all_insignificant': bool(all(r['coefs'][e]['p'] > 0.05
                                                for e in r['coefs'] if e < 0))
              if any(e < 0 for e in r['coefs']) else None}


def main():
    df = extract()
    print('contract-level sample: %s rows' % format(len(df), ','))
    print('  years %d-%d, countries %d' % (df.year.min(), df.year.max(), df.code.nunique()))

    R = {'n_contracts': int(len(df))}

    print()
    show('single_full', ev_study(df, 'single', COHORT, rel=(-4, 4)), R)
    print()
    show('single_cpv', ev_study(df, 'single', COHORT, rel=(-4, 4), cpv=True), R)
    print()
    show('foreign_win_full', ev_study(df, 'foreign_win', COHORT, rel=(-4, 4)), R)
    print()
    show('elec_share_full', ev_study(df, 'elec_share', COHORT, rel=(-4, 4)), R)
    print()
    print('  ===== robustness: drop HUN (only country in 2015 cohort) =====')
    show('single_noHUN', ev_study(df, 'single', COHORT, rel=(-4, 4), drop_codes=('HUN',)), R)
    print()
    show('single_noHUN_cpv', ev_study(df, 'single', COHORT, rel=(-4, 4), cpv=True,
                                      drop_codes=('HUN',)), R)
    print()
    show('foreign_win_noHUN', ev_study(df, 'foreign_win', COHORT, rel=(-4, 4),
                                       drop_codes=('HUN',)), R)
    print()
    co2 = {k: v for k, v in COHORT.items() if v is not None and v >= 2016}
    show('single_2016plus', ev_study(df, 'single', co2, rel=(-3, 4), drop_codes=('HUN',)), R)
    print()
    show('single_2016plus_cpv', ev_study(df, 'single', co2, rel=(-3, 4), cpv=True,
                                         drop_codes=('HUN',)), R)

    json.dump(R, open(OUT, 'w'), indent=1)
    print()
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

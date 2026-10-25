# -*- coding: utf-8 -*-
"""第一阶段补测：程序结构变量。

前几轮测过 tender_period / elec_auction / gpa / lots / n_offers，全部不显著。
但漏掉了 CN 里最关键的一组：程序类型。指令 2014/24/EU 对阈值以上可用哪些
程序（公开/限制/议标/竞争性对话）、是否可用加速程序、是否可用框架协议，
都有强制性规定。程序结构在阈值处跳变，就是真正的第一阶段。

本脚本从原始 CN 重新提取程序字段，并在阈值处做 RD。
输出 materials/results/v7_first_stage_procedures.json
"""
import csv, io, json, os, sys, zipfile
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_first_stage_procedures.json')
CACHE = os.path.join(HERE, 'cn_procedures.csv')
TOL = 1e-9

THRESH = {2013: (200000, 5000000), 2014: (207000, 5186000), 2015: (207000, 5186000),
          2016: (209000, 5225000), 2017: (209000, 5225000), 2018: (221000, 5548000),
          2019: (221000, 5548000), 2020: (214000, 5350000), 2021: (214000, 5350000),
          2022: (215000, 5382000), 2023: (215000, 5382000)}
ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}
EU28 = set(ISO2TO3.values())


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def pdate(s):
    s = (s or '').strip()
    if not s:
        return None
    MONTHS = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7,
              'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    if '-' in s:
        p = s.split('-')
        if len(p) != 3:
            return None
        try:
            d, y = int(p[0]), int(p[2])
        except ValueError:
            return None
        mon = MONTHS.get(p[1].upper()[:3])
        if mon is None:
            return None
    elif '/' in s:
        p = s.split('/')
        if len(p) != 3:
            return None
        try:
            d, mon, y = int(p[0]), int(p[1]), int(p[2])
        except ValueError:
            return None
        if not (1 <= mon <= 12):
            return None
    else:
        return None
    y = 2000 + y if y < 100 else y
    if not (1 <= d <= 31):
        return None
    return (y, mon, d)


def extract():
    if os.path.exists(CACHE):
        return pd.read_csv(CACHE)
    rows = []
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('cn_') and fn.endswith('.zip')):
            continue
        fy = int(fn[3:7])
        if fy not in THRESH:
            continue
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                if (row.get('ID_TYPE') or '').strip() != '2':
                    continue
                if (row.get('CANCELLED') or '0').strip() == '1':
                    continue
                code = ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
                if code not in EU28:
                    continue
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('W', 'S', 'U'):
                    continue
                ve = fnum(row.get('VALUE_EURO'))
                if ve is None or ve <= 0:
                    ve = fnum(row.get('VALUE_EURO_FIN_1'))
                if ve is None or not (1000 <= ve <= 1e9):
                    continue
                d_disp, d_app = pdate(row.get('DT_DISPATCH')), pdate(row.get('DT_APPLICATIONS'))
                tp = None
                if d_disp and d_app:
                    a, b = pd.Timestamp(*d_disp), pd.Timestamp(*d_app)
                    if b > a and (b - a).days < 400:
                        tp = (b - a).days
                rows.append({
                    'code': code, 'year': fy, 'type': tc, 'value_est': ve,
                    'r': np.log(ve) - np.log(THRESH[fy][1] if tc == 'W' else THRESH[fy][0]),
                    'top_type': (row.get('TOP_TYPE') or '').strip() or None,
                    'accelerated': 1 if (row.get('B_ACCELERATED') or '').strip() == 'Y' else 0,
                    'fra_agreement': 1 if (row.get('B_FRA_AGREEMENT') or '').strip() == 'Y' else 0,
                    'joint_proc': 1 if (row.get('B_INVOLVES_JOINT_PROCUREMENT') or '').strip() == 'Y' else 0,
                    'dyn_purch': 1 if (row.get('B_DYN_PURCH_SYST') or '').strip() == 'Y' else 0,
                    'gpa': 1 if (row.get('B_GPA') or '').strip() == 'Y' else 0,
                    'elec_auction': 1 if (row.get('B_ELECTRONIC_AUCTION') or '').strip() == 'Y' else 0,
                    'crit_price_w': fnum(row.get('CRIT_PRICE_WEIGHT')),
                    'tender_period': tp,
                    'lots': fnum(row.get('LOTS_NUMBER')),
                })
    df = pd.DataFrame(rows)
    df.to_csv(CACHE, index=False)
    return df


def rd(d, outcome, poly=1):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
    dd['above'] = (dd['r'] >= 0).astype(int)
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax', 'tu', 'tw']
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
            'p': round(float(p), 4), 'n': int(n)}


def main():
    df = extract()
    df['above'] = (df['r'] >= 0).astype(int)
    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    R = {'n_cn_procedures': int(len(df)), 'n_band20': int(len(band))}
    print('CN 程序字段样本 %s；±20%% 带 %s' % (format(len(df), ','), format(len(band), ',')))

    print('\n=== 程序类型分布（阈值两侧）===')
    ct = pd.crosstab(band['top_type'], band['above'], normalize='columns')
    print(ct.round(4).to_string())
    R['top_type_share'] = {str(k): {'below': round(float(v.get(0, 0)), 4),
                                    'above': round(float(v.get(1, 0)), 4)}
                           for k, v in ct.iterrows()}

    print('\n=== 第一阶段候选：程序与制度变量（±20%，线性，type FE）===')
    cand = {}
    for oc, lab in [('accelerated', '加速程序'), ('fra_agreement', '框架协议'),
                    ('joint_proc', '联合采购'), ('dyn_purch', '动态采购系统'),
                    ('gpa', 'GPA 覆盖'), ('elec_auction', '电子拍卖'),
                    ('tender_period', '投标期(天)'), ('crit_price_w', '价格权重'),
                    ('lots', '批次数')]:
        r = rd(band, oc)
        cand[oc] = r
        flag = ' <- SIG' if r.get('p', 1) < 0.05 else ''
        print('  %-12s %+9.3f (SE %.3f, p=%.4f, n=%s)%s'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ','), flag))
    R['first_stage_candidates'] = cand

    print('\n=== 程序类型哑变量（各自 RD，OPE 为基准组外的类别）===')
    tops = [t for t in band['top_type'].dropna().unique() if t]
    print('  出现的程序类型:', sorted(tops))
    tt = {}
    for t in sorted(tops):
        band['is_%s' % t] = (band['top_type'] == t).astype(float)
        r = rd(band, 'is_%s' % t)
        tt[t] = r
        flag = ' <- SIG' if r.get('p', 1) < 0.05 else ''
        print('  %-6s %+8.3f pp (SE %.3f, p=%.4f, n=%s)%s'
              % (t, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ','), flag))
    R['top_type_rd'] = tt

    # 多重检验校正（Holm）覆盖全部候选
    print('\n=== Holm 校正（全部第一阶段候选）===')
    items = [(k, v['p']) for k, v in cand.items() if 'p' in v] + \
            [(k, v['p']) for k, v in tt.items() if 'p' in v]
    items.sort(key=lambda x: x[1])
    m = len(items)
    holm = {}
    for rank, (k, p) in enumerate(items):
        adj = min(1.0, p * (m - rank))
        holm[k] = round(adj, 4)
        if adj < 0.05 or rank < 5:
            print('  %-16s 原始 p=%.4f → Holm p=%.4f %s'
                  % (k, p, adj, '显著' if adj < 0.05 else ''))
    R['holm_first_stage'] = holm

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()

"""v7.0：用开标前法定估计价值作 running variable 的阈值 RD。

动机：旧设计用 AWARD_VALUE_EURO 作 running variable，买方可在授奖环节
篡改（拆分、少报、改估值），且 TED 只含已公布合同造成样本自选择。
CN（招标公告）数据提供：
  - VALUE_EURO：开标前公布的法定估计价值（threshold 的法定判定变量）
  - DT_DISPATCH / DT_APPLICATIONS：可算投标期（指令规定阈值以上最短投标期，
    是机械第一阶段，验证制度确实改变）
  - FUTURE_CAN_ID：链接到授奖公告，取竞争结果

本脚本：
  1. 提取 CN（ID_TYPE=2 合同公告、S/U/W、未取消、EU-28、有估计价值）
  2. 提取 CAN 结果（按 ID_NOTICE_CAN 索引）
  3. 匹配 CN -> CAN
  4. RD：running var = log(CN 估计价值) - log(法定阈值)
     - 第一阶段：投标期天数
     - 结果：单投标份额、报价数
     - 诊断：密度/bunching、安慰剂剖面、带宽×阶数、donut、构成平衡

输出 materials/results/v7_estimate_rd.json + analysis/cn_matched.csv
"""
import csv, io, json, os, sys, zipfile
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_estimate_rd.json')
CACHE = os.path.join(HERE, 'cn_matched.csv')
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
MONTHS = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7,
          'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}


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


def pdate(s):
    """TED 日期有两种格式：2013-2016 用 '27-FEB-13'（DD-MMM-YY），
    2017 起用 '05/02/18'（DD/MM/YY）。都要解析。"""
    s = (s or '').strip()
    if not s:
        return None
    if '-' in s:
        parts = s.split('-')
        if len(parts) != 3:
            return None
        try:
            d, y = int(parts[0]), int(parts[2])
        except ValueError:
            return None
        mon = MONTHS.get(parts[1].upper()[:3])
        if mon is None:
            return None
    elif '/' in s:
        parts = s.split('/')
        if len(parts) != 3:
            return None
        try:
            d, mon, y = int(parts[0]), int(parts[1]), int(parts[2])
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


def build():
    if os.path.exists(CACHE):
        return pd.read_csv(CACHE)

    # ---- 1. CAN 结果索引 ----
    print('[1] 提取 CAN 结果索引…')
    can = {}
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                nid = (row.get('ID_NOTICE_CAN') or '').strip()
                if not nid:
                    continue
                n = fint(row.get('NUMBER_OFFERS'))
                ne = fint(row.get('NUMBER_OFFERS_ELECTR'))
                v = fnum(row.get('AWARD_VALUE_EURO'))
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                win = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                iso = (row.get('ISO_COUNTRY_CODE') or '').strip().upper()
                can[nid] = {
                    'n_offers': n, 'n_offers_elec': ne,
                    'single': 1 if (n is not None and n == 1) else (0 if n is not None else None),
                    'award_value': v, 'type': tc,
                    'foreign_win': 1 if (win and win != iso) else 0,
                    'elec_share': (ne / n) if (n and n >= 1 and ne is not None) else None,
                }
    print('    CAN 公告 %s 条' % format(len(can), ','))

    # ---- 2. CN 提取 + 匹配 ----
    print('[2] 提取 CN 并匹配 CAN…')
    rows = []
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('cn_') and fn.endswith('.zip')):
            continue
        file_year = int(fn[3:7])
        if file_year not in THRESH:
            continue
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                if (row.get('ID_TYPE') or '').strip() != '2':
                    continue                      # 只要合同公告
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
                if ve is None or ve <= 0:
                    continue
                d_disp = pdate(row.get('DT_DISPATCH'))
                d_app = pdate(row.get('DT_APPLICATIONS'))
                tp = None
                if d_disp and d_app:
                    a = pd.Timestamp(*d_disp)
                    b = pd.Timestamp(*d_app)
                    if b > a and (b - a).days < 400:
                        tp = (b - a).days
                nid = (row.get('FUTURE_CAN_ID') or '').strip()
                c = can.get(nid) if nid else None
                rows.append({
                    'id_cn': (row.get('ID_NOTICE_CN') or '').strip(),
                    'code': code, 'year': file_year, 'type': tc,
                    'value_est': ve, 'r': np.log(ve) - np.log(
                        THRESH[file_year][1] if tc == 'W' else THRESH[file_year][0]),
                    'tender_period': tp,
                    'lots': fint(row.get('LOTS_NUMBER')),
                    'elec_auction': 1 if (row.get('B_ELECTRONIC_AUCTION') or '').strip() == 'Y' else 0,
                    'gpa': 1 if (row.get('B_GPA') or '').strip() == 'Y' else 0,
                    'cpv2': (row.get('CPV') or 'NA')[:2] if (row.get('CPV') or 'NA')[:2].isdigit() else 'NA',
                    'has_can': 1 if c else 0,
                    'n_offers': c['n_offers'] if c else None,
                    'single': c['single'] if c else None,
                    'award_value': c['award_value'] if c else None,
                    'foreign_win': c['foreign_win'] if c else None,
                    'elec_share': c['elec_share'] if c else None,
                })
    df = pd.DataFrame(rows)
    df.to_csv(CACHE, index=False)
    print('    CN 匹配样本 %s 行（其中有 CAN 结果 %s）'
          % (format(len(df), ','), format(int(df.has_can.sum()), ',')))
    return df


def rd(d, outcome, poly=1, controls=(), cluster='code'):
    """RD：country×year 去模 + type 哑变量 + 国家聚类 SE。"""
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
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
        if c in ('log_value_est', 'tu', 'tw'):
            dd[c] = dd[c] if c != 'log_value_est' else np.log(dd['value_est'])
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
    df = build()
    df['above'] = (df['r'] >= 0).astype(int)
    df['log_value_est'] = np.log(df['value_est'])
    R = {'n_cn': int(len(df)), 'n_with_can': int(df.has_can.sum()),
         'match_rate': round(float(df.has_can.mean()), 4)}
    print('\nCN 样本 %s，匹配到 CAN %s (%.1f%%)'
          % (format(len(df), ','), format(int(df.has_can.sum()), ','), df.has_can.mean() * 100))

    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    print('±20%% 值空间带: %s（下 %s / 上 %s）'
          % (format(len(band), ','),
             format(int((band.above == 0).sum()), ','),
             format(int((band.above == 1).sum()), ',')))
    R['n_band20'] = int(len(band))

    # ---- 第一阶段：投标期 ----
    print('\n[第一阶段] 投标期天数（DT_APPLICATIONS - DT_DISPATCH）')
    fs = {}
    for bw in (0.05, 0.10, 0.20):
        d = band[((np.exp(band['r']) - 1).abs() <= bw + TOL)]
        for poly in (1, 2):
            r = rd(d, 'tender_period', poly=poly)
            fs['bw%d_p%d' % (int(bw * 100), poly)] = r
            print('  ±%d%% p%d: %+.2f 天 (SE %.2f, p=%.4f, n=%s)'
                  % (int(bw * 100), poly, r.get('tau_pp', 0), r.get('se_pp', 0),
                     r.get('p', 1), format(r.get('n', 0), ',')))
    R['first_stage_tender_period'] = fs
    print('  参考：指令 2014/24/EU 规定的公开程序最短投标期为 35 天（固定期限）')

    # ---- 结果：单投标份额 / 报价数 ----
    print('\n[结果] 单投标份额（匹配 CAN）')
    res = {}
    for bw in (0.05, 0.10, 0.15, 0.20, 0.25):
        d = band[((np.exp(band['r']) - 1).abs() <= bw + TOL)]
        for poly in (1, 2):
            r = rd(d, 'single', poly=poly)
            res['bw%d_p%d' % (int(bw * 100), poly)] = r
            print('  ±%d%% p%d: %+.2fpp (SE %.2f, p=%.4f, n=%s)'
                  % (int(bw * 100), poly, r.get('tau_pp', 0), r.get('se_pp', 0),
                     r.get('p', 1), format(r.get('n', 0), ',')))
    R['single'] = res

    # donut
    print('\n[结果] donut（±20%，线性）')
    dn = {}
    for w in (0.01, 0.02, 0.03):
        dd = band[band['r'].abs() > w + TOL]
        r = rd(dd, 'single', poly=1)
        dn['donut%d' % int(w * 100)] = r
        print('  ±%d%%: %+.2fpp (p=%.4f, n=%s)' % (int(w * 100), r.get('tau_pp', 0),
                                                   r.get('p', 1), format(r.get('n', 0), ',')))
    R['donut'] = dn

    # ---- 密度 / bunching（估计价值上） ----
    print('\n[密度] 估计价值的箱计数（0.02 宽）')
    BW = 0.02
    bins = np.arange(-12, 10)
    cnt = pd.Series(np.floor(band['r'].values / BW).astype(int)).value_counts()
    n = np.array([cnt.get(k, 0) for k in bins], dtype=float)
    L, Rr = n[bins <= -1].sum(), n[bins >= 1].sum()
    import math
    gap = math.log((Rr / 9 + 1) / (L / 12 + 1))
    print('  左 12 箱 %s 份 / 右 9 箱 %s 份；log gap %+.5f（下方超额 %.2f%%）'
          % (format(int(L), ','), format(int(Rr), ','), gap, (L / 12) / (Rr / 9) * 100 - 100))
    R['density'] = {'n_left': int(L), 'n_right': int(Rr), 'log_gap': round(gap, 5),
                    'excess_below_pct': round((L / 12) / (Rr / 9) * 100 - 100, 3),
                    'bin_minus1': int(n[bins == -1][0]), 'bin_0': int(n[bins == 0][0]),
                    'bin_plus1': int(n[bins == 1][0])}

    # ---- 安慰剂剖面 ----
    print('\n[安慰剂剖面] cutoff ∈ [0.7, 1.4]，各自 ±20% 邻域，线性')
    prof = {}
    for c in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
        d = df.copy()
        d['thr_pl'] = np.exp(np.log(d['value_est']) - d['r']) * c
        d['r'] = np.log(d['value_est']) - np.log(d['thr_pl'])
        d['above'] = (d['value_est'] >= d['thr_pl']).astype(int)
        b = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(b, 'single', poly=1)
        prof['%.2f' % c] = r
        flag = ' <- SIG' if r.get('p', 1) < 0.05 else ''
        print('  %.2fτ: %+.2fpp (SE %.2f, p=%.4f, n=%s)%s'
              % (c, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ','), flag))
    R['placebo_profile'] = prof
    nsig = sum(1 for v in prof.values() if v.get('p', 1) < 0.05)
    print('  显著断点数: %d / %d' % (nsig, len(prof)))
    R['n_placebo_sig'] = nsig

    # ---- 构成平衡 ----
    print('\n[构成平衡] ±5% 带内，阈值两侧 CN 特征')
    b05 = band[((np.exp(band['r']) - 1).abs() <= 0.05 + TOL)]
    bal = {}
    for col in ('lots', 'elec_auction', 'gpa', 'tender_period', 'cpv2'):
        if col == 'cpv2':
            continue
        lo = b05[b05.above == 0][col].dropna()
        hi = b05[b05.above == 1][col].dropna()
        if len(lo) and len(hi):
            bal[col] = {'below': round(float(lo.mean()), 3), 'above': round(float(hi.mean()), 3),
                        'diff': round(float(hi.mean() - lo.mean()), 3)}
            print('  %-14s 下 %8.2f  上 %8.2f  差 %+7.2f' % (col, lo.mean(), hi.mean(), hi.mean() - lo.mean()))
    for col in ('tender_period',):
        lo = b05[b05.above == 0][col].dropna(); hi = b05[b05.above == 1][col].dropna()
        if len(lo) and len(hi):
            t, p = stats.ttest_ind(hi, lo, equal_var=False)
            bal[col + '_t'] = {'t': round(float(t), 3), 'p': round(float(p), 4)}
            print('    (t=%.2f, p=%.4f)' % (t, p))
    R['balance'] = bal

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()

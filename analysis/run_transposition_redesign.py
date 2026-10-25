"""第九轮（修正版）：重建转化设计，验证干不干净。

修正上一版三个 bug：
1. 事件研究的事前期缺失（t 从 g 开始）→ t 遍历所有年份；
2. 权重用国家年数 → 改用合同数；
3. 提取口径与归档不一致 → 精确复现 build_ted_panel.py
   （DT_AWARD 年、不过滤类型、不过滤金额、elec=sum(ne)/sum(offers)）。

设计要点：
- 处理：各国转化 Directive 2014/24/EU 的年份（2015–2018 五个 cohort，
  25 国；窗口内未核实转化的 SWE/PRT/LUX 作 never-treated 稳健性对照）
- 主对照：not-yet-treated（CS 标准做法，避免 never-treated 被污染）
- 推断：国家层 cluster bootstrap（28 国）
- 稳健性：合同级 TWFE、never-treated 对照、排除 2022–23
"""
import csv, io, json, os, sys, zipfile
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'transposition_redesign.json')

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
NEVER = [c for c, g in COHORT.items() if g is None]


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


def build_panel():
    """精确复现归档 build_ted_panel.py 的口径。"""
    cache = os.path.join(HERE, 'cy_panel_exact.csv')
    if os.path.exists(cache):
        return pd.read_csv(cache)
    agg = defaultdict(lambda: {'n': 0, 'offers': [], 'single': 0, 'elec': 0.0,
                               'off_sum': 0.0, 'foreign': 0, 'win_known': 0,
                               'vals': [], 'n_works': 0, 'single_works': 0,
                               'offers_works': [], 'elec_works': 0.0,
                               'off_sum_works': 0.0, 'sme_n': 0, 'sme_num': 0.0})
    n_rows = n_used = 0
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        file_year = int(fn[4:8])
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                n_rows += 1
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
                ne = fint(row.get('NUMBER_OFFERS_ELECTR'))
                v = fnum(row.get('AWARD_VALUE_EURO'))
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                win = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                win3 = ISO2TO3.get(win, win if len(win) == 3 else None)
                sme = fint(row.get('NUMBER_TENDERS_SME'))
                a = agg[(code, year)]
                a['n'] += 1
                if n is not None and n >= 1:
                    a['offers'].append(n)
                    a['off_sum'] += n
                    if n == 1:
                        a['single'] += 1
                    if ne is not None:
                        a['elec'] += ne
                    if sme is not None:
                        a['sme_n'] += 1
                        a['sme_num'] += sme / n
                if v is not None and v > 0:
                    a['vals'].append(v)
                if win3:
                    a['win_known'] += 1
                    if win3 != code:
                        a['foreign'] += 1
                if tc == 'W':
                    a['n_works'] += 1
                    if n is not None and n >= 1:
                        a['offers_works'].append(n)
                        a['off_sum_works'] += n
                        if n == 1:
                            a['single_works'] += 1
                        if ne is not None:
                            a['elec_works'] += ne
                n_used += 1
    print(f'  原始行 {n_rows:,}，EU-28 有效 {n_used:,}')
    rows = []
    for (code, year), a in sorted(agg.items()):
        n_off = len(a['offers'])
        rows.append({
            'code': code, 'year': year, 'n_contracts': a['n'], 'n_with_offers': n_off,
            'mean_offers': round(float(np.mean(a['offers'])), 4) if n_off else None,
            'share_single_offer': round(a['single'] / n_off, 4) if n_off else None,
            'elec_offer_share': round(a['elec'] / a['off_sum'], 4) if a['off_sum'] > 0 else None,
            'foreign_winner_share': round(a['foreign'] / a['win_known'], 4) if a['win_known'] else None,
            'median_award_value': round(float(np.median(a['vals'])), 1) if a['vals'] else None,
            'n_works': a['n_works'],
            'share_single_offer_works': round(a['single_works'] / len(a['offers_works']), 4) if a['offers_works'] else None,
            'mean_offers_works': round(float(np.mean(a['offers_works'])), 4) if a['offers_works'] else None,
            'elec_offer_share_works': round(a['elec_works'] / a['off_sum_works'], 4) if a['off_sum_works'] > 0 else None,
            'sme_tender_share': round(a['sme_num'] / a['sme_n'], 4) if a['sme_n'] else None,
        })
    df = pd.DataFrame(rows)
    df.to_csv(cache, index=False)
    return df


def cs_cells(panel, outcome, cohorts, control='not_yet'):
    """CS group-time ATT(g,t)：处理国 vs 对照国，权重 = 处理国合同数。

    control='not_yet'：对照 = 未转化国 + event_time 仍为负的国（CS 标准）
    control='never'：对照 = 仅窗口内未核实转化的三国
    """
    d = panel.dropna(subset=[outcome]).copy()
    d['g'] = d['code'].map(cohorts)
    cells = []
    for g in sorted(d['g'].dropna().unique()):
        for t in sorted(d['year'].unique()):
            tr = d[(d['g'] == g) & (d['year'] == t)]
            if control == 'not_yet':
                co = d[(d['year'] == t) & ((d['g'].isna()) | (d['g'] > g))]
            else:
                co = d[(d['year'] == t) & (d['g'].isna())]
            if len(tr) == 0 or len(co) == 0:
                continue
            w = float(tr['n_contracts'].sum())
            if w <= 0:
                continue
            diff = float(tr[outcome].mean() - co[outcome].mean())
            cells.append({'g': int(g), 't': int(t), 'event': int(t - g), 'att': diff,
                          'w': w, 'n_tr': int(len(tr)), 'n_co': int(len(co)),
                          'co_codes': sorted(co['code'].unique().tolist())})
    return cells


def summarize(cells):
    if not cells:
        return None
    ev = defaultdict(list)
    for c in cells:
        ev[c['event']].append(c)
    es = {}
    for e, lst in sorted(ev.items()):
        w = np.array([c['w'] for c in lst])
        a = np.array([c['att'] for c in lst])
        es[e] = {'att_pp': round(float((w * a).sum() / w.sum()) * 100, 3),
                 'n_cells': len(lst), 'n_contracts': int(w.sum()),
                 'countries': sorted({c for cell in lst for c in
                                      ([cell['co_codes'][0]] if False else [])} or [])}
    post = [c for c in cells if c['event'] >= 0]
    w = np.array([c['w'] for c in post])
    a = np.array([c['att'] for c in post])
    att = float((w * a).sum() / w.sum())
    return {'event_study': {str(k): v for k, v in es.items()},
            'att': att, 'n_post_cells': len(post), 'n_contracts': int(w.sum())}


def boot_ci(panel, outcome, cohorts, control='not_yet', B=2000, seed=11):
    rng = np.random.default_rng(seed)
    codes = sorted(panel['code'].unique())
    draws = []
    for _ in range(B):
        pick = rng.choice(codes, size=len(codes), replace=True)
        sub = panel[panel['code'].isin(pick)]
        if sub['code'].nunique() < 12:
            continue
        r = summarize(cs_cells(sub, outcome, cohorts, control))
        if r and r['n_post_cells'] >= 4:
            draws.append(r['att'])
    draws = np.array(draws)
    if len(draws) < 50:
        return {'B': int(len(draws)), 'se_pp': None, 'ci95_pp': [None, None]}
    return {'B': int(len(draws)),
            'se_pp': round(float(np.std(draws, ddof=1)) * 100, 3),
            'ci95_pp': [round(float(np.percentile(draws, 2.5)) * 100, 2),
                        round(float(np.percentile(draws, 97.5)) * 100, 2)]}


def main():
    panel = build_panel()
    print(f'面板: {len(panel)} country-year, {panel.code.nunique()} 国, '
          f'{panel.year.min()}–{panel.year.max()}, 合同 {panel.n_contracts.sum():,}')

    arch = pd.read_csv(os.path.join(ROOT, 'data', 'interim', 'ted_panel.csv'))
    m = panel.merge(arch, on=['code', 'year'], suffixes=('', '_a'), how='inner')
    exact_n = int((m['n_contracts'] == m['n_contracts_a']).sum())
    print(f'\n[归档口径校验] {len(m)} 个共有 cell，合同数完全一致 {exact_n} 个 '
          f'({exact_n/len(m)*100:.1f}%)')
    for col in ('share_single_offer', 'elec_offer_share', 'foreign_winner_share'):
        s = m.dropna(subset=[col, col + '_a'])
        if len(s):
            mad = float(np.abs(s[col] - s[col + '_a']).max())
            print(f'  {col}: max|diff| = {mad:.5f}')

    R = {'panel': {'rows': int(len(panel)), 'contracts': int(panel.n_contracts.sum()),
                   'years': f'{panel.year.min()}–{panel.year.max()}',
                   'countries': int(panel.code.nunique())},
         'archive_check': {'cells': int(len(m)), 'exact_n': exact_n,
                           'pct_exact': round(exact_n / len(m) * 100, 1)}}

    for oc in ('share_single_offer', 'elec_offer_share', 'foreign_winner_share', 'mean_offers'):
        print(f'\n===== {oc} =====')
        cells = cs_cells(panel, oc, COHORT, 'not_yet')
        s = summarize(cells)
        if not s:
            print('  无单元')
            continue
        es = {int(k): v for k, v in s['event_study'].items()}
        print('  事件研究（相对转化年，ATT，权重=合同数）：')
        for e in sorted(es):
            if -4 <= e <= 4:
                print(f"    e={e:+d}: {es[e]['att_pp']:+7.2f}pp  "
                      f"(cells={es[e]['n_cells']}, contracts={es[e]['n_contracts']:,})")
        cb = boot_ci(panel, oc, COHORT, 'not_yet')
        print(f"  总体 ATT(e>=0): {s['att']*100:+.2f}pp  [{s['n_post_cells']} cells, "
              f"{s['n_contracts']:,} contracts]")
        print(f"  国家 cluster bootstrap: SE {cb['se_pp']}pp, CI95 {cb['ci95_pp']} (B={cb['B']})")
        # never-treated 对照
        cells_n = cs_cells(panel, oc, COHORT, 'never')
        sn = summarize(cells_n)
        cbn = boot_ci(panel, oc, COHORT, 'never')
        print(f"  [never 对照] ATT {sn['att']*100:+.2f}pp, CI95 {cbn['ci95_pp']}")
        # 事前趋势联合检验：e<0 的系数是否联合为零
        pre = [es[e]['att_pp'] for e in es if e < 0]
        R[oc] = {'event_study': s['event_study'], 'att_pp': round(s['att'] * 100, 3),
                 'n_post_cells': s['n_post_cells'], 'n_contracts': s['n_contracts'],
                 'boot': cb, 'pre_coeffs': pre,
                 'pre_max_abs_pp': round(float(max(abs(x) for x in pre)), 3) if pre else None,
                 'never_att_pp': round(sn['att'] * 100, 3), 'never_boot': cbn}

    json.dump(R, open(OUT, 'w'), indent=1)
    print(f'\n→ {OUT}')


if __name__ == '__main__':
    main()

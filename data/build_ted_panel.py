"""TED 合同级数据提取：CAN（合同授标公告）-> 国家-年采购竞争指标。

数据源：EU Open Data Portal TED CSV（ted-contract-award-notices-{year}.zip）
字段：ISO_COUNTRY_CODE / NUMBER_OFFERS / NUMBER_OFFERS_ELECTR /
      AWARD_VALUE_EURO / TYPE_OF_CONTRACT / WIN_COUNTRY_CODE / DT_AWARD
输出：data/interim/ted_panel.csv（country-year × 指标）
"""
import csv, io, os, sys, zipfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TED = os.path.join(BASE, 'data', 'external', 'ted')
OUT = os.path.join(BASE, 'data', 'interim')

ISO2TO3 = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP',
    'CZ': 'CZE', 'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA',
    'DE': 'DEU', 'GR': 'GRC', 'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA',
    'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX', 'MT': 'MLT', 'NL': 'NLD',
    'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK', 'SI': 'SVN',
    'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR',
}
EU28 = set(ISO2TO3.values())


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


agg = defaultdict(lambda: {'n': 0, 'offers': [], 'single': 0, 'elec': 0.0,
                           'off_sum': 0.0, 'foreign': 0, 'win_known': 0,
                           'vals': [], 'n_works': 0, 'single_works': 0,
                           'offers_works': [], 'elec_works': 0.0,
                           'off_sum_works': 0.0})
n_rows = n_used = 0
for fn in sorted(os.listdir(TED)):
    if not (fn.startswith('can_') and fn.endswith('.zip')):
        continue
    file_year = int(fn[4:8])
    z = zipfile.ZipFile(os.path.join(TED, fn))
    with z.open(z.namelist()[0]) as f:
        r = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
        for row in r:
            n_rows += 1
            code = ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
            if code not in EU28:
                continue
            if (row.get('CANCELLED') or '0').strip() == '1':
                continue
            # 授标年（优先 DT_AWARD，否则文件年）
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
            a = agg[(code, year)]
            a['n'] += 1
            if n is not None and n >= 1:
                a['offers'].append(n)
                a['off_sum'] += n
                if n == 1:
                    a['single'] += 1
                if ne is not None:
                    a['elec'] += ne
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
    print(f'  {fn}: 累计 {n_rows} 行，EU-28 有效 {n_used}')

import numpy as np
rows = []
for (code, year), a in sorted(agg.items()):
    n_off = len(a['offers'])
    row = {
        'code': code, 'year': year,
        'n_contracts': a['n'],
        'n_with_offers': n_off,
        'mean_offers': round(float(np.mean(a['offers'])), 4) if n_off else None,
        'share_single_offer': round(a['single'] / n_off, 4) if n_off else None,
        'elec_offer_share': round(a['elec'] / a['off_sum'], 4) if a['off_sum'] > 0 else None,
        'foreign_winner_share': round(a['foreign'] / a['win_known'], 4) if a['win_known'] else None,
        'median_award_value': round(float(np.median(a['vals'])), 1) if a['vals'] else None,
        'n_works': a['n_works'],
        'share_single_offer_works': round(a['single_works'] / len(a['offers_works']), 4) if a['offers_works'] else None,
        'mean_offers_works': round(float(np.mean(a['offers_works'])), 4) if a['offers_works'] else None,
        'elec_offer_share_works': round(a['elec_works'] / a['off_sum_works'], 4) if a['off_sum_works'] > 0 else None,
    }
    rows.append(row)

os.makedirs(OUT, exist_ok=True)
cols = list(rows[0].keys())
with open(os.path.join(OUT, 'ted_panel.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader(); w.writerows(rows)
print(f'\n已写 ted_panel.csv: {len(rows)} 个 country-year')
print(f'总行数 {n_rows}，EU-28 有效合同 {n_used}')

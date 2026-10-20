"""NEO v4.0 — 合同级微观面板（TED CAN，2013-2023，EU-28）

按 国×年×合同类型×CPV大类 分箱聚合合同级统计量，用于合同级回归
（用箱内合同特征吸收组成变异）。阈值稳定样本：高于各年 EU 阈值。
输出 data/interim/ted_micro.csv

用法：python data/build_micro_panel.py
"""
import csv, io, os, sys, json, zipfile
from collections import defaultdict
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TED = os.path.join(BASE, 'data', 'external', 'ted')

ISO2TO3 = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
           'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'GR': 'GRC',
           'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
           'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
           'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR'}

# 各年 EU 阈值（EUR，指令 2014/24 附表，2014-01 起；2013 用旧 2004/18 阈值）
# 货物/服务：2013=134k，2014-17=207k，2018-21=221k（每两年调整一次）
# 工程：2013=5.15M，2014-17=5.23M，2018-21=5.55M
THRESH = {
    2013: (134000, 5150000), 2014: (207000, 5235000), 2015: (207000, 5235000),
    2016: (207000, 5235000), 2017: (207000, 5235000),
    2018: (221000, 5482000), 2019: (221000, 5482000), 2020: (221000, 5482000),
    2021: (221000, 5482000),
}
# 稳定样本阈值（取高于对应年份 EU 阈值且有裕量）
MINV = {2013: 250000, 2014: 250000, 2015: 250000, 2016: 250000, 2017: 250000,
        2018: 250000, 2019: 250000, 2020: 250000, 2021: 250000,
        2022: 250000, 2023: 250000}
MINV_W = 6000000  # 工程（欧盟工程阈值 5.5M 左右，取整裕量）

# 2022/2023 实际 EU 阈值（2018 起 221k/5.482M 沿用至 2023）——2022-2023 若缺则用 2018 档


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def fint(x):
    try:
        return int(float(x))
    except Exception:
        return None


def cpv2(cpv):
    cpv = (cpv or '').strip()
    if len(cpv) >= 2 and cpv[:2].isdigit():
        return cpv[:2]
    return 'NA'


class Box:
    __slots__ = ('n', 'single', 'offsum', 'offers', 'elec', 'sme', 'othereu', 'nonu',
                 'logv', 'eauc', 'eufund', 'nawards', 'lots', 'foreignwin', 'values')

    def __init__(self):
        self.n = 0
        self.single = 0
        self.offsum = 0.0
        self.offers = []
        self.elec = 0.0
        self.sme = 0
        self.othereu = 0
        self.nonu = 0
        self.logv = 0.0
        self.eauc = 0
        self.eufund = 0
        self.nawards = 0
        self.lots = 0
        self.foreignwin = 0
        self.values = []


def main():
    agg = defaultdict(Box)
    years_seen = set()
    total = 0
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')):
            continue
        fy = int(fn[4:8])
        years_seen.add(fy)
        z = zipfile.ZipFile(os.path.join(TED, fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                code = ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
                if not code:
                    continue
                if (row.get('CANCELLED') or '0').strip() == '1':
                    continue
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('W', 'S', 'U'):
                    continue
                v = fnum(row.get('AWARD_VALUE_EURO'))
                if v is None or v <= 0:
                    continue
                thr = MINV_W if tc == 'W' else MINV.get(fy, 250000)
                if v < thr:
                    continue
                dt = (row.get('DT_AWARD') or '').strip()
                year = fy
                if dt and len(dt) >= 4 and dt[-4:].isdigit():
                    y = int(dt[-4:])
                    if 2005 <= y <= 2023:
                        year = y
                b = agg[(code, year, tc, cpv2(row.get('CPV')))]
                b.n += 1
                total += 1
                b.values.append(v)
                b.logv += np.log(v)
                if (row.get('B_ELECTRONIC_AUCTION') or '0').strip() == '1':
                    b.eauc += 1
                if (row.get('B_EU_FUNDS') or '0').strip() == '1':
                    b.eufund += 1
                b.nawards += fint(row.get('NUMBER_AWARDS')) or 0
                b.lots += fint(row.get('LOTS_NUMBER')) or 0
                n = fint(row.get('NUMBER_OFFERS'))
                if n is not None and n >= 1:
                    b.offers.append(n)
                    b.offsum += n
                    if n == 1:
                        b.single += 1
                    ne = fnum(row.get('NUMBER_OFFERS_ELECTR'))
                    if ne is not None:
                        b.elec += ne
                    ns = fnum(row.get('NUMBER_TENDERS_SME'))
                    b.sme += ns if ns is not None else 0
                    no = fnum(row.get('NUMBER_TENDERS_OTHER_EU'))
                    b.othereu += no if no is not None else 0
                    nn = fnum(row.get('NUMBER_TENDERS_NON_EU'))
                    b.nonu += nn if nn is not None else 0
                    wcc = (row.get('WIN_COUNTRY_CODE') or '').strip().upper()
                    if wcc and wcc != (row.get('ISO_COUNTRY_CODE') or '').strip().upper():
                        b.foreignwin += 1
    rows = []
    for (code, year, tc, c2), b in sorted(agg.items()):
        n_off = len(b.offers)
        rows.append({
            'code': code, 'year': year, 'type': tc, 'cpv2': c2,
            'n_contracts': b.n,
            'n_with_offers': n_off,
            'share_single_offer': (b.single / n_off) if n_off else None,
            'mean_offers': (b.offsum / n_off) if n_off else None,
            'median_offers': float(np.median(b.offers)) if n_off else None,
            'elec_offer_share': (b.elec / b.offsum) if b.offsum > 0 else None,
            'sme_tender_share': (b.sme / b.offsum) if b.offsum > 0 else None,
            'other_eu_tender_share': (b.othereu / b.offsum) if b.offsum > 0 else None,
            'non_eu_tender_share': (b.nonu / b.offsum) if b.offsum > 0 else None,
            'foreign_winner_share': (b.foreignwin / n_off) if n_off else None,
            'log_mean_value': (b.logv / b.n) if b.n else None,
            'elec_auction_share': (b.eauc / b.n) if b.n else None,
            'eu_funds_share': (b.eufund / b.n) if b.n else None,
            'mean_n_awards': (b.nawards / b.n) if b.n else None,
            'mean_lots': (b.lots / b.n) if b.n else None,
        })
    out = os.path.join(BASE, 'data', 'interim', 'ted_micro.csv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f'合同总数（阈值稳定）: {total:,}')
    print(f'箱面板行数: {len(rows):,} | 国 {len(set(r["code"] for r in rows))} | '
          f'年 {min(years_seen)}-{max(years_seen)} | 类型 {sorted(set(r["type"] for r in rows))} | '
          f'CPV2 {len(set(r["cpv2"] for r in rows))}')
    print(f'已写 {out}')
    meta = {'total_contracts': total, 'n_rows': len(rows),
            'years': sorted(years_seen),
            'threshold_rule': 'W: >=6,000,000 EUR; S/U: >=250,000 EUR; cancelled excluded',
            'source': 'EU Open Data Portal TED CAN 2013-2023'}
    with open(os.path.join(BASE, 'data', 'interim', 'ted_micro_meta.json'), 'w') as f:
        json.dump(meta, f, indent=1)


if __name__ == '__main__':
    main()

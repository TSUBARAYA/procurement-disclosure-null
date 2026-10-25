"""第九轮：CN 估计价值覆盖率的真实分母（未经估值过滤的 CN 合同公告数）。

论文 5.1/7.6 称覆盖率 "55% of 8.58 million"——分母无出处。本脚本从原始
CN zip 单遍计数：按年统计通过 (ID_TYPE=2, 未取消, EU-28, W/S/U) 过滤的
公告数（分母），以及其中携带可用估计价值的公告数（分子，即
run_v7_estimate_rd.py build() 实际保留的行）。
输出 materials/results/review9_cn_coverage.json
"""
import csv, io, json, os, zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TED = os.path.join(ROOT, 'data', 'external', 'ted')
OUT = os.path.join(ROOT, 'materials', 'results', 'review9_cn_coverage.json')
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


def main():
    by_year = defaultdict(lambda: {'filtered': 0, 'with_est': 0, 'grc_filtered': 0,
                                   'grc_with_est': 0})
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
                iso = (row.get('ISO_COUNTRY_CODE') or '').strip()
                code = ISO2TO3.get(iso)
                if code not in EU28:
                    continue
                tc = (row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('W', 'S', 'U'):
                    continue
                by_year[fy]['filtered'] += 1
                if code == 'GRC':
                    by_year[fy]['grc_filtered'] += 1
                ve = fnum(row.get('VALUE_EURO'))
                if ve is None or ve <= 0:
                    ve = fnum(row.get('VALUE_EURO_FIN_1'))
                if ve is not None and ve > 0:
                    by_year[fy]['with_est'] += 1
                    if code == 'GRC':
                        by_year[fy]['grc_with_est'] += 1
        print(fy, dict(by_year[fy]), flush=True)
    R = {'by_year': {str(y): by_year[y] for y in sorted(by_year)},
         'total_filtered': sum(v['filtered'] for v in by_year.values()),
         'total_with_est': sum(v['with_est'] for v in by_year.values()),
         'grc_filtered': sum(v['grc_filtered'] for v in by_year.values()),
         'grc_with_est': sum(v['grc_with_est'] for v in by_year.values())}
    R['coverage'] = round(R['total_with_est'] / R['total_filtered'] * 100, 2)
    json.dump(R, open(OUT, 'w'), indent=1)
    print('总计 过滤后 %s，其中带估计价值 %s（%.2f%%）；希腊 %s / %s'
          % (format(R['total_filtered'], ','), format(R['total_with_est'], ','),
             R['coverage'], format(R['grc_filtered'], ','), format(R['grc_with_est'], ',')))
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()

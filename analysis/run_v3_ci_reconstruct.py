"""v3.0 CI reconstruction (resolves verification item V1).

The archived results_v3.json interval [-3.69, +7.12] is produced by
estimators_v2.cell_ci (neo/identification/estimators_v2.py): the 2.5th/97.5th
percentiles of the eight post-period (g,t) cell ATTs. Its docstring calls it
"汇总 ATT 区间：跨 (g,t) 单元经验分位（保守，含单元间离散）" — a between-cell
dispersion range, not a sampling confidence interval, and not a bootstrap.
The point estimate (+3.37 pp) is the n_treated-weighted aggregation of the
same eight cells (aggregate()), whose unweighted cell mean is +2.42 pp — which
is why the archived bounds are not centered on the point estimate.

This script reproduces the point estimate and the archived bounds from the
original panel (neo/data/interim/ted_panel.csv) and the original estimator
code, then computes a reproducible cell-level t-interval: the eight (g,t)
cells are the unit of observation, cell weights are proportional to the number
of treated countries, and the critical value is t(0.975, 7). Both the archived
range and the reconstructed interval are saved for the paper's Table 3 note.
"""
import csv, json, sys
import numpy as np
import pandas as pd
from scipy import stats as st

sys.path.insert(0, 'c:/Users/OMEN/Desktop/neo/identification')
from estimators_v2 import build_cells, aggregate, cell_ci

BASE = 'c:/Users/OMEN/Desktop/neo'
cohorts = {}
with open(BASE + '/data/external/eu_transposition_2014_24.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        cohorts[r['code']] = int(r['event_year']) if r['event_year'] else None

ted = pd.read_csv(BASE + '/data/interim/ted_panel.csv')
ted = ted[ted['code'].isin(cohorts)].copy()
YEARS = sorted(ted['year'].unique())

out = {}
for oc, key in [('share_single_offer', 'single'), ('elec_offer_share', 'elec')]:
    sub = ted.dropna(subset=[oc]).copy()
    cells = build_cells(sub.assign(event_year=sub['code'].map(cohorts)), cohorts, YEARS, oc)
    agg = aggregate(cells)
    ci = cell_ci(cells)
    items = [v for (g, t), v in cells.items() if 2 <= t - g <= 3]
    atts = np.array([v['att'] for v in items])
    ns = np.array([v['n_treated'] for v in items], float)
    m = np.average(atts, weights=ns)                       # weighted point estimate
    sd = atts.std(ddof=1)                                  # between-cell dispersion
    w = ns / ns.sum()
    se = np.sqrt((w ** 2).sum()) * sd                      # weighted cell-level SE
    tcrit = st.t.ppf(0.975, len(atts) - 1)
    out[key] = {
        'point_pp': round(float(m * 100), 3),
        'archived_range_pp': [round(ci['ci_lo'] * 100, 3), round(ci['ci_hi'] * 100, 3)],
        'archived_note': '2.5/97.5 empirical percentiles of 8 (g,t) cell ATTs (estimators_v2.cell_ci)',
        'unweighted_cell_mean_pp': round(float(atts.mean() * 100), 3),
        'cell_sd_pp': round(float(sd * 100), 3),
        'cell_se_pp': round(float(se * 100), 3),
        'cell_t_ci95_pp': [round(float((m - tcrit * se) * 100), 3),
                           round(float((m + tcrit * se) * 100), 3)],
        'n_cells': len(atts),
        'cell_details': [{'g': int(g), 't': int(t), 'att_pp': round(v['att'] * 100, 3),
                          'n_treated': int(v['n_treated']), 'n_control': int(v['n_control'])}
                         for (g, t), v in sorted(cells.items()) if 2 <= t - g <= 3],
    }
    print(key, json.dumps({k: v for k, v in out[key].items() if k != 'cell_details'}, indent=1))

json.dump(out, open('../materials/results/review4_v3_ci_reconstruction.json', 'w'), indent=1)
print('saved review4_v3_ci_reconstruction.json')

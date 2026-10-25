"""Placebo cutoff tests at 70/80/120/130% of the true threshold (post-hoc, module 7.3 of revision).

Specification mirrors the pre-registered v6.0 main spec:
  single ~ above + r + above:r + type FE + country x year FE, country-clustered SEs
The cache (rd_sample_cache.csv) contains only contracts inside the +/-20% band
around the TRUE cutoff. Each placebo's feasible sample is therefore the
intersection of its own +/-20% window with the cached band. Where the cached band
leaves no contracts on one side of a placebo cutoff, the test is infeasible on
this cache and is reported as such (the original v6.0 run used the full TED
extract, so its 80% result is cited from results_v6.json, not re-estimated here).
"""
import numpy as np
import pandas as pd
import json
from scipy import stats as st

df = pd.read_csv('rd_sample_cache.csv')
df['ratio_v'] = np.exp(df['r'])
TOL = 1e-9  # same tolerance as the main pipeline


def rd_tau(d):
    d = d.dropna(subset=['r', 'above', 'single']).copy()
    d['ix'] = d['above'] * d['r']
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([
        d['single'].astype(float).rename('y'),
        d['above'].astype(float).rename('a'),
        d['r'].rename('r'),
        d['ix'].rename('ar'),
        keys.rename('k'),
    ], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    X = np.column_stack([
        np.ones(len(d)),
        (allv['a'] - gm['a']).values,
        (allv['r'] - gm['r']).values,
        (allv['ar'] - gm['ar']).values,
    ])
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    resid = yd - X @ beta
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    cl = d['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        meat += np.outer(X[m].T @ resid[m], X[m].T @ resid[m])
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    tau = beta[1] * 100
    se = np.sqrt(np.diag(V))[1] * 100
    return tau, se, n


out = {}
for pc in [0.7, 0.8, 1.2, 1.3]:
    key = f'{pc:.1f}'
    r_pl = df['r'] - np.log(pc)
    band = df[r_pl.abs() <= 0.2 + TOL]
    n_below_side = int((band['ratio_v'] < pc).sum())
    n_above_side = int((band['ratio_v'] >= pc).sum())
    rec = {'n_band_contracts': len(band), 'n_below_placebo': n_below_side, 'n_above_placebo': n_above_side}
    if n_below_side >= 200 and n_above_side >= 200:
        d = band.copy()
        d['above'] = (d['ratio_v'] >= pc).astype(float)
        d['r'] = r_pl[band.index]
        tau, se, nn = rd_tau(d)
        tcrit = st.t.ppf(0.975, 27)
        t = tau / se
        p = 2 * (1 - st.t.cdf(abs(t), df=27))
        rec.update({
            'tau_pp': round(float(tau), 3), 'se_pp': round(float(se), 3),
            'p': round(float(p), 4), 'n': nn,
            'ci95_pp': [round(float(tau - tcrit * se), 3), round(float(tau + tcrit * se), 3)],
        })
    else:
        rec['status'] = ('infeasible on cached +/-20% band: no comparison group on one side '
                         'of this placebo cutoff within the band')
    out[key] = rec
    print(key, rec)

json.dump(out, open('../materials/results/review4_placebo_extra.json', 'w'), indent=1)
print('saved review4_placebo_extra.json')

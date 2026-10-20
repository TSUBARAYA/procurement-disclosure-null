# High-Precision Null: Mandatory E-Procurement Disclosure and Market Competition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](requirements.txt)
[![Data: EU Open Data Portal](https://img.shields.io/badge/Data-EU%20TED-green.svg)](data/README.md)

Code, data manifests, pre-registration, and full result records for three
pre-registered quasi-experimental studies of mandatory e-procurement
disclosure, built on the EU Tenders Electronic Daily (TED) contract award
record (EU-28, 2013–2023, **6.78 million contracts**).

## TL;DR

Three designs with **disjoint identifying variation** — staggered national
transposition timing (v3.0), contract-level panels (v4.0), and a **legal
threshold discontinuity** (v6.0) — converge on the same result:

> Mandatory EU-wide disclosure procedures do **not** measurably change market
> competition among the contracts visible at the threshold. The final design
> bounds any effect below **0.6 percentage points** on the single-offer share
> (95% CI ±0.014; minimum detectable effect ≈ 0.001).

One mechanism *did* survive and is reported as a finding: digital depth raises
the **SME share of tenders by about a third** (0.025 → 0.35). Participation
responds; competition does not. Read against theories in which transparency
disciplines power, the result delineates a boundary: **disclosure without
accountability machinery does not constrain.**

## The three studies

| Version | Design | Identifying variation | Sample | Result |
|---|---|---|---|---|
| **v3.0** | Callaway–Sant'Anna group-time ATT on staggered adoption | National transposition dates of Directive 2014/24/EU | 6.78M contracts (country-year aggregates, 252 cells) | First stage strong (electronic-offer share +0.38~+0.43); competition outcomes null |
| **v4.0** | Contract-level two-way fixed effects with contract controls | Same dates, contract-level panel, 11-year window | 1.30M threshold-stable contracts, 16,429 country-year-type-CPV cells | Competition null; **SME participation +0.334 (p<0.001)** |
| **v6.0** | Sharp regression discontinuity at the legal threshold | **The procurement threshold itself** — a cutoff set by delegated regulation, not by any researcher or official | 326,718 contracts within ±20% of cutoff | **High-precision null** (CI ±0.014, MDE ≈ 0.001) |

Every study was pre-registered before its results were computed; the
pre-registration for the final design is frozen in
[`config/preregistration_v6.yaml`](config/preregistration_v6.yaml). All
failures, diagnostics, and specification choices are recorded — see
[`docs/failure_log.md`](docs/failure_log.md) — including the density-test
downgrade in v6.0 (contracts are 1.6% denser below the cutoff; conclusions are
therefore confined to the TED-visible sample, as the registered rule requires).

## Data

All data are from the **EU Open Data Portal** TED contract-award-notice
extracts (`ted-contract-award-notices-YYYY.zip`, 2013–2023), plus the legal
threshold table from Directive 2014/24/EU as amended by Commission Delegated
Regulations (EU) 2017/2365, 2019/1828, and 2021/2170 (parsed from the
Commission's ESPD review report COM(2017) 242), and the per-country
transposition dates of the directive.

This repository ships the **derived analysis panels** (see
[`data/README.md`](data/README.md) for the full download and rebuild
instructions):

- `data/interim/ted_panel.csv` — 252 country-year aggregates (v3.0 input)
- `data/interim/ted_micro.csv` — 16,429 country-year-type-CPV cells (v4.0 input)
- `data/external/eu_transposition_2014_24.csv` — 28 countries' transposition dates

## Repository structure

```
├── config/
│   └── preregistration_v6.yaml     # frozen pre-registration (threshold RD)
├── data/
│   ├── build_ted_panel.py          # raw TED notices -> country-year panel (v3.0)
│   ├── build_micro_panel.py        # raw TED notices -> contract-cell panel (v4.0)
│   ├── external/                   # transposition dates + threshold sources
│   ├── interim/                    # derived analysis panels (shipped)
│   └── README.md                   # data acquisition & rebuild guide
├── identification/
│   ├── estimators_v2.py            # group-time ATT, event study, synthetic control
│   ├── estimators_v4.py            # interacting-FE demeaning, WLS, clustered SE
│   ├── run_v3.py                   # v3.0 main analysis
│   ├── run_v4.py                   # v4.0 contract-level FE + dose-response
│   └── run_v6.py                   # v6.0 threshold RD (main + diagnostics)
├── report/
│   ├── MAIN_RESULTS_v3.md          # v3.0 report
│   ├── MAIN_RESULTS_v4.md          # v4.0 report
│   ├── MAIN_RESULTS_v6.md          # v6.0 report
│   └── results_*.json              # machine-readable results (all runs)
└── docs/
    ├── failure_log.md              # F8–F17: every failure, diagnostic, and downgrade
    └── data_dictionary.md          # variable definitions and sources
```

## Reproducing

```bash
pip install -r requirements.txt

# (optional) rebuild panels from raw TED extracts — see data/README.md
python data/build_ted_panel.py       # writes data/interim/ted_panel.csv
python data/build_micro_panel.py     # writes data/interim/ted_micro.csv

# v3.0: staggered-adoption group-time ATT (uses shipped ted_panel.csv)
python identification/run_v3.py      # writes report/results_v3.json

# v4.0: contract-level FE + dose-response (uses shipped ted_micro.csv)
python identification/run_v4.py      # writes report/results_v4.json

# v6.0: threshold RD (reads raw TED extracts; see data/README.md)
python identification/run_v6.py      # writes report/results_v6.json
```

v3.0 and v4.0 run on the shipped derived panels and complete in under a
minute. v6.0 reads the raw TED zip extracts (≈770 MB for 2013–2023) and takes
roughly 10–15 minutes of streaming parse; a smaller year range can be selected
by editing the file list in `run_v6.py`.

## Design highlights (v6.0)

- **Treatment**: contract awarded value ≥ the legal EU threshold for its type
  and year (supply/service: €134k→€221k over 2013–2023; works: €5.15M→€5.48M).
- **Running variable**: log(value) − log(applicable threshold).
- **Estimator**: local polynomial RD, linear and quadratic, bandwidths
  ±10/15/20/25%, country×year and contract-type fixed effects, standard errors
  clustered by awarding country (28 clusters).
- **Diagnostics**: McCrary-style density test, placebo cutoffs at 70/80/120/130%
  of the true threshold, and a pre-registered minimum detectable effect.
- **Honesty rule**: a significant density jump forces all conclusions to be
  confined to the TED-visible sample (triggered: 1.6% gap, p<0.0001 — reported,
  not hidden).

## Citation

```bibtex
@misc{procurement_disclosure_null_2026,
  title  = {High-Precision Null: Mandatory E-Procurement Disclosure and Market Competition},
  author = {NEO Research Program},
  year   = {2026},
  note   = {Code, data manifests, and pre-registered results for three
            quasi-experimental studies on EU TED contract data},
  url    = {https://github.com/TSUBARAYA/procurement-disclosure-null}
}
```

## License

Code: [MIT](LICENSE). Data: derived from EU public sources (TED / EUR-Lex);
see [`data/README.md`](data/README.md) for upstream attribution and reuse terms.

## Acknowledgments

The TED contract award notice dataset is published by the Publications Office
of the European Union via the EU Open Data Portal. Threshold values are from
Directive 2014/24/EU and its delegated regulations; the per-country
transposition table is from the European Commission's ESPD review report
COM(2017) 242.

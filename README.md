# Testing the Transparency–Competition Premise: Evidence from EU Public Procurement

Code, data manifests, pre-registration, and full result records for the paper
*Testing the Transparency–Competition Premise* — three quasi-experimental
designs on the complete EU Tenders Electronic Daily (TED) record (EU-28,
2013–2023), plus the complete audit trail of the six-version research program
that produced them.

**Paper (Markdown source)**: [`paper/transparency_and_competition.md`](paper/transparency_and_competition.md)

## TL;DR

> Within the TED-visible sample, the EU's mandatory disclosure regime left **no
> detectable change in competition intensity** at the legal threshold. The main
> design — a regression discontinuity on the variable the law actually uses, the
> contract notice's pre-award estimate — gives **−0.67 pp on the single-offer
> share (SE 1.46, p = 0.65, 95% CI [−3.66, +2.32], n = 179,065)**, detecting
> effects of roughly 4 points or larger at 80% power. No specification, on
> either running variable, produces a competitive gain.
>
> One outcome moves: the foreign-winner share falls by **1.21 pp (SE 0.49,
> p = 0.019)**, concentrated in 2020–2023. And one mechanism survives:
> digital depth is strongly associated with the SME share of tenders across
> countries (+33.4 pp dose-response; deciles 8.7% → 54.6%), whose within-country
> counterpart is smaller and only marginal (+7.44 pp, p = 0.095).
>
> The first stage of the threshold design is systematically absent (15
> candidates, none surviving multiple-testing correction), so the null is read
> as "no identifiable treatment at the cutoff" rather than "the reform did not
> work". Every correction this repository has been through — including a
> country-code bug that silently dropped Greece and moved the point estimate
> from +0.49 to −0.67 — is disclosed in the paper and in the failure log.

## The designs

| Version | Design | Identifying variation | Sample | Result |
|---|---|---|---|---|
| **v7.0 (main)** | Sharp RD at the legal threshold, running variable = the contract notice's pre-award **estimate** (`VALUE_EURO`), outcome from the linked award notice | the procurement threshold itself — a line set by delegated regulation | 4.69M notices, 28 countries; 339,636 in the ±20% band | null (−0.67 pp, CI [−3.66, +2.32]); foreign-winner −1.21 pp (p = 0.019) |
| v3.0 (auxiliary) | Callaway–Sant'Anna group-time ATT | staggered national transposition dates | 6.78M contracts, 252 country-year cells | first stage strong (e-offer share +38.2 pp); competition null |
| v4.0 (auxiliary) | Contract-level FE + dose-response | same dates, contract level | 5.92M contracts, 16,429 cells | competition null; SME dose-response +33.4 pp (p < 0.001) |
| v6.0 (archived) | Sharp RD on the **awarded** value | the threshold | 327,636 in the ±20% band | retained as the audit record; running variable rejected (4 of 16 placebo cutoffs significant) |

The two timing designs share one source of variation at two aggregation levels,
so the program offers **two independent legs**, not three. The designs identify
the effect of a procedural bundle, not of disclosure alone.

## Version history and corrections

This repository is updated in place; **history is never rewritten**. Two tags
pin the states the paper's audit refers to:

- **`v1.0-archive`** — the initially uploaded state (2026-10-20): v6.0 as the
  main design on the awarded value, with the erroneous 2013–2017 threshold
  schedule (headline +0.82 pp).
- **`v2.0`** — the current state, matching the paper: v7.0 main design on the
  notice estimate, 28 countries, corrected threshold schedule, headline
  −0.67 pp.

Corrections between the two (all disclosed in the paper and in
[`docs/failure_log.md`](docs/failure_log.md), records F18–F23):

1. **Threshold schedule** (F18): the frozen pre-registration's table was wrong
   for 2013–2017 (2013 should be EUR 200,000, not 207,000; 2016–17 EUR 209,000 /
   5,225,000). The frozen file is untouched (hash in
   [`docs/manifest.md`](docs/manifest.md)); the correction is a separate
   addendum. End-to-end re-run: headline +0.82 → +1.27 pp on the corrected
   schedule.
2. **Running variable** (F20): the award-value specification produces
   significant jumps at 4 of 16 placebo cutoffs — the signature of a manipulable
   sorting variable. v7.0 re-specifies the discontinuity on the notice's
   pre-award estimate, which the law actually uses.
3. **Country coverage** (F21): a country-code mapping bug (`GRC` instead of
   `GR`) silently dropped every Greek notice; the main design briefly ran on
   27 of 28 member states. Fixed and fully re-run: sample 4.46M → 4.69M,
   point estimate +0.49 → −0.67 pp. Both runs are reported.
4. **Density audit** (F19, F22): the frozen density test's rejection of symmetry
   is a bin-construction artifact; the adjacent-bin bootstrap had an
   implementation defect (subsampling instead of cluster resampling), since
   fixed. Corrected tests find no discontinuity at the line.

## Data

All raw data are public: the TED contract-award-notices and contract-notices
extracts from the EU Open Data Portal (11 annual zips, ≈1.1 GB, **not** shipped
— download per [`data/README.md`](data/README.md)), the statutory threshold
schedules (Directive 2004/18/EC and 2014/24/EU as amended), and the national
transposition dates (COM(2017) 242 and national sources). OpenTender/OCDS was
consulted for below-threshold coverage and rejected (its bidder field records
only the winner); the attempt is documented in the paper.

Shipped with the repository: the derived panels
([`data/interim/ted_panel.csv`](data/interim/ted_panel.csv),
[`data/interim/ted_micro.csv`](data/interim/ted_micro.csv)) so v3.0/v4.0
reproduce in under a minute, the 55 machine-readable result files, the frozen
pre-registration, and the full failure log. Large intermediate caches are
rebuilt from the raw extracts by the pipeline (see
[`docs/manifest.md`](docs/manifest.md)).

## Repository structure

```
├── config/
│   ├── preregistration_v6.yaml                  # frozen pre-registration (hash in docs/manifest.md)
│   └── preregistration_v6_threshold_addendum.md # correction addendum
├── data/
│   ├── build_ted_panel.py / build_micro_panel.py
│   ├── external/eu_transposition_2014_24.csv
│   ├── interim/                                 # derived panels (shipped)
│   └── README.md                                # raw-data download & rebuild guide
├── identification/                              # main-pipeline scripts (v3.0, v4.0, v6.0)
│   ├── estimators_v2.py / estimators_v4.py
│   └── run_v3.py / run_v4.py / run_v6.py        # re-runs write report/ (reproductions)
├── analysis/                                    # 41 pipeline & diagnostic scripts
│   ├── run_v7_estimate_rd.py                    # v7.0 main design (CN-to-CAN matcher + full spec set)
│   ├── run_v7_clean_subsamples.py               # cleaning rules, coverage, subsample decomposition
│   ├── run_v7_scale_placebo.py                  # foreign-winner scale tests, cleaned placebo battery
│   ├── run_v7_first_stage.py                    # 15 first-stage candidates + Holm correction
│   ├── run_v7_density_robust.py                 # McCrary-style tests, binscatter, high-publication subsample
│   ├── run_v7_density_test.py                   # adjacent-bin tests, country-clustered bootstrap
│   ├── run_review9_*.py                         # coverage, paper numbers, LOO, offer robustness, density slope, figures
│   └── run_v6_*.py / run_review8_*.py           # threshold correction, archived reproduction, diagnostics
├── figures/                                     # 12 builders + figure data + PNGs
├── materials/results/                           # 55 machine-readable result files
├── report/                                      # reproduction outputs (results_v3/v4/v6.json) + design reports
├── paper/
│   ├── transparency_and_competition.md          # the paper (Markdown source)
│   ├── verify_round4.py                         # 556 checks: paper text vs archived JSON
│   ├── verify_round8.py / md2docx.py / REVISION_NOTES.md
├── docs/
│   ├── failure_log.md                           # F8–F23: every failure, diagnostic, correction
│   ├── data_dictionary.md
│   └── manifest.md                              # hashes, version map, contents
├── Makefile / Dockerfile / requirements.txt
└── README.md
```

## Reproducing

```
pip install -r requirements.txt

make data       # download the 11 annual TED CAN + CN extracts (~1.1 GB, needs network)
make results    # every numeric result: v3/v4/v6 reproductions, v7.0 main design, diagnostics
make figures    # rebuild the five figures
make paper      # regenerate the .docx from the Markdown source
make verify     # 556 automated checks of every number in the text
```

Only numpy, pandas, scipy (and matplotlib for figures, python-docx for the
paper) are required. v3.0/v4.0 run on the shipped panels in under a minute;
v6.0 and v7.0 stream the raw extracts and take roughly 10–20 minutes each.

## Verification

- **556 automated checks** (`python paper/verify_round4.py`) re-derive every
  number in the paper text from the archived result JSONs; all pass.
- The three main-pipeline scripts were missing from the initial upload
  (`results_v3.json` and `results_v4.json` had no producing script). They were
  restored and re-run: `results_v3.json` reproduces to the last digit,
  `results_v4.json` matches to machine precision, and `results_v6.json` —
  including its erroneous threshold table — reproduces from the raw archives
  with zero differences across every field. Outputs go to `report/` so the
  reproduction checks the archive rather than replacing it.
- Of the 55 result files, 52 are reproducible from the shipped scripts; 3 are
  withdrawn (`bunching_eur_v6.json`, `digital_split_v6.json`,
  `results_v3_outlier_robust.json`) and are used by no number in the paper.

## Citation

```bibtex
@misc{procurement_disclosure_null_2026,
  title  = {Testing the Transparency--Competition Premise:
            Evidence from EU Public Procurement},
  author = {NEO Research Program},
  year   = {2026},
  note   = {Code, data manifests, pre-registration, and full audit trail for
            three quasi-experimental designs on EU TED contract data},
  url    = {https://github.com/TSUBARAYA/procurement-disclosure-null}
}
```

## License

Code: MIT (see `LICENSE`). Data: derived from EU public sources (TED /
EUR-Lex); see [`data/README.md`](data/README.md) for upstream attribution.

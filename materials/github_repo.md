# Open-Source Repository (the paper's reproducibility asset)

**URL**: https://github.com/TSUBARAYA/procurement-disclosure-null
**License**: MIT (code) / EU public data (data)
**Contents**: 63 Python files (11,250 lines), 55 machine-readable result files,
frozen pre-registration with its correction addendum, failure log F8–F23, and
the paper's Markdown source. Two tags pin the audited states: `v1.0-archive`
(the initially uploaded state) and `v2.0` (the current state, matching the
paper). See `docs/manifest.md` for hashes and the version map.

## Path mapping used in this paper

| Paper section | Repository path |
|---|---|
| v7.0 main design (threshold RD on the notice estimate) | `analysis/run_v7_estimate_rd.py` (+ `run_v7_clean_subsamples.py`, `run_v7_scale_placebo.py`, `run_v7_density_robust.py`, `run_v7_density_test.py`) |
| v7.0 first stage (15 candidates, Holm) | `analysis/run_v7_first_stage.py` |
| v6.0 threshold RD (archived; the frozen pipeline) | `identification/run_v6.py` + `identification/estimators_v4.py` |
| v6.0 statutory re-run / threshold correction | `analysis/run_v6_full_rerun.py`, `analysis/run_v6_rerun_final.py` |
| v3.0 group-time ATT / TWFE panel | `identification/run_v3.py` + `identification/estimators_v2.py` |
| v4.0 contract-level FE + dose-response | `identification/run_v4.py` + `identification/estimators_v4.py` |
| Data pipeline (raw TED → panels) | `data/build_ted_panel.py`, `data/build_micro_panel.py` |
| Density audit (frozen test, mechanical null, corrected tests) | `analysis/run_density_audit.py` |
| Density slope / continuity diagnostics | `analysis/run_review9_density_slope.py` |
| Coverage denominators, paper numbers, LOO, offer robustness, figure data | `analysis/run_review9_{coverage,paper_numbers,loo,offer_robust,figures_v7}.py` |
| Frozen pre-registration (SHA-256 in `docs/manifest.md`) | `config/preregistration_v6.yaml` |
| Threshold correction addendum | `config/preregistration_v6_threshold_addendum.md` |
| Failure log (all rounds, F8–F23) | `docs/failure_log.md` |
| Data dictionary | `docs/data_dictionary.md` |
| Machine-readable results (55 files) | `materials/results/*.json` |
| Reproduction outputs (v3/v4/v6 re-runs) | `report/results_v{3,4,6}.json` |
| The paper (Markdown source) | `paper/transparency_and_competition.md` |
| Automated verification (556 checks) | `paper/verify_round4.py` |
| Figure builders and data | `figures/redraw_figures.py`, `figures/*_v7.json`, `figures/fig*.png` |
| One-command reproduction | `Makefile` (`make all`), `Dockerfile` |

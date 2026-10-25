# Repository Manifest

Integrity record and version map for this repository. The manifest itself is
versioned; each entry states what it certifies and what it does not.

## Frozen pre-registration (v6.0 threshold RD)

| File | SHA-256 (of the committed bytes) | Status |
|---|---|---|
| `config/preregistration_v6.yaml` | `7fb646a88aaa0da3fba59bad92e462375785ef2c09e5291a016f8b7c5df0c021` | frozen; never edited after 2026-10-19 |
| `config/preregistration_v6_threshold_addendum.md` | see `docs/manifest.md` of tag `v2.0` | correction addendum (the frozen file itself is untouched) |

The hash certifies **integrity after the fact**: the published bytes are the
bytes that were committed, and any later edit would break the hash. It does
**not** certify that the plan the file records was correct — the frozen
threshold table was wrong for 2013–2017, which is why the correction lives in
a separate addendum (failure log F18; paper Section 7.4). The committed file
uses CRLF line endings; the hash above is over those bytes as committed.

## Version map

| Tag | Commit | State |
|---|---|---|
| `v1.0-archive` | `f08e999` | the initially uploaded state: v6.0 threshold RD on the **awarded** value with the **erroneous** 2013–2017 threshold schedule (headline +0.82 pp); v3.0/v4.0 auxiliary; frozen pre-registration; failure log F8–F17 |
| `v2.0` | this commit | current state, matching the paper: v7.0 main design (threshold RD on the contract notice's pre-award **estimate**, 28 countries, headline −0.67 pp, 95% CI [−3.66, +2.32], n = 179,065); v6.0 retained as the archived record; threshold schedule corrected; failure log extended to F23 |

The archived `v1.0-archive` state is preserved in git history and by its tag;
nothing was rewritten or deleted. The paper's Section 7.4 validation — that
the re-run reproduces the archive exactly when the wrong cutoffs are supplied
— can be checked against that tag.

## Contents (v2.0)

- **63 Python files, 11,250 lines**: 41 pipeline/diagnostic scripts in
  `analysis/`, 5 main-pipeline scripts in `identification/`, 12 figure builders
  in `figures/`, 2 panel builders in `data/`, 3 in `paper/`.
- **55 machine-readable result files** in `materials/results/` (52 reproducible
  from the shipped scripts; 3 withdrawn — see `README.md` audit table).
- **556 automated checks** (`python paper/verify_round4.py`) re-deriving every
  number in the paper text from the archived JSON; all pass.
- Derived panels `data/interim/ted_panel.csv` (252 country-year cells) and
  `ted_micro.csv` (16,429 contract cells), so v3.0/v4.0 reproduce in under a
  minute without the raw TED extracts. The large intermediate caches
  (`analysis/*.csv`, 33–399 MB each) are **not** shipped: they are rebuilt from
  the raw extracts in minutes, and the whole statutory-schedule grid has been
  re-extracted end to end and reproduces to the digit.
- Raw TED data (≈1.1 GB) is external; download and rebuild instructions are in
  `data/README.md`.

## Reproduction entry points

```
make data       # download the 11 annual TED CAN + CN extracts (~1.1 GB)
make results    # every numeric result (v3/v4/v6 reproductions, v7.0 main design, diagnostics)
make figures    # rebuild the five figures
make paper      # regenerate the .docx from paper/transparency_and_competition.md
make verify     # 556 checks: paper text vs archived JSON
```

Or directly: `python paper/verify_round4.py` (checks only; needs the shipped
results but not the raw data).

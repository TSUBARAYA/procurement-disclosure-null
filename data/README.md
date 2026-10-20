# Data: acquisition and rebuild guide

## Shipped in this repository

| File | Rows | Description |
|---|---|---|
| `interim/ted_panel.csv` | 252 | Country-year aggregates (input to v3.0): contract counts, single-offer share, mean offers, electronic-offer share, foreign-winner share, median award value |
| `interim/ted_micro.csv` | 16,429 | Country × year × contract-type × CPV2 cells (input to v4.0): the same outcomes plus contract characteristics (log mean value, mean lots, mean awards, electronic-auction share, EU-funds share) |
| `external/eu_transposition_2014_24.csv` | 28 | Per-country transposition year of Directive 2014/24/EU (25 dated + 3 censored), with sources |

## Raw data (not shipped — 770 MB)

The TED contract award notice (CAN) extracts are published by the Publications
Office of the European Union on the EU Open Data Portal and are **not**
redistributed here.

### Download

```bash
for y in 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
  curl -sL -o data/external/ted/can_$y.zip \
    "https://data.europa.eu/api/hub/store/data/ted-contract-award-notices-$y.zip"
done
```

Each archive contains one CSV (~75 columns) with one row per awarded contract.
Fields used: `ISO_COUNTRY_CODE`, `TYPE_OF_CONTRACT` (W/S/U), `AWARD_VALUE_EURO`,
`NUMBER_OFFERS`, `NUMBER_OFFERS_ELECTR`, `NUMBER_TENDERS_SME`, `WIN_COUNTRY_CODE`,
`CPV`, `CANCELLED`, `DT_AWARD`, `B_ELECTRONIC_AUCTION`, `B_EU_FUNDS`,
`NUMBER_AWARDS`, `LOTS_NUMBER`, `OUT_OF_DIRECTIVES`.

### Rebuild the derived panels

```bash
python data/build_ted_panel.py    # -> data/interim/ted_panel.csv
python data/build_micro_panel.py  # -> data/interim/ted_micro.csv
```

Both scripts stream the zip archives, filter cancellations, map two-letter
codes to ISO-3166 alpha-3, apply the threshold-stability rule (supply/service
≥ €250,000; works ≥ €6,000,000), and aggregate. Full extraction counts:
**6,782,760 contracts** (2013–2021, unfiltered) and **1,303,529 contracts**
(2013–2023, threshold-stable).

## Legal threshold table (used by v6.0)

Sub-central supply/service and works thresholds (EUR, excl. VAT), from
Directive 2014/24/EU Art. 4 as amended:

| Years | Supply/service | Works |
|---|---|---|
| 2013 | 207,000 | 5,235,000 |
| 2014–2017 | 207,000 | 5,235,000 |
| 2018–2019 | 221,000 | 5,548,000 |
| 2020–2021 | 214,000 | 5,350,000 |
| 2022–2023 | 215,000 | 5,382,000 |

2013 values carry over from Directive 2004/18/EC. Amendments: Commission
Delegated Regulations (EU) 2017/2365, 2019/1828, and 2021/2170.

## Transposition dates

`external/eu_transposition_2014_24.csv` records each member state's
transposition of Directive 2014/24/EU. The 19 dated entries visible in the
Commission's ESPD review report (COM(2017) 242, Annex Table 1) were parsed from
the original PDF; the remaining dated entries were verified against national
legal sources (e.g., Spain Ley 9/2017, Austria BVergG 2018, Sweden LOU
2016:1145). Sweden, Portugal, and Luxembourg had not notified the Commission
as of 2017-04-05 and are treated as censored (never-treated within the window).

## Upstream attribution and reuse

- **TED contract award notices**: Publications Office of the European Union,
  via the EU Open Data Portal (<https://data.europa.eu>). Reuse is governed by
  the EU Open Data Directive (2019/1024); the dataset carries no access
  restrictions beyond attribution.
- **Directive 2014/24/EU and delegated regulations**: EUR-Lex
  (<https://eur-lex.europa.eu>), reused under the Commission's legal notice.
- **COM(2017) 242**: European Commission, reused under the Commission's
  reuse-of-documents policy.

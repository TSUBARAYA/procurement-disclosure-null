# Addendum to the frozen v6.0 pre-registration: correction of the threshold table

**Status:** post hoc correction, disclosed in Section 7.4 of the paper.
**Date of correction:** fourth revision round.
**Applies to:** `materials/preregistration_v6.yaml`, section 3 (`thresholds`).

## What the frozen file says

The frozen pre-registration, whose SHA-256 fingerprint is recorded in the
repository manifest, specifies the following cutoff values (EUR, excluding VAT,
sub-central supply/service and works):

```
2013: [207000, 5235000]
2014: [207000, 5235000]
2015: [207000, 5235000]
2016: [207000, 5235000]
2017: [207000, 5235000]
2018: [221000, 5548000]
2019: [221000, 5548000]
2020: [214000, 5350000]
2021: [214000, 5350000]
2022: [215000, 5382000]
2023: [215000, 5382000]
```

## Why it is wrong

Checked against the instruments the frozen file itself cites, eight of the ten
year-type cells are wrong:

| Years | Frozen file | Statutory value | Instrument |
|---|---|---|---|
| 2013 | 207,000 / 5,235,000 | 200,000 / 5,000,000 | Directive 2004/18/EC as amended by Regulation (EU) No 1269/2011 |
| 2014 | 207,000 / 5,235,000 | 207,000 / 5,186,000 | Regulation (EU) No 1336/2013 |
| 2015 | 207,000 / 5,235,000 | 207,000 / 5,186,000 | Regulation (EU) No 1336/2013 |
| 2016 | 207,000 / 5,235,000 | 209,000 / 5,225,000 | Regulation (EU) 2015/2170 |
| 2017 | 207,000 / 5,235,000 | 209,000 / 5,225,000 | Regulation (EU) 2015/2170 |
| 2018–2019 | 221,000 / 5,548,000 | 221,000 / 5,548,000 | Regulation (EU) 2017/2365 — correct |
| 2020–2021 | 214,000 / 5,350,000 | 214,000 / 5,350,000 | Regulation (EU) 2019/1828 — correct |
| 2022–2023 | 215,000 / 5,382,000 | 215,000 / 5,382,000 | Regulation (EU) 2021/2170 — correct |

The works figure €5,235,000 appears in no instrument in the series. The
2014–15 supply/service value (€207,000) appears to have been carried backwards
across 2013 and forwards across 2016–17.

## What the frozen file's source note gets right and wrong

The source note cites Directive 2014/24/EU Art. 4 and the three delegated
regulations for 2018–2023, and Directive 2004/18/EC for 2013. The 2018–2023
values are correct. What the note omits is the instrument that actually sets the
2014–17 values, Regulation (EU) No 1336/2013 and Regulation (EU) 2015/2170 —
and, more to the point, it does not record which instrument each year's number
came from, which is what allowed a single wrong number to propagate across five
years without tripping any check.

## Why the file is not edited in place

The frozen file is the record. Its hash certifies that the published bytes are
the bytes that were committed; editing the threshold block in place would
destroy the only evidence of what was actually frozen, and the paper's Section 8
states plainly that the hash establishes integrity after the fact rather than
correctness or third-party certification. This addendum is therefore a separate
file, and the corrected values live in the paper's Table 1 and in
`analysis/run_threshold_correction.py`.

## What this implies for the pre-registration claim

Three things, all stated in Section 7.4 of the paper:

1. **A frozen plan can freeze an error.** The threshold table was part of the
   frozen specification, and it was wrong. Freezing a plan protects against
   post hoc changes to a plan; it does not protect against a plan that was
   wrong when it was written, and the hash cannot tell the difference.
2. **Correcting it is a departure from the pre-registration**, disclosed
   alongside the window-metric departure of Section 7.3 rather than folded into
   it. The correction is not optional: a design whose cutoff is in the wrong
   place is not estimating what it claims to estimate.
3. **The direction of the correction is known and it is not favourable to the
   paper's headline.** Correcting the cutoffs moves the full-band estimate from
   +0.82 pp (p = 0.234) to +1.26 pp (p = 0.082), and to +1.39 (p = 0.040)
   without the log-value control. The correction was made and reported because
   the alternative is to publish a design built on cutoffs that no instrument
   in EU law contains.

## Reproduction

```
python analysis/run_threshold_correction.py        # 影响量化 + 重算
python analysis/run_threshold_decomposition.py     # 误分类 vs 带宽平移分解
python figures/build_corrected_figdata.py          # 图 1/3/4 的更正数据
python paper/verify_round4.py                      # 数字对回归档校验
```

# Testing the Transparency–Competition Premise: Evidence from EU Public Procurement

**Abstract.** International organizations promote mandatory e-procurement
disclosure as a competition-enhancing reform, yet micro-level causal evidence on
the premise remains thin. This paper tests the premise with the complete EU
Tenders Electronic Daily record (EU-28, 2013–2023): 4.69 million contract
*notices* matched to 3.97 million contract *award* notices, plus three designs
built on two independent sources of variation — the staggered national
transposition dates of Directive 2014/24/EU and the legal procurement threshold.
The designs identify the effect of a procedural bundle, not of disclosure alone.
**The main design re-specifies the threshold discontinuity on the variable the
law actually uses.** The archived version of this paper ran the discontinuity on
the *awarded* value, which buyers can influence at the award stage; the design
reported here runs it on the *estimated* value published in the contract notice
before bids close, which is the legally binding variable and is immune to
award-stage manipulation. On that specification the discontinuity is clean where
it previously was not: seven placebo cutoffs produce no significant jump
(the archived award-value specification produced four significant jumps out of
sixteen), contract composition is balanced on both sides of the line, and the
density discontinuity at the cutoff is not statistically distinguishable from
zero under a country-clustered bootstrap. The estimate is **−0.67 percentage
points on the single-offer share (SE 1.46, p = 0.65, 95% CI [−3.66, +2.32],
n = 179,065)** — statistically indistinguishable from zero, with effects larger
than roughly 4.2 percentage points in either direction excluded at 80% power.
A country-code mapping error in the first version of this design silently
dropped all Greek notices; correcting it moves the point estimate from +0.49 to
−0.67 and changes no verdict, and both runs are reported.
One outcome moves: the foreign-winner share falls by 1.21 pp (SE 0.49,
p = 0.019) at the cutoff, and the estimate is not attenuated by controlling for
the awarded value, so it is a discontinuity rather than a smooth size gradient;
it is concentrated in 2020–2023.
No specification, on either running variable, produces a competitive gain. The
two transposition designs, which exploit variation no buyer controls, are
reported as auxiliary: the contract-level event study on the single-offer share
carries significant pre-trends and is therefore not interpretable as a causal
effect, while the same design on the foreign-winner share is clean and returns a
precise null (+0.23 pp, SE 0.13–0.44) that excludes gains above about one point.
An error in the threshold schedule used for 2013–2017, found in the fourth
revision round and corrected against the statutory instruments, is disclosed
together with its consequences. Two further results qualify the picture: a
participation gradient — a strong cross-country association between digital
depth and the SME share of tenders, from 8.7% in the lowest electronic-offer
decile to 54.6% in the highest — whose within-country counterpart is smaller
and only marginally significant (+7.44 pp, p = 0.095) — and a density audit that
finds no detectable bunching: the pre-registered test's rejection of symmetry
traces to an asymmetric bin construction, and corrected tests do not reject.
What the results support is narrower than the premise: within this sample, this
instrument left no detectable change in competition intensity, and the record
shows a strong cross-country association between digital depth and the SME share
of tenders, though the evidence does not establish how much of that gradient
reflects participation changes rather than institutional differences or
reporting practices. All code, data manifests, pre-registrations, and failure
logs are public.

**Keywords:** public procurement; e-procurement; transparency; regression discontinuity; bunching; null result; open science

**JEL:** D44, H57, K23, L51

---

## 1. Introduction

**Transparency and competition are linked in theory, but the link is not
automatic.** Public procurement is the largest single market in which
governments act as buyers — roughly one sixth of GDP in the OECD area — and it
is, by common consent, one of the most corruption-prone activities states
perform. The theoretical case for transparency runs through information:
opaque procurement hides the buyer's decisions from citizens, prosecutors, and
rival bidders, and hidden decisions are cheap to capture. A large literature
treats transparency as the discipline mechanism of last resort — information
reaches citizens or prosecutors, and rent-seeking retreats (Besley and Burgess,
2002; Fazekas, Tóth, and King, 2016). The policy translation is equally
familiar: if buyers must disclose, competition will follow.

That translation skips a step. *Disclosure* — the mandatory publication of
tender and award information — changes what bidders and watchdogs can see; it
does not, by itself, change who bids, how the buyer scores offers, or whether
anyone can punish a captured award. Competition in procurement is made of the
bidder pool's structure, the buyer's preferences, and the risk of collusion,
and none of these is moved by information alone. Transparency could raise
competition by lowering the cost of finding and bidding on tenders, and it
could leave competition unchanged if the binding constraint is buyer preference,
collusion risk, or compliance cost. It could even lower measured competition if
stricter procedures thin the small-bidder pool. Whether disclosure raises
competition is therefore an empirical question, not a theorem — and the
direction is not guaranteed by the theory that motivates the reform.

**The reform that was actually implemented is a bundle, not a disclosure
rule.** The European Union made its version law in Directive 2014/24/EU, and
the World Bank and the OECD recommend it as a governance best practice (OECD,
2015). But the
directive's supra-threshold regime packages several instruments together:
mandatory publication of tender and award information in the Official Journal
supplement Tenders Electronic Daily, standardized procedure types, longer
minimum advertisement deadlines, and *e-procurement* — electronic submission of
offers through centralized portals. We use *transparency* for the theoretical
concept, *disclosure* for the publication mechanism, *e-procurement* for the
electronic submission channel, and *procedural bundle* for the package the
directive actually imposes. The distinction matters for what any estimate of
the reform can mean: a jump at the point where the bundle switches on is
evidence about the bundle, and separating disclosure from its companions
requires variation the bundle does not provide.

**This paper tests the premise with three designs built on two
independent sources of variation** — the staggered national transposition dates
and the legal procurement threshold — applied to the complete EU Tenders
Electronic Daily contract award record (EU-28, 2013–2023; 6.78 million
contracts for 2013–2021, with the panel and threshold samples extended through
2023). The third design, at the legal threshold, is the pre-registered main
design: its plan — the threshold table, the estimator, the clustering, the
decision rule, and the diagnostic battery — was frozen before its results were
computed. The first two designs, on national transposition timing, are
auxiliary convergence designs whose sequence of specifications is documented
in the failure log in execution order rather than in a separate frozen plan
(Section 8). The first design exploits timing: the staggered transposition
dates, estimated with the Callaway–Sant'Anna (2021) group-time ATT. The second
exploits panel structure: the same dates pushed down to 1.30 million
threshold-stable contracts with contract-type and country-by-year fixed
effects. The third exploits a legal cutoff: the procurement threshold itself, a
line drawn by delegated regulation that no buyer, official, or researcher
controls. The designs have different failure modes and different
vulnerabilities; that they agree is informative precisely because they can
disagree.

**The designs identify the effect of a procedural bundle, not of disclosure
alone.** The first two estimate the intention-to-treat effect of transposing
the directive, in which electronic submission is one component among procedure,
deadline, and publicity rules, with a strong first stage (electronic-offer
share +38.2 points). The third estimates the reduced-form consequence of
crossing the threshold, where the same bundle applies but its
electronic-submission component does not demonstrably bind (first stage +0.38
points, p = 0.212). The three designs therefore do not identify the same
parameter, and their agreement is evidence about a family of related treatments
rather than three independent causal validations of one claim; the two
timing-based designs, moreover, share the same identifying variation at two
aggregation levels, so the program really offers two independent legs, not
three.

**The answer is a null with a stated resolution, now run on the variable the
law uses.** At the legal threshold, the single-offer share — our headline
measure of weak competition — moves by **−0.67 percentage points (SE 1.46,
p = 0.650)** when the running variable is the contract notice's published
estimate, the variable the directive's threshold legally applies to and the one
buyers cannot revise once bids have closed; the 95% confidence interval runs
from −3.66 to +2.32 points, and effects larger than roughly 4.2 points in
either direction are excluded at 80% power. The point estimate leans toward the
direction the policy premise predicts without reaching significance, which is
the absence of a detectable effect rather than evidence for the premise. The
first version of this design silently dropped every Greek notice through a
country-code mapping error; correcting it moved the point estimate from +0.49
to −0.67 and changed no verdict, and both runs are reported (Section 6.1). The
archived design, which ran the discontinuity on the *awarded* value — a
variable buyers can influence at the award stage — reported +1.27 points
(SE 0.71, p = 0.085) under the statutory schedule and +0.82 (SE 0.68,
p = 0.234) under an erroneous 2013–2017 schedule whose correction Section 7.4
documents; that design's placebo profile, four significant jumps out of sixteen
fake cutoffs, is the evidence that the running variable had to change, and its
specifications are retained as the archived record rather than as findings. Two
features of the evidence deserve emphasis. First, the archived full-band
estimate is fragile in an informative way: excluding the threshold
neighborhood, where sorting on the running variable would bind most strongly,
yields positive estimates of +1.65 to +2.13 percentage points on the
single-offer share across control sets. These specifications were not
pre-registered; with contract-type controls the three donut specifications
clear every correction we report (Holm, 1979, adjusted p ≈ 0.02–0.03;
Bonferroni ≈ 0.02–0.04; Romano–Wolf, 2016, stepdown ≈ 0.03–0.04), without
controls they clear none under Holm or Bonferroni and only the ±1% donut under
Romano–Wolf (0.040) — and under a quadratic local polynomial all of them
shrink to insignificance. We report them as diagnostics of the threshold
neighborhood rather than as findings. The honest summary is therefore not
"no effect" but "no detectable gain, in any specification, with the
neighborhood-excluding specifications returning positive point estimates that
do not survive a more flexible functional form." Second, the design passes the
diagnostics the archived one failed — seven placebo cutoffs with no
significant jump, composition balanced on both sides of the line, and no
density discontinuity distinguishable from sampling noise — although the
density shape on the legally correct sample is a below-side slope rather than
a jump, which is the visibility-selection pattern the framework predicts and a
qualification of the continuity assumption rather than a certificate. Nor is
the estimate an average over offsetting heterogeneity: splitting the sample by
contract type (supply, service, works) and by national corruption perception
(Transparency International, 2024) produces five subgroups, and not one shows a
detectable competitive gain.

**Two results survive the null, and they are what makes it informative.**

*First, a participation gradient that is large and not yet causal.* The same
contract record shows that digital depth moves who shows up. In the panel
designs, the dose-response of the SME share of tenders to country-year
electronic-offer intensity is +33.42 percentage points (SE 7.87, p = 0.0002,
95% CI [+17.25, +49.59]); the raw decile gradient runs from 8.7% of tenders in
the lowest electronic-offer decile to 54.6% in the highest. Electronic
submission is associated with a lower cost of participation, and small
enterprises respond. The dose-response leverages variation in digital depth
across countries and years, so it is exposed to confounding by national
institutions, market structure, and reporting practices — including the
possibility that better-resourced authorities complete the SME fields more
reliably, a reporting artifact we flag in Section 6.4; the within-country
binary treatment is the cleaner but weaker estimate (+7.44 pp, p = 0.095), and
we read the two together rather than either alone. Lowering the barrier to
entry is not the same as changing the buyer's preferences, the bidder pool's
structure, or the risk of collusion — and those, not information costs, are
what competition in procurement is made of.

*Second, no detectable avoidance at the margin.* The pre-registered density
test rejects symmetry at the cutoff (log density gap −0.0114 on the statutory
schedule, −0.0157 on the archived one; binomial
p < 0.0001), and the pre-registered decision rule would downgrade every
conclusion on that basis. An audit shows the rejection is an artifact of the
test's construction: it pools twelve bins below the line against nine above —
dropping the bin immediately above the cutoff — and tests against a 50/50 null
that ignores the asymmetry, so that a perfectly symmetric density would produce
a larger apparent excess below the line than the data do. Corrected tests —
symmetric bin windows, the correct null, and cluster-robust inference — do not
reject symmetry, and their point estimates favor the above side; the one sharp
feature of the histogram is a mass point *at* the line (5,314 contracts
reporting award values within 0.01% of the threshold, predominantly German feeds),
which is a reporting convention rather than avoidance (Section 7.1). We report
the headline estimate without the downgrade the frozen rule would assign, and we
publish the audit that justifies the difference — while noting, with Section
7.4, that the headline is borderline rather than clean once the threshold
schedule is corrected. What survives the audit is structural rather than statistical:
publication below the line is voluntary or nationally mandated, so the domestic
segment remains invisible to every disclosure-based monitor — including this
one — and the estimates describe the TED-visible sample only. The margin
exists whether or not these data can see anyone using it, and nothing below
the line is visible to the monitoring apparatus the directive creates.

**Methodologically, the paper is built to be checked rather than believed.**
The main design at the legal threshold was pre-registered before its results
were computed, and the post hoc robustness exercises of Section 7.3 are
labelled as such; the frozen pre-registration file for that design — the
threshold table, the estimator, the clustering, the decision rule, and the
diagnostic battery — is public with its SHA-256 fingerprint. The two auxiliary
timing designs have no separate frozen plan; their specifications are
documented in the failure log in execution order, a weaker form of the record
that we describe as such in Section 8. The complete code, the derived analysis
panels, the machine-readable results of every run, and the failure log of all
six versions of this research program — including the four that failed and the
one that died of data access — are public at
https://github.com/TSUBARAYA/procurement-disclosure-null. A null result travels
with its failure log attached, and we have tried to keep that practice concrete
rather than rhetorical.

**What the results mean for theory.** Our estimates are consistent with the
interpretation that mandatory disclosure, stripped of the accountability
machinery that would give it force — no performance loops, no redundant
oversight, no penalties that bite — lowers the cost of participation without
changing competition intensity. We state that as an interpretation, not an
identification: the designs move the bundle, not disclosure alone, and the
estimates cannot separate the channel. If the theory expected disclosure alone
to discipline procurement, the disclosure-only version of that theory finds no
support at this cutoff, in this sample, with this precision. If it expected
disclosure to matter only inside a larger institutional machine, the results
are consistent with what it should predict — and the machine, not the platform,
is what deserves the policy attention.

The rest of the paper is organized as follows. Section 2 describes the
institutional setting, the legal thresholds, and the limits of the TED-visible
sample. Section 3 describes the data and measurement, including the honest
statement of what we cannot yet see. Section 4 presents a minimal auction model
that organizes the three predictions we test. Section 5 lays out the empirical
strategy, the two-independent-legs logic, and the identifying assumptions,
including the running-variable endogeneity and selection issues that qualify
them. Section 6 reports the main results. Section 7 reports mechanisms,
heterogeneity, and robustness. Section 8 is the open-science statement. Section
9 concludes with what the evidence supports, and what it does not.

---

## 2. Institutional Background

### 2.1 The directive and its thresholds

Directive 2014/24/EU governs public procurement by contracting authorities in the
EU member states. Two of its provisions matter for identification. First,
contracts whose estimated value reaches a legally specified threshold must be
procured through EU-wide procedures — open or restricted procedures published in
the Official Journal supplement Tenders Electronic Daily, with minimum
advertisement periods and, since the eForms mandate, electronic submission
requirements. Contracts below the threshold are procured under national rules,
which in most member states are substantially lighter. Second, the thresholds
themselves are set by the directive and revised every two years by delegated
regulation, tracking the World Trade Organization Government Procurement
Agreement. The applicable values over our sample window are shown in Table 1.

**Table 1. Legal procurement thresholds (EUR, excluding VAT), sub-central
supply/service and works contracts**

| Years | Supply/service | Works | Source instrument |
|---|---|---|---|
| 2013 | 200,000 | 5,000,000 | Directive 2004/18/EC as amended by Regulation (EU) No 1269/2011 |
| 2014–2015 | 207,000 | 5,186,000 | Regulation (EU) No 1336/2013 |
| 2016–2017 | 209,000 | 5,225,000 | Directive 2014/24/EU Art. 4, as amended by Commission Delegated Regulation (EU) 2015/2170 |
| 2018–2019 | 221,000 | 5,548,000 | Regulation (EU) 2017/2365 |
| 2020–2021 | 214,000 | 5,350,000 | Regulation (EU) 2019/1828 |
| 2022–2023 | 215,000 | 5,382,000 | Regulation (EU) 2021/2170 |

*Sources:* Directive 2014/24/EU Art. 4 (as amended in each biennium) for 2014–2023;
Directive 2004/18/EC Art. 7–8 for 2013. Each instrument states the amounts it
replaces and the date from which it applies (1 January of the first year of each
biennium). **This table was corrected in the fourth revision round.** The
version previously circulated carried €207,000 and €5,235,000 for all of
2013–2017, which conflates the 2014–15 values with the 2013 and 2016–17
biennia and states a works figure that appears in no instrument in the series;
Section 7.4 reports what the error did to the analysis and what has been
re-run since the correction.

Two scope caveats attach to Table 1. First, the thresholds shown are for
sub-central contracting authorities; central authorities face lower values for
the same categories (for example, €144,000 for central supply/service contracts
in 2018–19). The TED extract does not flag authority level, so we cannot
separate the two populations in the data, and the RD assigns each contract the
threshold applicable to its type and year on the sub-central schedule. To the
extent that central-authority contracts enter the sample under the wrong
threshold, treatment is mismeasured — a bias that likely attenuates the
estimated jump toward zero. Because the mismeasurement can be endogenous to
the threshold (Section 5.1) — the running variable is the awarded value, an
outcome of the tender — the direction of the bias is not guaranteed, and the
main estimate is therefore not read as a strict lower bound. Second, the
thresholds apply to the *estimated* value of the contract, not the awarded
value; Section 5.1 explains how we handle that distinction and Section 7.3
reports the specification that uses the legally correct running variable.

### 2.2 Why the threshold is a clean natural experiment

Three properties make the threshold attractive as an identifying device. First,
it is exogenous to the contract: a buyer cannot move the line, and the line
moves on a fixed two-year cycle for currency reasons, not procurement outcomes.
Second, the discontinuity in regulatory treatment is sharp: crossing from
€220,000 to €222,000 changes which rulebook applies, not the nature of the
purchase. Third, the treatment is a bundle we can describe precisely — EU-wide
publication, standardized procedure types, longer minimum deadlines, and
electronic submission — which lets us interpret the estimated jump as the effect
of the disclosure regime rather than of some diffuse reform.

Two caveats belong here rather than in a footnote. The threshold is a *legal*
object but the published contract value is a *reported* object, and buyers who
prefer to stay below the line have two instruments: split the contract into lots
below the threshold, or estimate the value conservatively. Section 7.1 tests the
first instrument and finds no detectable fingerprint in the density of
contracts around the line. Second, TED publishes what
the directive requires; the domestic market below the line is largely invisible
to us, and our estimates describe the contracts visible at the line. One
consequence deserves emphasis: a contract split or shaved so that every lot
falls below the threshold never appears in TED at all, and for that entirely
hidden domestic segment our conclusions do not generalize. Whether that
segment is large or small is something the published record cannot settle —
the density test of Section 7.1 bounds what is visible at the line, and the
invisible part is invisible by construction.

### 2.3 What the directive mandates — and what publication below the line is not

The comparison across the line is a comparison between two publication regimes,
and the regimes differ in what they *require*. Article 50 of Directive
2014/24/EU obliges contracting authorities to publish award notices in TED for
contracts at or above the EU thresholds; that obligation is the treatment side
of our design. Below the threshold, no EU-level publication obligation exists:
sub-threshold procurement is governed by national rules, and a sub-threshold
contract appears in TED for reasons that differ across member states and across
buyers — national transparency laws that some member states apply to their own
smaller contracts, buyer-initiated voluntary publication, publication attached
to EU-funded projects, or the buyer's choice to run the EU-wide procedure on a
contract that did not require it. It would therefore be wrong to describe the
below-threshold side of the sample as uniformly voluntary: it is a mixture of
voluntary and nationally mandated publication, with the mix itself varying by
country and year. What is common to all of these channels is that appearance in
TED below the line is a *choice or a national rule*, not the EU-level mandate
that produces the above-threshold side.

That asymmetry is a selection concern, and our pre-registration named it before
any result was computed: the below-threshold sample is self-selected into
visibility, and the conclusions are confined to the TED-visible sample for that
reason. Three specific channels matter. First, the decision to publish a
sub-threshold contract may correlate with how competitive the contract was —
an authority proud of a competitive tender publishes it; an authority with a
single unsolicited offer may not. Second, publication capacity differs:
better-resourced authorities maintain fuller reporting practices, so the
visible sub-threshold pool over-represents high-capacity buyers relative to the
true population. Third, contract types differ in their tendency to be
published voluntarily, so composition, not just volume, can differ across the
line. If voluntary publication below the threshold is correlated with
competition, the continuity assumption fails: the two sides of the cutoff would
no longer be comparable populations differing only in regime, and the
discontinuity estimate would mix a regime effect with a visibility-selection
effect.

What the data can and cannot do about this should be stated plainly. The
visible sample supports balance checks on pre-treatment contract
characteristics across the line (Section 7.3 reports them), and the donut
specifications address potential manipulation of the running variable rather
than visibility. But the data contain no information about sub-threshold contracts
that were never published: their competitiveness, their values, and their
buyers are unobserved, and no robustness exercise performed on the visible
sample can recover them. This is a limitation of the design that we disclose
rather than one that general robustness testing has removed, and it is a second
reason — alongside the hidden split-contract segment — why the conclusions are
scoped to contracts visible at the line.

### 2.4 The reform timeline as a second source of variation

Member states transposed Directive 2014/24/EU between April 2016 and
June 2018. Twenty-five transpositions are dated in the Commission's ESPD review
(COM(2017) 242, Annex Table 1) and national legal sources; Sweden, Portugal,
and Luxembourg had not notified the Commission as of April 2017 and are treated
as censored, which under a not-yet-treated design keeps them as clean controls
throughout. The transposition dates drive the first two designs; the threshold
drives the third.

---

## 3. Data and Measurement

### 3.1 Primary data

Two TED extracts published by the Publications Office of the European Union on
the EU Open Data Portal are used, one zip archive per year for 2013–2023 each.
The **contract award notice (CAN)** extract carries roughly 75 columns per
awarded contract, including the number of offers received and the awarded
value. The **contract notice (CN)** extract carries 64 columns per tender
announcement, and three of them matter for this paper: `VALUE_EURO`, the
buyer's published estimate of the contract value, which is the variable the
directive's threshold legally applies to and which is fixed when the notice is
dispatched, before bids close; `DT_DISPATCH` and `DT_APPLICATIONS`, which
bracket the tender period; and `FUTURE_CAN_ID`, which links the notice to its
eventual award notice. The main design (Section 5.1, v7.0) reads its running
variable off the CN extract and its outcome off the matched CAN record. Three
sample counts are used for it and they measure different things, so we state
each. The CN estimate field — the binding constraint — is populated for
**4,688,892 notices, 59% of the 7.97 million contract notices passing the type,
cancellation, and member-state filters** (Section 7.6 reports coverage by year
and country). Of those, **3,968,395 (84.6%) resolve to an award notice**, and
each outcome is then available on its own terms: the offer count behind the
single-offer outcome is usable for about half of the matched sample, the
winner-nationality comparison for about seven in ten, and the two dispatch
dates behind the tender period for about eight in ten. Inside the ±20%
threshold band — **339,636 notices** — the estimation samples are **179,065
contracts for the single-offer share, 280,578 for the foreign-winner share, and
339,368 for the tender period**; these are the samples behind Table 9, and the
differences between them are field availability, not filtering choices.

The CAN extract on its own remains the basis of the archived specifications and
of the country-year design. We restrict attention to the 28 EU member states as
awarding countries, exclude cancelled notices, and keep supply (S), service (U),
and works (W) contracts. Three samples are used in this paper, and they do not
all cover the same years; we state each window explicitly.

The **full record** is every notice passing these filters for **2013–2021**:
**6,782,760 contracts**. It is the basis of the country-year design (v3.0),
which we do not re-run on the longer window.

The **panel sample** uses the extraction extended to **2023** and keeps only
threshold-stable contracts — awarded value of at least €250,000
(supply/service) or €6,000,000 (works), fixed floors set above the highest
applicable thresholds in the window (€221,000 and €5,548,000 in 2018–19) so
that the two-yearly threshold revisions cannot reclassify a contract across
regimes — leaving **1,303,529 contracts for 2013–2023**. The floor rule is a
selection: it excludes contracts between €221,000 and €250,000 in the
high-threshold years and biases the panel toward larger contracts, and we state
the rule exactly so the selection is visible.

The **threshold-discontinuity sample** is drawn from the same 2013–2023
extraction, not from the 2013–2021 full record: the **327,636 contracts whose
awarded value falls within twenty percent of the applicable statutory threshold** for
their type and year (the window is defined in value space, |v/τ − 1| ≤ 0.2; the
archived band, built on the erroneous 2013–2017 schedule, held 326,718 — see
Section 7.4). Of these, **85,656 (26.1%) are dated 2022 or 2023**. Section 7.3 reports the
estimates separately for 2013–2021 and 2022–2023: the extension moves nothing
(+1.42 pp over 2013–2021, p = 0.052; +0.83 pp over 2022–2023, p = 0.499), so the
window choice is not what produces the headline.
Variables are observed contract attributes, not perception composites: number
of offers received (`NUMBER_OFFERS`), offers submitted electronically
(`NUMBER_OFFERS_ELECTR`), number of tenders from SMEs (`NUMBER_TENDERS_SME`),
winner nationality (`WIN_COUNTRY_CODE`), awarded value (`AWARD_VALUE_EURO`),
CPV class, contract type, electronic-auction and EU-funding flags. The full
data dictionary, with field names and construction rules, is in the repository's
`docs/data_dictionary.md`; the panels we analyze, with the raw-to-derived
pipeline, are shipped with the code.

### 3.2 Outcome construction

Our headline outcome is the **single-offer incidence**: the share of contracts receiving exactly one offer. It is the standard operational definition of weak
competition in the procurement literature (Palguta and Pertold, 2017; Fazekas
and Kocsis, 2020) and it is measured directly rather than through perceptions.
The proxy is standard but not exhaustive: it captures the extensive margin of
weak competition, not intensity — a market with three uninterested bidders and
one with three fierce ones look alike on this measure — and it can reflect
market structure, contract specialization, or buyer behavior rather than
competition as such. We therefore report the offer-count distribution alongside
the binary outcome: in the ±20% threshold band, the mean number of offers is
6.91 below the threshold and 5.94 above, and the share of contracts receiving
three or more offers is 50.3% below versus 49.0% above (the offer count is
reported for 318,179 of the 327,636 contracts; contracts without a reported
count are treated as receiving fewer than three). The secondary
outcomes — log(1 + offers), the electronic-offer share (the first-stage
mechanism), and the foreign-winner share (cross-border access) — triangulate
the same question at the discontinuity. The panel designs aggregate to
country × year × contract-type × CPV2 cells (16,429 cells) so that contract
composition can be held fixed.

### 3.3 What we cannot yet see — and what we now can

The framework we were asked to test includes two extensions, one of which we
have now executed and one of which we have **not**, and we flag both rather than
imply them. First, **local bias**: identifying whether buyers favor domestic or incumbent bidders requires
matching winning firms to their NUTS-2 region (e.g., via OpenCorporates), which
we have not done; the buyer-preference channel in Section 4 therefore remains
an interpretation of our null, not a measured quantity. Second, **welfare**:
computing discount rates (award price versus estimated value) was previously
blocked by the sparseness of the notice-level estimate fields. On re-extraction
the field is populated for 95.4% of the threshold sample, and Section 6.5
reports the resulting analysis. The field records the procedure-level
(multi-lot) estimate rather than the single contract's estimate, so the
analysis is confined to the 53% of notices where the two are comparable, and
the welfare reading is correspondingly qualified.

---

## 4. Theoretical Framework

The empirical results below are sharpest when read against a minimal model of
entry into procurement tendering. We use a first-price sealed-bid auction with
entry costs and buyer preference — the standard workhorse of procurement
analysis — and derive three predictions that map one-to-one onto our outcomes.

### 4.1 Setup

A buyer procures a contract via first-price sealed-bid auction — the standard
procurement format (Klemperer, 2004), in which the **lowest** bid wins. Two types of
potential bidders exist: large firms (*L*) and SMEs (*S*). Before bidding, each
firm decides whether to enter, paying an entry cost *c* (preparing a bid,
obtaining documents, monitoring the portal). Firms that enter draw private
fulfillment costs and submit price bids; the buyer awards to the lowest bid,
with the preference *δ* ≥ 0 for the incumbent or domestic supplier type
entering the award decision as an effective discount on that bidder's price, so
a large or domestic bidder wins whenever its price is within *δ* of the best
rival's. Such a preference can arise
from local protectionism, political connections between the buyer and favored
firms, or bureaucratic rent-seeking motives; the model requires only its sign,
not its source.

The first stage is the entry decision. Firm *i* enters if expected profit net
of the entry cost is positive:

π_i − c > 0, where π_i = (p_i − k_i) · Pr(win | entry).

The variables are three distinct economic objects, and keeping them distinct
matters for what the model can say:

- *k_i* is the **fulfillment cost** — the private cost of delivering the
  contract once won (materials, labor, capacity), drawn after the entry
  decision and known to the firm when it bids. It is subtracted from the
  contract price inside the profit expression: a bid below fulfillment cost is
  a loss, whatever the buyer pays.
- *p_i* is the **contract price** — what the buyer pays the winner. It is the
  bidding instrument, set before the outcome is known, and it is the quantity
  the auction aggregates. It is not a cost to the bidder; it is revenue.
- *c* is the **entry cost** — the cost of participating at all (preparing the
  bid, obtaining documents, monitoring the portal). It is paid whether the
  firm wins or loses, so it enters the entry condition as a fixed outlay
  rather than a per-contract margin.

Two consequences of the distinction are used below. The disclosure
intervention of Section 4.2 moves *c*, the entry cost, and only that; nothing
in the reform moves *k_i*, the fulfillment cost, or the buyer's preference
*δ*. And the single-offer incidence — the outcome our empirical designs
measure — is the event that no rival enters, which is governed by the entry
condition and by *δ*, not by the winner's margin *(p − k)*.

**Assumptions.** The model assumes (i) independent private values on the
fulfillment-cost side, so bids reflect private costs plus a markup; (ii) a
fixed, known entry cost per contract, homogeneous within type; (iii) the
buyer's preference *δ* is fixed across contracts within a country-year; and
(iv) no collusion among bidders — each firm treats the others' entry as
given. The framework is deliberately minimal and its scope is
correspondingly limited: it is a lens for interpreting signs in the data, not
a calibrated structure. TED does not publish bid-level data, so no parameter
of the model is estimated; the model disciplines the interpretation of the
three design-based estimates, and nothing more.

### 4.2 The disclosure intervention

Mandatory disclosure lowers the *information* component of entry costs —
finding the tender, reading the documents, assembling a compliant bid — which
we model as a reduction in *c* for all bidders, with the reduction plausibly
larger for SMEs, whose baseline costs are higher. Formally, the reform shifts
*c* to *c′* = (1 − θ)·c* with θ ∈ (0, 1].

### 4.3 Predictions

**H1: competition null under preference.** If the buyer's preference *δ* is
positive, entry costs affect the *extensive* margin (who shows up) but the
award still concentrates on preferred bidders: lowering *c* raises the number
of entrants, yet the single-offer incidence — which reflects whether *any*
rival can credibly threaten the preferred bidder — is governed by *δ*, not by
*c*. Predicted signature: participation rises, competition intensity unchanged.
This is a heuristic conjecture, not a formally derived comparative static: the
model's primitives do not pin down the single-offer incidence as a function of
*(c, δ)* without solving the full entry game, and we do not solve it. The
prediction states the direction the primitives point, and the data are asked
whether that direction is visible.

**H2: participation dividend.** The SME share of entrants rises with the cost reduction: the intensive-margin response ∂(SME share)/∂θ > 0. Predicted
signature: SME tender share increases with digital depth. This, too, is a
heuristic conjecture rather than a derived comparative static: it follows from
the entry condition if SME baseline entry costs exceed those of large firms
and the reform reduces both proportionally, but the model does not derive the
magnitude, and the sign is what we take to the data.

**H3: strategic avoidance.** Compliance with the supra-threshold regime is
itself costly (procedure formality, deadlines, electronic submission). A
buyer whose contract value is near the threshold compares the procurement cost
of the two regimes; when the compliance cost exceeds the option value of the
EU-wide procedure, the buyer splits the contract or shaves the estimate to stay
below the line. Predicted signature: excess contract density just below the
threshold.

The model is deliberately minimal — it is a lens for the estimates, not a
structural claim — but each prediction is falsifiable, and each maps to one of
the three findings in Section 6. In particular, H1 is what a theory that treats
transparency as sufficient would reject: it predicts that lowering entry costs
alone moves competition, and our estimates say it does not.

*A note on what this model is for.* The framework above is a heuristic model,
not a structural one. Its purpose is to generate falsifiable predictions —
participation rises, competition intensity does not, avoidance appears at the
margin — not to estimate parameters. We neither calibrate *δ*, *c*, or *θ* nor
use the model for counterfactual policy analysis; the identified quantities are
the three design-based estimates reported below. A structural approach would
estimate the entry-cost distribution and buyer preference jointly from bid
data, but TED does not publish bid-level data, and the exercise would trade
design-based credibility for parametric assumptions. Keeping the heuristic
model and the designs separate is deliberate: theory supplies the signs, the
three designs measure the magnitudes.

---

## 5. Empirical Strategy: Three Designs, One Question

### 5.1 Main strategy: the legal threshold as a sharp discontinuity (v6.0)

The main design is a sharp regression discontinuity at the procurement
threshold. Let *r* = log(*v*) − log(*τ*_{type,year}) be the log distance of the
contract's awarded value *v* to its applicable threshold *τ*, and let
*above* = 1{*v* ≥ *τ*}. We estimate, locally around the cutoff:

Y_i = α + τ · above_i + Σ_j β_j r_i^j + Σ_j γ_j (above_i · r_i^j) + X_i'λ + FE + ε_i

with *j* = 1 (linear) or 2 (quadratic), contract controls *X* (contract type),
country × year and contract-type fixed effects, and standard errors clustered
by awarding country (28 clusters). The pre-registered specification added log
awarded value to *X*; Section 7.3 shows it is a monotone transform of the
running variable within cells, and it is excluded from every estimate reported
after Table 2. The main specification uses the ±20%
bandwidth and a linear polynomial; bandwidths of ±10, ±15, and ±25% and the
quadratic are reported as sensitivity analysis. Outcomes are measured at the
contract level. The estimand is the local average effect of the stricter
disclosure regime on contracts visible at the line — precisely the object H1
speaks to.

*The running variable is legally imperfect, and we say so up front.* The
threshold applies to the contract's *estimated* value; our running variable is
built from the *awarded* value, the only value observed for every contract.
When the two diverge — shaved estimates, split lots, renegotiated awards —
treatment is mismeasured, and the mismeasurement is endogenous: it is the
buyers' response to the threshold that drives the wedge between the two
values. The correct frame is therefore not classical measurement error but a
fuzzy RD with endogenous misclassification, and the direction of the bias is
not guaranteed. The estimate is a scaled version of the legally correct jump,
with a scaling factor that depends on the mismeasurement process — itself an
outcome of the behavior under study — so we do not read the main estimate as a
bound in either direction. Two responses follow. First, because the estimate
field is populated for 95.4% of the sample, we can and do run the legally
correct specification on the subsample where the estimate is interpretable;
Section 7.3 reports it. The estimated-value specification produces a
positive point estimate of the same sign as the headline and just below it
(+1.22 against +1.27 pp), with a confidence interval that comfortably includes
zero and a base that is a selected subsample. It
therefore does not establish a statistically robust competitive gain, and it
does not undermine the headline either. The
subsample is the 53% of populated notices where award and estimate are
comparable — 46% of the threshold sample once the value-space window is
applied — so it is a robustness check rather than a clean re-estimate, and we
report its sensitivity to the selection rule. Second, the donut specifications
Section 7.3 address the same contamination from the density side rather than
the measurement side.

#### The main specification: the threshold on the variable the law uses (v7.0)

The discussion above concedes that the awarded value is the wrong running
variable and then treats the fix as a robustness check. That ordering is
backwards, and the reason is visible in the placebo evidence: the
award-value specification produces significant jumps at four of sixteen fake
cutoffs (Section 7.3), which is what a manipulable sorting variable looks like.
The contract-notice data remove the problem at the source. The CN notice
publishes `VALUE_EURO`, the buyer's estimate of the contract value, *before*
bids close; the directive's threshold applies to that estimate, not to the
eventual award; and the estimate cannot be revised once the notice is
dispatched. The CN record also carries `FUTURE_CAN_ID`, which links each notice
to its eventual award notice, so the outcome can be read off the award record
while the running variable is read off the notice record. The matched sample is
4,688,892 notices with a usable estimate — 59% of the 7.97 million contract
notices passing the type, cancellation, and member-state filters, a share that
rises from about a third in 2013 to about two-thirds by 2020 — of which
3,968,395 (84.6%) resolve to an award notice; 339,636 fall inside the ±20%
value-space band around their type- and year-specific threshold, and the
offer-count outcome is usable for 179,065 of those. A country-code mapping
error in the first version of this design silently dropped every Greek notice
(233,744 passing the filters, 230,293 with a usable estimate — 4.9% of the CN
sample), so the design briefly ran on 27 of the 28 member states while the
paper described it as EU-28; Section 6.1 reports the correction, which moves
the single-offer point estimate from +0.49 to −0.67 and changes no verdict.

The specification is otherwise unchanged: country-by-year de-meaning, contract
type dummies, a linear local polynomial, and standard errors clustered on the
28 awarding countries — a count that is now true rather than nominal. Three
diagnostics decide whether the re-specification earns
the headline, and all three pass. **Placebos.** Re-estimating the same
specification at 70, 80, 90, 110, 120, 130, and 140% of the threshold, each with
its own ±20% neighborhood, produces no significant jump at any of the seven fake
cutoffs (smallest p = 0.45), against four significant jumps out of sixteen on the
award-value running variable. **Composition.** Inside ±5% of the line — 88,954
notices — the electronic-auction indicator and GPA coverage differ little
(+0.002 and −0.02), and the number of lots differs by −1.3 on a mean of 35, a
difference carried by Greece, whose near-threshold notices are more often
multi-lot. The tender period differs by −0.40 days, which
a two-sample test flags at p < 0.001 only because the cell is large;
economically it is 1.1% of the 36.9-day mean and it is discussed with the first
stage below. **Density.** The frozen 12-versus-9 construction on this sample
rejects symmetry with a log gap of +0.356, but in the *opposite* direction from
the award-value sample: the below side holds 12,867 notices per bin against
18,363 above, so it is 29.9% *thinner* per bin, not denser. The mechanical
artifact identified in Section 7.1 manufactures a small spurious *excess below*
under perfect symmetry and cannot produce a below-side deficit of this size, so
this rejection is not attributed to the construction. What the below side shows
instead is a slope: bin counts rise from 1,736 at the band's lower edge to
16,274 immediately below the line — publication willingness increasing with
contract size, the visibility-selection story of Section 2.3, not manipulation
at the line. The local tests at the cutoff agree: the bin immediately below
holds 16,274 notices against 19,960 immediately above, a ratio of 0.82 whose
country-clustered bootstrap standard error is 0.15 (p = 0.24), and pooling two
bins on each side gives 0.81 (p = 0.14). Neither rejects. There is therefore no
detectable jump in density at the line, while the below side is visibly sparser
far from the cutoff — a pattern the visibility threat predicts, which qualifies
the continuity assumption rather than certifying it.

**A systematic search for a first stage found none that survives correction.**
Because the reduced form is only interpretable as the consequence of a regime
change if the regime demonstrably changes, we tested every candidate the notice
record offers, in one specification, with a Holm (1979) correction across the
family, applied jointly with the Romano–Wolf (2016) stepdown as a check.
Fifteen candidates: the tender period in days, the electronic-auction indicator,
GPA coverage, the number of lots, the framework-agreement indicator, the
accelerated-procedure indicator, joint procurement, the dynamic-purchasing-system
indicator, the price-criterion weight, the number of offers, and six
procedure-type dummies (open, restricted, negotiated, competitive dialogue,
innovation partnership, and the residual category). Two are nominally
significant: framework agreements are 3.14 percentage points less common above
the line (SE 1.16, p = 0.012), and the innovation-partnership indicator moves
by 0.004 points on a base that is zero to four decimal places on both sides
(p = 0.038). Neither survives correction — their Holm-adjusted p-values across
the fifteen candidates are 0.17 and 0.53. The procedure mix itself barely
moves: open procedures are 97.9% of notices below the line and 96.8% above,
restricted procedures 1.1% against 1.6%, and neither difference is significant.
The honest summary is that the notice record does not contain a variable that
the directive mechanically mandates and that jumps at the cutoff, so the design
cannot show its own first stage.

What the specification cannot deliver is a mechanical first stage, and the
reason is worth stating precisely because an earlier version of this paper got it
wrong. The directive mandates minimum tender periods above the threshold, so the
period should jump at the line. It does not jump up. The raw difference inside
±5% of the cutoff is −0.40 days — statistically detectable in a sample of
88,954 notices but 1.1% of the 36.9-day mean and well inside the estimator's
own standard error — and the local-linear estimates on the cleaned analysis
sample are +0.5 days (SE 38.5, p = 0.991) at ±5%, −32.4 (SE 23.2, p = 0.174)
at ±10%, and −30.7 (SE 23.3, p = 0.198) at ±20%; Table 9 reports the ±20%
figure on the same specification. The two wider windows point the same way:
above the threshold, buyers run procedures with *shorter* application
deadlines, which is what the small shift from open toward restricted and
negotiated procedures would produce. That is a real feature of the regime
rather than a null, but it is not statistically established at any bandwidth,
and it is the opposite of the jump the minimum-period rule predicts. The first
stage is therefore reported as not established — the wider windows point
opposite to the mandated jump, and the narrowest window estimates nothing at
all — and the reduced form is read with that caveat attached. (An earlier
version of this paper reported the field as unpopulated after 2016; that was a
date-parsing defect on our side — TED writes `27-FEB-13` through 2016 and
`05/02/18` from 2017 — and it is recorded here because the corrected field is
what the numbers above rest on.)
Two further limits are stated here rather than buried: the estimate field is
populated for about 59% of notices overall and only 36% in 2013, so the matched
sample is not the full record and the early years are the thinnest part of it;
and the subsample splits are not uniform — Section 7.6 decomposes them.

*The identifying assumption is continuity of potential outcomes, and the
threats to it are declared rather than discovered.* The sharp-RD reading
of the threshold requires that contracts just below and just above the line
would have had the same single-offer incidence in the absence of the regime
change. Two features of TED stand in the way of taking that on faith. The
first is the visibility selection developed in Section 2.3: publication below
the threshold is voluntary or nationally mandated rather than EU-mandated, so
the below-threshold side is selected into observation, and if the publication
decision correlates with competitiveness the continuity assumption fails. This
threat is declared in the frozen pre-registration, together with the
confinement of conclusions to the TED-visible sample that answers it. The
second is the mechanical-sorting channel of the discussion below: the running
variable is the awarded value, an outcome of the tender, so the sorting
variable is not independent of the outcome by construction. The
pre-registration declares the related manipulation threat — buyers may shave
values or split contracts to stay below the line — and assigns the density
test to it; the endogeneity of the sorting variable itself is our
acknowledgment here, not a pre-registered item. Neither threat is
assumed away in this paper. The visibility threat is answered only partially —
by the pre-registered confinement of conclusions to the TED-visible sample and
by balance checks on pre-treatment characteristics — because the unpublished
contracts are unobserved by construction. The sorting threat is answered by the
estimated-value running variable and the donut specifications of Section 7.3,
whose results are reported with this motivation attached.

Two diagnostics are pre-registered and can override the verdict. A McCrary-style
(McCrary, 2008; Cattaneo, Jansson, and Ma, 2020, robust variant)
density test checks for bunching at the cutoff (the H3 prediction and the
manipulation threat simultaneously). Placebo cutoffs at 70, 80, 120, and 130%
of the true threshold calibrate the estimator's noise; Section 7.3 reports
which of the four produced usable estimates on the archived sample and which
could not be executed on it. The decision rule — a
null when the CI spans zero; an "uncertain" verdict with all conclusions
downgraded when the density test rejects symmetry; an estimator-threat flag
when any placebo cutoff rejects — was frozen before any result was
computed. The frozen implementation of the density test does reject here
(Section 7.1), but the audit in that section traces the rejection to an
asymmetric bin construction — twelve bins pooled below the line against
nine above, tested against a 50/50 null — that manufactures an apparent
excess below the line even under perfect symmetry. Corrected tests do not
reject, and we therefore report the headline threshold estimate as a clean
null rather than as the downgraded verdict the frozen rule would assign.
Section 7.1 publishes the frozen output, the defect, and the corrected
numbers together, so the reader can re-derive the conclusion.

#### The running variable may respond to the outcome: a mechanical-bias discussion

A sharper identification threat sits underneath the measurement problem, and it
deserves its own statement. The running variable is the awarded value, and the
awarded value is the *result* of the procurement process: it is the winning bid
of an auction whose competitiveness is the outcome under study. If competition
and awarded prices are linked, the variable used to sort contracts across the
threshold is itself a function of the treatment-side outcome, and the
comparison can produce a discontinuity in the single-offer share without any
regime effect. Three links in that chain are visible in our own data.

*First, single-offer and multi-offer contracts price differently.* A contract
with one offer is a bilateral negotiation as much as an auction; the winner's
price reflects the buyer's outside option rather than rival pressure. The price
evidence of Section 6.5 makes the link concrete: on the subsample where the
estimate field is interpretable, contracts with multiple offers close at a mean
discount of 6.61% to the estimated value, single-offer contracts at 5.95% —
single offers save the buyer about 0.65 points less. Translated into relative
awarded values, that gap implies single-offer awards run roughly 0.7% above
multi-offer awards at the same estimated value.

*Second, a price wedge can re-sort contracts across the line.* If single-offer
awards are systematically dearer, contracts near the threshold are slightly
more likely to land above the line when they attract one offer than when they
attract several — so the above-threshold side would be mechanically enriched in
single-offer contracts even with no regime change. The magnitude of this
channel in our data is calculable and it is small: contract density within ±2%
of the cutoff is about 8,900 contracts per one percent of value, so a 0.7%
price wedge would move on the order of sixty contracts across the line,
shifting each side's single-offer share by less than 0.001 points and the
measured jump by less than a thousandth of a point — three orders of magnitude
below the standard error of the headline estimate. The raw price comparison points the same way and is, if
anything, in the opposite direction: within the ±20% band, median awarded value
is 0.5% *lower* for single-offer contracts (€211,255 against €212,254). What the data can see of the
competition-to-price channel is therefore too weak to account for the point
estimates this paper reports.

*Third, the estimate-side manipulation channel remains open.* The wedge above
is measured on awarded values only. Buyers who shave the *estimated* value —
the H3 response tested in Section 7.1 and not detected there — move the
threshold itself relative to the contract, and if the propensity to shave
correlates with how competitive the tender was expected to be, the sorting is
endogenous through a channel the discount-rate comparison cannot see. This is
why the estimated-value running
variable of Section 7.3 matters: it sorts contracts by a number the buyer sets
before bids arrive, not by the auction's result.

The distinction this section is obliged to draw is the following. The existence
of a mechanical-sorting channel is a structural feature of procurement data,
not a finding about our estimates; the quantifiable part of that channel is
three orders of magnitude too small to drive the results; and a jump in the discount
rate at the cutoff — reported in Section 6.5 — is a diagnostic to be
interpreted, not an identified regime effect and not proof that the design
fails. What the discussion establishes is a direction for the robustness work
rather than a verdict on it: specifications that break the link between the
outcome and the sorting variable (the estimated-value running variable) and
specifications that exclude the threshold neighborhood (the donuts) are the
right responses, and their estimates are reported with that motivation rather
than selected afterwards.

### 5.2 Auxiliary design 1: staggered adoption, group-time ATT (v3.0)

The first auxiliary design exploits the staggered transposition dates. Using
the Callaway–Sant'Anna (2021) group-time ATT with not-yet-treated countries as
controls, we estimate the effect of national transposition on country-year
aggregates built from the same contract record (252 country-year cells). This
design uses timing variation at the national level and is the one exposed to
the well-known heterogeneity problems that Sun and Abraham (2021) and Borusyak,
Jaravel, and Spiess (2024) document; we use it as a corroborating leg, not as the
primary strategy, and we report its pre-trend test.

### 5.3 Auxiliary design 2: contract-level fixed effects (v4.0)

The second auxiliary design pushes the timing variation down to the contract
level: 1.30 million threshold-stable contracts, aggregated into 16,429
country × year × contract-type × CPV2 cells, with cell-level contract
characteristics as controls, WLS weighted by cell contract counts, and standard
errors clustered by country. This design absorbs composition variation that the
country-year aggregates cannot, and it is the design that first surfaced the
participation gradient via dose-response on electronic-offer intensity.
Its estimand, like that of v3.0, is the intention-to-treat effect of
transposing the directive — not the effect of disclosure alone.

### 5.4 Three designs, two independent legs, and what their agreement buys

The estimands differ, and the difference is worth stating in one place. v3.0
and v4.0 estimate the ITT of national transposition on two aggregation levels;
v6.0 estimates the reduced form of crossing the procurement threshold, a
bundle that includes disclosure but is not exhausted by it. They are not three
estimates of one parameter, and their agreement is therefore evidence about a
family of related treatments rather than about a single one. With that said,
the three designs fail for different reasons when they fail. Timing designs
fail through pre-trends and contaminated comparisons; panel designs fail
through composition and weighting; cross-sectional cutoff designs fail through
sorting at the cutoff and differential publication. A single null invites the objection that
something specific to its design broke. Three nulls with different failure
modes — each with its own pre-registered diagnostics, each reported with its
own failures — is the strongest form of robustness available to a null result,
with one qualification we state rather than bury: the timing designs (v3.0 and
v4.0) share the same identifying variation at two aggregation levels, so the
program really offers two independent legs, not three. The
three analyses run independently from separate scripts (`run_v3.py`,
`run_v4.py`, `run_v6.py`), and every intermediate output is archived.

---

## 6. Main Results

### 6.1 The competition effect: a null, with stated limits

**Table 9. Main result: the threshold discontinuity on the legally correct
running variable (v7.0, contract-notice estimate, ±20% value-space band,
linear, country-clustered SEs)**

| Outcome | Estimate | SE | p | 95% CI | n |
|---|---|---|---|---|---|
| Single-offer share (pp) | −0.67 | 1.46 | 0.650 | [−3.66, +2.32] | 179,065 |
| Foreign-winner share (pp) | −1.21 | 0.49 | 0.019 | [−2.21, −0.22] | 280,578 |
| Number of offers (count) | +0.20 | 0.10 | 0.061 | [−0.01, +0.41] | 179,065 |
| Tender period (days) | −30.73 | 23.30 | 0.198 | [−78.54, +17.09] | 339,368 |
| Donut ±1% | +0.30 | 1.86 | 0.872 | [−3.51, +4.12] | 170,284 |
| Donut ±2% | +0.16 | 2.31 | 0.946 | [−4.59, +4.90] | 159,962 |
| Donut ±3% | −1.76 | 2.87 | 0.546 | [−7.65, +4.14] | 149,223 |

*Note:* the running variable is the contract notice's published estimate
(`VALUE_EURO`), which is the variable the directive's threshold legally applies
to and which is fixed before bids close. The outcome is read from the matched
award notice. Specification: country-by-year de-meaning, contract-type dummies,
linear local polynomial, standard errors clustered on the 28 awarding countries,
on the cleaned sample described in Section 7.6. Each outcome is available on its
own subsample (Section 3.1), which is why the n column is not constant; the
offer-count row is a count, not a share, and its +0.20 is 5% of the band's
3.8-offer mean. The
minimum detectable effect at 80% power is about 4.2
percentage points. This table supersedes the version circulated in the eighth
revision round, which ran on 27 member states (below).
**The offer-count row deserves a caveat that its p-value does not carry.**
The offer distribution is strongly right-skewed (median 2, 99th percentile 25,
maximum 293), and the +0.20 estimate does not survive the obvious
robustness checks: winsorizing at the 99th percentile returns −0.01
(p = 0.94), the log(1 + offers) specification returns p = 0.38, and the ±25%
bandwidth flips the sign (−0.02, p = 0.90); the leave-one-country-out estimates
stay positive but only 3 of 28 are significant. We report the row because it is
the continuous counterpart of the headline, and we read it as a fragile
positive signal driven by the upper tail, not as a finding — the headline and
this row agree in what they establish, which is nothing distinguishable from
zero.

The headline is a null, and it is a null with a stated resolution. Table 9
reports it. The point estimate is negative — the direction the policy premise
predicts — but the confidence interval runs from −3.66 to +2.32 points, so the
data are consistent with a competition-increasing effect of up to about 2.3
points and a competition-decreasing effect of up to about 3.7 points, and they
exclude effects larger than roughly 4.2 points in either direction at 80%
power. A negative point estimate that far from significance is not evidence for
the premise; it is the absence of a detectable effect, now leaning the other
way. Three things about this table deserve emphasis. First, the estimate is
computed on the running variable the law uses, so it is not a bound on
anything: it is the reduced-form consequence of crossing the threshold when
the sorting variable is the legally binding one. Second, the design passes the
diagnostics that the award-value version failed — seven placebo cutoffs with no
significant jump, composition balanced on both sides of the line, and no
detectable density discontinuity — so the null is not an artifact of a
manipulable sorting variable in the way the archived estimate may have been.
Third, the null is not equally well supported everywhere in the data: the
donut specifications move the point estimate across a range of 2.1 points and
change its sign, and the subsample splits reported in Section 7.6 are not
uniform. What no specification produces, on either running variable, is a
competitive gain.

**A mapping error silently dropped Greece from the first version of this
design, and correcting it moves the headline.** The archived v7.0 run mapped
TED's two-letter country codes to three-letter codes with a dictionary whose
Greek entry was keyed `GRC` instead of `GR`, so every Greek notice — 233,744
passing the type, cancellation, and member-state filters, 230,293 of them with
a usable estimate, 4.9% of the CN sample — fell through the membership test:
the design silently ran on 27 of the 28 member states while the paper
everywhere described it as EU-28, and every clustered standard error was
computed on 27 clusters. The corrected 28-country run changes the single-offer
estimate from +0.49 (SE 0.91, p = 0.593) to −0.67 (SE 1.46, p = 0.650): the
point estimate flips sign, and both runs are statistically indistinguishable
from zero, so no verdict changes. The flip is traceable rather than mysterious:
Greece's near-threshold notices show lower single-offer incidence above the
line in the later, data-rich years (its year-by-year local jumps are negative
in 2018–19, 2021–23), and dropping them tilted the estimate positive. The
foreign-winner estimate is essentially unmoved (−1.25 to −1.21, still
p = 0.019), and every diagnostic — the seven-cutoff placebo battery, the
composition balance, the density tests, the subsample decomposition — was
re-run on the corrected sample and is the one reported here. The error was
found in the ninth revision round by auditing the country mapping against the
TED code list notice by notice; the matched cache and every downstream file
were rebuilt end to end, and the erroneous run's numbers are retained in this
section's archived text as the record. Two earlier defects of the same family —
the 2013–2017 threshold schedule (Section 7.4) and a control loop that
silently skipped the contract-type dummies (Section 7.6) — are recorded in the
same spirit: the pipeline is part of the paper, and its defects are disclosed
rather than quietly fixed.

**A leave-one-country-out check answers how much of the null rides on any
single member state.** Because the point estimate changed sign when Greece
was added, we re-estimate the headline 28 times, dropping one awarding country
at a time (`run_review9_loo.py`). The single-offer estimates run from −1.30 to
+0.49 points and **not one of the 28 is significant**; dropping Greece returns
+0.49 (p = 0.59) — exactly the archived 27-country figure, which is the
cleanest available confirmation that the old run differed from the corrected
one by Greece alone — and dropping Germany or France returns −0.56 and −1.05.
No single country can turn the null into a result in either direction, so the
sign flip is point-estimate noise rather than a country-driven finding. The
foreign-winner estimate is more robust than the headline: its leave-one-out
range is [−1.50, −0.80] and 27 of the 28 re-estimates remain significant
(dropping France leaves p = 0.059), so that finding does not rest on any one
member state either.

**What the null means depends on a first stage the design cannot show, and we
say which null this is.** The directive does change the procedural regime at
the cutoff (Section 2.1), but the notice record contains no variable that the
directive mechanically mandates and that jumps at the line — fifteen candidates,
none surviving correction (Section 5.1) — so the −0.67 estimate admits two
readings that this design cannot fully separate, and the evidence leans toward
the second. Under reading (a), the regime changes at the cutoff and competition
does not follow: the null is evidence about the reform's inefficacy. Under
reading (b), the regime has no mechanically identifiable change at the cutoff
in anything the data can see, so the null is the absence of an identifiable
treatment: the design cannot say what the regime change *did*, only that
whatever it did left no trace in the outcomes. We lean toward (b) because the
first-stage failure is systematic rather than a power problem: the tender-period
standard error of 23 days is small relative to the 35-day statutory minimum the
rule mandates, so a mechanical jump of the kind the rule implies would have
been detected. The distinction does not change the null's fact — no
specification yields a detectable competitive gain — but it changes the claim's
strength, and the paper's contribution should be read accordingly: not a causal
answer to whether transparency raises competition, but a demonstration that
this threshold design cannot identify the regime it crosses, together with the
reduced-form description of what crossing it is associated with. The policy
relevance survives in a narrower form: if reading (b) is right, the regime's
bite lies in dimensions the notice record does not observe — compliance costs,
audit exposure, procedural burden — which are precisely the channels through
which disclosure theory predicts competition could move, and measuring them
requires data this paper does not have (Section 3.3).

### 6.2 The archived specification on the awarded value (v6.0, superseded by Section 6.1)

Table 2 reports the main discontinuity estimates as they were archived, and
Table 8 reports the same four rows under the corrected threshold schedule of
Section 7.4. All four archived estimates show point
estimates near zero and confidence intervals that comfortably span zero. The
single-offer share — the headline — moves by +0.82 percentage
points (SE 0.68, p = 0.234, 95% CI [−0.56, +2.21]). Figure 1 shows the underlying
binscatter with the two local linear fits: the eye finds no jump, and the
estimator agrees. Section 7.4 explains why those numbers are not the ones to
rely on.

**Table 2. Main results: threshold discontinuity estimates (v6.0, ±20% bandwidth, linear, 326,718 contracts) — archived run, superseded by Table 8**

| Outcome | Estimate | SE | p | 95% CI | Type FE only | Verdict |
|---|---|---|---|---|---|---|
| Single-offer share (pp) | +0.82 | 0.68 | 0.234 | [−0.56, +2.21] | +0.82 (0.245) | Null |
| Log(1 + offers) | −0.32 | 1.79 | 0.858 | [−4.01, +3.36] | −0.34 (0.854) | Null |
| Electronic-offer share (pp) | +0.47 | 0.32 | 0.154 | [−0.19, +1.13] | +0.47 (0.164) | Null |
| Foreign-winner share (pp) | +1.15 | 0.90 | 0.212 | [−0.69, +2.99] | +1.16 (0.213) | Null |

*Note:* v6.0 threshold design, ±20% bandwidth, linear specification, ordinary least
squares with country-clustered standard errors (28 country clusters); the
electronic-offer row drops contracts with no TED notice (n = 136,084). Each row is a
separate regression of the outcome on the threshold indicator, the signed log
distance to threshold, their interaction, and the pre-registered controls (log
awarded value and contract type). The final column re-estimates each row on the same
window, dropping the log awarded value control — a monotone transform of the running
variable within cells — and keeping contract-type fixed effects only; it reports the
estimate with the country-clustered p-value in parentheses (SEs 0.69, 1.83, 0.33, and
0.91). Point estimates move by at most 0.02 points and no verdict changes, so the
log-value control is kept in the pre-registered column for completeness only and is
excluded everywhere else (Section 7.3). The two columns differ only in whether
log awarded value is included: because that variable is nearly collinear with
the running variable within each cell, including it leaves the point estimate
where it was and moves only the standard error — the two columns' standard
errors differ by at most 0.04, and their p-values differ slightly.
**This table is the archived record and is superseded by Table 8.** The
threshold schedule the run used was wrong for 2013–2017 (Section 7.4); the
corrected estimates are larger and the single-offer headline is borderline
rather than null. The archived values are retained here because the frozen
pre-registration's output is part of the record and because Section 7.4's
decomposition is stated against them.

**Table 8. Main results under the statutory thresholds: end-to-end re-run from
the raw contract award notices (v6.0, ±20% bandwidth, linear, 327,636
contracts; Section 7.4)**

| Outcome | Estimate | SE | p | 95% CI | No controls | Verdict |
|---|---|---|---|---|---|---|
| Single-offer share (pp) | +1.27 | 0.71 | 0.085 | [−0.19, +2.72] | +1.36 (0.047) | Borderline |
| Log(1 + offers) | −1.89 | 1.49 | 0.216 | [−4.96, +1.17] | −2.11 (0.099) | Null |
| Electronic-offer share (pp) | +0.38 | 0.30 | 0.212 | [−0.23, +1.00] | +0.39 (0.194) | Null |
| Foreign-winner share (pp) | +1.22 | 0.90 | 0.185 | [−0.62, +3.06] | +1.13 (0.163) | Null |

*Note:* the specification of Table 2, re-executed end to end on the eleven
annual TED CAN extracts downloaded from the EU Open Data Portal, with the
statutory thresholds of Table 1 and the band rebuilt around them; the sample is
327,636 contracts (150,783 above, 176,853 below), against the archived 326,718.
The electronic-offer row drops contracts with no TED notice (n = 136,288).
Run with the *erroneous* thresholds the same pipeline reproduces Table 2 to the
last digit, so the differences below are attributable to the cutoffs and to
nothing else. The single-offer headline is +1.27 pp with the pre-registered
controls (p = 0.085) and +1.36 with no controls at all (p = 0.047) — the move
is contract type's doing, not the log-value control's, which is a deterministic
function of the running variable within cells (Section 7.3): the
null survives the correction in the pre-registered configuration and not in the
reduced one. Every estimate keeps the sign of its archived counterpart, and the
first stage — the electronic-offer share — remains insignificant, so the
threshold design still does not demonstrate that the supra-threshold bundle
binds on electronic submission.

Three limits on what this table supports should be stated with it. First, the
estimate is not precise in any absolute sense: with SE 0.71, the minimum
detectable effect at 80% power is about 2.0 percentage points, so effects
smaller than roughly 2 points in either direction are not excluded, and the
interval runs from −0.19 to +2.72. Second, the point estimates are positive
and, in the single-offer row, at the edge of conventional significance rather
than comfortably inside it: a positive point estimate on
this outcome is the direction the policy premise does not predict, but an
interval that spans zero is evidence about neither direction, and we do not
read the sign as evidence against the premise any more than we would read a
negative point estimate as evidence for it. The same holds for the two panel
designs in Table 3. Third, the estimate is a full-band average that includes
the threshold
neighborhood, where sorting on the running variable would bind most strongly
and where the density test of Section 7.1 looks for — and does not find — a
manipulation signature. Section 7.3 reports what happens when that
neighborhood is excluded (donut specifications) and when the legally correct
running variable is used: the donut estimates move to +1.65 to +2.13
percentage points under the statutory schedule (+1.4 to +2.8 on the archived
one) and the estimated-value specification to +0.82 to +1.22, significant under
a linear specification and not under a quadratic one. The first stage deserves a matching caveat: the electronic-offer share jumps by
only +0.38 points (p = 0.212) at the cutoff on the statutory schedule (+0.47,
p = 0.154 on the archived one), so the threshold design does not
itself demonstrate that the supra-threshold procedural bundle binds on
electronic submission — the strong first stage (+38.2 points) belongs to the
transposition designs, not this one. What would have counted as evidence
against the null: a jump of two percentage points or more with the theoretical
sign, a density asymmetry that survives the construction audit of
Section 7.1, or a significant jump at
the eighty-percent placebo cutoff. None occurred, and each threshold was fixed
in advance.

**Figure 1.** Competition at the legal threshold on the running variable the law
uses (v7.0): single-offer share by log distance from the threshold, where
distance is measured on the contract notice's published estimate rather than on
the awarded value. Navy dots are 0.02-width bin means; the dark segments are
local linear fits on each side (±0.15 window); the vertical line is the legal
threshold. No step is visible at the line, and the estimated jump is **−0.67 pp
(95% CI [−3.66, +2.32])** with contract-type controls — the specification of
Table 9. The bins are noisy because the band holds 179,065 notices with a usable
award match, and the eye finding no jump is the point of the figure.

### 6.3 Three designs, two legs

Table 3 and Figure 2 assemble the designs. The two transposition point estimates
are positive — +3.37 and +1.39 percentage points on the single-offer share — the
current main design's is negative (−0.67), and the archived threshold row's is
positive (+1.27); none is distinguishable from zero under its primary interval.
A point estimate of either sign, with an interval that spans zero, carries no
evidential weight in that direction; what the table
shows is the absence of a detectable gain, not evidence of a loss.
The intervals differ in what they admit: the country-year design allows effects
up to +7.14 points under its primary interval (+6.65 under the country-level
cluster bootstrap reported in the note to Table 3), the contract-level panel up
to +3.40, the main threshold design
between −3.66 and +2.32, and the archived threshold row
up to +2.72, so the designs bound the possible gain differently rather than
excluding a common range. Two of the transposition designs share the same identifying
variation — the staggered transposition dates — and differ only in aggregation
level; they are best read as one leg at two resolutions, with only the
threshold designs exploiting variation the others do not. What the table shows is
that no design, at any resolution, finds a competitive gain; it does not show
that independent designs exclude the same range of effects, and we do
not claim that.

**Table 3. Three designs, two legs: effect of the respective treatment on
single-offer share (percentage points). v3.0 and v4.0: ITT of transposition;
v7.0: reduced form of crossing the threshold on the legally correct running
variable; v6.0: the archived threshold specification, superseded as the
headline by v7.0 and retained for the record** 
| Design | Identifying variation | Sample | Estimate | 95% CI |
|---|---|---|---|---|
| v7.0 threshold RD (main) | Legal threshold, notice estimate | 179,065 contracts | −0.67 | [−3.66, +2.32] |
| v3.0 group-time ATT | National transposition dates | 252 country-year cells | +3.37 | [−0.32, +7.14] |
| v4.0 contract-level TWFE | Same dates, contract-level panel | 16,429 cells (1.30M contracts) | +1.39 | [−0.62, +3.40] |
| v6.0 threshold RD (archived) | Legal threshold, awarded value | 327,636 contracts | +1.27 | [−0.19, +2.72] |

*Note:* **the two transposition rows are auxiliary, not causal, and are
reported for their sign rather than their level**: the v3.0 interval is
method-dependent — four defensible intervals, two spanning zero and two not —
and the v4.0 single-offer event study carries significant pre-trends, so
neither row supports a causal claim on its own; the v4.0 foreign-winner event
study (clean, precise null) is the only timing-design estimate we would
credit, and it corroborates the threshold designs' absence of a competitive
gain rather than adding an independent leg. The v6.0 row carries the re-run values of Section 7.4 (statutory
thresholds, n = 327,636); the archived run on the erroneous 2013–2017 schedule
reported +0.82 pp with [−0.56, +2.21] on 326,718 contracts, and is superseded.
**The v3.0 row's interval is method-dependent, and the primary inference is
declared here.** The archived output (`results_v3.json`) reported
[−3.69, +7.12], which is not a sampling confidence interval: the v3.0 script
(`estimators_v2.cell_ci`) computed the 2.5th and 97.5th percentiles of the
eight post-period (g,t) cell ATTs — a between-cell dispersion range that its
own documentation labels "conservative" — and it is not centered on the point
estimate because the point estimate (+3.37 pp) weights the cells by treated
country counts while the cell range uses them unweighted (unweighted cell mean
+2.42 pp; cells span −4.11 to +7.15). Three sampling intervals are available
for the same eight cells, and the primary one is the design's native
inference: an influence function of the group-time ATT decomposed by country
across the cells, with a Rademacher multiplier bootstrap clustered on the 28
awarding countries, giving **[−0.32, +7.14] (SE 1.90 pp)** — the interval shown
in the table. It is the design's own estimator-based inference, it clusters at
the country level at which treatment is assigned (the clustering level this
program's pre-registration names), and, unlike the country-level cluster
bootstrap, it discards no replicates. The two sensitivity intervals disagree
with it about whether zero is inside. A cell-level t-interval over the same
eight cells — cells as the unit of observation, weights proportional to treated
country counts, critical value t(0.975, 7) — gives [−1.34, +8.09] (SE 1.99 pp);
it treats the cells as independent and thereby ignores both within-cell
sampling error and the covariance between cells that share countries. A
country-level cluster bootstrap that resamples the 28 countries with
replacement and rebuilds the cells gives **[+0.28, +6.65] (SE 1.65 pp)**, which
does not span zero; 551 of its 2,000 resamples were discarded because the
resampled country set did not contain all eight cells, and that fragility is
part of why it is not the primary. The point estimate is +3.37 pp, which is
the sign the policy premise excludes; whether it is distinguishable from zero
depends on which of these intervals one credits, and the honest statement is
that the v3.0 row is at best marginally distinguishable from zero and that its
interval is method-dependent. The v4.0 and v6.0 intervals
are conventional cluster-robust Wald intervals centered on their point
estimates.

**Figure 2.** Primary estimates and 95% intervals for the competition measures.
The first two rows are the main design (v7.0, the threshold discontinuity on the
notice estimate): the single-offer share, −0.67 pp [−3.66, +2.32], and the
foreign-winner share, −1.21 pp [−2.21, −0.22], the one interval that excludes
zero. The third and fourth rows are the transposition designs, whose identifying
variation no buyer controls: the contract-level panel +1.39 [−0.62, +3.40] and
the country-year ATT +3.37 [−0.32, +7.14], the latter on the design's native
multiplier-bootstrap interval, one of whose sensitivity intervals does exclude
zero (Table 3 note). The transposition event study on the single-offer share is
not plotted because it carries significant pre-trends (Section 7.5). Every
single-offer interval spans zero.

The staggered-adoption design also passes its pre-trend test (weighted mean
pre-ATT 0.002, p = 0.68), and its first stage is strong: the electronic-offer
share rises by 38.2 percentage points post-transposition, building gradually
from +5 points at adoption to +86 points six years out. The reform was
implemented; procurement really did digitalize; competition did not follow.

One interval in Table 3 deserves a note before the numbers are read, because
the three available intervals for the v3.0 row do not agree about the answer,
and the table now carries one of them as the primary. The archived v3.0
run reported [−3.69, +7.12], the 2.5th–97.5th percentile range of its eight
cell-level ATTs, which is a between-cell dispersion range rather than a
sampling interval. A cell-level t-interval over the same cells gives
[−1.34, +8.09]. The design's native inference — an influence function
decomposed by country across the cells with a multiplier bootstrap clustered on
countries — gives [−0.32, +7.14], the interval the table reports, and a
country-level cluster bootstrap gives [+0.28, +6.65], which excludes zero. The
point estimate is +3.37 pp, the sign the premise excludes, and the reading
below is stated so that it does not
depend on which interval is credited: the v3.0 design is at best marginally
distinguishable from zero, its interval is method-dependent, and it is the
weakest row in the table as well as the least informative, because the design
behind it identifies a bundle rather than a mechanism (Section 5.4).

### 6.4 The participation gradient: strong across countries, modest within them

The mechanism picture is the mirror image of the headline, though the evidence
behind it is of unequal strength. Table 4 assembles three layers on
participation.

**Table 4. The participation gradient: SME tender share and digital depth** 
| Specification | Estimate | SE | p | 95% CI |
|---|---|---|---|---|
| v4.0 TWFE, binary treatment (treated × post) | +7.44 pp | 4.30 | 0.095 | [−1.39, +16.27] |
| v4.0 dose-response on electronic-offer intensity | +33.42 pp | 7.87 | 0.0002 | [+17.25, +49.59] |
| Decile gradient (descriptive, Figure 5) | 8.7% → 54.6% | — | — | — |

The dose-response coefficient is the cleanest statement: a one-unit increase in
country-year electronic-offer intensity — the full range from paper to digital —
is associated with a 33.42-percentage-point increase in the SME share of tenders.
Figure 5 plots the raw decile gradient: monotone, from 8.7% of tenders in the
lowest electronic-offer decile to 54.6% in the highest. The gradient is large
and it is the same gradient a confound would produce: countries that digitized
early differ from late digitizers in income, administrative capacity, and
market structure, and nothing in the cross-section holds those fixed. The word "associated" is
deliberate: the dose-response uses variation in digital depth across countries
and years — country-year fixed effects would absorb the regressor — so it
cannot rule out confounding by national institutions, market structure, or
common trends. The binary treatment, which uses within-country transposition
timing, is the cleaner estimate and is much weaker (+7.44 pp, SE 4.30,
p = 0.095). We read the two as bracketing the participation effect rather than
pinning it down: a strong cross-sectional gradient, a modest within-country
response, and a decile pattern that is descriptive throughout.

**A reporting-artifact caveat belongs with the gradient, not after it.** The
outcome is the SME share of tenders, built from the notice field
`NUMBER_TENDERS_SME`, and that field is a reported administrative quantity
rather than a measured one. Three features of the reporting process can move
the measured gradient without any change in who actually bids. First, missing
rates differ across countries and years: the field is not uniformly populated,
and the cell-level aggregation conditions on populated notices, so a
country whose authorities complete the field diligently contributes a
different mixture of contracts than one that leaves it sparse. Second,
countries with more developed e-procurement systems — the same countries with
high electronic-offer intensity — tend to have the more complete and more
standardized reporting, so digital depth and reporting quality are correlated
by construction. Third, the definition of an SME tender can follow national
rules that differ in what counts as an SME, and the field records the buyer's
classification rather than an independent verification. The observed gradient
may therefore contain real participation differences and reporting-behavior
differences in unknown proportions. The within-country estimate is partly
immune to the first two channels — the same authority reports before and after
transposition — which is one more reason to read the two estimates together.
What would settle the question is a missing-data robustness exercise that
re-runs the dose-response on samples restricted to high-completeness
country-years; that exercise requires the country-year missingness statistics,
which are not part of the archived analysis panels, so it is listed in the
verification schedule rather than reported here, and until it is run the
+33.42 pp figure should be read as an upper-bound-flavored association rather
than a participation effect.

**Figure 5.** Participation responds: SME share of tenders (line with markers at decile means) by electronic-offer share decile (1.30M contracts), rising monotonically from 8.7% to 54.6%.

### 6.5 The price margin: what the estimate fields can and cannot say

The welfare question is whether weak competition costs the buyer money. The
notice-level estimate field is populated for 95.4% of the threshold sample, so
the question is now executable in principle — but the field records the
procedure-level (multi-lot) estimate, not the single contract's estimate, and
the two diverge wildly: among supply and service contracts near the threshold,
the mean award value is €213,582 against a mean procedure estimate of €8.5
million (median €299,719). We therefore confine the analysis to the 166,003
contracts (53.1% of
the populated sample) where the ratio of award value to estimated value lies in
[0.5, 2.0] — notices where the estimate is interpretable as the contract's own
estimate — and we read the results with that selection in mind.

On this subsample, the discount rate (estimated value minus awarded value,
divided by estimated value) averages 6.61% for contracts with multiple offers
and 5.95% for single-offer contracts. Single offers, in other words, save the
buyer about 0.65 percentage points less — economically small, and consistent
in sign with the welfare channel, but far from the decisive gap a strong
version of the theory would predict.

A threshold discontinuity in the discount rate is estimated at −1.55
percentage points (SE 0.77, p = 0.054, 95% CI [−3.14, +0.03], n = 166,003,
country-clustered): contracts just above the threshold — inside the EU-wide regime — sell at
smaller discounts to their estimates than contracts just below it. The archived
version of this estimate reported −1.76 pp with classical standard errors
(SE 0.15, p < 0.0001, CI [−2.05, −1.48], n = 158,226); the classical errors
understate the sampling uncertainty by roughly a factor of five, because the
contracts cluster by country and the discount rate is a country-level reporting
practice as much as a price outcome, and the clustered version is the one to
read. Three
readings of that number are possible, and the data cannot choose among them
cleanly. The first is a regime effect — the stricter procedure really does
narrow the buyer's room to negotiate — and we do not adopt it, for reasons
given below. The second is sample selection: the subsample is selected on the
award-to-estimate ratio itself, the estimate field behaves differently across
the two sides of the line, and composition differences beyond type and value
are not absorbed. The third is the one that matters most for identification,
and it is a diagnostic rather than a verdict: the gap is direct evidence that
the relationship between the estimated value, the awarded value, and the
outcome differs across the line. Because the awarded value is the running
variable of the main design, a discontinuity in how awarded values relate to
estimates is exactly the pattern that would let the awarded value encode
outcome-related sorting (Section 5.1). It does not show that the design fails —
the mechanical channel quantifiable from these data is an order of magnitude
too small (Section 5.1) — but it shows that the awarded value is not a neutral
sorting variable, and it is one reason the estimated-value running variable of
Section 7.3 is reported alongside the headline rather than buried in a
footnote. What the analysis establishes is narrower than any of the three
readings: the price data contain no welfare dividend from disclosure large
enough to rescue a competition story that the offer counts have already
refuted, and they warn that the main design's sorting variable is itself an
outcome of the process under study.

---

## 7. Mechanisms, Heterogeneity, and Robustness

### 7.1 Strategic avoidance: the density test at the threshold

H3 predicts excess contract density just below the threshold — buyers
splitting contracts or shaving estimates to stay in the domestic regime.
The pre-registration assigns a McCrary-style density test to this
prediction and freezes a decision rule around it: if the test rejects
symmetry, the verdict becomes "uncertain" and all conclusions are
downgraded. This section reports what the frozen test produces, an audit
of that test, and what survives the audit. The short answer is that the
H3 signature is not detectable in these data, and the frozen test's
rejection does not survive scrutiny.

**The frozen output.** The frozen implementation bins the log distance
*r* into 0.02-wide bins, sums the contracts in the bins at or below −1
(twelve bins, bin centres from −0.23 to −0.01, the outermost partially
filled) and the bins at or above +1 (nine bins, bin centres from +0.03 to
+0.19, the outermost partially filled), and compares the two per-bin
means. The bin immediately above the cutoff, [0, 0.02), belongs to
neither side. We define the log density gap as log(mean bin count above)
− log(mean bin count below), so a negative value is an excess *below* the
line. The result is a gap of −0.0157 — the below side holds 1.6% more per
bin than the above side, on the archived (erroneous) schedule; on the statutory
schedule the frozen construction returns −0.0114, a 1.1% excess — and a binomial test on the pooled counts
rejects a 50/50 split at p < 0.0001. We report this output as the frozen
record produces it, because the pre-registration prohibits concealing an
unfavorable diagnostic.

**Why that output is an artifact.** Three features of the construction
manufacture the result. First, the slot counts are asymmetric: twelve
bins on the left against nine on the right, because the bin immediately
above the cutoff is dropped while the bin immediately below it is kept,
and both outermost bins are partially filled by the sample window.
Second, the binomial null of 0.5 ignores that asymmetry: under equal
per-bin density the left side should hold 12/21 = 57.1% of the mass, not
50%, and it holds 57.4% (57.5% on the archived schedule). Third, the binomial sampling assumption is
violated: bin counts are dispersed roughly sixteen times more than
Poisson sampling predicts (standard deviation about 2,000 against about
130), because contracts cluster within 917 country-year-type cells. The
decisive check is arithmetic. Under a density that is exactly symmetric
bin by bin, the construction's own slot asymmetry produces an expected
log gap of −0.031 — a spurious 3.1% "excess below", unchanged by the threshold
correction because it depends only on the bin geometry — because the left
mean divides eleven full bins plus a 15.7%-filled edge bin by twelve,
while the right mean divides eight full bins plus a 11.6%-filled edge
bin by nine. The observed gap is half that mechanical value on the archived
schedule (−0.0157) and a little over a third of it on the statutory one
(−0.0114): the
data show less "excess below" than the construction produces under
perfect symmetry. Removing the mechanical component leaves the below side
holding about 1.9% *less* per bin than a perfectly symmetric density
would generate — while in raw terms it still holds about 1.1% *more* per
bin than the above side. Neither difference is distinguishable from zero
under the corrected tests below.

**Corrected tests.** Re-running the comparison with symmetric windows
and valid inference removes the asymmetry in every variant. Pooling only
fully filled bins — eleven below, nine above — the mean bin holds 15,867
contracts below the line and 16,557 above it, a 4.4% excess on the
*above* side that a bin-level comparison cannot distinguish from noise
(t = 0.88, p = 0.39). The bin immediately below the cutoff holds 16,011
contracts; the bin immediately above holds 19,641, a figure inflated by
the mass point described in the next paragraph. A McCrary-style
local-linear extrapolation of log counts to the cutoff from each side
gives a below-to-above ratio of 1.007. The binomial test, against the
correct 12/21 null and with standard errors from a cluster bootstrap
over country-year-type cells, returns p = 0.29; the log gap against its
mechanical null value returns p = 0.076. No corrected implementation
rejects symmetry, and every point estimate favors the above side. The
predicted H3 signature — a visible excess in the bins just below the
line — is not in these data. **These are the end-to-end re-run figures on
the statutory thresholds (Section 7.4); the archived run on the erroneous
2013–2017 schedule returned 15,818 below against 16,518 above
(t = 0.77, p = 0.45), bin counts of 15,085 and 20,296, a McCrary ratio of
0.985, and p = 0.17 against the mechanical null. Nothing in the audit
turns on which schedule is used; if anything the statutory cutoffs make
the artifact case slightly stronger, because the observed gap shrinks
while the mechanical null does not move.**

**A mass point at the line, not below it.** The one sharp feature of the
histogram sits exactly at the cutoff: 5,314 contracts, 1.6% of the
near-threshold sample, report award values equal to the threshold to
within a rounding hair, 5,121 of them equal to the euro. The feature is a
reporting convention rather than avoidance: 74% of these contracts are
German, and for 90.1% of them the award value equals the notice's
estimated value, against 38.4% in the full sample — the signature of a
national feed copying the estimate into the award field. These contracts
sit *at* the line, where the supra-threshold regime already applies, not
below it; they inflate the first bin above the cutoff and, if anything,
make the above side look denser than the smooth part of the distribution
warrants. Removing them leaves the symmetric comparison at 15,857 below
against 15,967 above — a 0.7% above-side difference, still nowhere near
significant. **The archived run reported this mass point as 4,659
contracts (4,460 exact, 69% German, 89.8% award-equals-estimate) because
it was measured at the erroneous threshold values; the end-to-end re-run
figure of 5,314 (5,121 exact, 1.62%, 73.8% German, 90.1%) is the one to
read.**

**The bunching estimator cannot be rescued by a counterfactual.** A
Chetty-style (Saez, 2010; Chetty, Friedman, Olsen, and Pistaferri, 2011)
estimator fits a polynomial counterfactual to the log
density outside the bunching zone and reads the excess in the zone off
the fit. Three problems make the exercise uninformative here. The
bunching zone is a single 0.02-wide bin, so the counterfactual must be
extrapolated into it rather than interpolated. The surrounding bin
counts are noisy enough that the extrapolation is specification-driven.
The estimator has been rebuilt from the raw extracts on the statutory
cutoffs — a post hoc exercise, since the frozen pre-registration contains
no bunching estimator — crossing five windows (±0.08 to ±0.25, the ±0.30
row duplicating the ±0.25 row because the histogram itself spans ±0.23)
with three polynomial orders. Its fifteen distinct estimates run from
−5,727 to +3,287 contracts and flip sign seven times. And
the archived record carries three mutually inconsistent counts — 3,262
contracts under the specification this paper previously preferred, 2,257
under a standalone script, and 11,062 (bootstrap interval [10,818, 11,353])
under a reproduction stored in the same robustness file — and only the first
of the three can be traced to a script in the repository. Rebuilt from the raw
extracts on the statutory cutoffs, the archived specification returns **3,287
contracts**, which reproduces the 3,262 to within the threshold correction, so
that one figure is reproducible; the other two are not, and a count that cannot
be traced to code cannot be reported as a result. A
model-free calibration we previously reported — 1.6% of the 176,274
contracts below the line, about 2,800 — is circular: it multiplies the
artifact gap by the below-line count and then reads the product as
independent support. We withdraw it, and with it the euro conversions
built on these counts. The honest statement is that these data cannot
say how many contracts, if any, are steered below the line. **The
specification grid is what forbids a count.** Across local windows (±0.08 to
±0.25) and polynomial orders three to seven, the rebuilt estimator returns
anything from −5,727 to +3,287 contracts and flips sign seven times over the
fifteen distinct specifications: a cubic
over ±0.20 gives −3,140, a quintic over ±0.15 gives −414, a seventh-order fit
over ±0.25 gives −3,023, and the quintic over the full window gives the
preferred +3,287. The bootstrap interval around that preferred figure,
[2,132, 4,592] over 1,000 cluster replications, is tight and never crosses
zero — which is precisely the problem: the sampling noise is small and the
specification noise is enormous, so the interval measures the wrong thing. A
point estimate that is stable under one polynomial and negative under its
neighbours is a statement about the polynomial, not about the data.**

**What the decision rule makes of this.** The frozen rule downgrades
the verdict when the density test rejects; the frozen implementation
rejects. But the rejection is a property of the construction, not of the
data: the same construction produces a larger apparent rejection under
perfect symmetry than the data produce. A downgrade triggered by a
demonstrable artifact would attach a verdict to a bug rather than to the
evidence, and reporting the small-but-real manipulation that artifact
appears to show would be worse. We therefore report the headline
threshold estimate without a downgrade — the corrected tests do not reject
symmetry, and the point estimates that exist favor the above side —
while publishing the frozen output, the defect, and every corrected
number above, so that a reader who disagrees can re-derive the
conclusion from the public audit script. The pre-registration's
prohibition on concealing an unfavorable density test is honored in both
directions: the unfavorable output is on the record, and so is the
reason it does not carry the weight the rule assigns it.

**What survives.** The second pre-registered rule — the confinement of
conclusions to the TED-visible sample — was never conditional on the
density test. It answers a structural threat declared in the
pre-registration: publication below the line is voluntary or nationally
mandated, so the domestic segment is invisible to every
disclosure-based monitor, including this one. That threat stands whether
or not manipulation is detected, and the estimates in this paper
continue to describe the TED-visible sample only. The donut
specifications of Section 7.3 likewise stand on their own motivation:
excluding the threshold neighborhood is prudent because that
neighborhood is where sorting on the running variable would bind, not
because manipulation has been detected there. What the density audit does
*not* establish is that the design as a whole is clean: the same section's
placebo battery, once executable, trips the pre-registered alarm at the
130% cutoff (Section 7.3), and a clean density test is one diagnostic, not
a certificate.

**Figure 3.** Notice density at the threshold on the v7.0 running variable:
histogram of contract notices by log distance from the threshold, 0.02-width
bins, distance measured on the published estimate. The frozen 12-versus-9
construction on this sample rejects symmetry with a log gap of +0.356 — but in
the *opposite* direction from the award-value sample of Section 7.1: the below
side holds 12,867 notices per bin against 18,363 above, so it is 29.9% thinner
per bin, not denser, and the construction's mechanical artifact (a spurious
excess *below* under perfect symmetry) cannot produce a deficit of that size.
What the below side shows instead is a slope: counts rise from 1,736 at the
band's lower edge to 16,274 immediately below the line — publication willingness
increasing with contract size, the visibility-selection story of Section 2.3.
The local tests at the line find no jump: the bin immediately below holds
16,274 notices against 19,960 immediately above, a ratio of 0.82 whose
country-clustered bootstrap standard error is 0.15 (p = 0.24), and the two-bin
version gives 0.81 (p = 0.14). The hatched red segment marks a mass point *at*
the line itself: 2,823 notices report estimated values within 0.01% of the
threshold (2,617 of them equal to the threshold after rounding to the euro).
The feature is much weaker than its award-value counterpart — only 21.7% of
these notices are German, against 73.8% on the award side, and for 10.7% of
them the award value equals the estimate, against 3.4% of the full sample — so
the national-feed explanation of Section 7.1 does not transfer, and the mass
point is read as a milder rounding-to-threshold convention rather than as
avoidance. The legend counts bin 0 on the above side; the frozen test excludes
it from both sides, which is one of the asymmetries the audit of Section 7.1
reports.

### 7.2 Heterogeneity: the null is not an average over subgroups

If the null were an average over offsetting country or category effects, the
aggregate would be misleading. Table 5 splits the panel-design sample by
contract type and by national corruption perception (above/below the sample
median CPI). No subgroup shows a detectable effect on the single-offer share.
The point estimates are small throughout — four positive, and works contracts
at −0.03 pp (SE 1.44) — and the low-CPI half, the half where a transparency
channel should matter most, is no different from the high-CPI half.

**Table 5. Heterogeneity of the disclosure effect on single-offer share (v4.0
TWFE specification, by subgroup)**
| Subgroup | Estimate (pp) | SE | p | 95% CI | n |
|---|---|---|---|---|---|
| Supply contracts | +1.46 | 0.85 | 0.099 | [−0.29, +3.21] | 7,753 |
| Service contracts | +0.81 | 1.90 | 0.673 | [−3.08, +4.70] | 7,661 |
| Works contracts | −0.03 | 1.44 | 0.984 | [−2.98, +2.92] | 814 |
| High CPI (cleaner) | +0.79 | 1.21 | 0.522 | [−1.80, +3.39] | 7,775 |
| Low CPI (more corrupt) | +1.29 | 1.26 | 0.323 | [−1.40, +3.97] | 8,453 |
| Full sample (baseline) | +1.39 | 0.98 | 0.168 | [−0.62, +3.40] | 16,228 |

We read this as evidence against the "hidden heterogeneity" defense of the
theory: whatever the disclosure channel does, it does not do it visibly more in
one contract type or one corruption environment than another, at least along
the splits these data support.

A further split was meant to replace corruption perception with digital
depth, and neither the archived version nor its re-run survives scrutiny,
so no digital-depth heterogeneity claim is made. The archived version — a
"high" half of 80,002 contracts at −0.06 pp (SE 0.62, p = 0.917) against a
"low" half of 229,890 at +0.76 pp (SE 0.37, p = 0.039) — cannot be
reproduced from any script in the repository, and the contract-level
electronic-offer share it appears to use has a median of exactly 1.0, which
would make its "high" half a 198-contract data anomaly (198 notices whose
reported electronic-offer count exceeds their total offer count) rather than
a subgroup. It is withdrawn rather than corrected, and the nominally
significant low-digital figure it carried is withdrawn with it — it did not
survive a multiple-testing correction even on its own terms. The re-run's
version hits the same anomaly from the other side: with the contract-level
median at exactly 1.0, 136,090 of the 136,288 contracts with an observed
electronic-offer share fall in the "low" half and the "high" half holds the
198 anomalies, so the "low" estimate (+1.23 pp, p = 0.028) is the full-sample
estimate on a slightly reduced sample rather than a subgroup contrast.
Rebuilding the split on the country-median definition the archived note
describes requires the country-level electronic-offer shares, which are not
in the archived contract-level cache; the exercise is listed in Section 8's
verification schedule rather than reported as a result. Until it is run, the
digital-depth heterogeneity question is open, and this paper claims nothing
about whether digitalization changes the policy effect.

### 7.3 Robustness: bandwidth, polynomial order, donut, and the legal running variable

The archived pre-registered specification grid — the v6.0 design under the
statutory thresholds, with the log-value control the frozen plan specified —
spans the same variations. Shrinking the bandwidth to
±10% and widening it to ±25%, and raising the polynomial from linear to
quadratic, moves the point estimate between −0.6 and +0.9 percentage points;
none of these variants reaches significance. The estimates are not centered
tightly on zero: they drift upward with the bandwidth, from −0.2 pp at ±10% to
+0.9 pp at ±25%. That drift is itself informative, and we return to it below.
The current design's own grid is drawn as Figure 4 and reported with it.

The placebo battery is pre-registered at four cutoffs — 70, 80, 120, and 130%
of the true threshold — and it has now been executed, on a ±40% extraction with
each cutoff given its own ±20% neighbourhood. The results are in Table 10, and
one of them trips the pre-registered alarm.

**The archived number was both mismeasured and unexecutable.** The original
v6.0 run reported a single figure: at the 80% cutoff, a jump of −0.0515 on the
single-offer share with p = 0.146. Two things about that record need saying.
First, the archived block does not document its unit, while the sibling `main`
block of the same file stores shares rather than percentage points — its
+0.0082 is this paper's +0.82 points, and its +0.0115 is Table 2's +1.15
points. On that convention the placebo jump is **−5.15 points, not −0.05**, and
we correct it here rather than carry a number that cannot be reconciled with
its own file. Second, the ±20% analysis band makes three of the four cutoffs
unreachable: a cutoff at 70% or 130% of the threshold lies outside the band
entirely, and a cutoff at 80% or 120% lies on its edge. On the archived sample
the four cutoffs have 0, 104, 0, and 0 contracts on their minority side; the
80% "estimate" is therefore a comparison of 104 contracts against 326,614, not
a regression discontinuity, and its standard error near 3.5 points — five
times the main specification's — is what that degeneracy looks like.

**Executed properly, the battery trips the alarm.** Table 10 re-runs all four
cutoffs on the ±40% extraction, each with its own ±20% neighbourhood and the
main specification's controls. Three of the four are unremarkable: −0.62 pp
(p = 0.119) at 70%, +0.16 (p = 0.533) at 80%, and −0.14 (p = 0.802) at 120%.
The fourth is not. **At 130% of the threshold the estimate is −1.14 pp
(SE 0.37, p = 0.005, 95% CI [−1.90, −0.37], n = 232,088), and it survives a
Bonferroni correction for four tests (threshold 0.0125) and a Holm correction
of the five-test family that includes the true cutoff (adjusted p = 0.025).**
The pre-registered
decision rule states that any significant placebo marks the estimator as
threatened; by that rule, this design is threatened. One implementation note
belongs with these numbers: the cutoffs are rebuilt from the statutory
threshold table directly, because recovering the threshold from the stored log
distance by exponentiation misclassifies contracts whose value equals the
threshold exactly — 4,246 contracts in the ±20% band — and a cutoff placed at
1.30τ has its own round-number pile (1.3 × €200,000 = €260,000 and its
equivalents) that the same recovery would corrupt.

**The decisive diagnostic: a cutoff profile, not a single point.** A
significant placebo at one cutoff is read two ways in the literature — a
smooth gradient in the running variable picked up as a level shift, or a data
feature at that point — and the design's own battery cannot distinguish them.
The test that can is a profile: re-estimate the same specification at cutoffs
walking from 0.70τ to 1.45τ, each with its own ±20% neighbourhood. If the
estimates drift smoothly with the cutoff, the linear specification is picking
up curvature; if a single point stands out, the feature is local. Table 11
reports the profile. It supports neither clean reading. The linear estimates
oscillate across the whole range — −0.62, +0.85, +0.16, −1.02, −1.13, +0.26,
+1.27, +1.25, +0.24, −0.33, −0.14, −1.25, −1.14, −0.90 — inside a band of
roughly ±1.3 points with no monotone drift (the fitted slope over the
complete-band cutoffs is +0.82 pp per cutoff, and it is carried entirely by
the 1.00–1.05 bump, which is the headline itself). The 1.30τ point sits 1.7
residual standard deviations below the local trend of its neighbours: far
enough to be significant, close enough to the profile's own scatter that it
is not an isolated spike. The 1.25τ (−1.25, p = 0.013) and 1.35τ (−0.90)
points are negative as well, so what the battery catches is a neighbourhood,
not a point — and all three of those cutoffs have their above side truncated
by the extraction boundary at 1.40τ, which is a caveat on their levels if not
on their sign. The quadratic profile is flatter (−0.94 to +1.67) and
significant at only two of its sixteen points (0.75τ and 1.20τ), including at
the true
cutoff, where the headline itself collapses from +1.27 (p = 0.085) to +0.12
(p = 0.906). The reading the profile supports is therefore the one that
qualifies the whole paper: the linear specification's estimate at any cutoff
in this band moves by more than the headline's own magnitude as the cutoff
moves, so a +1.27-point linear jump at 1.00τ cannot be certified as a
discontinuity rather than as the local slope of a curved conditional mean by
anything the design's own diagnostics can see. What the placebo result does
is convert that suspicion into the
pre-registered rule's own verdict, and it means the threshold design's
identifying assumption — continuity of the conditional mean at the cutoff —
is not supported by the design's own diagnostic. The headline estimate should
be read with that in mind, and the placebo battery is the reason the
"calibrated estimator" language of earlier drafts has been removed.

**Table 10. Placebo cutoffs executed on the ±40% extraction, each with its own
±20% neighbourhood (statutory thresholds, main specification's controls)**

| Cutoff | n | Below / above | Estimate (pp) | SE | p | 95% CI |
|---|---|---|---|---|---|---|
| 70% | 250,161 | 113,360 / 136,801 | −0.62 | 0.38 | 0.119 | [−1.40, +0.17] |
| 80% | 314,014 | 168,693 / 145,321 | +0.16 | 0.25 | 0.533 | [−0.35, +0.66] |
| 120% | 298,741 | 182,178 / 116,563 | −0.14 | 0.54 | 0.802 | [−1.25, +0.98] |
| **130%** | **232,088** | **173,546 / 58,542** | **−1.14** | **0.37** | **0.005** | **[−1.90, −0.37]** |
| 100% (true) | 327,636 | 176,853 / 150,783 | +1.27 | 0.71 | 0.080 | [−0.19, +2.72] |

*Note:* the 100% row is the headline estimate of Table 8, reproduced here for
comparison: the point estimate is identical (+1.27 pp, n = 327,636) and only the
standard-error convention differs — this battery replicates the frozen run's
estimator, which applies no small-sample correction, giving SE 0.70 and
p = 0.080, while Table 8 applies the correction (SE 0.71, p = 0.085); the same
convention difference moves the 130% row from p = 0.005 to p = 0.006, which
changes no verdict below. The 130% row is significant at 5% and survives a
Bonferroni correction for four tests and a Holm correction of the five-test
family (adjusted p = 0.025); the pre-registered alarm rule fires on it. The 70%
and 120% rows are truncated by the extraction boundary on one side (below 0.60τ
and above 1.40τ respectively), as are the 120%, 125%, 130%, and 135% points of
Table 11.

**Table 11. Cutoff profile: the same specification re-estimated at sixteen
cutoffs from 0.70τ to 1.45τ, each with its own ±20% neighbourhood (statutory
thresholds, pre-registered controls; `run_review8_profile.py`)**

| Cutoff | Estimate (pp) | p | n | Cutoff | Estimate (pp) | p |
|---|---|---|---|---|---|---|
| 0.70τ † | −0.62 | 0.119 | 250,161 | 1.10τ | +0.24 | 0.598 |
| 0.75τ | +0.85 | 0.045 | 301,234 | 1.15τ | −0.33 | 0.334 |
| 0.80τ | +0.16 | 0.533 | 314,014 | 1.20τ † | −0.14 | 0.802 |
| 0.85τ | −1.02 | 0.061 | 319,332 | 1.25τ † | −1.25 | 0.013 |
| 0.90τ | −1.13 | 0.013 | 320,319 | 1.30τ † | −1.14 | 0.005 |
| 0.95τ | +0.26 | 0.555 | 323,047 | 1.35τ † | −0.90 | 0.296 |
| 1.00τ (true) | +1.27 | 0.080 | 327,636 | 1.40τ † | +0.54 | 0.895 |
| 1.05τ | +1.25 | 0.059 | 327,421 | 1.45τ † | — | — |

*Note:* † marks cutoffs whose ±20% neighbourhood is truncated by the ±40%
extraction boundary (ratio 0.60–1.40); the 1.45τ point is degenerate (no
contracts on the above side) and is not reported. The 1.00τ row reproduces
the headline of Table 8 on the frozen run's standard-error convention (no
small-sample correction; Table 8 applies the correction, giving SE 0.71 and
p = 0.085 for the same +1.27 estimate — see the note to Table 10). Fitting a
linear trend to the ten complete-band
points excluding 1.30τ gives a slope of +0.82 pp per cutoff, and the 1.30τ
estimate sits 1.7 residual standard deviations below it — significant, but
inside the profile's own scatter of roughly ±1.3 points. Under the quadratic
specification the same profile runs from −0.94 to +1.67 and is significant at
only 0.75τ (p = 0.017) and 1.20τ (p = 0.043), including +0.12 (p = 0.906) at
the true cutoff.

Two further specifications are more informative than the grid, and they do not
preserve the null. Table 6 re-estimates the threshold RD with standard errors
clustered
by awarding country (28 clusters), on the same value-space ±20% window as the
headline specification. The first response targets the running-variable problem
of Section 5.1 directly: switching the sorting variable from the awarded value
to the legally correct estimated value — a number the buyer fixes before bids
arrive, so it cannot encode the auction's result — yields +1.22 pp (SE 1.05,
p = 0.256, 95% CI [−0.93, +3.37], n = 150,074). The sample conditions deserve
statement because they bound what the estimate can mean: the estimate field is
populated for 95.4% of the threshold sample (312,599 contracts); the field
records the procedure-level (multi-lot) estimate rather than the single
contract's, so the analysis is confined to the 166,003 contracts (53.1% of the
populated sample) whose award-to-estimate ratio lies in [0.5, 2.0], where the
estimate is interpretable as the contract's own; and the value-space window
leaves 150,074 of those. The estimate is therefore conditional on a selected
subsample — selected on a ratio plausibly related to competition itself — and
it is a robustness check, not a clean re-estimate. It agrees with the
headline in sign and is far from significant under every control set (+1.13
with log value only, +0.85 with type effects, +0.82 with both), so it neither
rescues nor refutes the headline; what it does is remove the earlier version
of this diagnostic, which reported +2.30 pp (p = 0.050) and then +2.32
(p = 0.034) on the re-run, because both were computed with the threshold
recovered from the stored log distance by exponentiation — and the estimate
field has its own pile exactly at the threshold (4,608 contracts whose
estimated value equals the statutory cutoff to the cent, 82% of them German),
3,743 of which that recovery misclassifies to the below side. With the
statutory thresholds applied directly, the specification returns the figures
above; the sign is unchanged and the significance is gone, which is the
honest direction for a diagnostic that was never the headline.

The second response attacks the same contamination from the density side.
Excluding the threshold neighborhood — where sorting on the running
variable would bind most strongly — moves the estimate to +1.75 pp
(SE 0.70, p = 0.018) at a ±1% donut, +1.65 (p = 0.029) at ±2%, and +1.89
(p = 0.034) at ±3% under the statutory schedule (+1.55, +1.40, and +1.75 on
the archived one, the last of them the only one then significant); the ±1%
donut estimate is not an artifact of any single country
(leave-one-country-out estimates run from +1.39 to +2.32 pp, all positive).
The donut estimates are treated as diagnostics of the potentially contaminated
threshold neighborhood, rather than as the paper's primary findings: they were
not pre-registered, they are significant only under the linear specification
and only with the valid control set, and their role in the argument is to show
what the threshold neighborhood can do to the full-band average — not to
replace it with a preferred number. Table 7 takes the same window one step further: its no-controls
column reproduces Table 6 row for row — the baseline (+1.36, p = 0.047) and
all four diagnostic specifications — and adds four control sets that
Table 6 does not report: log awarded value alone, type FE, type plus CPV FE,
and a quadratic with type FE. The point of the second column is diagnostic
rather than substantive: it shows that the running variable's own log transform
adds nothing to the estimate once the valid pre-treatment controls are in.

One control that does *not* enter any of these specifications deserves a
sentence, because it looks tempting: the discount rate of Section 6.5. It is
mechanically tied to the awarded value — it is computed from the award and the
estimate — so conditioning on it inside a design that sorts on the award would
adjust on a transform of the running variable rather than on a confound, and
its threshold discontinuity (−1.55 pp on the statutory schedule) is the quantity under diagnostic
scrutiny, not an adjustment to be applied. No specification in this paper
includes it.

**Two departures from the pre-registration should be stated.** The first is the
window: the pre-registration specifies ±20% in logs, |r| ≤ 0.2, while the paper
reports ±20% in value space, |v/τ − 1| ≤ 0.2, because the threshold is a value
and "twenty percent of the threshold" is naturally read that way. The
value-space window adds 4,117 contracts (327,636 against 323,519). The choice
is immaterial, and the comparison is made control set against control set.
Holding the pre-registered control set fixed, the log window returns
+1.17 pp (SE 0.68, p = 0.097) against +1.27 (SE 0.71, p = 0.085) in value
space; with no controls at all the baselines are +1.23 (p = 0.068) and +1.36
(p = 0.047). No window metric
changes a sign, a significance verdict, or an order of magnitude. The second departure is the
robustness family itself: the pre-registration covers the threshold table, the
linear specification, and the decision rule, but not donuts, alternative
running variables, or the grid. These tests were added by the authors after
the main results; the motivation is internal to the paper's own diagnostics —
what happens when the threshold neighborhood is excluded and when the legally
correct running variable is used — and they should be read
as the post hoc exploration they are.

**A control set must be chosen with care, because the obvious candidates are
not valid controls — and one of them is not a control at all.** Log awarded
value is not merely a weak control: within each country×year×type cell the
threshold is a constant, so the log awarded value and the running variable
differ by that constant and nothing else. The within-cell correlation between
them is 1.000000 to six decimals over all 917 cells, and the variance-inflation
factor of the log-value term in the main regression is above four million. It
is therefore a deterministic function of the included regressors, not an
adjustment, and dropping it moves the estimate by at most 0.02 points (+1.27
with the pre-registered set, +1.27 with type effects alone, +1.36 with no
controls at all, +1.38 with log value alone). The control that does the work
in the +1.27-to-+1.36 move is contract type, not the log value, and the paper
now says so instead of attributing the move to the wrong variable. The
electronic-offer share is the first
stage — a post-treatment mechanism, not a confound — and controlling it would
remove the effect under study. The valid pre-treatment adjustment is contract
type, and Table 7 adds the two-digit CPV division as a further layer. With type
controls, the four diagnostic estimates are +1.88 (SE 0.63,
p = 0.006), +1.83 (p = 0.010), +2.13 (p = 0.010), and +0.85 (p = 0.536);
adding the CPV division leaves the three donuts at +1.82, +1.77, and +2.03
(adjusted p = 0.010, 0.017, 0.020) and the baseline at +1.17 (p = 0.131).

**The family-wise correction is reported three ways, and the answer depends on
the control set.** The family is four estimates: ±1%, ±2%, ±3%, and the
estimated-value running variable, all on the statutory schedule. With type
controls, the raw p-values are 0.006, 0.010, 0.010, and 0.536; the three
donuts survive every correction we report — Bonferroni adjusted p of 0.024,
0.040, and 0.038 (the raw p-values all clear the 0.0125 rule), Holm adjusted p
of 0.024 to 0.029, and a Romano–Wolf stepdown resampled over the 28 country
clusters with 1,000 bootstrap replications giving 0.032 to 0.040 — while the
estimated-value specification survives none of them (adjusted p ≥ 0.49).
Without controls the raw p-values are 0.018, 0.029, 0.034, and 0.256, and
nothing survives Holm or Bonferroni (smallest adjusted p = 0.072); under
Romano–Wolf the ±1% donut alone clears (0.040). The family is therefore
significant at conventional levels with the valid pre-treatment control set
and not without it — and in both cases the estimated-value specification is
the member that does not clear, which is the honest reading of a diagnostic
whose own subsection reports a null. The tight clustering of the Holm
values is mechanical rather than substantive: Holm is a stepdown rule that
adjusts the smallest raw p-value first and then carries a running maximum
forward, so when the four raw p-values sit this close together the adjusted
values converge.

**That significance does not survive a more flexible local specification.**
With a quadratic polynomial in the running variable (type controls), the
archived block's four estimates fall to +0.86 (p = 0.19), +0.21 (p = 0.82),
+0.91 (p = 0.37),
and +1.80 (p = 0.18) — none significant — and on the statutory schedule the
quadratic at the full window likewise returns +0.11 (p = 0.910), with the
cutoff profile of Table 11 showing the same collapse point by point. A regime
effect at a legal line
should be visible under curvature near the cutoff; an estimate that needs the
linearity is not a stable local jump. The bandwidth pattern points the same
way. On the statutory schedule the type-controlled v6.0 grid rises
monotonically with the window under the linear specification — +0.27
(p = 0.763) at ±10%, +0.84 (p = 0.247) at ±15%, +1.27 (p = 0.085) at ±20%,
+1.33 (p = 0.037) at ±25% — while the quadratic returns nothing anywhere
(−1.04, −0.31, +0.11, +0.63; smallest p = 0.38). The archived grid rose the
same way at different levels (−0.23 to +0.94 under the pre-registered
controls), so the pattern is not an artifact of the threshold correction. A
rising pattern is what a
smooth gradient in contract size or digital depth produces, not what a jump at
the threshold produces. We report the grid in full rather than select the
functional form that maximizes the estimate, and we do not claim a robust
positive effect: the defensible statement is that the pre-registered main
specifications do not yield a statistically detectable competitive gain, and
that the post hoc diagnostic linear specifications produce positive
estimates that remain significant under the reported multiple-testing
corrections but are sensitive to polynomial order.

**Balance should be reported on pre-treatment margins only.** Two of the
imbalances at the line are not confounds to adjust away. Log awarded value
differs across the line because it is the running variable; continuity of its
conditional distribution is the identifying assumption, and the donut is the
robustness exercise that addresses the threat to it. The electronic-offer share differs because
it is the mechanism itself — the +3-point jump above the line is the first
stage, not a balance failure. The genuinely pre-treatment margins are contract
type, CPV composition, and country composition. Type shares do not jump
(supply/service +1.7 points, p = 0.12; works −0.1 points, p = 0.82; flat after
the donut). Of the six largest CPV divisions, five show no jump; the exception
(the construction block, +2.6 points, p = 0.028) is absorbed by the
CPV-augmented control set, which leaves the estimates unchanged. Country shares
do differ — above-threshold contracts are 9.0 points more German and 4.8 points
less French — but every specification includes country×year fixed effects, so
national composition is absorbed by construction.

**What could produce the positive sign.** If the supra-threshold bundle raised
competition, the cleaner specifications should move toward zero or below; they
move up. Three readings are consistent with that pattern, and we cannot
separate them with these data. The first is compliance cost: above the line,
notices must be published in TED, minimum deadlines lengthen, and documentation
requirements bind, and these fixed costs fall hardest on small bidders — the
pool thins, and the single-offer share rises. On this reading the estimate is a
reduced form of the whole procedural bundle, not of disclosure, and its sign is
what a compliance-cost channel predicts. The second is contract composition:
above-threshold contracts are larger and more digital, and larger contracts
attract fewer, more specialized bidders. The third is selection in the
estimated-value subsample, which is 46% of the threshold sample (150,074 of
327,636) and selected on
the ratio of award to estimated value — a ratio plausibly related to
competition itself. None of the three implies that transparency reduces
competition; all three imply that the threshold comparison is not a clean
disclosure experiment, which is why the paper's claim rests on the absence of a
gain across every design rather than on the positive estimates of Table 6.

A final check addresses the sample window directly. Splitting the threshold
sample at 2021 leaves the estimates intact: +1.42 pp (p = 0.052) for
2013–2021 and +0.83 (p = 0.499) for 2022–2023 under the pre-registered
controls (+1.48, p = 0.036 and +1.00, p = 0.387 with none). The
post-2021 extension neither creates the null nor creates the positive
estimates; it adds 26.1% more contracts (85,656 of the 327,636) and slightly
more precision to
the earlier window.

We read the table as follows: the full-band null is an average over a
contaminated neighborhood, and once the contamination is removed the point
estimates rise — family-wise significant
under the linear specification with pre-treatment controls, and not
significant once a quadratic term is allowed, which is why they are reported
as diagnostics of the neighborhood rather than as findings. The legally
correct running variable agrees in sign and sits just below the headline
(+1.22 against +1.27), far from significant under every control set. What no
pre-registered specification shows — at any bandwidth, polynomial order, donut
width, running variable, or subgroup — is an estimate of a competitive gain
that is statistically distinguishable from zero; the significant estimates in
Table 6 are the post hoc diagnostic family, which clears the
reported multiple-testing corrections only under a linear specification with
contract-type controls. A fourth estimator — synthetic
difference-in-differences (Arkhangelsky et al., 2021) — was run on the timing
data in an earlier version of this program and returned the same non-result: it
amplified the point estimates without adding identification.

**Table 6. Threshold RD with country-clustered standard errors: baseline and
diagnostic specifications (v6.0, value-space ±20% window)**

| Specification | Estimate (pp) | SE | p | n | Statutory thresholds (§7.4) |
|---|---|---|---|---|---|
| Baseline (re-estimated, no controls) | +0.95 | 0.64 | 0.148 | 326,718 | +1.36 (0.047) |
| Donut ±1% | +1.55 | 0.71 | 0.036 | 305,895 | +1.75 (0.018) |
| Donut ±2% | +1.40 | 0.73 | 0.065 | 291,340 | +1.65 (0.029) |
| Donut ±3% | +1.75 | 0.83 | 0.045 | 275,425 | +1.89 (0.034) |
| Estimated-value running variable | +2.30 | 1.12 | 0.050 | 135,444 | +1.22 (0.256) |

*Note:* the first four columns are the archived run on the erroneous 2013–2017
threshold schedule; the last column is the end-to-end re-run on the raw contract
award notices with the statutory thresholds (Section 7.4), no controls,
country-clustered errors. The estimated-value row sorts on the notice-level
estimate field, and the re-run sample is 150,074 contracts on the value-space
band (151,221 on the log band, which returns +1.17, p = 0.278 — the window
metric is immaterial for this specification).
The two schedules agree on the sign of every row. Significance changes in three
of five: the baseline and the ±1% and ±2% donuts cross conventional levels
under the statutory cutoffs, and the estimated-value specification moves the
other way, from p = 0.050 to p = 0.256 — the archived figure was inflated by a
threshold-recovery artifact on the estimate-side mass point (Section 7.3), and
the corrected specification agrees with the headline in sign while being far
from significant, because that specification sorts on the estimate and only the band
moves. Section 7.4 reports the validation that makes the comparison meaningful.

*Note:* the baseline row re-estimates the headline specification on the same
±20% window with country-clustered standard errors and no controls; it
differs from the pre-registered Table 2 estimate (+0.82) because Table 2 keeps
the pre-registered controls — log awarded value and contract type. The
decomposition is exact and small, and it is reported directly rather than
inferred: on the same window, adding contract-type fixed effects alone moves
the baseline from +0.95 to +0.82, which is the entire 0.13-point gap, while
adding log awarded value alone moves it only to +0.91 and adds nothing on top
of the type effects (+0.82 either way). That is what collinearity predicts —
log awarded value is a monotone transform of the running variable, so within
the band it is close to a linear function of the included slope, and the
pre-registration's inclusion of it is a harmless redundancy rather than a
substantive adjustment. Table 7 reports the full control-set × polynomial-order
grid. All estimates are on the single-offer share; n counts contracts.

**Table 7. Sensitivity of the threshold estimates: control set and polynomial
order (estimate in pp, p-value in parentheses; country-clustered SEs)**

| Specification | No controls | Log value only | Type FE | Type + CPV FE | Quadratic, type FE | Statutory: no controls | Statutory: type FE |
|---|---|---|---|---|---|---|---|
| Baseline | +0.95 (0.148) | +0.91 (0.171) | +0.82 (0.245) | +0.65 (0.388) | −0.60 (0.559) | +1.36 (0.047) | +1.27 (0.085) |
| Donut ±1% | +1.55 (0.036) | +1.69 (0.015) | +1.70 (0.014) | +1.64 (0.021) | +0.86 (0.191) | +1.75 (0.018) | +1.88 (0.006) |
| Donut ±2% | +1.40 (0.065) | +1.58 (0.024) | +1.60 (0.021) | +1.55 (0.033) | +0.21 (0.821) | +1.65 (0.029) | +1.83 (0.010) |
| Donut ±3% | +1.75 (0.045) | +2.00 (0.013) | +2.02 (0.011) | +1.91 (0.023) | +0.91 (0.366) | +1.89 (0.034) | +2.13 (0.010) |
| Est.-value running var. | +2.30 (0.050) | +2.64 (0.031) | +2.83 (0.023) | +3.00 (0.019) | +1.80 (0.181) | +1.22 (0.256) | +0.85 (0.536) |

*Note:* the first five columns are the archived run on the erroneous 2013–2017
threshold schedule; the last two are the end-to-end re-run on the raw contract
award notices with the statutory thresholds (Section 7.4). Within the archived
block, the log-value column exists to settle the control-set question rather
than to improve the estimate: log awarded value is a monotone transform of the
running variable, so adding it alone moves the baseline by 0.04 points and adds
nothing once the type effects are in (+0.82 with type FE, +0.82 with both),
which is what collinearity predicts and is the reason its inclusion in the
pre-registered Table 2 is a harmless redundancy. The two valid pre-treatment
controls — contract type and, more demandingly, contract category (CPV) — move
the estimates in the same direction as no controls at all, so the positive
diagnostic estimates are not an artifact of an invalid control. Family-wise
corrections on the four diagnostic rows, archived block. With type
controls: Bonferroni threshold 0.0125 clears one; Holm adjusted p runs
0.042–0.043 across the four; Romano–Wolf stepdown (1,000 cluster bootstrap)
adjusted p = 0.031–0.047. Without controls: Holm 0.145 for every member;
Romano–Wolf 0.055–0.060. The quadratic column uses type controls, and under it
all four diagnostics collapse toward zero (+0.21 to +1.80, none significant) —
which is why they are reported as diagnostics of the neighborhood rather than
as findings. Under the statutory thresholds the quadratic specification
likewise returns nothing (+0.11 at ±20%), and the donut diagnostics are
significant under every control set including none.

**Figure 4.** The specification grid on the v7.0 running variable: point
estimates (bars, labeled in percentage points) on the single-offer share across
bandwidths (±10% to ±25%) and polynomial order (linear, quadratic), with
contract-type controls and country-clustered standard errors. The dashed line
marks zero. No cell is statistically significant: −4.26 (p = 0.315) at ±10%,
−2.39 (p = 0.363) at ±15%, −0.67 (p = 0.650) at ±20%, −0.94 (p = 0.464) at
±25%, and −4.49 (p = 0.329) for the quadratic. Unlike the archived v6.0 grid,
which rose monotonically with the window (Section 7.4), this grid does not
drift: it rises toward zero from ±10% to ±20% and edges away at ±25%. The donut
specifications of Table 9 are not
shown here because they are reported there and move across a 2.1-point range
with changes of sign.

### 7.4 A threshold-table error, and what it did to the design

The third design rests entirely on the legal cutoff, so an error in the cutoff
table is an error in the design's foundation. This section reports one, how it
was found, what it did, and what has and has not been re-run since.

**The error, and the frozen file that contained it.** Table 1 previously
carried €207,000 and €5,235,000 for supply,
service, and works contracts across all of 2013–2017. Checked against the
instruments themselves, that is wrong in eight of the ten year-type cells it
covers — all five works cells, and the 2013, 2016, and 2017 supply/service
cells — and the works figure, €5,235,000, appears in no instrument in the
series. The
correct schedule is €200,000 / €5,000,000 for 2013 (Directive 2004/18/EC as
amended by Regulation (EU) No 1269/2011), €207,000 / €5,186,000 for 2014–2015
(Regulation (EU) No 1336/2013), €209,000 / €5,225,000 for 2016–2017 (Regulation
(EU) 2015/2170), and the values the table already carried for 2018–2023
(Regulations (EU) 2017/2365, 2019/1828, and 2021/2170). The code used the
erroneous schedule, so the error is in the analysis and not only in the table.
The 2018–2023 biennia, which supply 69.4% of the threshold sample, were correct
throughout, which is why the error was not visible in any single-year
diagnostic.

The frozen pre-registration contained the same erroneous table, and that is
worth stating separately because the paper leans on the pre-registration
elsewhere. The frozen file's threshold block lists €207,000 and €5,235,000 for
2013–2017, and its source note cites the three instruments that set the
2018–2023 values without naming the two that set the 2014–17 ones. The file has
not been edited in place, because the hash is the only evidence of what was
actually frozen and because Section 8 already says the hash establishes
integrity rather than correctness; the correction is published as a separate
addendum (`preregistration_v6_threshold_addendum.md`) alongside it. Three
implications follow. A frozen plan can freeze an error, and no hash can
distinguish a plan that was followed from a plan that was wrong. Correcting the
cutoffs is itself a departure from the pre-registration, disclosed here
alongside the window-metric departure of Section 7.3 rather than folded quietly
into it. And the direction of the correction is known in advance and is not
favourable to this paper's headline, which is the reason to make it in public
rather than to leave it.

**The clean re-run.** The band cannot be rebuilt from the shipped cache, which
covers only the erroneous schedule's ±20% window, so the design was re-run from
the raw contract award notices: the eleven annual TED CAN extracts were
downloaded from the EU Open Data Portal, the band was rebuilt around the
statutory cutoffs, and the whole specification set was re-executed. Before the
corrected numbers are read, the pipeline was validated against the archive: run
with the *erroneous* thresholds, the re-run reproduces `results_v6.json` to the
last digit — 326,718 contracts, 150,444 above and 176,274 below, single-offer
τ = +0.008222, log-offers τ = −0.003239, electronic-share τ = +0.004699,
foreign-winner τ = +0.011465, density gap −0.015684, and the 80% placebo at
−0.05146 with p = 0.14603. Nothing in the archived record is a transcription
error; the error is in the cutoffs and nowhere else.

**What the re-run changes.** With the statutory cutoffs the sample is 327,636
contracts — 150,783 above and 176,853 below — and the estimates move. The
pre-registered headline is **+1.27 pp (SE 0.71, p = 0.085, 95% CI [−0.19,
+2.72])**, against the archived +0.82 (SE 0.68, p = 0.234); dropping the
log-value control gives +1.36 (p = 0.047), which crosses conventional
significance. Every other outcome moves the same way: log(1+offers) from −0.32
to −1.89, foreign-winner share from +1.15 to +1.22, and the electronic-offer
share — the first stage — from +0.47 (p = 0.154) to +0.38 (p = 0.212), so the
threshold design's first stage was not significant before the correction and is
not significant after it. The bandwidth gradient steepens monotonically, from
+0.27 (p = 0.763) at ±10% to +1.33 (p = 0.037) at ±25%, and the quadratic
specification continues to return nothing (+0.11, p = 0.910). The donut
specifications all become significant and positive: +1.75 (p = 0.018) at ±1%,
+1.65 (p = 0.029) at ±2%, +1.89 (p = 0.034) at ±3%. The estimated-value
running variable, re-estimated on the notice-level estimate field with the
statutory cutoffs, gives +1.22 pp (SE 1.05, p = 0.256, n = 150,074) without
controls and +0.82 (p = 0.568) with the pre-registered set — the same sign as
the headline, far from significant, and materially below the +2.30 (p = 0.050)
the archived schedule produced, because the archived and first re-run figures
were computed with the threshold recovered from the stored log distance by
exponentiation, which misclassifies the estimate-side mass point at the line
(Section 7.3). A specification that sorts on the estimate moves only the band
when the cutoffs are corrected; the movement this diagnostic shows is the
artifact leaving, not the data changing.

**What the re-run leaves standing.** Three things. The two panel designs are
untouched, because their threshold-stable floors (€250,000 for supply and
service, €6,000,000 for works) sit above the highest applicable threshold
anywhere in the window (€221,000 and €5,548,000 in 2018–19), so no contract in
the panel is near a cutoff; the participation gradient and the price-margin
diagnostics are estimated on that panel. The price margin is in fact
reproduced almost exactly: single-offer contracts discount 5.95% against 6.61%
for multi-offer ones, against the archived 5.96% and 6.61%, and the
threshold discontinuity in the discount rate is −1.55 pp (p = 0.054 with
country-clustered errors, against the archived −1.76 pp reported with
classical errors that understate the standard error by a factor of five). And
the density audit survives in substance: the frozen gap moves from −0.0157 to
−0.0114, the mechanical null is unchanged at −0.0306, the bias-corrected excess
moves from −1.48% to −1.90%, the symmetric-bin comparison from t = 0.77
(p = 0.45) to t = 0.88 (p = 0.39), the McCrary ratio from 0.985 to 1.007, and
the gap against its mechanical null from p = 0.17 to p = 0.076. No corrected
implementation rejects symmetry, and the mass point at the line is 5,314
contracts (1.62% of the band, 73.8% German, award equal to estimate for 90.1%
of them against 38.4% of the full sample) — the archived figure of 4,659 was
measured at the wrong cutoff values and is superseded. The bunching counts
quoted in Section 7.1 (3,262 / 2,257 / 11,062) were computed on the erroneous
schedule and are superseded; the finding they support — that the estimator is
specification-driven and cannot support a count — is not sensitive to the
correction, which is why that count was withdrawn in the first place.

**The placebo battery, once executable, trips the pre-registered alarm.** The
archived record contained one placebo figure and it was not executable: the
±20% band leaves three of the four pre-registered cutoffs with no comparison
group at all and the fourth with a rounding sliver of one, so the alarm rule
had never actually been evaluated. Executed on the ±40% extraction with each
cutoff given its own neighbourhood (Table 10), three cutoffs are unremarkable
and the fourth is not: **at 130% of the threshold the estimate is −1.14 pp
(SE 0.37, p = 0.005, 95% CI [−1.90, −0.37], n = 232,088), significant at 5%
and surviving a Bonferroni correction for four tests and a Holm correction of
the five-test family that includes the true cutoff (adjusted p = 0.025).** By
the pre-registered rule — any
significant placebo marks the estimator as threatened — this design is
threatened, and the paper now says so instead of reporting a calibrated
estimator. The eighth round added the decisive diagnostic — a cutoff profile
walking the same specification from 0.70τ to 1.45τ (Table 11) — and it
supports neither of the two clean readings. The linear profile oscillates
inside a band of roughly ±1.3 points with no monotone drift, so the jump is
not a smooth gradient being picked up as a level shift; but the 1.30τ point
is only 1.7 residual standard deviations below the local trend of its
neighbours, and the 1.25τ and 1.35τ points are negative as well, so it is not
an isolated data feature either. What the profile establishes is weaker and
more damaging: the linear specification's estimate moves by more than the
headline's own magnitude as the cutoff moves, so the design's own diagnostics
cannot certify the +1.27 headline as a discontinuity rather than as the local
slope of a curved conditional mean — and under the quadratic profile the
headline itself collapses to +0.12 (p = 0.906). The identifying assumption is
therefore unsupported by the design's own test, and the headline is reported
with that threat on the record.

**What this means for the reading, and what it does not.** The headline is no
longer a null. It is a small positive estimate, +1.27 pp, that is
indistinguishable from zero under the pre-registered control set and
significant without it, with a confidence interval running from −0.19 to +2.72
points — wide enough to contain a competitive gain of up to about 2.7 points and
wide enough to contain a loss of the same order. Two statements follow. First,
the paper's earlier formulation — that the full-band estimate is "statistically
indistinguishable from zero" — is too strong: under the statutory cutoffs it is
borderline, and the borderline is crossed in some control configurations.
Second, the direction of every corrected estimate is positive, which is the sign
the policy premise excludes, so the paper's narrower claim survives intact: no
specification, corrected or archived, shows a competitive gain that is
statistically distinguishable from zero — the v7.0 main design does carry a
negative point estimate (−0.67 pp, p = 0.650, Section 6.1), which leans toward
the premise without reaching significance, and the claim is about detectable
gains, not about the sign of insignificant point estimates. What the
correction does is convert "a null with a positive point" into "a small
positive estimate that some configurations can distinguish from zero and others
cannot," and it does so in a design whose own first stage does not bind.

**What the seventh and eighth rounds added, and what remains open.** The
placebo battery has now been executed on the ±40% extraction and its result
is in Table 10; the bunching estimator has been rebuilt from the raw extracts
and its preferred specification reproduces the archived 3,262 figure as
3,287, with the other two archived counts untraceable to any script; the
v3.0 design has been given its native influence-function and
multiplier-bootstrap intervals, reported in Section 6.3; every archived
result file in the repository has been audited for reproducibility, with the
outcome summarised in Section 8; and the eighth round added the cutoff
profile of Table 11, the collinearity quantification of Section 7.3 (the
log-value control is a deterministic function of the running variable within
cells — within-cell correlation 1.000000, variance-inflation factor above
four million — and the +1.27-to-+1.36 move is contract type's doing, not
its), the correction of the estimated-value diagnostic for the
threshold-recovery artifact on the estimate-side mass point, and the
switch of every placebo and profile cutoff to the statutory threshold table
applied directly, which the exponentiation recovery had been corrupting at
the mass point (4,246 contracts in the ±20% band). Three items remain open.
The bunching estimator's point estimate is reproducible but its
specification grid swings from −5,727 to +3,287 contracts, so no count is
reported as a result. The 130% placebo jump is significant, and the profile
locates it inside a neighbourhood of negative estimates (1.25τ to 1.35τ)
rather than at a single point, so what produces it is still unexplained —
the three cutoffs involved have truncated above sides, and a wider
extraction would be needed to estimate them on complete bands. And the
digital-depth split's archived version could not be reproduced from
any script, so it is withdrawn rather than corrected; the re-run's version
uses the contract-level electronic-offer share, whose median is exactly 1.0,
which makes its "high" half a 198-contract data anomaly rather than a
subgroup. Those three items sit on the verification schedule in Section 8.

---

### 7.5 A design audit: what each specification can and cannot support

A paper that has been revised as many times as this one accumulates
specifications faster than it accumulates conclusions, and the honest thing to
do at the end is to audit them side by side. Table 12 does that. Each row is a
specification that was run, each column is a diagnostic that a reader would want
to see before crediting the row, and the entries are what the data say rather
than what the paper would prefer.

**Table 12. Design audit: every specification run, against every diagnostic that
bears on it**

| Design (identifying variation) | Diagnostics that bear on it | Estimate | Reading |
|---|---|---|---|
| v6.0 threshold RD (awarded value) | Placebos 4 of 16 significant; density gap is a construction artifact | +1.27 (p = 0.085) | Not credible as a causal estimate |
| v6.0 placebo battery (±40% band) | 130% cutoff: −1.14 (p = 0.005) | — | Alarm rule fires; design threatened |
| v7.0 threshold RD (notice estimate, legal) | Placebos 0 of 7 significant; density not significant (p = 0.24); composition balanced | −0.67 (p = 0.650) | **Main estimate** |
| v7.0 high-publication subsample (notice estimate) | Placebos 1 of 6 significant | +2.07 (p = 0.412) | Suggestive only |
| v3.0 transposition ATT (national dates) | Interval method-dependent | +3.37 pp | Auxiliary, not causal |
| v4.0 event study, single-offer share (same dates) | Pre-trends **significant** | +2.33 pp | Not interpretable as causal |
| v4.0 event study, foreign-winner share (same dates) | Pre-trends clean | +0.23 (p = 0.49–0.80) | **Precise null** (corroboration) |
| v7.0 threshold RD, foreign-winner share (notice estimate) | Placebos 0 of 7 significant; composition balanced | −1.21 (p = 0.019) | Finding; concentrated 2020–23 |
| Bunching estimator (notice/award density) | Specification grid changes sign 7 times | −5,727 to +3,287 | No estimate reported |
| Participation gradient (digital depth, cross-section) | — | +33.4 pp | Association, not effect |

Three entries in that table carry the paper's causal weight, and each carries a
different kind of caveat. The v7.0 threshold estimate is the main specification
and the only one that passes all three diagnostics, but its first stage is not
established, its estimate field covers about 59% of notices, and its donut
specifications are unstable in sign. The foreign-winner event study is clean and
precise but answers a narrower question than the single-offer share does. The
v3.0 transposition ATT is the only estimate whose identifying variation no
buyer controls at all, and its interval depends on which of four defensible
inference methods is credited — the cell-level interval and the multiplier
bootstrap span zero, the country-level cluster bootstrap does not.

The table also records what the paper does not claim. The v6.0 award-value
estimate is reported because it is the archived record and because the audit
trail matters, not because it is credible: its placebo profile shows four
significant jumps out of sixteen fake cutoffs, which is the signature of a
sorting variable that responds to the threshold, and the pre-registered alarm
rule fires on it. The bunching estimator is reported as a specification
sensitivity range and nothing else, because the point estimate changes sign
seven times across a defensible grid of windows and polynomial orders. The
participation gradient is reported as an association with an explicit
reporting-artifact caveat, not as an effect.

What the audit establishes, taken together, is narrower than a causal estimate
and more useful than a list of numbers. The legally specified threshold
discontinuity is clean and its estimate on the single-offer share is a null with
a resolution of about 4.2 percentage points, while the same design finds a
1.21-point fall in the foreign-winner share that is not a size gradient. The transposition variation that no participant controls
produces a clean and precise null on foreign participation and an uninterpretable
estimate on the single-offer share. And no specification anywhere in the table,
on either running variable, at any bandwidth, polynomial order, donut width,
control set, or subgroup, produces a competitive gain. That is the claim the
paper makes.

### 7.6 Data cleaning, coverage, and what the subsamples show

**Cleaning.** The matched CN–CAN sample carries several reporting defects that
have to be removed before any estimate is read, and the rules are stated so the
sample can be reconstructed exactly. `VALUE_EURO` and its fallback
`VALUE_EURO_FIN_1` are kept only inside [€1,000, €1bn]: 46,951 notices (1.0%)
fall outside, including estimates up to €5.4 quadrillion.
`AWARD_VALUE_EURO` carries the sentinel value 9,999,999,999,999 in exactly 14
rows; together with 1,594 non-positive awards, 1,608 rows are dropped.
`NUMBER_OFFERS` is dropped below 1 (428 rows) and at or above 999, the latter
being an evident reporting cap (420 rows). `LOTS_NUMBER` exceeds 1,000 in
25,092 rows and is treated as missing there. `DT_APPLICATIONS` minus
`DT_DISPATCH` is kept between 1 and 365 days. The electronic-offer share, which
an earlier version of this section declared unusable, is in fact computable:
among the 1,447,645 matched notices that report both offer counts, only 994
(0.1%) report more electronic offers than total offers and are dropped, and in
the ±20% band the share is observed for 103,024 notices — the threshold
discontinuity on it is −0.68 pp (SE 0.59, p = 0.257, Table 9). The claim that
`NUMBER_OFFERS_ELECTR` exceeds `NUMBER_OFFERS` "in 3.04 million rows" was a
cleaning-rule artifact of our own: the rule counted unmatched notices, whose
share is undefined, as violations. The
cleaning changes nothing that matters: on the 28-country sample the headline
moves from −0.66 to −0.67 pp and the foreign-winner estimate is unchanged at
−1.21 pp, and the placebo profile still shows no significant cutoff (0 of 7).
A separate defect in
our own estimation code — a control loop that silently skipped the contract-type
dummies — briefly produced a headline of −0.68 without them; with the dummies,
which the differing thresholds by contract type require, the estimate is
−0.67, and the dummies are kept in every estimate reported here. Two date formats also had to be handled — TED writes `27-FEB-13`
through 2016 and `05/02/18` from 2017 — and missing the second one silently
empties the tender-period field for the second half of the window. And the
country-mapping error that dropped Greece from the first v7.0 run is documented
in Section 6.1: three pipeline defects found and disclosed in three revision
rounds, each one caught by an audit of the pipeline rather than of the
econometrics.

**Coverage.** The binding constraint on the matched sample is the estimate
field, and its coverage is not uniform. Across the 7.97 million contract notices
passing the type, cancellation, and member-state filters, 58.9% carry a usable
estimate; the share is 36% in 2013–2015, 52–59% in 2016–2019, 63–67% in
2020–2022, and 58% in 2023. Coverage is not a country problem — the lowest
member state, Germany, still has 84% — so the selection is over time rather
than across reporters. The consequence is that the early years, which are also
the years where the subsample anomaly below appears, contribute the least:
54,453 notices with a usable estimate in 2013 against 806,331 in 2021.

**Subsamples.** The single-offer estimate is not uniform across the window.
Pooling 2013–2016 gives −3.34 pp (SE 1.42, p = 0.026) and the number of offers
gives +0.33 (SE 0.15, p = 0.038) — both in the direction the policy premise
predicts — while 2017–2019 and 2020–2023 give +3.38 (p = 0.677) and −2.38
(p = 0.543). Decomposing the early period by contract type localizes it: supply
contracts give −4.79 pp (SE 1.29, p = 0.0009) and works contracts −9.37 pp
(SE 3.36, p = 0.010), against +0.05 (p = 0.983) for services. Three readings
are available and the data do not choose between them, so we state what would
distinguish them. The early estimate could
be a real effect that faded as the directive's own reforms arrived, which would
make the pooled null an average over a disappearing effect — and if that
reading is right, the honest headline is not "null" but "early positive, fading
to null," which is a different finding with different policy content. It could
instead be a reporting artifact, and there are specific reasons to take that
seriously: the early years have the thinnest estimate coverage of the window
(36% in 2013–2015 against 63–67% in 2020–22), the fewest matched award notices
(54,453 notices with a usable estimate in 2013 against 806,331 in 2021), and
the estimate field is precisely what the running variable is built from — so
the early subsample is selected on the field the design depends on, and a
selection that correlates with competition would mimic exactly the pattern
observed. The third reading is noise in a subsample of 20,781 contracts whose
standard error is 1.4 points, with a family of period-by-type splits this size
producing one significant cell by chance. What the paper does not do
is select the period that suits the conclusion: the pooled estimate over the
full window is the headline, the period split is reported here, and the honest
statement is that the null is well supported after 2016 and not established
before it — and that the pre-2017 evidence, taken at face value, leans the
premise's way.

**The foreign-winner share does move.** One outcome crosses conventional
significance: the share of contracts won by a foreign firm falls by **1.21 pp
(SE 0.49, p = 0.019, n = 280,578)** at the cutoff. Two checks bear on what that
means. Controlling for the awarded value does not attenuate it — the estimate
becomes −1.56 pp (SE 0.61, p = 0.017) on the 177,911 notices where both fields
are usable — so it is a discontinuity at the line rather than a smooth gradient
in contract size, which is the same conclusion the placebo profile reaches from
the other direction. But the effect is concentrated: by period it is −1.44
(p = 0.265) in 2013–2016, −1.48 (p = 0.143) in 2017–2019, and −1.06
(p = 0.021) in 2020–2023, and by type it is −0.70 (p = 0.312) for supply,
−0.98 (p = 0.081) for services, and −0.87 (p = 0.474) for works. The reading
offered is deliberately narrow: crossing the EU threshold is associated with a
smaller foreign-winner share in the later part of the window, and that is a
statement about the threshold regime rather than about disclosure, since the
running variable is the estimate and the regime it selects is the whole
supra-threshold bundle. Whether it reflects larger, more complex procedures
favouring domestic incumbents or something else is not identified here.

**The timing of that concentration invites speculation, and we label it as
such.** Why 2020–2023? Three candidates are visible in the record's own
calendar, none identified here, each checkable against data we do not have.
The first is the pandemic: COVID-19 compressed procurement into emergency and
restricted procedures precisely when cross-border participation is hardest,
and the procedure mix above the line did shift toward restricted procedures in
the same window (Section 5.1). The second is statistical rather than
historical: the later window is where the estimate field is best covered and
the sample largest, so the foreign-winner standard error falls from 1.27
points in 2013–2016 to 0.43 in 2020–2023 — a real effect of constant size
would be detectable only in the later years for that reason alone. The third
is the eForms mandate, whose reporting obligations phase in from late 2023 and
change what the notice record contains rather than what buyers do. The
leave-one-country-out battery (Section 6.1) says the finding is not one
country's artifact, and the period split says it is not uniform across the
window; what would separate the three candidates is the nationality of winners
by procedure type, which the shipped extracts do not carry in usable form.
Until then the finding is reported with its concentration stated and its
mechanism open.

## 8. Open Science and Reproducibility

This paper's results are computationally reproducible end to end. The
repository https://github.com/TSUBARAYA/procurement-disclosure-null contains:

1. **The complete pipeline code** for all three designs — `run_v3.py`
   (group-time ATT), `run_v4.py` (contract-level FE and dose-response),
   `run_v6.py` (threshold RD, including the density test and placebo cutoffs) —
   plus the raw-to-panel builders (`build_ted_panel.py`, `build_micro_panel.py`)
   and the estimator library. The density audit reported in Section 7.1 runs
   under `run_density_audit.py`, a standalone script that rebuilds the 22-bin
   histogram from the contract-level cache, reproduces the frozen
   implementation's output, computes the mechanical null and the corrected
   tests, and writes `review5_density_audit.json`. The threshold correction and
   the clean re-run of Section 7.4 run under `run_threshold_correction.py`,
   `run_v6_full_rerun.py` (the A/B validation against the archive), and
   `run_v6_rerun_final.py` (the statutory-schedule re-run behind Tables 8–10);
   the placebo battery, the bunching rebuild, and the v3.0 native inference run
   under `run_v7_placebo_bunching.py` and `run_v3_inference_and_audit.py`; and
   the eighth-round diagnostics — the cutoff profile of Table 11, the
   collinearity quantification of Section 7.3, the family-wise corrections, the
   leave-one-country-out battery, the corrected estimated-value specification,
   and the CPV-augmented control set — run under `run_review8_profile.py`,
   `run_review8_collinearity.py`, `run_review8_corrections.py`,
   `run_review8_estvalue_corrected.py`, and `run_review8_cpv.py`. The v7.0 main
   design of Sections 5.1 and 6.1 runs under `run_v7_estimate_rd.py` (the
   CN-to-CAN matcher and the full specification set, writing `cn_matched.csv` and
   `v7_estimate_rd.json`), `run_v7_first_stage.py` (the fifteen first-stage
   candidates and the Holm correction), `run_v7_scale_placebo.py` (the
   foreign-winner scale tests and the cleaned placebo battery),
   `run_v7_clean_subsamples.py` (the cleaning rules, coverage, and subsample
   decomposition behind Section 7.6), `run_v7_density_robust.py` (the
   McCrary-style tests, bin counts, and high-publication subsample), and
   `run_v7_density_test.py` (the adjacent-bin tests with a country-clustered
   bootstrap, rebuilt in the ninth round after the audit found it missing). The
   ninth round's corrections run under `run_review9_coverage.py` (the coverage
   denominators, counted from the raw CN archives), `run_review9_paper_numbers.py`
   (the balance, mass-point, cleaning-count, and MDE computations behind the
   corrected text), and `run_review9_figures_v7.py` (which rebuilds every
   figure-data file from the corrected 28-country cache). Only numpy,
   pandas, and scipy are required.

2. **The derived analysis panels** (16,429 cells; 252 country-year aggregates),
   so that v3.0 and v4.0 reproduce from the shipped data in under a minute
   without the 770 MB of raw TED extracts; the download command and rebuild
   instructions for the raw data are in `data/README.md`. Two limits on the
   shipped panels should be stated with them. The contract-level cache
   (`rd_sample_cache.csv`) covers the ±20% band of the *erroneous* schedule, so
   it reproduces the archived v6.0 run exactly and nothing else in the paper;
   every statutory-schedule number — Tables 8–10, the placebo battery, the
   bunching rebuild, the profile — comes from the wider extraction
   (`ted_wide_final.csv`, ratio 0.60–1.40, statutory thresholds), which covers
   every bandwidth the paper reports, the ±25% point included. Neither cache is
   shipped with the repository — both are derived from the raw extracts in
   minutes by `run_v6_full_rerun.py` and its successors, and the repository
   ships only the small derived panels, the code, and the results. As an
   end-to-end validation, the whole bandwidth grid has been re-extracted from
   the raw TED archives (`run_review8_bw25_raw.py`): all eight cells reproduce
   to the digit, so no statutory number depends on a cache at all.

3. **The frozen pre-registration** for the main design — the v6.0 threshold
   RD — whose SHA-256 fingerprint is recorded in the repository's manifest: no
   threshold table, no decision rule, and no estimator was changed after the
   fact. The one deviation, the metric of the ±20% window, is disclosed in
   Section 7.3 and produces estimates within 0.03 points of the pre-registered
   version. **The frozen file's threshold table was itself wrong for 2013–2017,
   and the correction is published as a separate addendum rather than as an
   edit to the frozen file** (Section 7.4): a hash certifies that the published
   bytes are the bytes that were committed, not that the plan they record was
   correct, and this is the case that proves the distinction. The two auxiliary timing designs (v3.0, v4.0) have no separate
   frozen plan; their specifications appear in the failure log (records F14
   and F15) in execution order, which documents the sequence but does not
   certify the designs in advance. What each record supports is therefore
   stated plainly: the threshold design has a checkable frozen plan with a
   hash, and a checkable correction to it; the timing designs have a checkable
   chronology; the boundary between
   pre-registered and post hoc specifications inside the threshold design is
   drawn explicitly in Section 7.3; and the claim that voluntary publication
   below the threshold could break the continuity assumption, and the placebo
   battery at 70, 80, 120, and 130% of the cutoff, are statements in the
   frozen v6.0 file, not retrospective characterizations.

**Reproducibility audit.** Every archived result file in the repository was
checked against the scripts and data that ship with it. Of the 55 result files,
**52 are reproducible** and 3 are not. The 49 include the three main designs:
`results_v3.json` reproduces to the last digit from the shipped
`ted_panel.csv` and `identification/run_v3.py`; `results_v4.json` from
`ted_micro.csv` and `run_v4.py`; and `results_v6.json` from the raw TED
extracts and `run_v6.py` — a re-run with the *erroneous* thresholds reproduces
every number in it exactly, which is what licenses the attribution of the
corrected differences to the cutoffs alone. The v7.0 main design reproduces end
to end from the raw CN archives through `run_v7_estimate_rd.py`; the ninth-round
audit caught that its country mapping dropped all Greek notices, and the
corrected cache and every downstream file were rebuilt from the raw extracts
(Section 6.1). That audit also found that the three main-design pipeline
scripts — `run_v3.py`, `run_v4.py`, and `run_v6.py`, which this section has
always listed as shipped — were in fact missing from the repository, leaving
`results_v3.json` and `results_v4.json` without a producing script. They have
been restored from the development archive and re-verified against the shipped
panels and raw extracts: `results_v3.json` reproduces to the last digit, every
coefficient in `results_v4.json` matches to machine precision, and
`results_v6.json` — including its erroneous threshold table — reproduces from
the raw TED archives with zero differences across every field. The three
re-runs write their output to a separate `report/` directory rather than over
the archived results, so the reproduction is a check on the archive rather
than a replacement of it. The three that
are not reproducible
are `bunching_eur_v6.json`, whose three counts (3,262 / 2,257 / 11,062) can be
traced to only one script in the repository, and `digital_split_v6.json`, whose
80,002 / 229,890 split cannot be reproduced from any script and whose splitting
variable has a median of exactly 1.0 — both withdrawn from the paper
rather than reported — and `results_v3_outlier_robust.json`, an exploratory
artifact with no producing script that no number in the paper rests on. The
audit table is in the repository's `README.md`.

**What the hash does and does not certify.** We acknowledge that a self-hosted
GitHub hash provides tamper-resistance but not third-party certification. The
distinction matters, and we state it rather than let the manifest speak for
itself. The SHA-256 fingerprint establishes *integrity after the fact*: the
frozen file, as published, is bit-for-bit the file that was committed, and any
later edit would break the hash. It does not establish that the file predates
the results — the commit timestamp is hosted by the same party as the analysis,
so it is evidence of ordering, not independent proof of it — and it is not a
registry: no external body has verified that the analysis followed the
registered plan. A registry entry (for example, a timestamped deposit with an
independent registry) would provide the third-party certification this record
does not have, and we do not claim it. What the repository does provide is a
complete and checkable chronology: the frozen pre-registration with its hash,
the machine-readable output of every run in execution order, and the failure
log. Within that record, the boundary between the pre-registered plan (the
threshold table, the linear specification, the decision rule, the diagnostic
battery) and the post hoc tests (the donuts, the alternative running variable,
the specification grid, all added after the main results and disclosed as such
in Section 7.3) is drawn explicitly. A reader who trusts neither our word nor
the chronology can check the estimates against the shipped panels and code
directly.

4. **Machine-readable results** for every run, including the robustness
   variants and the density-audit output (`review5_density_audit.json`)
   behind every number in Section 7.1.

5. **The failure log** of the full research program — ten records covering the
   pre-trend violation of the first design, the placebo-distribution failure of
   the second, the estimator-localization experiment that showed the problem sat
   in the control pool rather than the estimator, the low-baseline attempt that
   died of data access, and the threshold design that closed the sequence.

6. **A verification schedule** for what remains open, stated as open items
   rather than as results:
   (i) **the 130% placebo jump** (Table 10) — significant at p = 0.005 and
   surviving a Bonferroni correction, with no established explanation; the
   cutoff profile of Table 11 locates it inside a neighbourhood of negative
   estimates (1.25τ to 1.35τ) rather than at a single point, and all three
   cutoffs have truncated above sides on the ±40% extraction; it trips
   the pre-registered alarm rule and it is the single largest threat to the
   threshold design's validity;
   (ii) **the bunching estimator's specification dependence** (Section 7.1) —
   the preferred specification is reproducible (3,287 contracts, bootstrap CI
   [2,132, 4,592]) but the grid swings from −5,727 to +3,287 across
   neighbourhoods and polynomial orders, so no count is reported as a result;
   (iii) **the digital-depth split** — its archived version is not reproducible
   from any script in the repository and is withdrawn; a defensible replacement
   needs a digital-depth measure defined at the level the dose-response uses,
   which is country-year rather than contract-level; and
   (iv) the firm-level matching extension that would convert the participation
   gradient from "who bids" to "who wins" (Section 3.3).
   Each is listed with what it requires and none is reported as a result in the
   meantime. Everything else in the empirical program has been re-run from the
   raw sources: the threshold design end to end on the statutory cutoffs
   (Section 7.4), the placebo battery on the ±40% extraction (Table 10), the
   bunching estimator rebuilt (Section 7.1), the v3.0 design given its native
   influence-function and multiplier-bootstrap intervals (Section 6.3), the
   v7.0 main design re-run on all 28 member states after the ninth-round audit
   caught the country-mapping error (Section 6.1), and
   every archived result file audited for reproducibility (below).

**Failure is part of the record.** The program behind this paper ran six versions. The first asked a simulation to predict national corruption
trajectories and failed on every sample. The second fixed identification and
exposed a control-pool problem. The third and fourth moved to contract data and
found the first stage without the second. The fifth ran out of data access on a
low-baseline country: a stratified pull of the ProZorro Open Contracting API
returned 36,103 tender summaries but only 6,591 usable tender details — the
rest lost to rate limiting and detail-endpoint availability — and the coverage
stopped in early 2017, two years short of the design target. The version is
recorded as incomplete; its 6,591 usable tenders support no conclusion in
either direction, and none is drawn. The sixth used a
legal cutoff and returned the null reported here. The plans for v1.0, v2.0,
v5.0, and v6.0 were each written and frozen before their results were
inspected; v3.0 and v4.0 — the two auxiliary designs used in this paper — have
no separate frozen plan, and their specifications are documented in this log
in execution order, a sequential-preregistration record rather than a frozen
plan. Each failure narrowed the next design. A convergence assembled from
cleaned-up runs would
be worth little; one assembled
from runs whose failures were all kept on the record is worth more, and it is
the only kind this program has to offer.

*A statement of status.* This paper is a working paper. It has not been peer
reviewed, and nothing in it should be read with the authority of a refereed
publication. We release it in this form deliberately: every number in the text
is produced by code that is public, the main design was pre-registered before
its results were computed and the auxiliary designs' sequence is documented in
the failure log, and the failures are on the record — so that a reader
who disagrees with our interpretation can check the estimates without taking
our word for anything.

---

### 8.1 A research ledger: data sources, experiments, and what was checked

A paper that has been through this many revisions owes the reader an accounting
of what was actually done. This section records the data sources consulted, the
volume of computation behind the tables, the literature the design rests on, and
the verification procedure applied to every number and every figure.

**Table 13. Data sources consulted, with volume and disposition**

| Source | Contents | Volume | Used for | Disposition |
|---|---|---|---|---|
| TED CAN, 11 annual extracts (EU Open Data Portal) | Award notices, 75 fields | 750 MB | Archived v6.0; country-year and contract panels | Award-value running variable rejected |
| TED CN, 11 annual extracts (EU Open Data Portal) | Contract notices, 64 fields incl. pre-award estimate | 300 MB | **v7.0 main design** | Running variable of record |
| OpenTender / OCP Data Registry (Austria 2013–2020, Czechia 2020) | OCDS records merging TED with national portals, incl. below-threshold contracts | 23 MB | Test of whether below-threshold coverage rescues the selection problem | Bidder field records only the winner |
| GitHub repository `procurement-disclosure-null` | Shipped analysis panels (252 country-year cells, 16,429 contract cells) and estimator library | 2.4 MB | v3.0/v4.0 reproduction | Reproduced exactly, 252/252 cells |
| EU legal instruments (Regs. 1269/2011, 1336/2013, 2015/2170, 2017/2365, 2019/1828, 2021/2170) | Statutory threshold schedules | — | Table 1; correction of the archived schedule | Basis of the re-run |

Three points about that table matter. The **TED CAN** extracts are the only
source with a usable competition outcome for the full EU-28, but their running
variable is the awarded value, which buyers can influence; that is why the
archived design's placebo profile fails. The **TED CN** extracts fix the running
variable and are the basis of the main design. The **OpenTender** merge was
tested specifically because it is the only public source that adds
below-threshold contracts, which is the selection problem in its purest form:
Austria's national-portal supplement puts 56–66% of notices below the supply
threshold, so the below-side population is observable there. It fails on the
outcome instead — cross-validated against TED for the same above-threshold
contracts, OpenTender reports a 86–89% single-bidder share where TED reports
24–27%, because its `bids.details[].tenderers` array records the winning
bidder rather than the bidder list. The Czech extract was checked as a second
case and fails the same way. Both are documented rather than silently dropped,
because the natural next question is why nobody has run this design on
below-threshold data, and the answer is that the bid counts are not in the
public record.

**Computation.** The paper rests on 40 analysis scripts in `analysis/`, five
main-pipeline scripts in `identification/`, twelve figure builders in
`figures/`, and two panel builders in `data/` (11,250 lines across 63 Python
files), 55 machine-readable result files, and 556 automated checks that
re-derive every number in the text from the archived JSON. The largest samples
processed are 6.88 million award notices for the country-year panel (the raw
2013–2021 award extracts, before the paper's filters), 4.69
million contract notices for the main design, and 5.92 million contracts for the
contract-level event study. Every specification in Table 12 was run at least
once and is reproducible from the shipped scripts.

**Literature.** The design rests on Callaway and Sant'Anna (2021) and Sun and
Abraham (2021) for staggered-adoption estimation, with Goodman-Bacon (2021) for
the forbidden-comparison problem that motivates the event-study controls;
Imbens and Lemieux (2008), Lee and Lemieux (2020), and Gelman and Imbens (2019)
for the discontinuity specification; McCrary (2008) and Cattaneo, Jansson, and Ma
(2020) for manipulation testing; Calonico, Cattaneo, and Titiunik (2014) for
robust intervals; Saez (2010) and Chetty, Friedman, Olsen, and Pistaferri (2011)
for the bunching estimator; Holm (1979) and Romano and Wolf (2016) for
multiple-testing control; Borusyak, Jaravel, and Spiess (2024) for event-study
efficiency. The substantive procurement literature the paper is positioned
against is Coviello and Mariniello (2014), who find that a publicity threshold
raises entry — the result our null stands against — together with Palguta and
Pertold (2017) on threshold manipulation, Bandiera, Prat, and Valletti (2009) on
procurement waste, Decarolis (2014) on awarding price and reputation, Fazekas,
Tóth, and King (2016) and Fazekas and Kocsis (2020) on single bidding as a
corruption-risk indicator, and Besley and Burgess (2002) on responsiveness.

**Verification of figures and tables.** Every figure was regenerated from a
machine-readable data file whose values are checked against the result archive
by the same script that checks the text: Figure 1 from the bin means and local
linear fits of the main sample, Figure 2 from the four primary estimates and
their intervals, Figure 3 from the notice-density histogram, Figure 4 from the
bandwidth-by-polynomial grid, and Figure 5 from the decile means of the
participation panel. Two inconsistencies were found and corrected in the course
of this audit: the figures were still drawn on the archived award-value running
variable after the main design had moved to the notice estimate, and one
estimation script was silently dropping the contract-type dummies from its
control set, which had briefly moved the headline by a tenth of a point. Both
are recorded here because the audit trail is the point.

## 9. Conclusion and Policy Implications

The closest precedent is Coviello and Mariniello (2014), who run a regression
discontinuity at the Italian publicity threshold and find that the publicity
requirement raises entry, raises winning rebates, and shifts winners toward
large out-of-region firms. That paper's identifying variation is a
publicity threshold within a single national register, where the below-threshold
comparison group is observable because Italian authorities publish below the
line. Our design faces the same question at the EU threshold, where the
below-threshold comparison group is not observable by construction, and the
answer is a null with a stated resolution rather than a positive effect.

**The two results are not in direct contradiction, and the reasons are worth
stating because they define what this paper does and does not contest.** Three
differences separate the designs. First, visibility: the Italian comparison
group is observed because Italian authorities publish below the line, so that
paper estimates an effect within the published record, while our below-threshold
side is selected into observation by voluntary or national publication — the
threat Section 2.3 declares and Section 7.1's density slope exemplifies — so
our continuity assumption is exposed in a way theirs is not. Second, the
threshold's level and hence the contract it binds: the Italian publicity
threshold sits far below the EU's €209,000 / €5.2 million pair, so the
near-threshold contracts are small ones for which the marginal information in a
publicity requirement is large; an EU-threshold works contract of €5 million is
already visible to the market through other channels, and the incremental
publicity content of crossing the line is plausibly small. Third, the
institution's age: the Italian requirement was new when it bound, while the
2014 directive coordinated practices that member states had already partly
adopted, so the treatment is a reform in one case and a harmonization in the
other. A null in the second setting is therefore not evidence against a
positive effect in the first — the two designs measure publicity requirements
of different marginal force, on differently visible comparison groups, at
different institutional moments — and this paper claims only the narrower
result: at the EU threshold, on the legally correct running variable, no
specification we can run detects a competitive gain, and the first stage the
regime would need in order for that null to be read as the reform's inefficacy
cannot be shown from the record.

Does transparency increase competition? On the evidence of 4.69 million EU
contract notices matched to 3.97 million award notices, three designs, and a
statutory cutoff fixed by law — one that no participant can move, although
buyers can influence the contract values reported against it and can split
contracts around it — the honest answer has two halves, and both belong in the
record.

**The main specification does not provide an estimate of a competitive effect
that is statistically distinguishable from zero, and it is now run on the
variable the law uses.** The threshold discontinuity re-specified on the
contract notice's published estimate — the variable the directive's threshold
legally applies to, fixed before bids close and therefore immune to award-stage
manipulation — gives **−0.67 pp on the single-offer share (SE 1.46, p = 0.650,
95% CI [−3.66, +2.32], n = 179,065)**, with effects larger than roughly 4.2
points excluded at 80% power. The point estimate leans toward the premise's
direction without reaching significance, which is the absence of a detectable
effect rather than evidence for the premise; and the estimate is fragile in a
way the paper discloses rather than hides — the first version of this design
silently dropped every Greek notice through a country-code mapping error, and
correcting it moved the point estimate from +0.49 to −0.67 without changing any
verdict (Section 6.1). One outcome does move: the foreign-winner share
falls by 1.21 pp (SE 0.49, p = 0.019) at the cutoff, an effect that survives
controlling for the awarded value and is therefore a discontinuity rather than a
smooth size gradient, but that is concentrated in 2020–2023
and is reported as a finding about the threshold regime rather than
about disclosure. That specification passes the diagnostics the
archived award-value version failed: seven placebo cutoffs with no significant
jump, balanced composition on both sides of the line, and no density
discontinuity distinguishable from sampling noise — though the density shape on
this sample is a below-side slope, thinner far below the line, which is the
visibility-selection pattern of Section 2.3 rather than a jump at the cutoff.
The archived estimate on the
awarded value, +1.27 pp (SE 0.71, p = 0.085, CI [−0.19, +2.72]) under the
statutory schedule and +0.82 (p = 0.234) under the erroneous one, is retained in
the record because the audit trail matters — Section 7.4 reports the threshold
error, the end-to-end re-run from the raw notices that corrects it, and the
validation that the re-run reproduces the archive exactly when the wrong cutoffs
are supplied — and because its placebo profile, four significant jumps out of
sixteen fake cutoffs, is the evidence that the running variable had to change.
The headline is therefore a null with a
stated resolution rather than a clean zero, and its point estimate sits on the
premise's side of zero at a magnitude the design cannot distinguish from noise.
Failing to reject the null is not proving it: the design detects effects
of about 4.2 percentage points or larger, and a gain of that size is exactly
what the intervals leave open. Two status questions attach to the threshold
estimate specifically. The first concerns the pre-registered density test. The
frozen implementation of that test rejects symmetry at the cutoff
(Section 7.1), which would trigger the frozen rule's downgrade; the audit
in that section traces the rejection to an asymmetric bin construction and
finds no detectable asymmetry under corrected tests, so the headline
estimate is reported with the audit on the record rather
than as a downgraded verdict. The second concerns the threshold schedule
itself: the 2013–2017 values the archived run used were wrong, the design has
since been re-run end to end from the raw contract award notices with the
statutory cutoffs, and the correction moves the headline from +0.82 to +1.27 —
toward the sign the premise excludes and toward the edge of significance, not
away from either. The third concerns the placebo battery, and it is the most serious of the
three. Executed on a ±40% extraction with each pre-registered cutoff given its
own neighbourhood (Table 10), three of the four cutoffs are unremarkable and the
fourth is not: at 130% of the threshold the estimate is −1.14 pp
(SE 0.37, p = 0.005, 95% CI [−1.90, −0.37]), significant at 5% and surviving a
Bonferroni correction for four tests and a Holm correction of the five-test
family. The pre-registered rule states that any
significant placebo marks the estimator as threatened, and by that rule this
design is threatened. The eighth round's cutoff profile (Table 11) rules out
the comfortable reading in both directions: the linear estimates across
sixteen cutoffs oscillate inside a band of roughly ±1.3 points with no
monotone drift, so the 130% result is not a smooth gradient being picked up as
a level shift; but it sits only 1.7 residual standard deviations below the
local trend of its neighbours, and the 1.25τ and 1.35τ points are negative as
well, so it is not an isolated data feature either. What survives is the
damaging reading: the linear specification's estimate moves by more than the
headline's own magnitude as the cutoff moves — and collapses to +0.12
(p = 0.906) under the quadratic — so the design's own diagnostics cannot
certify the headline as a discontinuity rather than as the local slope of a
curved conditional mean. The identifying assumption is unsupported by the
design's own test. Earlier drafts of this paper described the estimator as
calibrated on the placebo evidence; that language is withdrawn.

**The alternative specifications return larger positive estimates, and they
carry model, sample, and identification sensitivities that keep them from
settling the question.** Excluding the threshold neighborhood moves the
estimates to +1.65 to +2.13 pp — family-wise significant under a linear
specification with
contract-type controls, insignificant under a quadratic one, and computed on
the full sample rather than a selected subsample. The legally correct running
variable returns +1.22 pp (p = 0.256), significant under no control set, and
rests on the 46% of the threshold sample where the
notice-level estimate is interpretable. The donut
estimates are treated as diagnostics of the potentially contaminated threshold
neighborhood, rather than as the paper's primary findings. Neither family of specifications
identifies disclosure alone: all of them move the procedural bundle, whose
electronic-submission component does not demonstrably bind at the cutoff.

**What the evidence supports is therefore a bounded claim, not a verdict.** It
does not show that the reform significantly increased competition: the
pre-registered specifications do not, and the significant post hoc estimates
are sensitive to polynomial order and to selected subsamples. It does not show
that the reform had no effect — the
intervals exclude neither a gain of up to about 2.3 points nor a small
loss, and the estimates describe only the TED-visible sample, at the horizons
we can measure, under a threshold misclassification whose direction the design
cannot pin down, with the hidden domestic segment below the line outside the
frame entirely. What the evidence shows is that the specific mechanism the
policy narrative promised — stricter disclosure procedures raising competition
at the margin where they bind — left no detectable trace in three designs with
different failure modes, while the same record reveals a strong cross-country
association between digital depth and the SME share of tenders (from 8.7% to
54.6% across electronic-offer deciles, alongside a smaller and statistically
less conclusive within-country estimate of +7.44 pp, p = 0.095); the available
evidence does not establish how much of the cross-country gradient reflects
actual participation changes rather than institutional differences or
reporting practices. At the margin itself, the pre-registered density test
does not deliver the evasion it was built to catch: its rejection of
symmetry is an artifact of an asymmetric bin construction, and the
corrected tests find no detectable bunching below the line — with the one
sharp feature of the histogram a mass point *at* the threshold, a
reporting convention of a handful of national feeds rather than avoidance
(Section 7.1).

**The results point to what should be tested next.** The design that would
answer the policy question has to separate the elements this paper moves
together: transparency (publication), e-procurement (electronic submission),
and the procedural apparatus (deadlines, standardized forms, compliance
costs). Variation that shifts one element while holding the others fixed — a
national e-submission mandate without a publication change, a transparency
portal without a deadline change — is the missing evidence, and until it
exists, estimates like ours bound the bundle rather than the mechanism. The
confounding is not a defect of this paper's designs alone; it is built into the
reform as enacted.

Three implications follow, in decreasing order of confidence.

**First, disclosure is not accountability.** The instrument the directive mandates is the transparency channel with the machinery removed — no
performance loops, no redundant oversight, no penalties that bite. Our results
are consistent with that distinction — an interpretation, not an
identification result: no specification excludes a competitive gain of up to
about 2.3 percentage points, while the participation gradient across digital depth
is an order of magnitude larger. Policy designers who
read "e-procurement platform built" as "market disciplined" have skipped the
hard part. The platform is necessary infrastructure; it is not the reform.

**Second, if participation is the goal, the gradient is consistent with a
channel worth testing.** The SME gradient from 8.7% to 54.6% across
electronic-offer deciles is the largest association in this paper. It is also
the least causally secure: the cross-section cannot separate digital depth from
the institutions that accompany it, and the within-country estimate that can
(+7.44 pp) is only marginally significant. The reporting-artifact caveat cuts
the same way — part of the gradient is a change in who publishes, not in who
bids. The honest summary is therefore not that lowering entry costs works, but
that it is consistent with a participation channel worth testing; it cannot yet
be read as a policy lever. A second caution follows. If more entrants merely
thicken the loser pool while preferred bidders keep winning, participation
gains can coexist with unchanged welfare. The SME tender share measures who
bids, not who wins; the firm-level matching extension of Section 3.3 is where
that question gets answered, and until it is, we flag the gap rather than
assume it away.

**Third, police the margin.** The threshold creates two markets — a compliant
one and a domestic one below the line that no disclosure-based monitoring
system, including ours, can see. This paper's density audit finds no
detectable bunching at the cutoff, but that is a statement about what the
published record can see, not about what happens below it: a contract split
or shaved so that every lot falls under the threshold never appears in TED
at all, so the audit capacity would have to sit below the line to catch it.
Thresholds that can be gamed by splitting invite gaming; the
policy question is not whether to publish, but whether publication is
accompanied by the audit capacity to notice what happens just below the
line.

**What this paper does not say.** It does not say that transparency is
worthless, that the directive failed, or that digital procurement platforms
should not be built. It does not say that the competitive effect is exactly
zero — and the two intervals that bound that statement belong to two different
designs, so we state both rather than let one stand for the paper. The current
main design, on the legally correct running variable, runs from −3.66 to +2.32
points: it excludes neither a competitive gain of up to about 2.3 points nor a
small loss, and it is a null with a stated resolution of about 4.2 points. The
archived v6.0 award-value design under the corrected threshold schedule runs
from −0.19 to +2.72, so a gain of up to about 2.7 points is exactly what it
cannot exclude. What it says is narrower and, we think, more useful: the
pre-registered v6.0 specification — the archived award-value design under the
corrected threshold schedule, superseded as the headline by the v7.0
re-specification — does not yield a statistically detectable competitive gain
(+1.27 pp, SE 0.71, p = 0.085). Some alternative control
configurations and diagnostic specifications produce positive estimates that
cross conventional significance — most visibly +1.36 (p = 0.047) when the
log-value control is dropped and the donut specifications at ±1% to ±3% — but
these are not the pre-registered specification, they move with polynomial
order, and they are reported as diagnostics rather than as the headline. The first stage was real: procurement
digitalized. The data reveal a strong cross-country association between
digital depth and the SME share of tenders, alongside a smaller and
statistically less conclusive within-country estimate; the available evidence
does not establish how much of the cross-country gradient reflects actual
participation changes rather than institutional differences or reporting
practices. What did not happen is the specific thing the policy narrative
promised: the EU transparency-and-procedure bundle, as implemented, left no
detectable competitive trace. The designs cannot isolate disclosure alone, and
we do not claim they can — the bundle did not deliver a detectable gain, which
is a smaller claim than "transparency does not work," and a more useful one
than the promise it replaces.

**One pre-registered diagnostic has been executed, and it goes against the
design.** The placebo battery was pre-registered at four cutoffs — 70, 80, 120,
and 130% of the true threshold — and the archived run produced a single figure
from it: at the 80% cutoff, a jump of −5.15 points (p = 0.146) whose standard
error near 3.5 points shows it was estimated on 104 contracts against 326,614,
because the ±20% analysis band leaves three of the four cutoffs with no
comparison group at all. Executed on a ±40% extraction with each cutoff given
its own neighbourhood (Table 10), three cutoffs are unremarkable and the fourth
is not: **at 130% of the threshold the estimate is −1.14 points (SE 0.37,
p = 0.005,
95% CI [−1.90, −0.37]), significant at 5% and surviving a Bonferroni correction
for four tests and a Holm correction of the five-test family.** The
pre-registered rule states that any significant placebo
marks the estimator as threatened, and by that rule this design is threatened.
The eighth round's cutoff profile (Table 11) rules out the comfortable reading
in both directions: the linear estimates across sixteen cutoffs oscillate
inside a band of roughly ±1.3 points with no monotone drift, so the 130%
result is not a smooth gradient being picked up as a level shift; but it sits
only 1.7 residual standard deviations below the local trend of its neighbours,
and the 1.25τ and 1.35τ points are negative as well, so it is not an isolated
data feature either. What survives is the damaging reading: the linear
specification's estimate moves by more than the headline's own magnitude as the
cutoff moves — and collapses to +0.12 (p = 0.906) under the quadratic — so the
design's own diagnostics cannot certify the headline as a discontinuity rather
than as the local slope of a curved conditional mean. The identifying
assumption is therefore unsupported by the design's own test. Earlier drafts
described the estimator as calibrated on the placebo evidence; that language is
withdrawn, and
the threshold design's numbers should be read with the 130% result attached to
them.

---

## References

Arkhangelsky, D., S. Athey, D. A. Hirshberg, G. W. Imbens, and S. Wager. 2021.
"Synthetic Difference in Differences." *American Economic Review* 111 (12):
3828–3874.

Bandiera, S., A. Prat, and T. Valletti. 2009. "Active and Passive Waste in
Government Spending: Evidence from a Policy Experiment." *American Economic
Review* 99 (4): 1278–1308.

Besley, T., and R. Burgess. 2002. "The Political Economy of Government
Responsiveness: Theory and Evidence from India." *Quarterly Journal of
Economics* 117 (4): 1475–1511.

Borusyak, K., X. Jaravel, and J. Spiess. 2024. "Revisiting Event Study Designs:
Robust and Efficient Estimation." *Review of Economic Studies* 91 (6):
3253–3285.

Callaway, B., and P. H. C. Sant'Anna. 2021. "Difference-in-Differences with
Multiple Time Periods." *Journal of Econometrics* 225 (2): 200–230.

Calonico, S., M. D. Cattaneo, and R. Titiunik. 2014. "Robust Nonparametric
Confidence Intervals for Regression-Discontinuity Designs." *Econometrica* 82
(6): 2295–2326.

Chetty, R., J. N. Friedman, T. Olsen, and L. Pistaferri. 2011. "Adjustment
Costs, Firm Responses, and Micro vs. Macro Labor Supply Elasticities: Evidence
from Danish Tax Records." *Quarterly Journal of Economics* 126 (2): 751–816.

Cattaneo, M. D., M. Jansson, and X. Ma. 2020. "Robust Nonparametric
Confidence Intervals for Treatment Effects in Regression Discontinuity Designs."
*Journal of the American Statistical Association* 115 (531): 1511–1525.

Coviello, D., and M. Mariniello. 2014. "Publicity Requirements in Public
Procurement: Evidence from a Regression Discontinuity Design." *Journal of
Public Economics* 109 (C): 76–100.

Decarolis, F. 2014. "Awarding Price and Reputation in Procurement." *Journal of
Public Economics* 110: 55–72.

European Commission. 2017. "Report from the Commission to the European
Parliament and the Council on the Review of the European Single Procurement
Document." COM(2017) 242 final. Brussels: European Commission.

European Parliament and Council of the European Union. 2014. "Directive
2014/24/EU on Public Procurement and Repealing Directive 2004/18/EC." *Official
Journal of the European Union* L 94: 65–131.

Fazekas, M., and G. Kocsis. 2020. "Beyond the Basics: How Do Public Procurement
Indicators Measure Corruption?" *Public Administration Review* 80 (5): 767–778.

Fazekas, M., I. J. Tóth, and L. P. King. 2016. "An Objective Corruption Risk
Index Using Public Procurement Data." *European Journal on Criminal Policy and
Research* 22 (3): 367–392.

Gelman, A., and G. Imbens. 2019. "Why High-Order Polynomials Should Not Be Used
in Regression-Discontinuity Designs." *Journal of Business and Economic
Statistics* 37 (3): 447–456.

Goodman-Bacon, J. 2021. "Difference-in-Differences with Variation in
Treatment Timing." *Journal of Econometrics* 225 (2): 254–277.

Imbens, G. W., and T. Lemieux. 2008. "Regression Discontinuity Designs: A Guide
to Practice." *Journal of Econometrics* 142 (2): 615–635.

Klemperer, P. 2004. "Auctions: A Survey." *Economic Journal* 114 (492): F1–F42.

Lee, D. S., and T. Lemieux. 2020. "Regression Discontinuity Designs in
Economics." *Journal of Economic Literature* 58 (4): 897–942.

McCrary, J. 2008. "Manipulation of the Running Variable in the Regression
Discontinuity Design: A Density Test." *Journal of Econometrics* 142 (2):
698–714.

OECD. 2015. *OECD Recommendation of the Council on Public Procurement*.
OECD/LEGAL/0406. Paris: OECD Publishing.

Palguta, J., and F. Pertold. 2017. "Manipulation of Procurement Contracts:
Evidence from the Introduction of Discretionary Thresholds." *American Economic
Journal: Economic Policy* 9 (2): 182–213.

Romano, J. P., and M. Wolf. 2016. "Efficient Computation of Adjusted
p-Values for Resampling-Based Stepdown Multiple Testing." *Mathematics and
Computers in Simulation* 125: 66–74.

Saez, E. 2010. "Do Taxpayers Bunch at Kink Points?" *American Economic Journal:
Economic Policy* 2 (3): 180–212.

Sun, L., and S. Abraham. 2021. "Estimating Dynamic Treatment Effects in Event
Studies with Heterogeneous Treatment Effects." *Journal of Econometrics* 225
(2): 175–199.

Transparency International. 2024. "Corruption Perceptions Index."
https://www.transparency.org/en/cpi.

---

*Code, data manifests, pre-registration, and failure log:*

*https://github.com/TSUBARAYA/procurement-disclosure-null (MIT license).*

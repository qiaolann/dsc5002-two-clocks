# Two clocks, one comparison

**Calendar- versus age-anchored views of functional health in China and England, 2011–2018**

[**English**](README.md) · [简体中文](README.zh-CN.md)

DSC5002 Exploratory Data Analysis and Visualization — group project
Hanchao LIU · Bojun SONG · Haonan QI · Zhengyuan LI · Bin LIAO · Zhirui CHEN

---

## The question

Cross-national comparisons of ageing are usually made on the **calendar clock**: take the same survey year in each country, average the outcome, read off the gap. The trouble is that the two samples are not the same age, and their age mix changes as panels age and refresh. An alternative is the **age clock**: compare people of the same age, whichever round they were observed in.

This project asks what each clock says about the same data, and how far apart the two answers are. The outcome is functional limitation — the count of activities of daily living (bathing, dressing, eating, getting in and out of bed, using the toilet; 0–5) and instrumental activities (managing money, taking medication, shopping, preparing meals; 0–4).

## The answer in one paragraph

On the calendar clock the China–England gap is small and stable: **+0.07** ADL limitations across four rounds. On the age clock the same data give **−0.05 at age 50 and +0.33 at age 79**, because ADL limitations rise about **2.3 times faster** with age in China on the count scale (IADL, 4.4 times). The two readings agree only around age 55–60. Neither is wrong; they answer different questions, and reporting one without the other invites the wrong inference.

## Data

Two harmonised HRS-family panel surveys, taken from the Gateway to Global Aging Data files.

| | CHARLS (China) | ELSA (England) |
| --- | --- | --- |
| Population | adults 45+, spouses regardless of age | adults 50+, private households |
| Rounds used | waves 1–4 (2011, 2013, 2015, 2018) | waves 5, 6, 7, 9 (2010–11 … 2018–19) |
| Round pairing | by fieldwork midpoint; average mismatch ≈ 0.8 years | |
| Person-rounds, ages 50–79 | 59,049 | 33,362 |
| Unique respondents | 21,177 | 12,162 |

The two files share the same variable definitions because both were harmonised against the US HRS, so `rWadlfive` and `rWiadlfour` are built from identical item batteries in both countries. Two natural outcomes were excluded after inspection: self-rated health (not fielded in CHARLS wave 4) and immediate word recall (a within-age-band break of 0.4–0.9 words in CHARLS wave 4, larger than the entire age gradient, consistent with a change in test administration).

## Design

- **Axis A, calendar anchoring** — mean limitation counts per round with 95% intervals, plus the composition and sample flow that sit behind those means.
- **Axis B, age anchoring** — the outcome regressed on age (centred at 65) with round fixed effects, separately by country, standard errors clustered on the person; a pooled model with an age × country interaction tests whether the gradients differ.
- **The gap curve** — country differences predicted at every age from 50 to 79 by simulating 2,000 draws from the coefficient distribution.
- **Robustness** — dropping round 1 (CHARLS wave-1 IADL runs about 0.06 high), adding the harmonised education indicator, person fixed effects, and two alternative link functions (Poisson for the count, logit for having any limitation).

Estimates are unweighted and describe the samples, not the national populations.

## Key numbers

| | China | England | Contrast |
| --- | --- | --- | --- |
| ADL slope, per year (0–5 scale) | 0.0221 (0.0207–0.0235) | 0.0094 (0.0078–0.0110) | 2.36× (1.93–2.79) |
| IADL slope, per year (0–4 scale) | 0.0207 (0.0194–0.0219) | 0.0047 (0.0036–0.0058) | 4.39× (3.30–5.47) |
| Same contrast, Poisson (log rate) | | | 1.77× / 1.66× |
| Same contrast, logit (any limitation) | | | 1.35× / 1.87× |
| Calendar-anchored gap, ADL | | | +0.072 |
| Age-anchored gap, ADL at 50 / 65 / 79 | | | −0.047 / +0.146 / +0.326 |
| Share worsening over seven years | 18% | 12% | |

The direction of the contrast survives every specification; its **size depends on the scale**, which is why the report quotes the count-scale multiplier together with a caveat.

## Repository layout

```
code/                 analysis pipeline, run in this order
  xj_common.py        paths, colour scheme, round mapping, CI helper
  01_extract.py       .dta / .tab  ->  parquet, only the needed columns
  04_build_panel.py   wide -> long, ages 50-79, four matched rounds
  05_analysis.py      descriptives, age models, gap decomposition, robustness
  05b_link_functions.py  Poisson and logit variants, scale comparison
  06_figures.py       the ten figures
  10_tables.py        the two tables
  09_typeset.py       markdown -> A4 PDF
  07_build_report.py  markdown -> docx
  02_*, 03_*          exploration and data-quality checks kept for provenance

output/figures/       ten figures (PNG 300 dpi + PDF), two table images
output/tables/        every number quoted in the report, as CSV
report/               the submitted report (PDF)

Group project/        raw survey data - not tracked here (large, course licence)
data_clean/           derived caches - not tracked here (regenerated by the pipeline)
```

## Figures

| # | File | Shows |
| --- | --- | --- |
| 1 | `F1_design` | how the four rounds are paired in fieldwork time |
| 2 | `F2_calendar_anchored` | calendar view: both series flat, gap small |
| 3 | `F3_composition` | how the age mix shifts as samples refresh |
| 4 | `F4_sample_flow` | attrition versus refreshment in the two panels |
| 5 | `F5_age_adl` | age view for ADL, gradients crossing near 54 |
| 6 | `F6_age_iadl` | age view for IADL, steeper divergence |
| 7 | `F7_gap_by_age` | the two clocks on one axis — the central result |
| 8 | `F8_within_person` | who actually changes: worsening is a minority |
| 9 | `F9_slope_robustness` | four specifications, and the multiplier by scale |
| 10 | `F10_diabetes` | a counter-example where the calendar axis moves |

## Reproducing

The raw files are not in this repository. With `GH_CHARLS_d2.dta` and `gh_elsa_h.tab` placed under `Group project/`:

```bash
python -u code/01_extract.py
python -u code/04_build_panel.py
python -u code/05_analysis.py
python -u code/05b_link_functions.py
python -u code/06_figures.py
python -u code/10_tables.py
python -u code/09_typeset.py
```

Requirements: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `pymupdf`; `python-docx` for the editable report (a copy is vendored under `code/vendor`).

## Interpretation notes

- The age gradient from a cross-section combines age with cohort of birth; person fixed effects remove the cohort component but introduce attrition selection.
- Self-reported difficulty is filtered through expectation and adaptation. Harmonised items reduce this but do not remove it, and there are no anchoring vignettes here to test it. This is the largest threat to the cross-national comparison.
- Diabetes is measured as "ever told by a doctor", so its calendar trend mixes incidence with diagnosis.
- Which axis is informative depends on the outcome: for functional limitation the age axis carries the finding, for diabetes the calendar axis does.

## References

Zhao Y, Hu Y, Smith JP, Strauss J, Yang G. Cohort profile: the China Health and Retirement Longitudinal Study (CHARLS). *International Journal of Epidemiology*. 2014;43(1):61–68.

Steptoe A, Breeze E, Banks J, Nazroo J. Cohort profile: the English Longitudinal Study of Ageing. *International Journal of Epidemiology*. 2013;42(6):1640–1648.

Gateway to Global Aging Data. *Harmonized CHARLS Documentation, Version D.2*; *Harmonized ELSA Documentation, Version H*.

Katz S, Ford AB, Moskowitz RW, Jackson BA, Jaffe MW. Studies of illness in the aged: the index of ADL. *JAMA*. 1963;185:914–919.

Lawton MP, Brody EM. Assessment of older people: self-maintaining and instrumental activities of daily living. *The Gerontologist*. 1969;9(3):179–186.

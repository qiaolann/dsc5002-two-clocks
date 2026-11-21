"""Trim the compact tex a little further: smaller figures, one-line captions,
tighter float glue, and about 100 words of prose removed."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(os.path.dirname(HERE), "report", "report.tex")

with open(TEX, encoding="utf-8") as f:
    s = f.read()

orig_len = len(s)

# 1. tighter float glue
s = s.replace(
    "\\setlength{\\textfloatsep}{6pt plus 2pt minus 2pt}\n"
    "\\setlength{\\floatsep}{6pt plus 2pt minus 2pt}\n"
    "\\setlength{\\intextsep}{6pt plus 2pt minus 2pt}\n"
    "\\setlength{\\abovecaptionskip}{2pt}\n"
    "\\setlength{\\belowcaptionskip}{1pt}",
    "\\setlength{\\textfloatsep}{4pt plus 1pt minus 1pt}\n"
    "\\setlength{\\floatsep}{4pt plus 1pt minus 1pt}\n"
    "\\setlength{\\intextsep}{4pt plus 1pt minus 1pt}\n"
    "\\setlength{\\abovecaptionskip}{1pt}\n"
    "\\setlength{\\belowcaptionskip}{0pt}")

# 2. smaller figures
s = s.replace("width=0.92\\textwidth", "width=0.86\\textwidth")
s = s.replace("width=0.96\\textwidth", "width=0.90\\textwidth")

# 3. one-line captions
caps = [
 ("Four calendar-matched rounds. CHARLS waves 1--4 (orange) are paired with the closest ELSA wave (blue); dashed lines connect fieldwork midpoints.",
  "Calendar matching: CHARLS waves 1--4 paired with the closest ELSA wave; dashed lines join fieldwork midpoints."),
 ("Calendar-anchored means with 95\\% intervals. Both series are close to flat and the gap is small.",
  "Calendar-anchored means (95\\% intervals): both series flat, gap small."),
 ("Why the calendar means cannot be read directly. Left: age-band composition by round. Right: respondents per round---China grows through refreshment, England shrinks.",
  "Composition and sample flow: age-band shares by round (left), respondents per round (right)."),
 ("Age-anchored view. Hollow points are 5-year bin means (95\\% CI); lines are the fitted gradient from the within-round model with 95\\% bands. The ADL lines cross near age 54.",
  "Age-anchored view: 5-year bin means (95\\% CI) and fitted gradients (95\\% bands); ADL lines cross near 54."),
 ("The same comparison along the age axis. The rising curve is the predicted gap at each age; the flat dashed line with its band is the unadjusted calendar gap.",
  "Both readings on one axis: the predicted gap by age (curve) and the unadjusted calendar gap (dashed)."),
 ("Within-person change in the ADL count. Left: share whose count rose between consecutive rounds (95\\% CI). Right: cumulative change between round 1 and round 4.",
  "Within-person change: share worsening between rounds (left), cumulative change 1$\\rightarrow$4 (right)."),
 ("Robustness. Left and centre: slopes under four specifications (hollow = variants). Right: the China-to-England multiplier under three link functions on a log axis; all intervals sit above one, but the multiplier shrinks from 2.4 to 1.4 with the scale.",
  "Robustness: slopes under four specifications (left, centre) and the China-to-England multiplier under three link functions (right)."),
 ("A different outcome, a different picture. Left: prevalence by age. Right: age-standardised prevalence by round.",
  "A different outcome: diabetes prevalence by age (left) and age-standardised by round (right)."),
]
for a, b in caps:
    assert a in s, a[:50]
    s = s.replace(a, b)

# 4. prose trims
trims = [
 ("IADL averages 0.40 and 0.14, then 0.36 and 0.15. The gap averages $+0.072$ ADL and $+0.216$ IADL points, varying by about 0.03 across rounds. A reader would conclude that older Chinese adults report somewhat more limitation and that the gap is stable.",
  "IADL averages 0.40 and 0.14, then 0.36 and 0.15. The gap averages $+0.072$ ADL and $+0.216$ IADL points, varying by about 0.03 across rounds: older Chinese adults report somewhat more limitation, and the gap looks stable."),
 ("The cohort's mean age rises only about five years over seven years of fieldwork, so older respondents left faster. China adds 3,000--3,300 respondents per round against 1,900--2,500 losses; England's losses overtake refreshment from 2015 and its sample shrinks by about 1,000 per round. Ageing and replacement are happening at once, and the flat series are their net.",
  "The cohort's mean age rises only about five years over seven of fieldwork, so older respondents left faster. China adds 3,000--3,300 per round against 1,900--2,500 losses; England's losses overtake refreshment from 2015. Ageing and replacement happen at once, and the flat series are their net."),
 ("We ask how large the China--England gap is on each clock, whether the age gradients differ, and how much the choice of clock changes the number a reader takes away. On the calendar clock the gap is small and stable (+0.07 ADL); on the age clock it runs from $-0.05$ at 50 to $+0.33$ at 79, because limitations rise 2.3 times faster with age in China. The readings answer different questions, but reporting only one invites the wrong inference.",
  "We ask how large the gap is on each clock, whether the age gradients differ, and how much the choice of clock changes the reader's answer. Calendar: a small, stable +0.07 ADL. Age: $-0.05$ at 50 rising to $+0.33$ at 79, because limitations rise 2.3 times faster with age in China. Reporting only one clock invites the wrong inference."),
 ("\\emph{Care environment}: adaptations and assistive technology may delay limitation in England, but we measure none of it, so this stays a hypothesis.",
  "\\emph{Care environment}: adaptations may delay limitation in England, but we measure none of it, so this stays a hypothesis."),
]
for a, b in trims:
    assert a in s, a[:50]
    s = s.replace(a, b)

with open(TEX, "w", encoding="utf-8", newline="\n") as f:
    f.write(s)
print("chars:", orig_len, "->", len(s))

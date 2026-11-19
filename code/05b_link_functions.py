"""Step 5b: the same age model under two alternative link functions.

The count outcomes are sparse (82-85% of respondents report zero limitations), so
a linear model is a convenience. Here we re-estimate the gradient with a Poisson
model for the count and a logistic model for "any limitation", and record how the
China/England contrast changes. Log-link models give log-rate / log-odds slopes,
so the country contrast is reported as a ratio of ratios.

Output: output/tables/T6_link_functions.csv
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xj_common as COMMON  # noqa: E402

panel = COMMON.load_panel()
panel["eng"] = (panel["country"] == "England").astype(int)
panel["age_c"] = panel["age"] - 65

rows = []
for var in ["adlfive", "iadlfour"]:
    d = panel.dropna(subset=[var]).copy()
    d["any"] = (d[var] > 0).astype(float)

    # ---- linear (reference; already in T3, recomputed here for the ratio)
    for country in COMMON.COUNTRIES:
        x = d[d["country"] == country]
        m = smf.ols(f"{var} ~ age_c + C(round)", data=x).fit(
            cov_type="cluster", cov_kwds={"groups": x["pid"]})
        rows.append(dict(outcome=var, link="linear", country=country,
                         est=m.params["age_c"], se=m.bse["age_c"],
                         p=m.pvalues["age_c"], n=int(m.nobs), unit="points/year"))

    # ---- Poisson (log rate)
    for country in COMMON.COUNTRIES:
        x = d[d["country"] == country]
        m = smf.poisson(f"{var} ~ age_c + C(round)", data=x).fit(
            disp=0, cov_type="cluster", cov_kwds={"groups": x["pid"]})
        rows.append(dict(outcome=var, link="poisson", country=country,
                         est=m.params["age_c"], se=m.bse["age_c"],
                         p=m.pvalues["age_c"], n=int(m.nobs), unit="log rate/year"))

    # ---- Logit (any limitation)
    for country in COMMON.COUNTRIES:
        x = d[d["country"] == country]
        m = smf.logit("any ~ age_c + C(round)", data=x).fit(
            disp=0, cov_type="cluster", cov_kwds={"groups": x["pid"]})
        rows.append(dict(outcome=var, link="logit", country=country,
                         est=m.params["age_c"], se=m.bse["age_c"],
                         p=m.pvalues["age_c"], n=int(m.nobs), unit="log odds/year"))

    # ---- pooled interaction, per link
    for link, formula, fam in [("linear", f"{var} ~ age_c * eng + C(round)", smf.ols),
                               ("poisson", f"{var} ~ age_c * eng + C(round)", smf.poisson),
                               ("logit", "any ~ age_c * eng + C(round)", smf.logit)]:
        if fam is smf.ols:
            m = fam(formula, data=d).fit(cov_type="cluster",
                                         cov_kwds={"groups": d["pid"]})
        else:
            m = fam(formula, data=d).fit(disp=0, cov_type="cluster",
                                         cov_kwds={"groups": d["pid"]})
        b, se = m.params["age_c:eng"], m.bse["age_c:eng"]
        rows.append(dict(outcome=var, link=link, country="interaction",
                         est=b, se=se, p=m.pvalues["age_c:eng"], n=int(m.nobs),
                         unit="difference"))

out = pd.DataFrame(rows)

# country contrast: ratio of slopes (linear) or ratio of ratios (log links)
summary = []
for var in ["adlfive", "iadlfour"]:
    for link in ["linear", "poisson", "logit"]:
        sub = out[(out.outcome == var) & (out.link == link)].set_index("country")
        ch, en = sub.loc["China"], sub.loc["England"]
        # ratio of slopes, i.e. how much faster the log/linear gradient rises
        ratio = ch["est"] / en["est"]
        se_r = abs(ratio) * np.sqrt((ch["se"] / ch["est"]) ** 2 +
                                    (en["se"] / en["est"]) ** 2)
        summary.append(dict(outcome=var, link=link, ratio=ratio, se_ratio=se_r,
                            ci_lo=ratio - 1.96 * se_r, ci_hi=ratio + 1.96 * se_r,
                            interaction_p=sub.loc["interaction", "p"]))
summary = pd.DataFrame(summary).round(4)

out.round(4).to_csv(os.path.join(COMMON.TABLES, "T6_link_functions.csv"),
                    index=False)
summary.to_csv(os.path.join(COMMON.TABLES, "T6b_link_ratios.csv"), index=False)
print(out.round(3).to_string(index=False))
print("\nCountry contrast (China / England):")
print(summary.to_string(index=False))

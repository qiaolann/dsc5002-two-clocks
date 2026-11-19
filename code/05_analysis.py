"""Step 5: descriptives, models and the two-anchoring decomposition."""
import os
import sys

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xj_common as COMMON  # noqa: E402

rng = np.random.default_rng(20261205)

panel = COMMON.load_panel()
panel["eng"] = (panel["country"] == "England").astype(int)

# ------------------------------------------------------------------ calendar
cal_rows = []
for (country, rnd, label), d in panel.groupby(["country", "round", "round_label"]):
    for var in ["adlfive", "iadlfour", "diabe"]:
        m, hw = COMMON.ci_mean(d[var])
        cal_rows.append(dict(country=country, round=rnd, round_label=label, var=var,
                             mean=m, ci=hw, n=int(d[var].notna().sum())))
cal = pd.DataFrame(cal_rows)
cal.to_csv(os.path.join(COMMON.TABLES, "T2_calendar_means.csv"), index=False)

# composition
comp = (panel.groupby(["country", "round", "round_label"])
        .agg(n=("pid", "size"), age=("age", "mean"), p65=("age", lambda s: (s >= 65).mean()))
        .reset_index())
comp.to_csv(os.path.join(COMMON.TABLES, "T2b_composition.csv"), index=False)

# baseline-cohort only (observed in round 1) -> shows the refreshment effect
base_ids = set(panel.loc[panel["round"] == 1, "pid"])
coh = panel[panel["pid"].isin(base_ids)]
comp_coh = (coh.groupby(["country", "round", "round_label"])["age"].mean()
            .reset_index().rename(columns={"age": "age_baseline_cohort"}))
comp_coh.to_csv(os.path.join(COMMON.TABLES, "T2c_baseline_cohort_age.csv"), index=False)

# ---------------------------------------------------------------------- models
FORM = "{y} ~ age_c * eng + C(round)"


def fit(df, formula):
    d = df.dropna(subset=formula.split("~")[0].strip())
    res = smf.ols(formula, data=d).fit(cov_type="cluster",
                                       cov_kwds={"groups": d["pid"]})
    return res, d


def slope_table(res, label, var):
    b = res.params["age_c"]
    se = res.bse["age_c"]
    out = dict(model=label, outcome=var, term="age slope (per year)",
               est=b, se=se, ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se,
               p=res.pvalues["age_c"], n=int(res.nobs))
    return out


rows = []
for var in ["adlfive", "iadlfour"]:
    f = FORM.format(y=var)
    for country in COMMON.COUNTRIES:
        d = panel[panel["country"] == country]
        res, dd = fit(d, "{} ~ age_c + C(round)".format(var))
        r = slope_table(res, country, var)
        r["r2"] = res.rsquared
        rows.append(r)
    res, dd = fit(panel, f)
    r = slope_table(res, "pooled: England", var)
    r["r2"] = res.rsquared
    rows.append(r)
    # interaction
    b = res.params["age_c:eng"]
    se = res.bse["age_c:eng"]
    rows.append(dict(model="pooled: age x England", outcome=var,
                     term="age_c:eng", est=b, se=se,
                     ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se,
                     p=res.pvalues["age_c:eng"], n=int(res.nobs), r2=res.rsquared))
    # interaction-only p (robust F)
    ftest = res.f_test("age_c:eng = 0")
    rows[-1]["p_joint"] = float(ftest.pvalue)

slopes = pd.DataFrame(rows).round(4)
slopes.to_csv(os.path.join(COMMON.TABLES, "T3_age_slopes.csv"), index=False)
print(slopes.to_string(index=False))

# ------------------------------------------------------- predicted contrast
def predict_draws(res, newdata, n=4000):
    """Parametric simulation of predicted values from a cluster-OLS fit."""
    di = res.model.data.design_info
    X = np.asarray(patsy.build_design_matrices([di], newdata)[0])
    beta = rng.multivariate_normal(res.params.values, res.cov_params().values, n)
    return (X @ beta.T).T  # n_draws x n_rows


contrast_rows = []
AGES = np.arange(50, 80)
for var in ["adlfive", "iadlfour"]:
    res, _ = fit(panel, FORM.format(y=var))
    # rows ordered: age -> eng(0/1) -> round(1..4)
    nd = pd.DataFrame([{"age_c": a - 65, "eng": e, "round": r}
                       for a in AGES for e in (0, 1) for r in (1, 2, 3, 4)])
    draws = predict_draws(res, nd, n=2000)   # n_draws x n_rows
    draws = draws.reshape(draws.shape[0], len(AGES), 2, 4)

    ch = draws[:, :, 0, :].mean(axis=2)     # average over the 4 rounds
    en = draws[:, :, 1, :].mean(axis=2)
    diff = ch - en
    point = {"ch": ch, "en": en}
    for i, a in enumerate(AGES):
        g = diff[:, i]
        contrast_rows.append(dict(var=var, age=int(a), gap=g.mean(),
                                  lo=np.percentile(g, 2.5),
                                  hi=np.percentile(g, 97.5),
                                  china=ch[:, i].mean(), england=en[:, i].mean()))
    # keep the predicted level draws for the figures
    np.save(os.path.join(COMMON.DATA_CLEAN, f"pred_{var}.npy"), diff[:, :])
    np.save(os.path.join(COMMON.DATA_CLEAN, f"predlev_{var}.npy"),
            np.stack([ch, en], axis=1))

contrasts = pd.DataFrame(contrast_rows)
contrasts.to_csv(os.path.join(COMMON.TABLES, "T4_age_contrasts.csv"), index=False)

# calendar vs age-anchored gap summary
summary = []
for var in ["adlfive", "iadlfour"]:
    raw = (cal[cal["var"] == var].pivot(index="round", columns="country", values="mean"))
    raw_gap = (raw["China"] - raw["England"]).mean()
    ct = contrasts[contrasts["var"] == var].dropna(subset=["gap"]).set_index("age")["gap"]
    summary.append(dict(
        var=var,
        calendar_gap_unadjusted=raw_gap,
        age_matched_gap_50=ct.loc[50], age_matched_gap_65=ct.loc[65],
        age_matched_gap_79=ct.loc[79]))
summary = pd.DataFrame(summary).round(4)
summary.to_csv(os.path.join(COMMON.TABLES, "T4b_gap_summary.csv"), index=False)
print("\n", summary.to_string(index=False))

# ------------------------------------------------------------- robustness 1-3
rob = []


def add_rob(var, label, df, formula):
    res, dd = fit(df, formula)
    b, se = res.params["age_c"], res.bse["age_c"]
    row = dict(outcome=var, check=label, est=b, se=se,
               ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se, n=int(res.nobs))
    if "age_c:eng" in res.params:
        row["int_est"] = res.params["age_c:eng"]
        row["int_p"] = res.pvalues["age_c:eng"]
    rob.append(row)


for var in ["adlfive", "iadlfour"]:
    # R1: drop the first round (checks the CHARLS wave-1 IADL level shift)
    d = panel[panel["round"] >= 2]
    for country in COMMON.COUNTRIES:
        add_rob(var, f"{country} excl. round 1", d[d["country"] == country],
                f"{var} ~ age_c + C(round)")
    add_rob(var, "pooled excl. round 1", d, FORM.format(y=var))

    # R2: adjust for education (3-tier harmonised scale)
    d = panel.dropna(subset=["edu"])
    for country in COMMON.COUNTRIES:
        add_rob(var, f"{country} + education", d[d["country"] == country],
                f"{var} ~ age_c + C(round) + C(edu)")

    # R3: within-person change (person fixed effects), all with >= 2 waves
    for country in COMMON.COUNTRIES:
        d = panel[panel["country"] == country].dropna(subset=[var, "age"])
        cnt = d.groupby("pid")["round"].transform("nunique")
        d = d[cnt >= 2].copy()
        # within-transform
        cols = [var, "age_c"]
        dm = d[[var, "age_c", "pid", "round"]].copy()
        for c in cols:
            dm[c] = dm[c] - dm.groupby("pid")[c].transform("mean")
        fe = smf.ols(f"{var} ~ age_c + C(round)", data=dm).fit(
            cov_type="cluster", cov_kwds={"groups": dm["pid"]})
        b, se = fe.params["age_c"], fe.bse["age_c"]
        rob.append(dict(outcome=var, check=f"{country} within-person FE", est=b, se=se,
                        ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se, n=int(fe.nobs)))

robust = pd.DataFrame(rob).round(4)
robust.to_csv(os.path.join(COMMON.TABLES, "T5_robustness.csv"), index=False)
print("\n", robust.to_string(index=False))

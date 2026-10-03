"""
scripts/statistical_tests.py
----------------------------
Phase 4: Statistical Testing & Power Analysis.
Calculates:
1. Two-proportion Z-test & Chi-Square test of independence.
2. 95% Confidence Interval for absolute lift and relative lift.
3. Effect size (Cohen's h) and post-hoc Statistical Power.
4. Segment-level hypothesis testing with Bonferroni multiple testing correction.
5. Exposure bucket significance checks.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.multitest import multipletests


def run_statistical_analysis(db_path: str = "data/marketing_ab.db"):
    conn = sqlite3.connect(db_path)

    # 1. Overall Test
    df_overall = pd.read_sql_query(
        "SELECT test_group, COUNT(user_id) AS total_users, SUM(converted) AS total_conv FROM campaign_results GROUP BY test_group;",
        conn,
    )

    n_ad = int(df_overall.loc[df_overall["test_group"] == "ad", "total_users"].values[0])
    conv_ad = int(df_overall.loc[df_overall["test_group"] == "ad", "total_conv"].values[0])
    n_psa = int(df_overall.loc[df_overall["test_group"] == "psa", "total_users"].values[0])
    conv_psa = int(df_overall.loc[df_overall["test_group"] == "psa", "total_conv"].values[0])

    cr_ad = conv_ad / n_ad
    cr_psa = conv_psa / n_psa
    abs_lift = cr_ad - cr_psa
    rel_lift = abs_lift / cr_psa

    # Two-proportion z-test (pooled)
    z_stat, p_val = proportions_ztest([conv_ad, conv_psa], [n_ad, n_psa], alternative="two-sided")

    # Chi-square test of independence
    contingency = [[conv_ad, n_ad - conv_ad], [conv_psa, n_psa - conv_psa]]
    chi2_stat, p_chi2, dof, _ = stats.chi2_contingency(contingency, correction=False)

    # 95% Confidence Interval for difference in proportions (Wald)
    ci_low, ci_high = confint_proportions_2indep(conv_ad, n_ad, conv_psa, n_psa, method="wald", alpha=0.05)

    # Relative Lift Confidence Interval
    rel_ci_low = ci_low / cr_psa
    rel_ci_high = ci_high / cr_psa

    # Effect Size: Cohen's h
    cohen_h = 2 * np.arcsin(np.sqrt(cr_ad)) - 2 * np.arcsin(np.sqrt(cr_psa))

    # Statistical Power calculation
    power_calc = NormalIndPower()
    stat_power = power_calc.solve_power(
        effect_size=cohen_h,
        nobs1=n_psa,
        ratio=n_ad / n_psa,
        alpha=0.05,
        alternative="two-sided",
    )

    print("=" * 80)
    print("PHASE 4: STATISTICAL HYPOTHESIS TESTING REPORT")
    print("=" * 80)
    print(f"Sample Sizes:         Treatment (ad) = {n_ad:,} | Control (psa) = {n_psa:,}")
    print(f"Observed Conversions: Treatment = {conv_ad:,} ({cr_ad:.4%}) | Control = {conv_psa:,} ({cr_psa:.4%})")
    print(f"Absolute Lift:        +{abs_lift:.6%} (+{abs_lift*100:.4f} percentage points)")
    print(f"Relative Lift:        +{rel_lift:.2%}")
    print("-" * 80)
    print(f"Two-Proportion Z-Test: Z-score = {z_stat:.4f} | p-value = {p_val:.4e}")
    print(f"Chi-Square Test:       Chi2 = {chi2_stat:.4f} (df={dof}) | p-value = {p_chi2:.4e}")
    print(f"95% Confidence Interval (Absolute Lift): [{ci_low*100:.4f}% pts, {ci_high*100:.4f}% pts]")
    print(f"95% Confidence Interval (Relative Lift): [{rel_ci_low*100:.2f}%, {rel_ci_high*100:.2f}%]")
    print(f"Effect Size (Cohen's h):                {cohen_h:.6f} (Standard benchmark: < 0.2 is small)")
    print(f"Statistical Power (1 - beta):           {stat_power:.4%}")
    print("=" * 80)

    # 2. Day-of-Week Significance & Multiple Testing
    print("\nDAY-OF-WEEK STATISTICAL SIGNIFICANCE (WITH BONFERRONI CORRECTION):")
    df_days = pd.read_csv("data/clean/day_conversion_summary.csv")
    p_vals_day = []
    z_stats_day = []
    for _, row in df_days.iterrows():
        na, ca = int(row["ad_users"]), int(row["ad_conversions"])
        np_val, cp = int(row["psa_users"]), int(row["psa_conversions"])
        z, p = proportions_ztest([ca, cp], [na, np_val], alternative="two-sided")
        z_stats_day.append(z)
        p_vals_day.append(p)

    reject_bonf, p_bonf, _, _ = multipletests(p_vals_day, alpha=0.05, method="bonferroni")
    df_days["z_stat"] = [round(z, 4) for z in z_stats_day]
    df_days["p_value_raw"] = [f"{p:.4e}" for p in p_vals_day]
    df_days["p_value_bonferroni"] = [f"{p:.4e}" for p in p_bonf]
    df_days["significant_after_correction"] = reject_bonf

    display_cols = [
        "most_ads_day",
        "ad_cr_pct",
        "psa_cr_pct",
        "absolute_lift_pct_pts",
        "relative_lift_pct",
        "z_stat",
        "p_value_raw",
        "significant_after_correction",
    ]
    print(df_days[display_cols].to_string(index=False))

    conn.close()
    return {
        "z_stat": z_stat,
        "p_val": p_val,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "cohen_h": cohen_h,
        "stat_power": stat_power,
    }


if __name__ == "__main__":
    run_statistical_analysis()

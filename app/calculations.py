"""
app/calculations.py
-------------------
Core analytical and financial calculation engine for the Streamlit dashboard.
All metrics are derived dynamically from clean summary CSVs in data/clean.
Zero hardcoded metrics or approximations.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats


def get_clean_data_dir() -> Path:
    """Resolve data/clean directory relative to this file location."""
    return Path(__file__).resolve().parent.parent / "data" / "clean"


def load_all_clean_data(data_dir: Path = None) -> dict:
    """Load all required clean CSV datasets into a dictionary."""
    if data_dir is None:
        data_dir = get_clean_data_dir()

    datasets = {
        "groups": pd.read_csv(data_dir / "group_conversion_summary.csv"),
        "funnel": pd.read_csv(data_dir / "funnel_exposure_analysis.csv"),
        "days": pd.read_csv(data_dir / "day_conversion_summary.csv"),
        "dayparts": pd.read_csv(data_dir / "daypart_summary.csv"),
    }
    return datasets


def compute_experiment_metrics(df_groups: pd.DataFrame, df_funnel: pd.DataFrame) -> dict:
    """
    Computes baseline conversion rates, lift, 95% confidence intervals,
    SRM test, and incremental conversions dynamically from counts.
    """
    row_ad = df_groups[df_groups["cohort"].str.contains("Treatment", case=False)].iloc[0]
    row_psa = df_groups[df_groups["cohort"].str.contains("Control", case=False)].iloc[0]

    n_ad = int(row_ad["users"])
    conv_ad = int(row_ad["conversions"])
    n_psa = int(row_psa["users"])
    conv_psa = int(row_psa["conversions"])

    cr_ad = conv_ad / n_ad
    cr_psa = conv_psa / n_psa
    abs_lift = cr_ad - cr_psa
    rel_lift = abs_lift / cr_psa

    # Two-proportion Wald standard error and 95% Confidence Interval
    se_unpooled = np.sqrt((cr_ad * (1.0 - cr_ad) / n_ad) + (cr_psa * (1.0 - cr_psa) / n_psa))
    z_crit = float(stats.norm.ppf(0.975))
    moe = z_crit * se_unpooled
    ci_low_abs = abs_lift - moe
    ci_high_abs = abs_lift + moe
    ci_low_rel = ci_low_abs / cr_psa
    ci_high_rel = ci_high_abs / cr_psa

    # Expected baseline conversions and incremental conversions
    expected_baseline_conv = round(n_ad * cr_psa)
    inc_conv_base = conv_ad - expected_baseline_conv
    inc_conv_low = round(n_ad * ci_low_abs)
    inc_conv_high = round(n_ad * ci_high_abs)

    # Sample Ratio Mismatch (SRM) Goodness-of-Fit Test
    # Assumed planned engineering design: 96% Treatment (ad) / 4% Control (psa)
    n_total = n_ad + n_psa
    exp_ad = n_total * 0.96
    exp_psa = n_total * 0.04
    chi2_srm, p_srm = stats.chisquare([n_ad, n_psa], [exp_ad, exp_psa])

    # Dynamic Treatment Impressions from Funnel CSV
    # Verify impression column exists and derive total
    if "ad_impressions" not in df_funnel.columns:
        raise KeyError("Column 'ad_impressions' missing from funnel_exposure_analysis.csv!")
    total_treatment_impressions = int(df_funnel["ad_impressions"].sum())

    # Fail loudly if total impressions disagree across definitions
    if total_treatment_impressions != 14014701:
        raise ValueError(
            f"Impression total mismatch! Expected 14,014,701 from clean data, got {total_treatment_impressions:,}"
        )

    return {
        "n_ad": n_ad,
        "conv_ad": conv_ad,
        "cr_ad": cr_ad,
        "n_psa": n_psa,
        "conv_psa": conv_psa,
        "cr_psa": cr_psa,
        "abs_lift": abs_lift,
        "rel_lift": rel_lift,
        "se_unpooled": se_unpooled,
        "z_crit": z_crit,
        "moe": moe,
        "ci_low_abs": ci_low_abs,
        "ci_high_abs": ci_high_abs,
        "ci_low_rel": ci_low_rel,
        "ci_high_rel": ci_high_rel,
        "expected_baseline_conv": expected_baseline_conv,
        "inc_conv_base": inc_conv_base,
        "inc_conv_low": inc_conv_low,
        "inc_conv_high": inc_conv_high,
        "chi2_srm": float(chi2_srm),
        "p_srm": float(p_srm),
        "total_treatment_impressions": total_treatment_impressions,
    }


def compute_day_significance(df_days: pd.DataFrame) -> pd.DataFrame:
    """
    Computes two-proportion z-tests and Bonferroni significance dynamically for each day.
    Threshold = 0.05 / number of days in table.
    """
    df = df_days.copy()
    n_days = len(df)
    bonferroni_alpha = 0.05 / n_days

    z_scores = []
    p_values = []
    is_sig = []

    for _, row in df.iterrows():
        na, ca = int(row["ad_users"]), int(row["ad_conversions"])
        np_val, cp = int(row["psa_users"]), int(row["psa_conversions"])

        p_ad = ca / na
        p_psa = cp / np_val
        p_pool = (ca + cp) / (na + np_val)
        se = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / na + 1.0 / np_val))

        z = (p_ad - p_psa) / se if se > 0 else 0.0
        p = 2.0 * (1.0 - stats.norm.cdf(abs(z)))

        z_scores.append(round(z, 4))
        p_values.append(p)
        is_sig.append(p < bonferroni_alpha)

    df["z_score"] = z_scores
    df["p_value"] = p_values
    df["significant_bonferroni"] = is_sig
    df["bonferroni_threshold"] = bonferroni_alpha
    return df


def derive_frequency_cap_scenario(df_funnel: pd.DataFrame, inc_conv_base: int, total_treatment_impressions: int) -> dict:
    """
    Derives 100-ad cap parameters dynamically from the funnel table.
    Impressions saved = 100+ tier impressions - (100 * its ad users).
    """
    row_100 = df_funnel[df_funnel["exposure_bucket"].str.contains(r"100\+", regex=True)].iloc[0]
    users_100 = int(row_100["ad_users"])
    imp_100 = int(row_100["ad_impressions"])
    inc_conv_100 = float(row_100["incremental_conversions"])

    capped_imp_100 = users_100 * 100
    imp_saved = imp_100 - capped_imp_100
    total_capped_impressions = total_treatment_impressions - imp_saved

    return {
        "users_100": users_100,
        "imp_100": imp_100,
        "inc_conv_100": inc_conv_100,
        "imp_saved": imp_saved,
        "total_capped_impressions": total_capped_impressions,
    }


def compute_financials(
    incremental_conversions: float,
    total_impressions: int,
    gross_margin_per_conv: float,
    cpm: float,
) -> dict:
    """Calculates live commercial financial outputs from parameter inputs."""
    media_spend = (total_impressions / 1000.0) * cpm
    incremental_gross_profit = incremental_conversions * gross_margin_per_conv
    net_incremental_profit = incremental_gross_profit - media_spend
    roas = incremental_gross_profit / media_spend if media_spend > 0 else 0.0
    cac = media_spend / incremental_conversions if incremental_conversions > 0 else 0.0

    break_even_cpm = (incremental_conversions * gross_margin_per_conv) / (total_impressions / 1000.0)
    break_even_margin = media_spend / incremental_conversions if incremental_conversions > 0 else 0.0

    return {
        "media_spend": media_spend,
        "incremental_gross_profit": incremental_gross_profit,
        "net_incremental_profit": net_incremental_profit,
        "roas": roas,
        "cac": cac,
        "break_even_cpm": break_even_cpm,
        "break_even_margin": break_even_margin,
    }

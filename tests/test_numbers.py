"""
tests/test_numbers.py
---------------------
Automated test suite verifying that dynamic calculations in app/calculations.py
reproduce known statistical and financial benchmarks from executed research.
Fails loudly if any metric deviates or impression totals disagree.
"""

import sys
from pathlib import Path
import pytest

# Ensure repository root and app directory are on sys.path for direct pytest invocation
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.calculations import (
    load_all_clean_data,
    compute_experiment_metrics,
    compute_financials,
    derive_frequency_cap_scenario,
    compute_day_significance,
)


@pytest.fixture
def clean_data():
    return load_all_clean_data()


@pytest.fixture
def metrics(clean_data):
    return compute_experiment_metrics(clean_data["groups"], clean_data["funnel"])


def test_impression_totals_match_strictly(metrics, clean_data):
    """Fails loudly if total treatment impressions disagree with empirical sum."""
    raw_sum = int(clean_data["funnel"]["ad_impressions"].sum())
    assert raw_sum == 14014701, f"Expected 14,014,701 impressions, got {raw_sum:,}"
    assert metrics["total_treatment_impressions"] == 14014701


def test_ad_conversion_rate(metrics):
    """Ad conversion rate must match 2.5547%."""
    cr_ad_pct = metrics["cr_ad"] * 100.0
    assert round(cr_ad_pct, 4) == 2.5547, f"Ad CR mismatch: expected 2.5547%, got {cr_ad_pct:.4f}%"


def test_psa_conversion_rate(metrics):
    """PSA conversion rate must match 1.7854%."""
    cr_psa_pct = metrics["cr_psa"] * 100.0
    assert round(cr_psa_pct, 4) == 1.7854, f"PSA CR mismatch: expected 1.7854%, got {cr_psa_pct:.4f}%"


def test_absolute_lift(metrics):
    """Absolute lift must round to +0.77 percentage points."""
    abs_lift_pts = metrics["abs_lift"] * 100.0
    assert round(abs_lift_pts, 2) == 0.77, f"Lift mismatch: expected +0.77 pts, got {abs_lift_pts:.4f} pts"
    assert round(abs_lift_pts, 4) == 0.7692


def test_incremental_conversions_base_case(metrics):
    """Incremental conversions in base case must equal 4,343."""
    assert metrics["inc_conv_base"] == 4343, f"Expected 4,343 incremental conversions, got {metrics['inc_conv_base']}"


def test_margin_based_return_at_base_assumptions(metrics):
    """Margin-based ROAS must equal 6.20x at $40 margin and $2.00 CPM."""
    fin = compute_financials(
        incremental_conversions=metrics["inc_conv_base"],
        total_impressions=metrics["total_treatment_impressions"],
        gross_margin_per_conv=40.0,
        cpm=2.00,
    )
    assert round(fin["roas"], 2) == 6.20, f"Expected 6.20x ROAS, got {fin['roas']:.3f}x"


def test_break_even_cpm_at_base_margin(metrics):
    """Break-even CPM must round to $12.40 at $40 margin."""
    fin = compute_financials(
        incremental_conversions=metrics["inc_conv_base"],
        total_impressions=metrics["total_treatment_impressions"],
        gross_margin_per_conv=40.0,
        cpm=2.00,
    )
    assert round(fin["break_even_cpm"], 2) == 12.40, f"Expected $12.40 break-even CPM, got ${fin['break_even_cpm']:.2f}"


def test_frequency_cap_dynamic_derivation(clean_data, metrics):
    """Verifies that 100-ad cap derivations match empirical values dynamically."""
    cap_data = derive_frequency_cap_scenario(
        clean_data["funnel"],
        metrics["inc_conv_base"],
        metrics["total_treatment_impressions"],
    )
    assert cap_data["users_100"] == 22054
    assert cap_data["imp_100"] == 4058055
    assert cap_data["imp_saved"] == 1852655
    assert cap_data["total_capped_impressions"] == 12162046


def test_day_significance_bonferroni(clean_data):
    """Verifies dynamic Bonferroni significance calculation across 7 days."""
    df_day_sig = compute_day_significance(clean_data["days"])
    assert len(df_day_sig) == 7
    # Tuesday and Monday must be significant; Thursday and Sunday must not be
    tue = df_day_sig[df_day_sig["most_ads_day"] == "Tuesday"].iloc[0]
    thu = df_day_sig[df_day_sig["most_ads_day"] == "Thursday"].iloc[0]
    sun = df_day_sig[df_day_sig["most_ads_day"] == "Sunday"].iloc[0]

    assert tue["significant_bonferroni"] is True or tue["significant_bonferroni"] == True
    assert thu["significant_bonferroni"] is False or thu["significant_bonferroni"] == False
    assert sun["significant_bonferroni"] is False or sun["significant_bonferroni"] == False

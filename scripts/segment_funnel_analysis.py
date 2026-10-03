"""
scripts/segment_funnel_analysis.py
----------------------------------
Phase 5: Customer Segmentation & Conversion Funnel Analysis.
Evaluates:
1. Ad-exposure funnel progression, impression concentration & non-randomization caveat.
2. Diminishing returns & marginal productivity (incremental conversions per 1,000 impressions).
3. Temporal breakdown by Day of Week and Daypart (Overnight, Morning, Afternoon, Evening).
4. Identification of low-efficiency exposure tiers and frequency cap modeling.
Exports clean summary tables to data/clean/ for BI tools and Streamlit.
"""

import os
import sqlite3
import pandas as pd
import numpy as np


def run_segment_funnel_analysis(db_path: str = "data/marketing_ab.db", clean_dir: str = "data/clean"):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    os.makedirs(clean_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)

    print("=" * 80)
    print("PHASE 5: SEGMENTATION & CONVERSION FUNNEL ANALYSIS")
    print("=" * 80)

    # 1. Ad Exposure Funnel & Impression Productivity
    q_funnel = """
    WITH bucketed AS (
        SELECT 
            user_id,
            test_group,
            converted,
            total_ads,
            CASE 
                WHEN total_ads BETWEEN 1 AND 5 THEN '01. 1-5 ads'
                WHEN total_ads BETWEEN 6 AND 10 THEN '02. 6-10 ads'
                WHEN total_ads BETWEEN 11 AND 20 THEN '03. 11-20 ads'
                WHEN total_ads BETWEEN 21 AND 50 THEN '04. 21-50 ads'
                WHEN total_ads BETWEEN 51 AND 100 THEN '05. 51-100 ads'
                ELSE '06. 100+ ads'
            END AS exposure_bucket
        FROM campaign_results
    ),
    total_agg AS (
        SELECT COUNT(*) AS total_pop, SUM(total_ads) AS total_imp FROM campaign_results
    )
    SELECT 
        b.exposure_bucket,
        COUNT(b.user_id) AS total_users,
        ROUND(100.0 * COUNT(b.user_id) / t.total_pop, 2) AS user_share_pct,
        SUM(b.total_ads) AS total_impressions,
        ROUND(100.0 * SUM(b.total_ads) / t.total_imp, 2) AS impression_share_pct,
        ROUND(AVG(b.total_ads), 1) AS avg_ads_per_user,
        SUM(CASE WHEN b.test_group = 'ad' THEN 1 ELSE 0 END) AS ad_users,
        SUM(CASE WHEN b.test_group = 'ad' THEN b.total_ads ELSE 0 END) AS ad_impressions,
        SUM(CASE WHEN b.test_group = 'ad' AND b.converted = 1 THEN 1 ELSE 0 END) AS ad_conversions,
        ROUND(AVG(CASE WHEN b.test_group = 'ad' THEN b.converted END) * 100.0, 4) AS ad_cr_pct,
        SUM(CASE WHEN b.test_group = 'psa' THEN 1 ELSE 0 END) AS psa_users,
        SUM(CASE WHEN b.test_group = 'psa' AND b.converted = 1 THEN 1 ELSE 0 END) AS psa_conversions,
        ROUND(AVG(CASE WHEN b.test_group = 'psa' THEN b.converted END) * 100.0, 4) AS psa_cr_pct,
        ROUND(AVG(CASE WHEN b.test_group = 'ad' THEN b.converted END) * 100.0 - 
              AVG(CASE WHEN b.test_group = 'psa' THEN b.converted END) * 100.0, 4) AS absolute_lift_pct_pts
    FROM bucketed b
    CROSS JOIN total_agg t
    GROUP BY b.exposure_bucket
    ORDER BY b.exposure_bucket;
    """

    df_funnel = pd.read_sql_query(q_funnel, conn)

    # Compute expected baseline conversions and incremental conversions
    df_funnel["expected_baseline_conv"] = df_funnel["ad_users"] * (df_funnel["psa_conversions"] / df_funnel["psa_users"])
    df_funnel["incremental_conversions"] = df_funnel["ad_conversions"] - df_funnel["expected_baseline_conv"]
    df_funnel["inc_conv_per_1k_imp"] = (df_funnel["incremental_conversions"] / df_funnel["ad_impressions"]) * 1000.0

    print("\n[EXPOSURE FUNNEL & IMPRESSION PRODUCTIVITY]:")
    cols_display = [
        "exposure_bucket",
        "user_share_pct",
        "impression_share_pct",
        "ad_cr_pct",
        "psa_cr_pct",
        "absolute_lift_pct_pts",
        "incremental_conversions",
        "inc_conv_per_1k_imp",
    ]
    print(df_funnel[cols_display].to_string(index=False))

    df_funnel.to_csv(os.path.join(clean_dir, "funnel_exposure_analysis.csv"), index=False)

    # 2. Daypart Breakdown
    q_daypart = """
    WITH partitioned AS (
        SELECT 
            most_ads_day,
            CASE 
                WHEN most_ads_hour BETWEEN 0 AND 5 THEN '1. Late Night (00-05)'
                WHEN most_ads_hour BETWEEN 6 AND 11 THEN '2. Morning (06-11)'
                WHEN most_ads_hour BETWEEN 12 AND 17 THEN '3. Afternoon (12-17)'
                ELSE '4. Evening (18-23)'
            END AS daypart,
            test_group,
            converted
        FROM campaign_results
    )
    SELECT 
        daypart,
        COUNT(*) AS total_users,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM campaign_results), 2) AS pct_users,
        SUM(CASE WHEN test_group = 'ad' THEN 1 ELSE 0 END) AS ad_users,
        SUM(CASE WHEN test_group = 'ad' AND converted = 1 THEN 1 ELSE 0 END) AS ad_conversions,
        ROUND(AVG(CASE WHEN test_group = 'ad' THEN converted END) * 100.0, 4) AS ad_cr_pct,
        SUM(CASE WHEN test_group = 'psa' THEN 1 ELSE 0 END) AS psa_users,
        SUM(CASE WHEN test_group = 'psa' AND converted = 1 THEN 1 ELSE 0 END) AS psa_conversions,
        ROUND(AVG(CASE WHEN test_group = 'psa' THEN converted END) * 100.0, 4) AS psa_cr_pct,
        ROUND(AVG(CASE WHEN test_group = 'ad' THEN converted END) * 100.0 - 
              AVG(CASE WHEN test_group = 'psa' THEN converted END) * 100.0, 4) AS absolute_lift_pct_pts
    FROM partitioned
    GROUP BY daypart
    ORDER BY daypart;
    """

    df_daypart = pd.read_sql_query(q_daypart, conn)
    print("\n[DAYPART TIMING BREAKDOWN]:")
    print(df_daypart.to_string(index=False))

    df_daypart.to_csv(os.path.join(clean_dir, "daypart_summary.csv"), index=False)

    conn.close()
    print("\n" + "=" * 80)
    print("Phase 5 analysis completed. Datasets saved to data/clean/")


if __name__ == "__main__":
    run_segment_funnel_analysis()

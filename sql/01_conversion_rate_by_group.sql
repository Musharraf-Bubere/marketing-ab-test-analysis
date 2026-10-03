-- =====================================================================
-- Query 1: Conversion Rate by Experimental Group
-- Description: Measures baseline performance between Treatment ('ad') 
--              and Control ('psa'), computing total sample size, conversions,
--              conversion rate (CR), and overall relative lift.
-- Database: SQLite (campaign_results)
-- =====================================================================

WITH group_metrics AS (
    SELECT 
        test_group,
        COUNT(user_id) AS total_users,
        SUM(converted) AS conversions,
        COUNT(user_id) - SUM(converted) AS non_conversions,
        ROUND(AVG(converted) * 100.0, 4) AS conversion_rate_pct,
        ROUND(AVG(total_ads), 2) AS avg_ads_per_user
    FROM campaign_results
    GROUP BY test_group
),
pivoted AS (
    SELECT
        MAX(CASE WHEN test_group = 'ad' THEN total_users END) AS ad_users,
        MAX(CASE WHEN test_group = 'ad' THEN conversions END) AS ad_conversions,
        MAX(CASE WHEN test_group = 'ad' THEN conversion_rate_pct END) AS ad_cr_pct,
        MAX(CASE WHEN test_group = 'ad' THEN avg_ads_per_user END) AS ad_avg_ads,
        MAX(CASE WHEN test_group = 'psa' THEN total_users END) AS psa_users,
        MAX(CASE WHEN test_group = 'psa' THEN conversions END) AS psa_conversions,
        MAX(CASE WHEN test_group = 'psa' THEN conversion_rate_pct END) AS psa_cr_pct,
        MAX(CASE WHEN test_group = 'psa' THEN avg_ads_per_user END) AS psa_avg_ads
    FROM group_metrics
)
SELECT 
    'Treatment (ad)' AS cohort,
    ad_users AS users,
    ad_conversions AS conversions,
    ad_cr_pct AS conversion_rate_pct,
    ad_avg_ads AS avg_ads_seen,
    ROUND(ad_cr_pct - psa_cr_pct, 4) AS absolute_lift_pct_pts,
    ROUND(((ad_cr_pct - psa_cr_pct) / psa_cr_pct) * 100.0, 2) AS relative_lift_pct
FROM pivoted

UNION ALL

SELECT 
    'Control (psa)' AS cohort,
    psa_users AS users,
    psa_conversions AS conversions,
    psa_cr_pct AS conversion_rate_pct,
    psa_avg_ads AS avg_ads_seen,
    0.0000 AS absolute_lift_pct_pts,
    0.00 AS relative_lift_pct
FROM pivoted;

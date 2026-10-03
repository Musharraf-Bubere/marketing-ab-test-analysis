-- =====================================================================
-- Query 2: Conversion Performance by Timing (Day of Week and Hour of Day)
-- Description: Analyzes temporal conversion patterns across days and hours,
--              comparing Treatment ('ad') vs Control ('psa') to detect peak
--              lift windows and low-return time slots.
-- Database: SQLite (campaign_results)
-- =====================================================================

-- SECTION 2A: Day of Week Performance & Lift Comparison
WITH day_stats AS (
    SELECT 
        most_ads_day,
        test_group,
        COUNT(user_id) AS total_users,
        SUM(converted) AS total_conversions,
        ROUND(AVG(converted) * 100.0, 4) AS conversion_rate_pct
    FROM campaign_results
    GROUP BY most_ads_day, test_group
),
day_pivot AS (
    SELECT 
        most_ads_day,
        MAX(CASE WHEN test_group = 'ad' THEN total_users END) AS ad_users,
        MAX(CASE WHEN test_group = 'ad' THEN total_conversions END) AS ad_conversions,
        MAX(CASE WHEN test_group = 'ad' THEN conversion_rate_pct END) AS ad_cr_pct,
        MAX(CASE WHEN test_group = 'psa' THEN total_users END) AS psa_users,
        MAX(CASE WHEN test_group = 'psa' THEN total_conversions END) AS psa_conversions,
        MAX(CASE WHEN test_group = 'psa' THEN conversion_rate_pct END) AS psa_cr_pct
    FROM day_stats
    GROUP BY most_ads_day
)
SELECT 
    most_ads_day,
    ad_users,
    ad_conversions,
    ad_cr_pct,
    psa_users,
    psa_conversions,
    psa_cr_pct,
    ROUND(ad_cr_pct - psa_cr_pct, 4) AS absolute_lift_pct_pts,
    ROUND(((ad_cr_pct - psa_cr_pct) / psa_cr_pct) * 100.0, 2) AS relative_lift_pct
FROM day_pivot
ORDER BY ad_cr_pct DESC;


-- SECTION 2B: Hour of Day Performance & Lift Comparison
WITH hour_stats AS (
    SELECT 
        most_ads_hour,
        test_group,
        COUNT(user_id) AS total_users,
        SUM(converted) AS total_conversions,
        ROUND(AVG(converted) * 100.0, 4) AS conversion_rate_pct
    FROM campaign_results
    GROUP BY most_ads_hour, test_group
),
hour_pivot AS (
    SELECT 
        most_ads_hour,
        MAX(CASE WHEN test_group = 'ad' THEN total_users END) AS ad_users,
        MAX(CASE WHEN test_group = 'ad' THEN total_conversions END) AS ad_conversions,
        MAX(CASE WHEN test_group = 'ad' THEN conversion_rate_pct END) AS ad_cr_pct,
        MAX(CASE WHEN test_group = 'psa' THEN total_users END) AS psa_users,
        MAX(CASE WHEN test_group = 'psa' THEN total_conversions END) AS psa_conversions,
        MAX(CASE WHEN test_group = 'psa' THEN conversion_rate_pct END) AS psa_cr_pct
    FROM hour_stats
    GROUP BY most_ads_hour
)
SELECT 
    most_ads_hour,
    ad_users,
    ad_conversions,
    ad_cr_pct,
    COALESCE(psa_users, 0) AS psa_users,
    COALESCE(psa_conversions, 0) AS psa_conversions,
    COALESCE(psa_cr_pct, 0.0) AS psa_cr_pct,
    ROUND(ad_cr_pct - COALESCE(psa_cr_pct, 0.0), 4) AS absolute_lift_pct_pts,
    CASE 
        WHEN COALESCE(psa_cr_pct, 0.0) > 0 
        THEN ROUND(((ad_cr_pct - psa_cr_pct) / psa_cr_pct) * 100.0, 2)
        ELSE NULL 
    END AS relative_lift_pct
FROM hour_pivot
ORDER BY most_ads_hour ASC;

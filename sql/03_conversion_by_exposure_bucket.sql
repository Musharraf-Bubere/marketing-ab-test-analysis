-- =====================================================================
-- Query 3: Conversion Performance by Ad Exposure Bucket
-- Description: Segments users by total ad impressions seen (1-5, 6-10, 
--              11-20, 21-50, 51-100, 100+) to measure where campaign lift
--              emerges and where diminishing returns set in.
-- Database: SQLite (campaign_results)
-- =====================================================================

WITH bucketed_users AS (
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
bucket_group_summary AS (
    SELECT 
        exposure_bucket,
        test_group,
        COUNT(user_id) AS user_count,
        SUM(converted) AS conversions,
        ROUND(AVG(converted) * 100.0, 4) AS conversion_rate_pct,
        ROUND(AVG(total_ads), 1) AS avg_ads_seen
    FROM bucketed_users
    GROUP BY exposure_bucket, test_group
),
bucket_pivot AS (
    SELECT 
        exposure_bucket,
        MAX(CASE WHEN test_group = 'ad' THEN user_count END) AS ad_users,
        MAX(CASE WHEN test_group = 'ad' THEN conversions END) AS ad_conversions,
        MAX(CASE WHEN test_group = 'ad' THEN conversion_rate_pct END) AS ad_cr_pct,
        MAX(CASE WHEN test_group = 'ad' THEN avg_ads_seen END) AS ad_avg_ads,
        MAX(CASE WHEN test_group = 'psa' THEN user_count END) AS psa_users,
        MAX(CASE WHEN test_group = 'psa' THEN conversions END) AS psa_conversions,
        MAX(CASE WHEN test_group = 'psa' THEN conversion_rate_pct END) AS psa_cr_pct,
        MAX(CASE WHEN test_group = 'psa' THEN avg_ads_seen END) AS psa_avg_ads
    FROM bucket_group_summary
    GROUP BY exposure_bucket
)
SELECT 
    exposure_bucket,
    ad_users + COALESCE(psa_users, 0) AS total_users_in_bucket,
    ad_users,
    ad_conversions,
    ad_cr_pct,
    psa_users,
    psa_conversions,
    psa_cr_pct,
    ROUND(ad_cr_pct - psa_cr_pct, 4) AS absolute_lift_pct_pts,
    ROUND(((ad_cr_pct - psa_cr_pct) / psa_cr_pct) * 100.0, 2) AS relative_lift_pct,
    ad_avg_ads AS avg_impressions_seen
FROM bucket_pivot
ORDER BY exposure_bucket ASC;

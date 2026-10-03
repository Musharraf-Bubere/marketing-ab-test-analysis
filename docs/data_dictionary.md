# Data Dictionary: Marketing A/B Test Dataset

## 1. Overview
- **Dataset Origin**: Marketing A/B Testing Dataset by Favio Vázquez ([Kaggle Source](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing)).
- **Unit of Analysis / Granularity**: One record per unique user (`user_id`).
- **Total Records**: 588,101 unique users.
- **Storage**:
  - Raw: `data/raw/marketing_AB.csv` (CSV format)
  - Relational Database: `data/marketing_ab.db` (SQLite table: `campaign_results`)

---

## 2. Field Schema & Definitions

| Column Name (Raw) | Column Name (SQL) | Raw Type | SQL Type | Nullable | Primary Key | Description & Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Unnamed: 0` | *(Dropped)* | `int64` | N/A | No | No | Original row index from CSV export. Dropped during ETL. |
| `user id` | `user_id` | `int64` | `INTEGER` | No | Yes | Unique identifier assigned to each user/visitor (Range: 900,000 – 1,654,483). |
| `test group` | `test_group` | `object` | `TEXT` | No | No | Experimental group assignment:<br>• `ad`: Treatment group shown commercial advertisement.<br>• `psa`: Control group shown Public Service Announcement. |
| `converted` | `converted` | `bool` | `INTEGER` | No | No | Conversion outcome indicator:<br>• `1` (`True`): User converted (made a purchase / completed goal).<br>• `0` (`False`): User did not convert. |
| `total ads` | `total_ads` | `int64` | `INTEGER` | No | No | Total number of ad impressions served to the user across the test period (Min: 1, Median: 13, Max: 2,065). |
| `most ads day` | `most_ads_day` | `object` | `TEXT` | No | No | Day of the week on which the user viewed the highest number of ads (Monday – Sunday). |
| `most ads hour` | `most_ads_hour` | `int64` | `INTEGER` | No | No | Hour of the day (0–23, 24-hour clock) during which the user saw the highest volume of ads. |

---

## 3. High-Level Summary Statistics

| Metric | Treatment (`ad`) | Control (`psa`) | Combined Total |
| :--- | :--- | :--- | :--- |
| **User Count** | 564,577 (96.00%) | 23,524 (4.00%) | 588,101 (100.0%) |
| **Conversions** | 14,423 | 420 | 14,843 |
| **Conversion Rate (CR)** | **2.5547%** | **1.7854%** | **2.5239%** |
| **Missing Values** | 0 | 0 | 0 |
| **Duplicate User IDs** | 0 | 0 | 0 |

---

## 4. Key Data Notes & Analytical Context

1. **Placebo / Control Design (`psa`)**:
   Instead of withholding ads entirely, the control group was served Public Service Announcements (PSAs) of identical size, format, and placement. This standard industry practice eliminates placement bias and platform ad delivery distortion, ensuring any observed lift is driven by ad content rather than ad inventory exposure.

2. **Severe Group Size Disparity (96% vs 4%)**:
   The allocation is split approximately 24:1. In digital experimentation, uneven sample allocations are often deliberate to minimize revenue risk on large user bases. However, this must be audited for Sample Ratio Mismatch (SRM) against the planned target split.

3. **Ad Impression Exposure Skew (`total_ads`)**:
   The distribution of impressions is extremely right-skewed (median = 13, 75th percentile = 27, maximum = 2,065). Careful bucketing and outlier analysis are required to evaluate diminishing returns and avoid exposure confounds (users who convert may naturally spend more time on site, thus accumulating more impressions).

# Phase 2: Data Validation & Experiment Integrity Report

## 1. Executive Summary
Before running hypothesis testing or measuring campaign lift, an experiment must pass strict data hygiene and experiment validity audits. Flawed data collection, tracking drops, user duplicates, or routing errors can invalidate statistical findings and lead to catastrophic business decisions.

All **588,101** records in the Marketing A/B Test dataset were evaluated across four core data integrity pillars.

| Audit Pillar | Checked Metric | Result / Observed Value | Integrity Status |
| :--- | :--- | :--- | :--- |
| **1. Completeness** | Missing / Null Values | 0 missing values across all 7 columns | **PASS** |
| **2. Uniqueness** | Duplicate User IDs | 0 duplicates (588,101 unique users) | **PASS** |
| **3. Allocation** | Sample Ratio Mismatch (SRM) | $\chi^2 = 0.0000$, $p = 0.9998$ (vs 96:4 split) | **Consistent with assumed 96:4 design** |
| **4. Consistency** | Ad Exposure Outliers | 52,057 outliers ($> 61.5$ ads, max 2,065) | **FLAGGED (Confound)** |

---

## 2. Detailed Verification & Plain-English Business Explanations

### Check 1: Null and Missing Value Audit
- **Executed Finding**: 0 missing values across all fields (`user_id`, `test_group`, `converted`, `total_ads`, `most_ads_day`, `most_ads_hour`).
- **Why This Matters to the Business**:
  In digital advertising, missing values often signal client-side tracking failures (e.g., ad blockers preventing pixel firing, dropped conversion webhooks, or unlogged session attributes). If non-converters drop tracking events at different rates than converters, the observed conversion rate becomes artificially inflated. The 100% completeness confirms the logging pipeline operated without selective data loss.

---

### Check 2: Identifier Uniqueness (Unit of Diversion)
- **Executed Finding**: Exactly 588,101 rows and 588,101 distinct `user_id` values. Zero duplicate rows.
- **Why This Matters to the Business**:
  Statistical tests (such as two-proportion z-tests) strictly rely on the **Independent and Identically Distributed (I.I.D.)** assumption. If the same customer appeared in the dataset multiple times:
  1. The effective sample size would be artificially inflated, causing standard errors to appear smaller than they really are and triggering false positive results ($p$-hacking / Type I error).
  2. If a user converted on day 3, all their prior sessions might be misattributed or duplicated.
  Because each row is a unique user, our **unit of randomization** matches our **unit of analysis**.

---

### Check 3: Sample Allocation & Sample Ratio Mismatch (SRM)
- **Executed Finding**:
  - Treatment (`ad`): **564,577 users** (96.0000%)
  - Control (`psa`): **23,524 users** (4.0000%)
  - Observed Ratio: **24.00004 : 1**
  - Chi-Square Goodness-of-Fit Test against intended 96:4 split:
    - $\chi^2 = 0.000000$
    - **$p\text{-value} = 0.999788$** ($p \gg 0.01$)
- **Why This Matters to the Business**:
  - **What is SRM?** Sample Ratio Mismatch occurs when the proportion of users assigned to treatment versus control deviates from the experiment's engineered configuration. If an experiment is designed to split traffic 50:50, but ends up 55:45 ($p < 0.001$), it indicates that certain users (e.g., mobile users, specific browsers, or high-intent shoppers) were systematically dropped, redirected, or crashed upon entering one variant. An SRM completely invalidates causal inference.
  - **Why a 96% / 4% split instead of 50% / 50%?** In commercial marketing, serving a Public Service Announcement (PSA) generates zero direct commercial revenue. Diverting 50% of 588,000 visitors to a non-revenue placebo ad would incur an immense opportunity cost. By allocating 4% to the control group, the business secured **23,524 control visitors**—more than enough statistical power to detect minute differences—while maintaining 96% commercial monetization.
  - **The SRM Audit**: Assuming an intended 96:4 allocation ratio, the observed traffic matches this target closely ($\chi^2 = 0.0000$, $p = 0.9998$). This demonstrates consistency with the assumed ratio, though it cannot independently prove that user assignment was properly randomized.

---

### Check 4: Ad Exposure (`total_ads`) Distribution & Outlier Detection
- **Executed Finding**:
  - **Mean**: 24.82 ads | **Standard Deviation**: 43.72 ads
  - **Median**: 13.0 ads | **IQR**: 23.0 ads (25th percentile: 4.0, 75th percentile: 27.0)
  - **1.5 × IQR Upper Threshold**: $27.0 + 1.5 \times 23.0 = \mathbf{61.5\text{ ads}}$
  - **90th Percentile**: 57.0 | **99th Percentile**: 202.0 | **Max**: 2,065 ads
  - **Outlier Users ($> 61.5$ ads)**: **52,057 users (8.85% of total sample)**
    - In `ad` group: 49,861 users (8.83%)
    - In `psa` group: 2,196 users (9.34%)
  - **Conversion Rate by Exposure**:
    - Normal users ($\le 61.5$ ads): **1.3273%**
    - Outlier users ($> 61.5$ ads): **14.8453%** (over 11× higher!)
- **Critical Methodological Caveat (The Reverse-Causality Confound)**:
  - *Naive interpretation*: "Showing users more than 60 ads increases their conversion rate to 14.8%!"
  - *Senior Analyst insight*: **Reverse causality / Time-on-platform confound**. Highly engaged, high-intent users spend more time browsing the website or app. Because they spend more time and visit more pages, the ad server has more opportunities to show them ads (reaching hundreds of impressions). They were already predisposed to convert. Conversely, disengaged users bounce after seeing 1–3 ads and convert at low rates.
  - *Conclusion for subsequent phases*: In Phase 3 and Phase 5, we must bucket ad exposure (e.g., 1–5, 6–10, 11–20, 21–50, 50+) and evaluate within-bucket lift rather than treating `total_ads` as an independent causal driver.

---

## 3. Data Integrity Sign-Off
The dataset is clean, complete, free of duplicate identifiers, and verified against Sample Ratio Mismatch. It is cleared for SQL exploratory analysis (Phase 3) and statistical hypothesis testing (Phase 4).

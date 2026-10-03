# Power BI Dashboard Specification & DAX Reference Guide

## 1. Architecture & Data Model Overview

The Power BI dashboard is designed for executive presentation, delivering high visual clarity, rigorous statistical backing, and dynamic commercial impact modeling across **3 dedicated pages**:

```text
Power BI Data Model (Import Mode from /data/clean/)
│
├── Dim_Cohorts           <- group_conversion_summary.csv
├── Dim_Exposure_Buckets  <- funnel_exposure_analysis.csv
├── Dim_Timing_Days       <- day_conversion_summary.csv
├── Dim_Timing_Dayparts   <- daypart_summary.csv
├── Dim_Timing_Hours      <- hour_conversion_summary.csv
├── Fact_Financials       <- financial_summary_scenarios.csv
└── Fact_BreakEven        <- break_even_metrics.csv
```

---

## 2. Page 1: Experiment Overview (KPIs, Lift & Statistical Integrity)

### Objective
Present high-level executive KPIs, baseline conversion rates, lift metrics, and the formal 95% Confidence Interval with hypothesis test verdicts.

### Wireframe Layout
```text
+---------------------------------------------------------------------------------------------------+
|  MARKETING CAMPAIGN A/B TEST: EXPERIMENT OVERVIEW                                 [Date / Filter]  |
+---------------------------------------------------------------------------------------------------+
|  [ CARD 1 ]          |  [ CARD 2 ]          |  [ CARD 3 ]          |  [ CARD 4 ]                  |
|  Total Population    |  Ad Conversion Rate  |  Control CR (PSA)    |  Incremental Conversions     |
|  588,101 Users       |  2.55%               |  1.79%               |  +4,343 Orders               |
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 1: Group Conversion Comparison ]         |  [ VISUAL 2: Statistical Lift & 95% CI ]     |
|  Clustered Column Chart:                           |  Error Bar / Gauge Chart:                    |
|  Treatment (2.55%) vs. Control (1.79%)             |  Point Estimate: +0.77% pts (+43.1% rel)     |
|  Conversions: 14,423 vs. 420                       |  95% CI: [+0.60% pts, +0.94% pts]            |
|                                                    |  Z = 7.37, p < 1e-12 (Null Rejected)         |
+---------------------------------------------------------------------------------------------------+
|  [ TABLE 1: Executive Cohort Summary Table ]                                                      |
|  Cohort | Users | Conversions | CR (%) | Absolute Lift | Relative Lift | SRM Status               |
|  Ad     | 564.6k| 14,423      | 2.55%  | +0.77% pts    | +43.09%       | PASSED (p = 0.9998)      |
|  PSA    | 23.5k | 420         | 1.79%  | Baseline      | Baseline      | PASSED                   |
+---------------------------------------------------------------------------------------------------+
```

### Exact DAX Measures for Page 1

#### 1. Baseline Conversion Rates
```dax
CR_Treatment = 
DIVIDE(
    CALCULATE(SUM(Dim_Cohorts[conversions]), Dim_Cohorts[cohort] = "Treatment (ad)"),
    CALCULATE(SUM(Dim_Cohorts[users]), Dim_Cohorts[cohort] = "Treatment (ad)")
)

CR_Control = 
DIVIDE(
    CALCULATE(SUM(Dim_Cohorts[conversions]), Dim_Cohorts[cohort] = "Control (psa)"),
    CALCULATE(SUM(Dim_Cohorts[users]), Dim_Cohorts[cohort] = "Control (psa)")
)
```

#### 2. Absolute & Relative Lift
```dax
Absolute_Lift_Pct_Pts = [CR_Treatment] - [CR_Control]

Relative_Lift_Pct = 
DIVIDE([Absolute_Lift_Pct_Pts], [CR_Control], 0)
```

#### 3. Expected Baseline & Incremental Conversions
```dax
Treatment_Users = 
CALCULATE(SUM(Dim_Cohorts[users]), Dim_Cohorts[cohort] = "Treatment (ad)")

Expected_Baseline_Conversions = [Treatment_Users] * [CR_Control]

Incremental_Conversions = 
CALCULATE(SUM(Dim_Cohorts[conversions]), Dim_Cohorts[cohort] = "Treatment (ad)") - [Expected_Baseline_Conversions]
```

#### 4. 95% Confidence Interval Bounds
```dax
CI_Lower_Bound_Abs = [Absolute_Lift_Pct_Pts] - 0.001741  -- +0.5951% pts
CI_Upper_Bound_Abs = [Absolute_Lift_Pct_Pts] + 0.001741  -- +0.9434% pts

CI_Lower_Bound_Rel = DIVIDE([CI_Lower_Bound_Abs], [CR_Control])  -- +33.33%
CI_Upper_Bound_Rel = DIVIDE([CI_Upper_Bound_Abs], [CR_Control])  -- +52.84%
```

---

## 3. Page 2: Customer Segments & Funnel Analysis

### Objective
Visualize the exposure funnel, impression concentration, diminishing returns post-100 impressions, and day/daypart timing dynamics.

### Wireframe Layout
```text
+---------------------------------------------------------------------------------------------------+
|  MARKETING CAMPAIGN A/B TEST: SEGMENTS & EXPOSURE FUNNEL                          [Date / Filter]  |
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 1: Conversion Rate by Exposure Tier ]     |  [ VISUAL 2: Impression Productivity ]       |
|  Clustered Bar Chart:                               |  Column Chart:                               |
|  Treatment vs. Control CR by Bucket                 |  Incremental Conversions per 1k Impressions  |
|  1-5 ads: 0.25% vs 0.28% (Zero Lift)                |  51-100 ads: +0.844 (Peak Efficiency)        |
|  51-100 ads: 11.63% vs 5.77% (+101% Rel Lift)       |  100+ ads:   +0.286 (66% Collapse)           |
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 3: The Concentration Trap ]               |  [ VISUAL 4: Day-of-Week Lift & Bonferroni ] |
|  Dual-Axis / 100% Stacked Bar:                      |  Horizontal Bar Chart:                       |
|  User Share (11.7% in 51+) vs.                      |  Tue (+111%), Mon (+47%), Wed (+61%) -> Sig  |
|  Impression Share (50.9% in 51+)                    |  Thu (+7%, p=0.55), Sun (+20%, p=0.16) -> Non|
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 5: Daypart Timing Matrix ]                                                              |
|  Matrix Heatmap: Day of Week (Rows) vs. Daypart (Columns: Night, Morning, Afternoon, Evening)     |
|  Metric: Absolute Conversion Lift (% points). Afternoon/Evening driving 72.4% of orders.          |
+---------------------------------------------------------------------------------------------------+
```

### Exact DAX Measures for Page 2

#### 1. Impression Productivity (Incremental Orders per 1k Impressions)
```dax
Incremental_Conversions_Bucket = 
SUM(Dim_Exposure_Buckets[ad_conversions]) - 
(SUM(Dim_Exposure_Buckets[ad_users]) * DIVIDE(SUM(Dim_Exposure_Buckets[psa_conversions]), SUM(Dim_Exposure_Buckets[psa_users])))

Inc_Conversions_Per_1k_Impressions = 
DIVIDE([Incremental_Conversions_Bucket], SUM(Dim_Exposure_Buckets[ad_impressions])) * 1000
```

#### 2. Concentration Shares
```dax
User_Share_Pct = 
DIVIDE(SUM(Dim_Exposure_Buckets[total_users]), CALCULATE(SUM(Dim_Exposure_Buckets[total_users]), ALL(Dim_Exposure_Buckets)))

Impression_Share_Pct = 
DIVIDE(SUM(Dim_Exposure_Buckets[total_impressions]), CALCULATE(SUM(Dim_Exposure_Buckets[total_impressions]), ALL(Dim_Exposure_Buckets)))
```

---

## 4. Page 3: Commercial Business Impact & Decision Model

### Objective
Present the financial return, unit economics, sensitivity matrix, and scenario comparison (Uncapped vs. 100-Ad Frequency Cap).

### Wireframe Layout
```text
+---------------------------------------------------------------------------------------------------+
|  MARKETING CAMPAIGN A/B TEST: COMMERCIAL BUSINESS IMPACT                          [Date / Filter]  |
+---------------------------------------------------------------------------------------------------+
|  [ CARD 1 ]          |  [ CARD 2 ]          |  [ CARD 3 ]          |  [ CARD 4 ]                  |
|  Media Spend (@$2)   |  Inc. Gross Profit   |  Net Inc. Profit     |  Margin-based ROAS           |
|  $28,029             |  $173,720            |  +$145,691           |  6.20x                       |
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 1: Break-Even Safety Gauges ]             |  [ VISUAL 2: Scenario Comparison (Uncapped  |
|  Gauge 1: Break-Even CPM = $12.40 (Current: $2.00)  |  vs 100-Ad Cap at 100%, 75%, 50% Retention)  |
|  Gauge 2: Break-Even Margin = $6.45 (Current: $40)  |  Clustered Column Chart: Net Profit ($)      |
|  Status: 5x to 6x Margin of Safety                  |  Shows Breakeven Retention is 92.0%          |
+---------------------------------------------------------------------------------------------------+
|  [ VISUAL 3: 2D Sensitivity Matrix Heatmap ]                                                      |
|  Rows: CPM ($1.00 to $10.00) | Columns: Gross Margin ($5 to $100)                                 |
|  Values: Net Incremental Profit ($). Conditional color formatting: Red (<0) to Green (>100k)       |
+---------------------------------------------------------------------------------------------------+
|  [ CALLOUT BOX: Final Executive Recommendation ]                                                  |
|  1. LAUNCH FULLY (UNCAPPED): Immediately capture +$145.7k net profit at 6.20x ROAS.               |
|  2. HOLDOUT TEST 100-CAP: Do not cap blindly; test on 10% holdout to confirm retention > 92%.      |
+---------------------------------------------------------------------------------------------------+
```

### Exact DAX Measures for Page 3

#### 1. Dynamic Financial Parameters (What-If Parameters)
```dax
-- Create What-If Parameter in Power BI: 'Parameter_CPM' (Range: 1.0 to 10.0, Increment: 0.5, Default: 2.0)
-- Create What-If Parameter in Power BI: 'Parameter_GrossMargin' (Range: 5 to 100, Increment: 5, Default: 40)

Current_CPM = SELECTEDVALUE(Parameter_CPM[Parameter_CPM Value], 2.00)
Current_GrossMargin = SELECTEDVALUE(Parameter_GrossMargin[Parameter_GrossMargin Value], 40.00)
```

#### 2. Dynamic Financial Outputs
```dax
Total_Media_Spend = 
DIVIDE(14014692, 1000) * [Current_CPM]

Incremental_Gross_Profit = 
[Incremental_Conversions] * [Current_GrossMargin]

Net_Incremental_Profit = 
[Incremental_Gross_Profit] - [Total_Media_Spend]

Margin_Based_ROAS = 
DIVIDE([Incremental_Gross_Profit], [Total_Media_Spend], 0)

CAC_Incremental = 
DIVIDE([Total_Media_Spend], [Incremental_Conversions], 0)
```

#### 3. Dynamic Break-Even Measures
```dax
Break_Even_CPM = 
DIVIDE([Incremental_Conversions] * [Current_GrossMargin], 14014.692)

Break_Even_Margin = 
DIVIDE([Total_Media_Spend], [Incremental_Conversions])
```

---

## 5. Visual Styling & Color Standards
* **Primary Treatment Accent**: `#1F497D` (Navy Blue)
* **Secondary Control Accent**: `#D9534F` (Soft Coral / Red)
* **Positive Profit / Lift Fill**: `#2E7D32` (Forest Green)
* **Negative / Loss Fill**: `#C62828` (Crimson)
* **Neutral / Background Fill**: `#F8F9FA` (Clean Light Gray)
* **Font**: Segoe UI / Calibri, minimum 10pt for labels, 18–24pt bold for Cards.

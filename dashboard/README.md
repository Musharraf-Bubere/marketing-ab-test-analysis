# Dashboard Architecture & Power BI Specification Guide

This directory contains the supporting documentation, financial models, and implementation specifications for the Power BI design specification companion: **"Marketing Campaign A/B Test and Conversion Funnel Analysis"**.

> [!NOTE] Live Functional Dashboard
> The live interactive dashboard for this project is deployed as a Streamlit web application at:
> **https://marketing-ab-test-analysis.streamlit.app/**
> 
> The documentation in this directory and [`../docs/powerbi_dashboard_specification.md`](../docs/powerbi_dashboard_specification.md) provides the data model architecture and DAX specification to implement the dashboard in Power BI Desktop if desired.

---

## 📂 Directory Contents
* **[`business_impact_model.xlsx`](business_impact_model.xlsx)**: Complete dynamic Excel financial model featuring 5 tabs (Inputs, Executive Summary, 2D Sensitivity Matrix, Scenario Comparison, and Timing Hypothesis) with live formulas and hypothetical assumptions.
* **[`../docs/powerbi_dashboard_specification.md`](../docs/powerbi_dashboard_specification.md)**: Full technical implementation guide containing wireframes, layout coordinates, visual styling rules, and exact copy-paste DAX formulas for every measure.

---

## 🛠 How to Build & Publish the Dashboard in Power BI

### Step 1: Ingest Clean Datasets
In Power BI Desktop, select **Get Data -> Text/CSV** and import the aggregated files from `data/clean/`:
1. `group_conversion_summary.csv` -> Baseline & overall cohort KPIs
2. `funnel_exposure_analysis.csv` -> Exposure tiers & impression productivity
3. `day_conversion_summary.csv` -> Day-of-week conversion rates & lifts
4. `daypart_summary.csv` -> Daypart temporal performance
5. `financial_summary_scenarios.csv` -> Commercial ROI across statistical bounds
6. `break_even_metrics.csv` -> Break-even CPM and margin metrics

### Step 2: Implement DAX Measures
Open [`docs/powerbi_dashboard_specification.md`](../docs/powerbi_dashboard_specification.md) and copy the DAX measures into your Power BI model. Key measures include:
* `CR_Treatment`, `CR_Control`, `Absolute_Lift_Pct_Pts`, `Relative_Lift_Pct`
* `Expected_Baseline_Conversions`, `Incremental_Conversions`
* `CI_Lower_Bound_Abs`, `CI_Upper_Bound_Abs`
* `Inc_Conversions_Per_1k_Impressions` (Productivity Metric)
* `Total_Media_Spend`, `Incremental_Gross_Profit`, `Net_Incremental_Profit`, `Margin_Based_ROAS`
* `Break_Even_CPM`, `Break_Even_Margin`

### Step 3: Build the 3 Dashboard Pages
Follow the wireframe layouts defined in the specification:
* **Page 1: Experiment Overview** (KPI Cards, Cohort Table, Statistical Lift & 95% CI Error Bar)
* **Page 2: Segments and Timing** (Exposure Funnel, Impression Productivity, Budget Concentration, Daypart Heatmap)
* **Page 3: Commercial Business Impact** (Financial Cards, Break-Even Gauges, 2D Sensitivity Matrix, Scenario Comparison)

### Step 4: Export Screenshots & Publish
1. Take high-resolution screenshots of each page and save them in:
   * `docs/screenshots/01_experiment_overview.png`
   * `docs/screenshots/02_segments_and_timing.png`
   * `docs/screenshots/03_business_impact.png`
2. Publish to Power BI Service (**File -> Publish -> Publish to Power BI**).
3. If public sharing is enabled, generate a "Publish to Web" public link and add it to the project `README.md`.

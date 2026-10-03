# Marketing Campaign A/B Test and Conversion Funnel Analysis

[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/sqlite-3-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, portfolio-grade analytics project evaluating whether a commercial marketing ad campaign generated a statistically significant and commercially viable lift in conversion rates compared to a baseline Public Service Announcement (PSA) placebo group.

---

## 🎯 Executive Business Question
> **"Did the ad campaign actually increase conversions, for whom, and should the company roll it out?"**

This project moves beyond academic statistical testing to provide decision-makers with:
1. **Rigorous Statistical Verification**: Hypothesis testing, Sample Ratio Mismatch (SRM) checks, confidence intervals, and statistical power calculations.
2. **Behavioral & Funnel Segmentation**: Analysis of conversions across days of the week, peak hours, and ad exposure volume to identify diminishing returns and ad fatigue.
3. **Financial Impact Modeling**: ROI, cost per incremental conversion, and sensitivity tables under varying commercial assumptions.
4. **Actionable Business Recommendations**: Clear decision frameworks on full rollout, targeted segmentation, or exposure capping.

---

## 📂 Repository Structure

```text
marketing-ab-test-analysis/
│
├── app/                     # Interactive Streamlit Web Application (Live Demo)
│   ├── streamlit_app.py     # Main 3-tab dashboard application
│   └── calculations.py      # Dynamic calculations & metric derivation module
│
├── data/
│   ├── raw/                 # Original dataset (excluded from git tracking)
│   ├── clean/               # Aggregated clean CSV exports powering app & BI tools
│   └── marketing_ab.db      # Local SQLite database (generated via ETL pipeline)
│
├── sql/                     # Analytical SQL queries (conversion, timing, exposure)
├── notebooks/               # Jupyter notebooks for statistical modeling & EDA
├── dashboard/               # Financial model & dashboard documentation
│   ├── business_impact_model.xlsx      # Interactive Excel sensitivity model
│   └── README.md            # Dashboard documentation & metrics dictionary
│
├── docs/                    # Research reports, data dictionary, methodology
│   ├── data_validation_report.md
│   ├── statistical_testing_report.md
│   ├── segment_funnel_report.md
│   ├── business_impact_report.md
│   └── powerbi_dashboard_specification.md
│
├── scripts/                 # Reusable Python scripts (ETL, validation, models)
├── tests/                   # Automated pytest suite verifying all numerical benchmarks
│   └── test_numbers.py      # Regression tests ensuring zero metric discrepancies
│
├── .gitignore               # Excludes raw data, virtual environments, cache
├── README.md                # Project documentation and summary
└── requirements.txt         # Pinned Python project dependencies
```

---

## 📊 Dataset Overview
- **Source**: [Kaggle: Marketing A/B Testing Dataset by Favio Vázquez](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing)
- **Scale**: 588,101 unique users
- **Groups**:
  - **Treatment (`ad`)**: 564,577 users shown commercial ads (CR: 2.5547%)
  - **Control (`psa`)**: 23,524 users shown Public Service Announcements (CR: 1.7854%)
- **Full Schema**: Detailed column descriptions are available in [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## 🌐 Interactive Streamlit Dashboard

A live, interactive web dashboard companion to the Power BI specification is available to test commercial assumptions, explore exposure thresholds, and audit experimental integrity.

- **Live Cloud App**: `[Deployed Link: Add your Streamlit Cloud URL here]`
- **Local Run**:
  ```bash
  streamlit run app/streamlit_app.py
  ```

### Dashboard Tabs:
1. **Experiment Overview**: Executive KPI cards, conversion rate comparison with 95% confidence intervals, and a dynamic Sample Ratio Mismatch (SRM) $\chi^2$ check.
2. **Segments & Funnel Dynamics**: Exposure saturation curves (diminishing returns at 100+ ads), daily conversion lifts with Bonferroni-corrected significance, and hourly diurnal patterns.
3. **Financial Impact & What-If**: Live sensitivity analysis across CPM and Gross Margin sliders, break-even threshold calculators, and dynamic Scenario A vs. Scenario B (100-ad frequency cap) risk-return modeling.

---

## 🚀 Quickstart & Reproduction

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Musharraf-Bubere/marketing-ab-test-analysis.git
cd marketing-ab-test-analysis

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Verify Numerical Integrity
Run the automated test suite to verify that all statistical metrics and dynamic derivations match verified benchmarks:
```bash
pytest tests/test_numbers.py -v
```

### 3. Ingest Dataset into SQLite (Optional / Full Pipeline)
Place `marketing_AB.csv` into `data/raw/` and run the automated ETL script:
```bash
python scripts/load_to_sqlite.py
```
This builds the SQLite database `data/marketing_ab.db` with indexed tables and clean snake_case fields.

---

## 🛠 Project Roadmap & Phases
- [x] **Phase 1: Setup, Repository Scaffolding & SQLite Ingestion**
- [x] **Phase 2: Data Validation & Experiment Integrity (SRM & Outlier Audit)**
- [x] **Phase 3: SQL Exploratory & Conversion Analysis**
- [x] **Phase 4: Statistical Testing & Power Analysis (Hypothesis Testing)**
- [x] **Phase 5: Customer Segmentation & Exposure Funnel Analysis**
- [x] **Phase 6: Commercial ROI & Sensitivity Financial Model**
- [x] **Phase 7A: Power BI Specification & DAX Data Model (Design Blueprint)**
- [x] **Phase 7B: Interactive Streamlit Web Application (Live Functional Demo)**
- [ ] **Phase 8: Project Synthesis, Resume Bullets & Final Polish**

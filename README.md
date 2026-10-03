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
├── data/
│   ├── raw/                 # Original dataset (excluded from git tracking)
│   ├── clean/               # Processed/aggregated data exports for BI tools
│   └── marketing_ab.db      # Local SQLite database (generated via ETL script)
│
├── sql/                     # Analytical SQL queries (conversion, timing, exposure)
├── notebooks/               # Jupyter notebooks for statistical modeling & EDA
├── dashboard/               # Power BI / Tableau dashboard files & specifications
├── docs/                    # Data dictionary, methodology notes, and artifacts
│   └── data_dictionary.md   # Full schema & metric definitions
│
├── scripts/                 # Reusable Python scripts (ETL, pipeline)
│   └── load_to_sqlite.py    # Automated SQLite ingestion pipeline
│
├── .gitignore               # Excludes raw data, virtual environments, cache
├── README.md                # Project documentation and summary
└── requirements.txt         # Python project dependencies
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

## 🚀 Quickstart & Reproduction

### 1. Clone & Set Up Environment
```bash
git clone <remote-url>
cd marketing-ab-test-analysis

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Ingest Dataset into SQLite
Place `marketing_AB.csv` into `data/raw/` and run the automated ETL script:
```bash
python scripts/load_to_sqlite.py
```
This builds the SQLite database `data/marketing_ab.db` with indexed tables and clean snake_case fields.

---

## 🛠 Project Roadmap & Phases
- [x] **Phase 1: Setup, Repository Scaffolding & SQLite Ingestion**
- [ ] **Phase 2: Data Validation & Experiment Integrity (SRM & Outlier Audit)**
- [ ] **Phase 3: SQL Exploratory & Conversion Analysis**
- [ ] **Phase 4: Statistical Testing & Power Analysis (Hypothesis Testing)**
- [ ] **Phase 5: Customer Segmentation & Exposure Funnel Analysis**
- [ ] **Phase 6: Commercial ROI & Sensitivity Financial Model**
- [ ] **Phase 7: Interactive Executive Dashboard (Power BI)**
- [ ] **Phase 8: Project Synthesis, Resume Bullets & Final Polish**

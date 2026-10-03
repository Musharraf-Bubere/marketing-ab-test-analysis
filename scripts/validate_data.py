"""
scripts/validate_data.py
------------------------
Phase 2 Data Validation & Experiment Integrity Audit.
Executes automated checks for:
1. Missing values and nulls.
2. Duplicate user records.
3. Group imbalance and Sample Ratio Mismatch (SRM).
4. Ad exposure distribution and outlier detection (total_ads).
"""

import pandas as pd
import numpy as np
from scipy import stats


def run_data_validation(csv_path: str = "data/raw/marketing_AB.csv"):
    df = pd.read_csv(csv_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    print("=" * 60)
    print("PHASE 2: DATA VALIDATION & EXPERIMENT INTEGRITY REPORT")
    print("=" * 60)

    # 1. Null / Missing Value Check
    print("\n[CHECK 1] Null and Missing Value Audit:")
    nulls = df.isnull().sum()
    print(nulls.to_string())
    assert nulls.sum() == 0, "Dataset contains unexpected missing values!"
    print("-> Result: PASS (0 missing values across all columns)")

    # 2. Duplicate User Check
    print("\n[CHECK 2] Duplicate Identifier Audit:")
    total_rows = len(df)
    unique_users = df["user_id"].nunique()
    duplicates = df["user_id"].duplicated().sum()
    print(f"Total Rows: {total_rows:,}")
    print(f"Unique Users: {unique_users:,}")
    print(f"Duplicate User IDs: {duplicates:,}")
    assert duplicates == 0, "Dataset contains duplicate user IDs!"
    print("-> Result: PASS (Each row represents a distinct, unique user)")

    # 3. Sample Ratio Mismatch (SRM) & Group Imbalance Check
    print("\n[CHECK 3] Sample Allocation & SRM Audit:")
    n_ad = (df["test_group"] == "ad").sum()
    n_psa = (df["test_group"] == "psa").sum()
    prop_ad = n_ad / total_rows
    prop_psa = n_psa / total_rows

    print(f"Treatment ('ad'):  {n_ad:,} users ({prop_ad:.4%})")
    print(f"Control   ('psa'):  {n_psa:,} users ({prop_psa:.4%})")
    print(f"Observed Ratio:     {n_ad / n_psa:.5f} : 1")

    # Chi-Square test against intended 96:4 split (0.96 / 0.04)
    exp_ad_96 = total_rows * 0.96
    exp_psa_04 = total_rows * 0.04
    chi2_96, p_96 = stats.chisquare([n_ad, n_psa], [exp_ad_96, exp_psa_04])
    print(f"Chi-Square SRM Test vs 96:4 intended split:")
    print(f"  - Chi2 Statistic: {chi2_96:.6f}")
    print(f"  - p-value:        {p_96:.6f}")
    if p_96 > 0.01:
        print("-> Result: PASS (No SRM detected against 96:4 design; p > 0.01)")
    else:
        print("-> Result: FAIL (Evidence of Sample Ratio Mismatch)")

    # 4. Outlier Analysis in Ad Exposure (total_ads)
    print("\n[CHECK 4] Ad Exposure (total_ads) Distribution & Outliers:")
    q25 = df["total_ads"].quantile(0.25)
    median = df["total_ads"].median()
    q75 = df["total_ads"].quantile(0.75)
    iqr = q75 - q25
    upper_whisker = q75 + 1.5 * iqr

    print(f"Mean total ads:     {df['total_ads'].mean():.2f}")
    print(f"Standard Deviation: {df['total_ads'].std():.2f}")
    print(f"Min:                {df['total_ads'].min()}")
    print(f"25th Percentile:    {q25:.1f}")
    print(f"50th (Median):      {median:.1f}")
    print(f"75th Percentile:    {q75:.1f}")
    print(f"90th Percentile:    {df['total_ads'].quantile(0.90):.1f}")
    print(f"95th Percentile:    {df['total_ads'].quantile(0.95):.1f}")
    print(f"99th Percentile:    {df['total_ads'].quantile(0.99):.1f}")
    print(f"99.9th Percentile:  {df['total_ads'].quantile(0.999):.1f}")
    print(f"Max:                {df['total_ads'].max()}")
    print(f"IQR:                {iqr:.1f} | 1.5*IQR Upper Bound: {upper_whisker:.1f}")

    outliers = df[df["total_ads"] > upper_whisker]
    outlier_count = len(outliers)
    print(f"\nOutliers (> {upper_whisker} ads): {outlier_count:,} ({outlier_count / total_rows:.2%})")
    print(f"  - Outliers in 'ad' group:  {(outliers['test_group'] == 'ad').sum():,} ({(outliers['test_group'] == 'ad').sum() / n_ad:.2%})")
    print(f"  - Outliers in 'psa' group: {(outliers['test_group'] == 'psa').sum():,} ({(outliers['test_group'] == 'psa').sum() / n_psa:.2%})")

    cr_normal = df[df["total_ads"] <= upper_whisker]["converted"].mean()
    cr_outliers = outliers["converted"].mean()
    print(f"Conversion Rate among normal users (<= {upper_whisker} ads): {cr_normal:.4%}")
    print(f"Conversion Rate among outlier users (> {upper_whisker} ads):   {cr_outliers:.4%}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_data_validation()

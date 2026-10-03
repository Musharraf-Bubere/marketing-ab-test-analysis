"""
scripts/run_sql_queries.py
--------------------------
Executes all SQL queries from the /sql directory against data/marketing_ab.db,
displays verification tables in console, and exports clean aggregate CSVs
to data/clean/ for downstream BI dashboard consumption (Phase 7).
"""

import os
import sqlite3
import pandas as pd


def execute_sql_pipeline(
    db_path: str = "data/marketing_ab.db",
    clean_dir: str = "data/clean",
):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Run scripts/load_to_sqlite.py first.")

    os.makedirs(clean_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)

    print("=" * 80)
    print("PHASE 3: SQL ANALYSIS PIPELINE EXECUTION")
    print("=" * 80)

    # 1. Overall Group Conversion Summary
    with open("sql/01_conversion_rate_by_group.sql", "r", encoding="utf-8") as f:
        q1 = f.read()
    df_q1 = pd.read_sql_query(q1, conn)
    print("\n[QUERY 1] Overall Conversion Rate by Group:")
    print(df_q1.to_string(index=False))
    df_q1.to_csv(os.path.join(clean_dir, "group_conversion_summary.csv"), index=False)

    # 2. Timing Analysis (Day and Hour)
    with open("sql/02_conversion_by_day_and_hour.sql", "r", encoding="utf-8") as f:
        q2_full = f.read()

    # Split into sections 2A (Day) and 2B (Hour)
    sections = q2_full.split("-- SECTION 2B:")
    q2_day = sections[0].replace("-- SECTION 2A: Day of Week Performance & Lift Comparison", "").strip()
    q2_hour = ("-- SECTION 2B:" + sections[1]).strip()

    df_day = pd.read_sql_query(q2_day, conn)
    print("\n[QUERY 2A] Conversion by Day of Week:")
    print(df_day.to_string(index=False))
    df_day.to_csv(os.path.join(clean_dir, "day_conversion_summary.csv"), index=False)

    df_hour = pd.read_sql_query(q2_hour, conn)
    print("\n[QUERY 2B] Conversion by Hour of Day (Sample):")
    print(df_hour.head(6).to_string(index=False))
    print("...")
    print(df_hour.tail(6).to_string(index=False))
    df_hour.to_csv(os.path.join(clean_dir, "hour_conversion_summary.csv"), index=False)

    # 3. Ad Exposure Buckets
    with open("sql/03_conversion_by_exposure_bucket.sql", "r", encoding="utf-8") as f:
        q3 = f.read()
    df_q3 = pd.read_sql_query(q3, conn)
    print("\n[QUERY 3] Conversion by Ad Exposure Bucket:")
    print(df_q3.to_string(index=False))
    df_q3.to_csv(os.path.join(clean_dir, "exposure_bucket_summary.csv"), index=False)

    # 4. Executive Group Comparison Summary
    with open("sql/04_group_comparison_summary.sql", "r", encoding="utf-8") as f:
        q4 = f.read()
    df_q4 = pd.read_sql_query(q4, conn)
    print("\n[QUERY 4] Executive KPI Summary & Incremental Impact:")
    print(df_q4.to_string(index=False))
    df_q4.to_csv(os.path.join(clean_dir, "executive_experiment_summary.csv"), index=False)

    conn.close()
    print("\n" + "=" * 80)
    print(f"All queries executed successfully. Clean aggregated CSVs exported to: {clean_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    execute_sql_pipeline()

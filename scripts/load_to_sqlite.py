"""
scripts/load_to_sqlite.py
------------------------
ETL script to load the raw marketing A/B test CSV into a local SQLite database.
Standardizes column names to snake_case and sets optimal SQL data types.
"""

import os
import sqlite3
import pandas as pd


def load_csv_to_sqlite(
    csv_path: str = "data/raw/marketing_AB.csv",
    db_path: str = "data/marketing_ab.db",
    table_name: str = "campaign_results",
):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV not found at: {csv_path}")

    print(f"Reading dataset from: {csv_path}...")
    df = pd.read_csv(csv_path)

    # Clean and standardize column names
    # Drop redundant unnamed index column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    df.columns = [
        col.strip().lower().replace(" ", "_") for col in df.columns
    ]

    # Convert boolean converted column to integer (1 / 0) for SQLite compatibility and easy AVG() aggregations
    df["converted"] = df["converted"].astype(int)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"Connecting to SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table with explicit schema and constraints
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            user_id INTEGER PRIMARY KEY,
            test_group TEXT NOT NULL,
            converted INTEGER NOT NULL,
            total_ads INTEGER NOT NULL,
            most_ads_day TEXT NOT NULL,
            most_ads_hour INTEGER NOT NULL
        );
    """)

    print(f"Writing {len(df):,} records to table '{table_name}'...")
    df.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False,
        chunksize=25000,
    )

    # Create index on test_group and conversion for query performance
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_test_group ON {table_name}(test_group);")
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_converted ON {table_name}(converted);")
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_day_hour ON {table_name}(most_ads_day, most_ads_hour);")

    conn.commit()

    # Verification
    cursor.execute(f"SELECT COUNT(*), SUM(converted), AVG(converted) FROM {table_name};")
    total_records, total_converted, conversion_rate = cursor.fetchone()
    print("Database verification:")
    print(f"  - Total records: {total_records:,}")
    print(f"  - Total converted: {total_converted:,}")
    print(f"  - Overall conversion rate: {conversion_rate:.4%}")

    conn.close()
    print("SQLite load completed successfully.")


if __name__ == "__main__":
    load_csv_to_sqlite()

#!/usr/bin/env python3
"""
Convert Consumer Edge Combined CSV.gz files to Parquet using streaming writes.
Avoids loading all data into memory simultaneously.
"""

import pyarrow as pa
import pyarrow.csv as pv_csv
import pyarrow.parquet as pq
from pathlib import Path
import time
import sys

INPUT_DIR = Path("/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_combined_2026-01-12/brand-and-geography-cohort-breakout")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_combined_2026-01-12/parquet")
OUTPUT_FILE = OUTPUT_DIR / "consumer_edge_brand_geo_combined.parquet"

def main():
    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv.gz"))
    print(f"Found {len(csv_files)} CSV files to convert")

    if len(csv_files) == 0:
        print("ERROR: No CSV files found!")
        sys.exit(1)

    print("Converting CSV files to Parquet (streaming)...")
    total_rows = 0
    writer = None

    for i, f in enumerate(csv_files):
        table = pv_csv.read_csv(f)
        total_rows += table.num_rows

        if writer is None:
            writer = pq.ParquetWriter(OUTPUT_FILE, table.schema, compression='snappy')

        writer.write_table(table)

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(csv_files)} files ({total_rows:,} rows so far)...")

    writer.close()

    total_time = (time.time() - start_time) / 60
    file_size_gb = OUTPUT_FILE.stat().st_size / 1e9

    print(f"\nTotal rows: {total_rows:,}")
    print(f"Parquet file size: {file_size_gb:.2f} GB")
    print(f"Total time: {total_time:.2f} minutes")

    metadata = pq.read_metadata(OUTPUT_FILE)
    print(f"Row groups: {metadata.num_row_groups}")
    print(f"Columns: {metadata.num_columns}")

if __name__ == "__main__":
    main()

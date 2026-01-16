#!/usr/bin/env python3
"""
Step 3: Filter 2024 Advan data by state.

Array job - processes one state at a time based on SLURM_ARRAY_TASK_ID.
"""

import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
import os
import sys

ADVAN_INPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/advan_foot_traffic_2024_2026-01-12/foot-traffic-monthly-2024")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/advan_2024_filtered")

STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
    'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
    'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
    'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

KEEP_COLUMNS = [
    'PLACEKEY', 'PARENT_PLACEKEY', 'LOCATION_NAME', 'BRANDS',
    'TOP_CATEGORY', 'SUB_CATEGORY', 'NAICS_CODE',
    'LATITUDE', 'LONGITUDE', 'STREET_ADDRESS', 'CITY', 'REGION', 'POSTAL_CODE',
    'ISO_COUNTRY_CODE', 'DATE_RANGE_START', 'DATE_RANGE_END',
    'RAW_VISIT_COUNTS', 'RAW_VISITOR_COUNTS', 'VISITS_BY_DAY',
    'VISITOR_HOME_CBGS', 'VISITOR_DAYTIME_CBGS', 'VISITOR_COUNTRY_OF_ORIGIN',
    'MEDIAN_DWELL', 'BUCKETED_DWELL_TIMES',
    'RELATED_SAME_DAY_BRAND', 'RELATED_SAME_WEEK_BRAND',
    'DEVICE_TYPE', 'NORMALIZED_VISITS_BY_STATE_SCALING',
    'NORMALIZED_VISITS_BY_REGION_NAICS_VISITS', 'NORMALIZED_VISITS_BY_REGION_NAICS_VISITORS',
    'NORMALIZED_VISITS_BY_TOTAL_VISITS', 'NORMALIZED_VISITS_BY_TOTAL_VISITORS'
]


def filter_state(state: str):
    """Filter all 2024 Advan files for a single state."""
    print(f"=" * 60)
    print(f"FILTERING STATE: {state}")
    print(f"=" * 60)

    output_state_dir = OUTPUT_DIR / state
    output_state_dir.mkdir(parents=True, exist_ok=True)

    parquet_files = sorted(ADVAN_INPUT_DIR.glob("*.parquet"))
    print(f"Found {len(parquet_files)} input parquet files")

    total_rows = 0
    files_processed = 0

    for pq_file in parquet_files:
        month = pq_file.name.split('--')[0]

        output_file = output_state_dir / f"{state}_{month}.parquet"

        if output_file.exists():
            existing = pd.read_parquet(output_file)
            total_rows += len(existing)
            files_processed += 1
            print(f"  {month}: Already exists ({len(existing):,} rows)")
            continue

        print(f"  Processing: {pq_file.name}")

        try:
            df = pd.read_parquet(pq_file)

            if 'REGION' not in df.columns:
                print(f"    WARNING: No REGION column, skipping")
                continue

            filtered = df[(df['REGION'] == state) & (df['ISO_COUNTRY_CODE'] == 'US')].copy()

            if len(filtered) == 0:
                print(f"    No data for {state}")
                continue

            available_cols = [c for c in KEEP_COLUMNS if c in filtered.columns]
            filtered = filtered[available_cols]

            filtered.to_parquet(output_file, index=False)
            total_rows += len(filtered)
            files_processed += 1

            print(f"    Saved: {len(filtered):,} rows")

        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\n{state} complete: {total_rows:,} total rows across {files_processed} files")
    return total_rows


def main():
    task_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0))

    if task_id < 0 or task_id >= len(STATES):
        print(f"ERROR: Invalid task ID {task_id}. Valid range: 0-{len(STATES)-1}")
        sys.exit(1)

    state = STATES[task_id]
    print(f"Task {task_id}: Processing state {state}")

    filter_state(state)

    print("\nDone!")


if __name__ == "__main__":
    main()

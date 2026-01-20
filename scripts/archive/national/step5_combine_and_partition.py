#!/usr/bin/env python3
"""
Step 5: Combine all state outputs and partition by month.

Creates 12 monthly parquet files for the final national dataset.
"""

import pandas as pd
from pathlib import Path

INPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/partisan_lean_by_state")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/outputs/location_partisan_lean/national_2024")


def main():
    print("=" * 60)
    print("STEP 5: COMBINE AND PARTITION BY MONTH")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    state_files = sorted(INPUT_DIR.glob("*.parquet"))
    print(f"Found {len(state_files)} state files")

    if len(state_files) == 0:
        print("ERROR: No state files found")
        return

    print("\nLoading all state files...")
    all_dfs = []
    for sf in state_files:
        state = sf.stem
        df = pd.read_parquet(sf)
        print(f"  {state}: {len(df):,} POI-months")
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal combined: {len(combined):,} POI-months")

    combined['month'] = pd.to_datetime(combined['date_range_start']).dt.strftime('%Y-%m')

    print("\nPartitioning by month...")
    for month, month_df in combined.groupby('month'):
        output_file = OUTPUT_DIR / f"{month}.parquet"
        month_df.to_parquet(output_file, index=False)
        print(f"  {month}: {len(month_df):,} POI-months -> {output_file.name}")

    print("\n" + "=" * 60)
    print("FINAL DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total POI-months: {len(combined):,}")
    print(f"  Unique POIs: {combined['placekey'].nunique():,}")
    print(f"  States: {combined['region'].nunique()}")
    print(f"  Months: {combined['month'].nunique()}")
    print(f"  Mean rep_lean: {combined['rep_lean'].mean():.4f}")
    print(f"  Median rep_lean: {combined['rep_lean'].median():.4f}")
    print(f"  Std dev: {combined['rep_lean'].std():.4f}")
    print(f"  Mean pct_visitors_matched: {combined['pct_visitors_matched'].mean():.1f}%")

    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("Done!")


if __name__ == "__main__":
    main()

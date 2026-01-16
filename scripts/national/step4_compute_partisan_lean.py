#!/usr/bin/env python3
"""
Step 4: Parse visitor CBGs and compute weighted partisan lean.

Array job - processes one state at a time based on SLURM_ARRAY_TASK_ID.
Uses national CBG lookup for cross-border visitor matching.
"""

import pandas as pd
import json
from pathlib import Path
import os
import sys

FILTERED_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/advan_2024_filtered")
CBG_LOOKUP = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/inputs/cbg_partisan_lean_national.parquet")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/partisan_lean_by_state")
UNMATCHED_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/unmatched_cbgs")

STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
    'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
    'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
    'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]


def parse_visitor_cbgs(cbg_json: str) -> dict:
    """Parse visitor_home_cbgs JSON string to dict."""
    if pd.isna(cbg_json) or cbg_json == '' or cbg_json == '{}':
        return {}
    try:
        return json.loads(cbg_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def process_state(state: str, cbg_lookup: pd.DataFrame):
    """Process all months for a single state."""
    print(f"=" * 60)
    print(f"COMPUTING PARTISAN LEAN: {state}")
    print(f"=" * 60)

    state_dir = FILTERED_DIR / state
    if not state_dir.exists():
        print(f"ERROR: No filtered data for {state}")
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    UNMATCHED_DIR.mkdir(parents=True, exist_ok=True)

    monthly_files = sorted(state_dir.glob(f"{state}_*.parquet"))
    print(f"Found {len(monthly_files)} monthly files")

    if len(monthly_files) == 0:
        print("No files to process")
        return None

    all_results = []
    all_unmatched = []

    for pq_file in monthly_files:
        month = pq_file.stem.split('_')[1]
        print(f"\n  Processing: {month}")

        df = pd.read_parquet(pq_file)
        print(f"    Loaded {len(df):,} POIs")

        df['parsed_cbgs'] = df['VISITOR_HOME_CBGS'].apply(parse_visitor_cbgs)
        df = df[df['parsed_cbgs'].apply(len) > 0].copy()
        print(f"    POIs with visitor data: {len(df):,}")

        if len(df) == 0:
            continue

        def cbg_dict_to_list(d):
            return [(str(k).zfill(12), v) for k, v in d.items()]

        df['cbg_list'] = df['parsed_cbgs'].apply(cbg_dict_to_list)
        df = df.explode('cbg_list')
        df = df[df['cbg_list'].notna()].copy()

        if len(df) == 0:
            continue

        df['cbg_geoid'] = df['cbg_list'].apply(lambda x: x[0])
        df['visitor_count'] = df['cbg_list'].apply(lambda x: x[1])

        df = df.merge(
            cbg_lookup[['cbg_geoid', 'two_party_rep_share_2020']],
            on='cbg_geoid',
            how='left'
        )

        unmatched_mask = df['two_party_rep_share_2020'].isna()
        if unmatched_mask.any():
            unmatched_cbgs = df[unmatched_mask].groupby('cbg_geoid').agg({
                'visitor_count': 'sum',
                'PLACEKEY': 'nunique'
            }).reset_index()
            unmatched_cbgs.columns = ['cbg_geoid', 'total_visitors', 'poi_count']
            unmatched_cbgs['state'] = state
            unmatched_cbgs['month'] = month
            all_unmatched.append(unmatched_cbgs)

        matched = df[~unmatched_mask].copy()
        print(f"    Matched records: {len(matched):,} ({len(matched)/len(df)*100:.1f}%)")

        if len(matched) == 0:
            continue

        matched['weighted_rep'] = matched['visitor_count'] * matched['two_party_rep_share_2020']

        keep_cols = ['PLACEKEY', 'PARENT_PLACEKEY', 'LOCATION_NAME', 'BRANDS',
                     'TOP_CATEGORY', 'SUB_CATEGORY', 'NAICS_CODE', 'CITY', 'REGION', 'MEDIAN_DWELL']
        available_cols = [c for c in keep_cols if c in matched.columns]

        agg_dict = {
            'visitor_count': 'sum',
            'weighted_rep': 'sum',
        }
        for col in available_cols:
            if col != 'PLACEKEY':
                agg_dict[col] = 'first'

        grouped = matched.groupby('PLACEKEY').agg(agg_dict).reset_index()

        unmatched_by_poi = df[unmatched_mask].groupby('PLACEKEY')['visitor_count'].sum().reset_index()
        unmatched_by_poi.columns = ['PLACEKEY', 'unmatched_visitors']

        grouped = grouped.merge(unmatched_by_poi, on='PLACEKEY', how='left')
        grouped['unmatched_visitors'] = grouped['unmatched_visitors'].fillna(0)

        grouped = grouped.rename(columns={
            'PLACEKEY': 'placekey',
            'PARENT_PLACEKEY': 'parent_placekey',
            'LOCATION_NAME': 'location_name',
            'BRANDS': 'brands',
            'TOP_CATEGORY': 'top_category',
            'SUB_CATEGORY': 'sub_category',
            'NAICS_CODE': 'naics_code',
            'CITY': 'city',
            'REGION': 'region',
            'MEDIAN_DWELL': 'median_dwell',
            'visitor_count': 'total_visitors',
        })

        grouped['rep_lean'] = grouped['weighted_rep'] / grouped['total_visitors']
        grouped['pct_visitors_matched'] = grouped['total_visitors'] / (grouped['total_visitors'] + grouped['unmatched_visitors']) * 100
        grouped['date_range_start'] = month
        grouped = grouped.drop(columns=['weighted_rep'])

        all_results.append(grouped)
        print(f"    Output: {len(grouped):,} POIs")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        output_file = OUTPUT_DIR / f"{state}.parquet"
        combined.to_parquet(output_file, index=False)
        print(f"\n{state}: Saved {len(combined):,} POI-months to {output_file}")

    if all_unmatched:
        unmatched_combined = pd.concat(all_unmatched, ignore_index=True)
        unmatched_file = UNMATCHED_DIR / f"{state}_unmatched.parquet"
        unmatched_combined.to_parquet(unmatched_file, index=False)
        print(f"Unmatched CBGs: {len(unmatched_combined):,} unique CBGs logged")

    return combined if all_results else None


def main():
    task_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0))

    if task_id < 0 or task_id >= len(STATES):
        print(f"ERROR: Invalid task ID {task_id}. Valid range: 0-{len(STATES)-1}")
        sys.exit(1)

    state = STATES[task_id]
    print(f"Task {task_id}: Processing state {state}")

    print(f"\nLoading national CBG lookup from: {CBG_LOOKUP}")
    cbg_lookup = pd.read_parquet(CBG_LOOKUP)
    print(f"  Loaded {len(cbg_lookup):,} CBGs")

    process_state(state, cbg_lookup)

    print("\nDone!")


if __name__ == "__main__":
    main()

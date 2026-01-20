#!/usr/bin/env python3
"""
Prepare data for the Stakeholder Ideology Dashboard.

Steps:
1. Load partisan lean data (most recent 12 months)
2. Join with raw Advan to get lat/lon coordinates
3. Aggregate to unique POIs with time-averaged partisan lean
4. Compute local baseline (average of neighbors within 1km, same category)
5. Create summary tables (brand, MSA)

Output:
- poi_with_coords.parquet: ~unique POIs with coords + partisan lean + excess lean
- brand_summary.parquet: brand-level aggregates
- msa_summary.parquet: MSA-level aggregates
- category_list.json: available categories for filtering
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import gc
from time import time
import warnings
warnings.filterwarnings('ignore')

PARTISAN_LEAN_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/national")
ADVAN_SOURCE_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/foot_traffic_monthly_complete_2026-01-12/monthly-patterns-foot-traffic")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data")

RECENT_MONTHS = 12


def load_partisan_lean_recent():
    """Load most recent N months of partisan lean data."""
    print("=" * 60)
    print("STEP 1: Loading partisan lean data")
    print("=" * 60)

    files = sorted(PARTISAN_LEAN_DIR.glob("partisan_lean_*.parquet"))
    if not files:
        raise ValueError(f"No partisan lean files found in {PARTISAN_LEAN_DIR}")

    recent_files = files[-RECENT_MONTHS:]
    print(f"Found {len(files)} total files, using last {len(recent_files)}")
    print(f"Loading {recent_files[0].stem} to {recent_files[-1].stem}")

    dfs = []
    for f in recent_files:
        df = pd.read_parquet(f)
        dfs.append(df)
        print(f"  Loaded {f.stem}: {len(df):,} rows", flush=True)

    combined = pd.concat(dfs, ignore_index=True)
    del dfs
    gc.collect()

    print(f"Total rows: {len(combined):,}")
    return combined


def load_advan_coordinates():
    """Load placekey -> lat/lon mapping from raw Advan data."""
    print("\n" + "=" * 60)
    print("STEP 2: Loading coordinates from Advan source")
    print("=" * 60)

    coord_dfs = []

    csv_files = sorted(ADVAN_SOURCE_DIR.glob("*.csv.gz"))
    print(f"Found {len(csv_files)} csv.gz files")

    sample_files = csv_files[::20]
    print(f"Sampling {len(sample_files)} files for coordinates (every 20th file)...")

    for i, f in enumerate(sample_files):
        try:
            df = pd.read_csv(
                f,
                compression='gzip',
                usecols=['PLACEKEY', 'LATITUDE', 'LONGITUDE', 'LOCATION_NAME'],
                dtype={'PLACEKEY': str, 'LOCATION_NAME': str}
            )
            coord_dfs.append(df)
            if (i + 1) % 10 == 0:
                print(f"  Loaded {i+1}/{len(sample_files)} files...", flush=True)
        except Exception as e:
            print(f"  Error loading {f.name}: {e}")
            continue

    if not coord_dfs:
        raise ValueError("No coordinate data found!")

    coords = pd.concat(coord_dfs, ignore_index=True)
    del coord_dfs
    gc.collect()

    coords = coords.drop_duplicates(subset=['PLACEKEY'])
    coords = coords.rename(columns={
        'PLACEKEY': 'placekey',
        'LATITUDE': 'latitude',
        'LONGITUDE': 'longitude',
        'LOCATION_NAME': 'location_name'
    })

    print(f"Total unique POIs with coordinates: {len(coords):,}")
    return coords


def aggregate_to_poi_level(df):
    """Aggregate monthly data to POI level with time-averaged metrics."""
    print("\n" + "=" * 60)
    print("STEP 3: Aggregating to POI level")
    print("=" * 60)

    poi_agg = df.groupby('placekey').agg({
        'brand': 'first',
        'city': 'first',
        'region': 'first',
        'cbsa_title': 'first',
        'top_category': 'first',
        'sub_category': 'first',
        'naics_code': 'first',
        'rep_lean_2020': 'mean',
        'rep_lean_2016': 'mean',
        'total_visitors': 'sum',
        'matched_visitors': 'sum',
        'pct_visitors_matched': 'mean',
        'year_month': 'count'
    }).reset_index()

    poi_agg = poi_agg.rename(columns={
        'year_month': 'months_observed',
        'rep_lean_2020': 'mean_rep_lean_2020',
        'rep_lean_2016': 'mean_rep_lean_2016'
    })

    poi_agg['naics_code'] = (poi_agg['naics_code']
        .fillna('')
        .astype(str)
        .str.replace(r'\.0$', '', regex=True))
    poi_agg['naics_2'] = poi_agg['naics_code'].str[:2]
    poi_agg['naics_3'] = poi_agg['naics_code'].str[:3]
    poi_agg['naics_4'] = poi_agg['naics_code'].str[:4]
    poi_agg['naics_5'] = poi_agg['naics_code'].str[:5]
    poi_agg['naics_6'] = poi_agg['naics_code'].str[:6]

    print(f"Unique POIs: {len(poi_agg):,}")
    print(f"POIs with brand: {poi_agg['brand'].notna().sum():,}")
    print(f"POIs with NAICS: {(poi_agg['naics_code'] != '').sum():,}")
    return poi_agg


def join_coordinates(poi_df, coords_df):
    """Join POI data with coordinates."""
    print("\n" + "=" * 60)
    print("STEP 4: Joining coordinates")
    print("=" * 60)

    merged = poi_df.merge(coords_df, on='placekey', how='left')

    has_coords = merged['latitude'].notna()
    print(f"POIs with coordinates: {has_coords.sum():,} ({100*has_coords.mean():.1f}%)")
    print(f"POIs missing coordinates: {(~has_coords).sum():,}")

    merged = merged[has_coords].copy()
    return merged


def create_brand_summary(df):
    """Create brand-level summary statistics."""
    print("\n" + "=" * 60)
    print("STEP 5: Creating brand summary")
    print("=" * 60)

    branded = df[df['brand'].notna() & (df['brand'] != '')].copy()

    brand_summary = branded.groupby('brand').agg({
        'placekey': 'count',
        'mean_rep_lean_2020': ['mean', 'std', 'median'],
        'mean_rep_lean_2016': ['mean', 'std'],
        'total_visitors': 'sum',
        'cbsa_title': 'nunique',
        'region': 'nunique',
        'top_category': 'first'
    }).reset_index()

    brand_summary.columns = [
        'brand', 'n_locations',
        'mean_rep_lean_2020', 'std_rep_lean_2020', 'median_rep_lean_2020',
        'mean_rep_lean_2016', 'std_rep_lean_2016',
        'total_visitors', 'n_msas', 'n_states', 'top_category'
    ]

    brand_summary = brand_summary.sort_values('n_locations', ascending=False)

    print(f"Brands: {len(brand_summary):,}")
    print(f"Brands with 50+ locations: {(brand_summary['n_locations'] >= 50).sum():,}")

    return brand_summary


def create_msa_summary(df):
    """Create MSA-level summary statistics."""
    print("\n" + "=" * 60)
    print("STEP 6: Creating MSA summary")
    print("=" * 60)

    msa_df = df[df['cbsa_title'].notna()].copy()

    msa_summary = msa_df.groupby('cbsa_title').agg({
        'placekey': 'count',
        'mean_rep_lean_2020': ['mean', 'std', 'median'],
        'total_visitors': 'sum',
        'brand': lambda x: x.notna().sum(),
        'region': 'first'
    }).reset_index()

    msa_summary.columns = [
        'cbsa_title', 'n_pois',
        'mean_rep_lean_2020', 'std_rep_lean_2020', 'median_rep_lean_2020',
        'total_visitors', 'n_branded_pois', 'region'
    ]

    msa_summary = msa_summary.sort_values('n_pois', ascending=False)

    print(f"MSAs: {len(msa_summary):,}")

    return msa_summary


def create_category_list(df):
    """Create list of available categories and NAICS codes."""
    categories = df['top_category'].dropna().value_counts()
    category_list = [
        {'category': cat, 'count': int(count)}
        for cat, count in categories.items()
    ]

    naics_2_counts = df[df['naics_2'] != ''].groupby('naics_2').size()
    naics_list = [
        {'naics_2': code, 'count': int(count)}
        for code, count in naics_2_counts.items()
    ]

    return {'categories': category_list, 'naics_codes': naics_list}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    partisan_df = load_partisan_lean_recent()
    coords_df = load_advan_coordinates()
    poi_df = aggregate_to_poi_level(partisan_df)
    del partisan_df
    gc.collect()

    poi_df = join_coordinates(poi_df, coords_df)
    del coords_df
    gc.collect()

    brand_summary = create_brand_summary(poi_df)
    msa_summary = create_msa_summary(poi_df)
    category_list = create_category_list(poi_df)

    print("\n" + "=" * 60)
    print("STEP 7: Saving outputs")
    print("=" * 60)

    poi_output = OUTPUT_DIR / "poi_with_coords.parquet"
    poi_df.to_parquet(poi_output, index=False)
    print(f"Saved POI data: {poi_output} ({len(poi_df):,} rows)")

    brand_output = OUTPUT_DIR / "brand_summary.parquet"
    brand_summary.to_parquet(brand_output, index=False)
    print(f"Saved brand summary: {brand_output} ({len(brand_summary):,} rows)")

    msa_output = OUTPUT_DIR / "msa_summary.parquet"
    msa_summary.to_parquet(msa_output, index=False)
    print(f"Saved MSA summary: {msa_output} ({len(msa_summary):,} rows)")

    category_output = OUTPUT_DIR / "filter_options.json"
    with open(category_output, 'w') as f:
        json.dump(category_list, f, indent=2)
    print(f"Saved filter options: {category_output} ({len(category_list['categories'])} categories, {len(category_list['naics_codes'])} NAICS codes)")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)

    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Files created:")
    for f in OUTPUT_DIR.glob("*"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name}: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()

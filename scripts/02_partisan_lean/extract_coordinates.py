#!/usr/bin/env python3
"""
Extract POI coordinates (latitude, longitude) from raw Advan data.

Creates a deduplicated lookup table: placekey → (latitude, longitude)
This avoids re-running the full partisan lean computation just to add coordinates.

Usage:
    python3 extract_coordinates.py

Output:
    outputs/poi_coordinates.parquet - deduplicated placekey → lat/lon mapping
"""

import pandas as pd
from pathlib import Path
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("/global/scratch/users/maxkagan/01_foot_traffic_location/advan/foot_traffic_monthly_complete_2026-01-12/monthly-patterns-foot-traffic")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs")
OUTPUT_PATH = OUTPUT_DIR / "poi_coordinates.parquet"

COLUMNS_TO_READ = ['PLACEKEY', 'LATITUDE', 'LONGITUDE']


def main():
    logger.info("=" * 60)
    logger.info("Extracting POI coordinates from raw Advan data")
    logger.info("=" * 60)

    files = sorted(RAW_DATA_DIR.glob("*.csv.gz"))
    logger.info(f"Found {len(files)} raw Advan files")

    if not files:
        logger.error("No files found!")
        return 1

    all_coords = []
    seen_placekeys = set()

    for i, f in enumerate(files):
        if i % 100 == 0:
            logger.info(f"Processing file {i+1}/{len(files)}... ({len(seen_placekeys):,} unique placekeys so far)")

        try:
            df = pd.read_csv(
                f,
                compression='gzip',
                usecols=COLUMNS_TO_READ,
                dtype={'PLACEKEY': str}
            )

            df.columns = df.columns.str.lower()
            df = df.dropna(subset=['placekey', 'latitude', 'longitude'])

            new_rows = df[~df['placekey'].isin(seen_placekeys)]
            if len(new_rows) > 0:
                all_coords.append(new_rows)
                seen_placekeys.update(new_rows['placekey'])

        except Exception as e:
            logger.warning(f"Error processing {f.name}: {e}")
            continue

    if not all_coords:
        logger.error("No valid coordinates found!")
        return 1

    logger.info(f"Concatenating {len(all_coords)} chunks...")
    coords_df = pd.concat(all_coords, ignore_index=True)

    coords_df = coords_df.drop_duplicates(subset=['placekey'], keep='first')

    logger.info(f"Final coordinate table: {len(coords_df):,} unique POIs")
    logger.info(f"Latitude range: [{coords_df['latitude'].min():.4f}, {coords_df['latitude'].max():.4f}]")
    logger.info(f"Longitude range: [{coords_df['longitude'].min():.4f}, {coords_df['longitude'].max():.4f}]")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    coords_df.to_parquet(OUTPUT_PATH, index=False, compression='snappy')
    logger.info(f"Saved to {OUTPUT_PATH}")

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    logger.info(f"File size: {file_size_mb:.1f} MB")

    logger.info("=" * 60)
    logger.info("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Step 0: Download and process CBSA (Metropolitan Statistical Area) crosswalk.

This script:
1. Downloads the NBER CBSA-to-FIPS county crosswalk (sourced from Census Bureau)
2. Creates a county FIPS → CBSA code/title mapping
3. Saves as parquet for fast lookup

Output: /global/scratch/users/maxkagan/project_oakland/inputs/cbsa_crosswalk.parquet
"""

import pandas as pd
import logging
from pathlib import Path
import requests
import io

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("/global/scratch/users/maxkagan/project_oakland/inputs")
OUTPUT_FILE = OUTPUT_DIR / "cbsa_crosswalk.parquet"

CBSA_URL = "https://data.nber.org/cbsa-csa-fips-county-crosswalk/2023/cbsa2fipsxw_2023.csv"


def download_cbsa_delineation():
    """Download CBSA crosswalk CSV from NBER."""
    logger.info(f"Downloading CBSA crosswalk from {CBSA_URL}")

    try:
        response = requests.get(CBSA_URL, timeout=60)
        response.raise_for_status()

        df = pd.read_csv(io.StringIO(response.text), dtype=str)
        logger.info(f"Downloaded {len(df)} rows")
        logger.info(f"Columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        logger.error(f"Failed to download: {e}")
        return None


def process_cbsa_crosswalk(df):
    """Process CBSA data into county → CBSA mapping."""
    logger.info("Processing CBSA crosswalk...")

    result = df[['cbsacode', 'cbsatitle', 'fipsstatecode', 'fipscountycode']].copy()

    if 'metropolitanmicropolitanstatis' in df.columns:
        result['metro_micro'] = df['metropolitanmicropolitanstatis']

    result.columns = ['cbsa_code', 'cbsa_title', 'state_fips', 'county_fips'] + (
        ['metro_micro'] if 'metropolitanmicropolitanstatis' in df.columns else []
    )

    result = result.dropna(subset=['cbsa_code', 'state_fips', 'county_fips'])

    result['state_fips'] = result['state_fips'].str.zfill(2)
    result['county_fips'] = result['county_fips'].str.zfill(3)
    result['county_fips_full'] = result['state_fips'] + result['county_fips']

    logger.info(f"Processed {len(result)} county-CBSA mappings")
    logger.info(f"Unique CBSAs: {result['cbsa_code'].nunique()}")
    logger.info(f"Unique counties: {result['county_fips_full'].nunique()}")

    return result


def main():
    """Run CBSA crosswalk setup."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = download_cbsa_delineation()
    if df is None:
        logger.error("Failed to download CBSA data")
        return 1

    crosswalk = process_cbsa_crosswalk(df)
    if crosswalk is None:
        logger.error("Failed to process CBSA data")
        return 1

    try:
        crosswalk.to_parquet(OUTPUT_FILE, index=False, compression='snappy')
        logger.info(f"Saved CBSA crosswalk to {OUTPUT_FILE}")

        logger.info("\nSample data:")
        logger.info(crosswalk.head(10).to_string())

        return 0
    except Exception as e:
        logger.error(f"Failed to save: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

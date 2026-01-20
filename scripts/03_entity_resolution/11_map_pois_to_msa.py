#!/usr/bin/env python3
"""
Map unbranded POIs to MSAs for Tier 2 singleton matching.

Steps:
1. Build placekey → poi_cbg lookup from partisan lean files
2. Load US POIs and join with poi_cbg
3. Identify unbranded POIs (not covered by national brand matches)
4. Map POIs to MSAs using county FIPS from POI_CBG
5. Output unbranded POIs with MSA assignment, partitioned by MSA

Output: unbranded_pois_by_msa/ directory with one parquet per MSA
"""

import pandas as pd
from pathlib import Path
import logging
import sys

sys.path.insert(0, '/global/scratch/users/maxkagan/measuring_stakeholder_ideology/inputs')
from paw_to_cbsa_crosswalk import CBSA_TO_PAW

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
PARTISAN_LEAN_DIR = PROJECT_DIR / "outputs" / "national"
POI_FILE = PROJECT_DIR / "inputs" / "entity_resolution" / "advan_pois_us_only.parquet"
BRAND_MATCHES_FILE = PROJECT_DIR / "outputs" / "entity_resolution" / "brand_matches_validated.parquet"
CBSA_CROSSWALK_FILE = PROJECT_DIR / "inputs" / "cbsa_crosswalk.parquet"
PAW_MSA_FILE = PROJECT_DIR / "outputs" / "entity_resolution" / "paw_company_by_msa.parquet"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "entity_resolution" / "unbranded_pois_by_msa"


def normalize_msa_name(cbsa_title: str) -> str:
    """Convert CBSA title to MSA filename format used by PAW position files."""
    if pd.isna(cbsa_title):
        return None
    name = cbsa_title.lower()
    name = name.replace(', ', '_').replace(' ', '_').replace('-', '-')
    name = name.replace('/', '-').replace('.', '')
    name = ''.join(c for c in name if c.isalnum() or c in '-_')
    return name


def build_placekey_cbg_lookup():
    """Build placekey → poi_cbg lookup from ALL partisan lean files."""
    logger.info("Building placekey → poi_cbg lookup from ALL partisan lean files...")

    files = sorted(PARTISAN_LEAN_DIR.glob("partisan_lean_*.parquet"))
    logger.info(f"Found {len(files)} partisan lean files")

    all_lookups = []
    for i, f in enumerate(files):
        df = pd.read_parquet(f, columns=['placekey', 'poi_cbg'])
        df = df.drop_duplicates(subset=['placekey'])
        all_lookups.append(df)
        if (i + 1) % 10 == 0:
            logger.info(f"  Processed {i + 1}/{len(files)} files...")

    logger.info("Concatenating and deduplicating...")
    lookup = pd.concat(all_lookups, ignore_index=True)
    lookup = lookup.drop_duplicates(subset=['placekey'])
    logger.info(f"Lookup table: {len(lookup):,} unique placekeys with poi_cbg (from {len(files)} months)")

    return lookup


def main():
    logger.info("=== Mapping Unbranded POIs to MSAs ===")

    placekey_cbg = build_placekey_cbg_lookup()

    logger.info("Loading US POIs...")
    pois = pd.read_parquet(POI_FILE)
    logger.info(f"Total US POIs: {len(pois):,}")

    pk_col = 'PLACEKEY' if 'PLACEKEY' in pois.columns else 'placekey'
    pois = pois.rename(columns={pk_col: 'placekey'})

    logger.info("Joining poi_cbg to POIs...")
    pois = pois.merge(placekey_cbg, on='placekey', how='left')
    has_cbg = pois['poi_cbg'].notna()
    logger.info(f"POIs with poi_cbg: {has_cbg.sum():,} ({100*has_cbg.mean():.1f}%)")

    logger.info("Loading brand matches...")
    brand_matches = pd.read_parquet(BRAND_MATCHES_FILE)
    matched_brand_ids = set(brand_matches['safegraph_brand_id'].unique())
    logger.info(f"Matched brand IDs: {len(matched_brand_ids):,}")

    brand_id_col = 'SAFEGRAPH_BRAND_IDS' if 'SAFEGRAPH_BRAND_IDS' in pois.columns else 'safegraph_brand_ids'
    if brand_id_col not in pois.columns:
        logger.error(f"No brand ID column found. Columns: {pois.columns.tolist()}")
        return

    pois['is_branded'] = pois[brand_id_col].notna() & (pois[brand_id_col] != '')
    pois['has_matched_brand'] = pois[brand_id_col].isin(matched_brand_ids)

    branded_count = pois['is_branded'].sum()
    matched_brand_count = pois['has_matched_brand'].sum()
    logger.info(f"POIs with any brand: {branded_count:,}")
    logger.info(f"POIs with matched brand: {matched_brand_count:,}")

    unbranded = pois[~pois['has_matched_brand'] & has_cbg].copy()
    logger.info(f"Unbranded POIs with CBG (for Tier 2 matching): {len(unbranded):,}")

    logger.info("Loading CBSA crosswalk...")
    cbsa_xw = pd.read_parquet(CBSA_CROSSWALK_FILE)
    logger.info(f"CBSA crosswalk: {len(cbsa_xw):,} county-MSA mappings")

    unbranded['county_fips_full'] = unbranded['poi_cbg'].astype(str).str[:5]

    unbranded = unbranded.merge(
        cbsa_xw[['county_fips_full', 'cbsa_code', 'cbsa_title', 'metro_micro']],
        on='county_fips_full',
        how='left'
    )

    in_msa = unbranded['cbsa_code'].notna()
    logger.info(f"Unbranded POIs in MSAs: {in_msa.sum():,} ({100*in_msa.mean():.1f}%)")
    logger.info(f"Unbranded POIs outside MSAs (rural): {(~in_msa).sum():,} ({100*(~in_msa).mean():.1f}%)")

    metro_count = (unbranded['metro_micro'] == 'Metropolitan Statistical Area').sum()
    micro_count = (unbranded['metro_micro'] == 'Micropolitan Statistical Area').sum()
    logger.info(f"  - In Metropolitan areas: {metro_count:,}")
    logger.info(f"  - In Micropolitan areas: {micro_count:,}")

    logger.info("Loading PAW MSA list to match naming convention...")
    paw_msa = pd.read_parquet(PAW_MSA_FILE, columns=['msa'])
    paw_msa_names = set(paw_msa['msa'].unique())
    logger.info(f"PAW has {len(paw_msa_names)} MSAs")

    def map_cbsa_to_paw(cbsa_title):
        """Map CBSA title to PAW MSA name using crosswalk."""
        normalized = normalize_msa_name(cbsa_title)
        if normalized is None:
            return None
        # Check crosswalk first (for name mismatches)
        if normalized in CBSA_TO_PAW:
            return CBSA_TO_PAW[normalized]
        # Otherwise use normalized name directly if it's in PAW
        if normalized in paw_msa_names:
            return normalized
        return None

    unbranded['paw_msa'] = unbranded['cbsa_title'].apply(map_cbsa_to_paw)

    # Log crosswalk usage
    used_crosswalk = unbranded['cbsa_title'].apply(lambda x: normalize_msa_name(x) in CBSA_TO_PAW if pd.notna(x) else False)
    logger.info(f"POIs mapped via crosswalk: {used_crosswalk.sum():,}")

    matchable = unbranded['paw_msa'].notna()
    logger.info(f"Unbranded POIs matchable to PAW MSAs: {matchable.sum():,}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    unbranded_matchable = unbranded[matchable].copy()

    name_col = 'LOCATION_NAME' if 'LOCATION_NAME' in unbranded_matchable.columns else 'location_name'
    if name_col not in unbranded_matchable.columns:
        logger.warning("No location_name column found")
        name_col = None

    cols_to_keep = ['placekey', name_col, 'paw_msa', 'cbsa_code', 'county_fips_full']
    if 'LATITUDE' in unbranded_matchable.columns:
        cols_to_keep.extend(['LATITUDE', 'LONGITUDE'])
    elif 'latitude' in unbranded_matchable.columns:
        cols_to_keep.extend(['latitude', 'longitude'])

    cols_to_keep = [c for c in cols_to_keep if c is not None and c in unbranded_matchable.columns]

    output_df = unbranded_matchable[cols_to_keep].copy()
    rename_map = {'paw_msa': 'msa'}
    if name_col and name_col != 'location_name':
        rename_map[name_col] = 'location_name'
    if 'LATITUDE' in output_df.columns:
        rename_map['LATITUDE'] = 'latitude'
        rename_map['LONGITUDE'] = 'longitude'
    output_df = output_df.rename(columns=rename_map)

    if 'location_name' in output_df.columns:
        output_df = output_df.dropna(subset=['location_name'])

    logger.info(f"\nSaving {len(output_df):,} unbranded POIs partitioned by MSA...")

    msa_counts = output_df.groupby('msa').size().sort_values(ascending=False)
    logger.info(f"Top 10 MSAs by POI count:")
    for msa, count in msa_counts.head(10).items():
        logger.info(f"  {msa}: {count:,}")

    for msa in output_df['msa'].unique():
        msa_df = output_df[output_df['msa'] == msa]
        output_path = OUTPUT_DIR / f"{msa}.parquet"
        msa_df.to_parquet(output_path, index=False, compression='snappy')

    logger.info(f"\nSaved to {OUTPUT_DIR}")
    logger.info(f"Total MSA files: {len(output_df['msa'].unique())}")

    summary_path = OUTPUT_DIR / "_summary.parquet"
    summary = pd.DataFrame({
        'msa': msa_counts.index,
        'poi_count': msa_counts.values
    })
    summary.to_parquet(summary_path, index=False)
    logger.info(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build PAW Company × MSA lookup table from MSA position files.

Extracts unique (rcid, company_name) pairs from each MSA's position file
and combines into a single table for Tier 2 singleton matching.

Output: paw_company_by_msa.parquet
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MSA_POSITIONS_DIR = Path("/global/scratch/users/maxkagan/04_vrscores/merge_splink_fuzzylink/step11_company_enriched")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/entity_resolution")


def extract_msa_from_filename(filepath: Path) -> str:
    """Extract MSA name from position file path."""
    name = filepath.stem.replace("_positions", "")
    return name


def process_msa_file(filepath: Path) -> pd.DataFrame:
    """Extract unique companies from one MSA position file."""
    msa_name = extract_msa_from_filename(filepath)

    cols_to_read = ['pos_rcid', 'pos_company_name', 'pos_ultimate_parent_rcid']

    df = pd.read_parquet(filepath, columns=cols_to_read)

    companies = df.groupby('pos_rcid').agg({
        'pos_company_name': 'first',
        'pos_ultimate_parent_rcid': 'first'
    }).reset_index()

    companies['msa'] = msa_name
    companies = companies.rename(columns={
        'pos_rcid': 'rcid',
        'pos_company_name': 'company_name',
        'pos_ultimate_parent_rcid': 'ultimate_parent_rcid'
    })

    employee_counts = df.groupby('pos_rcid').size().reset_index(name='employee_count_msa')
    employee_counts = employee_counts.rename(columns={'pos_rcid': 'rcid'})
    companies = companies.merge(employee_counts, on='rcid', how='left')

    return companies[['rcid', 'company_name', 'ultimate_parent_rcid', 'msa', 'employee_count_msa']]


def main():
    logger.info("=== Building PAW Company × MSA Table ===")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    msa_files = sorted(MSA_POSITIONS_DIR.glob("*_positions.parquet"))
    logger.info(f"Found {len(msa_files)} MSA position files")

    all_companies = []

    for i, filepath in enumerate(msa_files):
        if i % 50 == 0:
            logger.info(f"Processing MSA {i+1}/{len(msa_files)}: {filepath.stem}")

        try:
            companies = process_msa_file(filepath)
            all_companies.append(companies)
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            continue

    logger.info("Combining all MSA company tables...")
    combined = pd.concat(all_companies, ignore_index=True)

    combined['rcid'] = combined['rcid'].astype('Int64')
    combined['ultimate_parent_rcid'] = combined['ultimate_parent_rcid'].astype('Int64')
    combined['employee_count_msa'] = combined['employee_count_msa'].astype('Int64')

    logger.info(f"Total rows: {len(combined):,}")
    logger.info(f"Unique companies (rcid): {combined['rcid'].nunique():,}")
    logger.info(f"Unique MSAs: {combined['msa'].nunique():,}")

    multi_msa = combined.groupby('rcid')['msa'].nunique()
    multi_msa_companies = (multi_msa > 1).sum()
    logger.info(f"Companies in multiple MSAs: {multi_msa_companies:,}")

    output_path = OUTPUT_DIR / "paw_company_by_msa.parquet"
    combined.to_parquet(output_path, index=False, compression='snappy')
    logger.info(f"Saved to {output_path}")

    logger.info("\n=== Sample Output ===")
    logger.info(combined.head(10).to_string())


if __name__ == "__main__":
    main()

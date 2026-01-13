#!/usr/bin/env python3
"""
Step 7: Brand Heterogeneity Analysis - Variance Decomposition.

This script computes variance decomposition for brand × geography analysis:
1. Cross-MSA variation (between-geography): How much does Target/Walmart/Starbucks differ by metro?
2. Within-MSA variation (within-geography): How much variation within same brand in same metro?
3. Variance decomposition with ICC (intraclass correlation)

Uses full panel (2019-2025) to compute time-averaged partisan lean per location.

Outputs:
- brand_heterogeneity_summary.parquet: Brand-level metrics (n_locations, n_msas, between/within variance, ICC)
- brand_msa_summary.parquet: Brand × MSA level metrics
- variance_decomposition_report.csv: Summary statistics
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
import glob

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

INPUT_DIR = Path("/global/scratch/users/maxkagan/project_oakland/outputs/location_partisan_lean/national_full")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/project_oakland/outputs/brand_heterogeneity")

MIN_LOCATIONS_PER_BRAND = 10
MIN_MSAS_PER_BRAND = 3
MIN_LOCATIONS_PER_MSA = 2


def load_national_data():
    """Load all monthly parquet files into single DataFrame."""
    logger.info("Loading national data...")

    parquet_files = sorted(glob.glob(str(INPUT_DIR / "*.parquet")))
    logger.info(f"Found {len(parquet_files)} monthly files")

    if not parquet_files:
        logger.error(f"No parquet files found in {INPUT_DIR}")
        return None

    all_data = []
    for file_path in parquet_files:
        df = pd.read_parquet(file_path)
        all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"Loaded {len(combined):,} POI-month observations")

    return combined


def compute_location_averages(df):
    """Compute time-averaged partisan lean per location."""
    logger.info("Computing time-averaged partisan lean per location...")

    location_avg = df.groupby(['placekey', 'brand', 'cbsa_title', 'region']).agg({
        'rep_lean_2020': 'mean',
        'rep_lean_2016': 'mean',
        'date_range_start': 'count'
    }).reset_index()

    location_avg.columns = ['placekey', 'brand', 'cbsa_title', 'region',
                            'mean_rep_lean_2020', 'mean_rep_lean_2016', 'n_months']

    logger.info(f"Computed averages for {len(location_avg):,} unique locations")

    return location_avg


def compute_brand_msa_summary(location_avg):
    """Compute brand × MSA level statistics."""
    logger.info("Computing brand × MSA level statistics...")

    branded = location_avg[location_avg['brand'].notna() & (location_avg['brand'] != '')]
    with_msa = branded[branded['cbsa_title'].notna()]

    brand_msa = with_msa.groupby(['brand', 'cbsa_title']).agg({
        'placekey': 'count',
        'mean_rep_lean_2020': ['mean', 'std'],
        'mean_rep_lean_2016': ['mean', 'std'],
        'n_months': 'mean'
    }).reset_index()

    brand_msa.columns = ['brand', 'cbsa_title', 'n_locations',
                         'mean_rep_lean_2020', 'sd_rep_lean_2020',
                         'mean_rep_lean_2016', 'sd_rep_lean_2016',
                         'avg_months_observed']

    brand_msa['sd_rep_lean_2020'] = brand_msa['sd_rep_lean_2020'].fillna(0)
    brand_msa['sd_rep_lean_2016'] = brand_msa['sd_rep_lean_2016'].fillna(0)

    logger.info(f"Computed statistics for {len(brand_msa):,} brand-MSA combinations")

    return brand_msa


def compute_variance_decomposition(location_avg, brand_msa):
    """Compute variance decomposition for each brand."""
    logger.info("Computing variance decomposition...")

    branded = location_avg[location_avg['brand'].notna() & (location_avg['brand'] != '')]
    with_msa = branded[branded['cbsa_title'].notna()]

    brand_counts = with_msa.groupby('brand').agg({
        'placekey': 'count',
        'cbsa_title': 'nunique'
    }).reset_index()
    brand_counts.columns = ['brand', 'n_locations', 'n_msas']

    eligible_brands = brand_counts[
        (brand_counts['n_locations'] >= MIN_LOCATIONS_PER_BRAND) &
        (brand_counts['n_msas'] >= MIN_MSAS_PER_BRAND)
    ]['brand'].tolist()

    logger.info(f"Found {len(eligible_brands)} brands with sufficient coverage")

    results = []

    for brand in eligible_brands:
        brand_data = with_msa[with_msa['brand'] == brand]

        n_locations = len(brand_data)
        n_msas = brand_data['cbsa_title'].nunique()

        overall_mean_2020 = brand_data['mean_rep_lean_2020'].mean()
        overall_var_2020 = brand_data['mean_rep_lean_2020'].var()

        overall_mean_2016 = brand_data['mean_rep_lean_2016'].mean()
        overall_var_2016 = brand_data['mean_rep_lean_2016'].var()

        msa_means = brand_data.groupby('cbsa_title')['mean_rep_lean_2020'].mean()
        between_var_2020 = msa_means.var() if len(msa_means) > 1 else 0

        msa_vars = brand_data.groupby('cbsa_title')['mean_rep_lean_2020'].var().fillna(0)
        within_var_2020 = msa_vars.mean()

        icc_2020 = between_var_2020 / (between_var_2020 + within_var_2020) if (between_var_2020 + within_var_2020) > 0 else np.nan

        msa_means_16 = brand_data.groupby('cbsa_title')['mean_rep_lean_2016'].mean()
        between_var_2016 = msa_means_16.var() if len(msa_means_16) > 1 else 0

        msa_vars_16 = brand_data.groupby('cbsa_title')['mean_rep_lean_2016'].var().fillna(0)
        within_var_2016 = msa_vars_16.mean()

        icc_2016 = between_var_2016 / (between_var_2016 + within_var_2016) if (between_var_2016 + within_var_2016) > 0 else np.nan

        results.append({
            'brand': brand,
            'n_locations': n_locations,
            'n_msas': n_msas,
            'mean_rep_lean_2020': overall_mean_2020,
            'sd_rep_lean_2020': np.sqrt(overall_var_2020) if overall_var_2020 > 0 else 0,
            'between_msa_var_2020': between_var_2020,
            'within_msa_var_2020': within_var_2020,
            'total_var_2020': overall_var_2020,
            'icc_2020': icc_2020,
            'mean_rep_lean_2016': overall_mean_2016,
            'sd_rep_lean_2016': np.sqrt(overall_var_2016) if overall_var_2016 > 0 else 0,
            'between_msa_var_2016': between_var_2016,
            'within_msa_var_2016': within_var_2016,
            'total_var_2016': overall_var_2016,
            'icc_2016': icc_2016
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('n_locations', ascending=False)

    logger.info(f"Computed variance decomposition for {len(results_df)} brands")

    return results_df


def generate_report(brand_summary, brand_msa):
    """Generate summary report."""
    logger.info("Generating summary report...")

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("BRAND HETEROGENEITY ANALYSIS - VARIANCE DECOMPOSITION REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    report_lines.append("OVERALL STATISTICS")
    report_lines.append("-" * 40)
    report_lines.append(f"Total brands analyzed: {len(brand_summary)}")
    report_lines.append(f"Total brand-MSA combinations: {len(brand_msa)}")
    report_lines.append(f"Total locations: {brand_summary['n_locations'].sum():,}")
    report_lines.append("")

    report_lines.append("ICC DISTRIBUTION (2020)")
    report_lines.append("-" * 40)
    report_lines.append(f"Mean ICC: {brand_summary['icc_2020'].mean():.3f}")
    report_lines.append(f"Median ICC: {brand_summary['icc_2020'].median():.3f}")
    report_lines.append(f"Min ICC: {brand_summary['icc_2020'].min():.3f}")
    report_lines.append(f"Max ICC: {brand_summary['icc_2020'].max():.3f}")
    report_lines.append("")
    report_lines.append("Interpretation: Higher ICC = geography explains more variance")
    report_lines.append("")

    report_lines.append("TOP 20 BRANDS BY LOCATION COUNT")
    report_lines.append("-" * 40)
    top_20 = brand_summary.head(20)
    for _, row in top_20.iterrows():
        report_lines.append(
            f"{row['brand'][:30]:<30} | Locs: {row['n_locations']:>6,} | MSAs: {row['n_msas']:>4} | "
            f"Mean: {row['mean_rep_lean_2020']:.3f} | ICC: {row['icc_2020']:.3f}"
        )
    report_lines.append("")

    report_lines.append("BRANDS WITH HIGHEST ICC (Geography Dominates)")
    report_lines.append("-" * 40)
    high_icc = brand_summary[brand_summary['n_locations'] >= 100].nlargest(10, 'icc_2020')
    for _, row in high_icc.iterrows():
        report_lines.append(
            f"{row['brand'][:30]:<30} | ICC: {row['icc_2020']:.3f} | Locs: {row['n_locations']:>6,}"
        )
    report_lines.append("")

    report_lines.append("BRANDS WITH LOWEST ICC (Brand Identity Dominates)")
    report_lines.append("-" * 40)
    low_icc = brand_summary[brand_summary['n_locations'] >= 100].nsmallest(10, 'icc_2020')
    for _, row in low_icc.iterrows():
        report_lines.append(
            f"{row['brand'][:30]:<30} | ICC: {row['icc_2020']:.3f} | Locs: {row['n_locations']:>6,}"
        )
    report_lines.append("")

    report_lines.append("MOST REPUBLICAN-LEANING BRANDS (2020)")
    report_lines.append("-" * 40)
    most_rep = brand_summary[brand_summary['n_locations'] >= 100].nlargest(10, 'mean_rep_lean_2020')
    for _, row in most_rep.iterrows():
        report_lines.append(
            f"{row['brand'][:30]:<30} | Rep Lean: {row['mean_rep_lean_2020']:.3f} | Locs: {row['n_locations']:>6,}"
        )
    report_lines.append("")

    report_lines.append("MOST DEMOCRATIC-LEANING BRANDS (2020)")
    report_lines.append("-" * 40)
    most_dem = brand_summary[brand_summary['n_locations'] >= 100].nsmallest(10, 'mean_rep_lean_2020')
    for _, row in most_dem.iterrows():
        report_lines.append(
            f"{row['brand'][:30]:<30} | Rep Lean: {row['mean_rep_lean_2020']:.3f} | Locs: {row['n_locations']:>6,}"
        )

    return "\n".join(report_lines)


def main():
    """Run brand heterogeneity analysis."""
    logger.info("Starting brand heterogeneity analysis...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_national_data()
    if df is None:
        return 1

    location_avg = compute_location_averages(df)

    brand_msa = compute_brand_msa_summary(location_avg)

    brand_summary = compute_variance_decomposition(location_avg, brand_msa)

    try:
        brand_summary.to_parquet(OUTPUT_DIR / "brand_heterogeneity_summary.parquet", index=False)
        logger.info(f"Saved brand summary to {OUTPUT_DIR / 'brand_heterogeneity_summary.parquet'}")

        brand_msa.to_parquet(OUTPUT_DIR / "brand_msa_summary.parquet", index=False)
        logger.info(f"Saved brand-MSA summary to {OUTPUT_DIR / 'brand_msa_summary.parquet'}")

        report = generate_report(brand_summary, brand_msa)
        with open(OUTPUT_DIR / "variance_decomposition_report.txt", 'w') as f:
            f.write(report)
        logger.info(f"Saved report to {OUTPUT_DIR / 'variance_decomposition_report.txt'}")

        print("\n" + report)

        return 0

    except Exception as e:
        logger.error(f"Failed to save outputs: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

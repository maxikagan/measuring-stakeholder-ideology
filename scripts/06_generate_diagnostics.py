#!/usr/bin/env python3
"""
Step 6: Generate diagnostic report on data quality.

This script:
1. Summarizes unmatched CBGs (by state, by frequency)
2. Generates data quality metrics (coverage, partisan lean distribution)
3. Creates summary statistics table
4. Outputs CSV report for review

Output: /global/scratch/users/maxkagan/project_oakland/outputs/diagnostics/
Files:
  - unmatched_cbgs_summary.csv
  - data_quality_metrics.csv
  - final_dataset_stats.csv
"""

import logging
import pandas as pd
from pathlib import Path
import glob
from collections import Counter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
UNMATCHED_DIR = Path("/global/scratch/users/maxkagan/project_oakland/intermediate/unmatched_cbgs")
PARTISAN_DIR = Path("/global/scratch/users/maxkagan/project_oakland/intermediate/advan_2024_partisan")
FINAL_DIR = Path("/global/scratch/users/maxkagan/project_oakland/outputs/location_partisan_lean/national_2024")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/project_oakland/outputs/diagnostics")


def generate_diagnostics():
    """Generate diagnostic report."""
    logger.info("Starting Step 6: Generate diagnostics...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Summarize unmatched CBGs
    logger.info("Summarizing unmatched CBGs...")
    unmatched_files = sorted(glob.glob(str(UNMATCHED_DIR / "*.parquet")))

    if unmatched_files:
        all_unmatched = []
        for file_path in unmatched_files:
            try:
                df = pd.read_parquet(file_path)
                all_unmatched.append(df)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

        if all_unmatched:
            unmatched_df = pd.concat(all_unmatched, ignore_index=True)

            # Summary by state
            state_summary = unmatched_df.groupby('state').size().reset_index(name='unmatched_cbg_count')
            state_summary = state_summary.sort_values('unmatched_cbg_count', ascending=False)

            # Top unmatched CBGs
            cbg_counts = Counter(unmatched_df['unmatched_cbg'])
            top_cbgs = pd.DataFrame(
                [{'unmatched_cbg': cbg, 'occurrence_count': count}
                 for cbg, count in cbg_counts.most_common(100)],
                columns=['unmatched_cbg', 'occurrence_count']
            )

            # Save summaries
            state_summary.to_csv(OUTPUT_DIR / "unmatched_cbgs_by_state.csv", index=False)
            top_cbgs.to_csv(OUTPUT_DIR / "top_unmatched_cbgs.csv", index=False)

            logger.info(f"Unmatched CBG summary:")
            logger.info(f"  Total unmatched CBG mentions: {len(unmatched_df)}")
            logger.info(f"  Unique unmatched CBGs: {len(cbg_counts)}")
            logger.info(f"  States with unmatched CBGs: {len(state_summary)}")

    # 2. Data quality metrics from partisan lean files
    logger.info("Computing data quality metrics...")
    partisan_files = sorted(glob.glob(str(PARTISAN_DIR / "*.parquet")))

    quality_metrics = []
    total_pois = 0
    total_visitors = 0
    total_unmatched = 0

    for file_path in partisan_files:
        try:
            df = pd.read_parquet(file_path)
            state_name = Path(file_path).stem.split('_')[3]  # Extract state from filename

            total_pois += len(df)
            state_visitors = df['total_visitors'].sum()
            state_unmatched = df['unmatched_visitors'].sum()

            total_visitors += state_visitors
            total_unmatched += state_unmatched

            avg_pct_matched = df['pct_visitors_matched'].mean()
            pois_with_data = (df['total_visitors'] > 0).sum()

            quality_metrics.append({
                'state': state_name,
                'poi_count': len(df),
                'pois_with_visitor_data': pois_with_data,
                'total_visitors': state_visitors,
                'unmatched_visitors': state_unmatched,
                'avg_pct_matched': avg_pct_matched,
                'mean_rep_lean': df['rep_lean'].mean(),
                'median_rep_lean': df['rep_lean'].median(),
                'std_rep_lean': df['rep_lean'].std()
            })
        except Exception as e:
            logger.warning(f"Failed to process {file_path}: {e}")

    if quality_metrics:
        quality_df = pd.DataFrame(quality_metrics).sort_values('state')
        quality_df.to_csv(OUTPUT_DIR / "data_quality_metrics_by_state.csv", index=False)

        logger.info(f"Data quality metrics:")
        logger.info(f"  Total POIs: {total_pois}")
        logger.info(f"  Total visitors: {total_visitors}")
        logger.info(f"  Total unmatched visitors: {total_unmatched}")
        logger.info(f"  Overall % matched: {100 * total_visitors / (total_visitors + total_unmatched):.2f}%")

    # 3. Final dataset summary
    logger.info("Computing final dataset statistics...")
    final_files = sorted(glob.glob(str(FINAL_DIR / "*.parquet")))

    final_stats = []
    for file_path in final_files:
        try:
            df = pd.read_parquet(file_path)
            month = Path(file_path).stem

            final_stats.append({
                'month': month,
                'poi_month_observations': len(df),
                'mean_rep_lean': df['rep_lean'].mean(),
                'median_rep_lean': df['rep_lean'].median(),
                'std_rep_lean': df['rep_lean'].std(),
                'min_rep_lean': df['rep_lean'].min(),
                'max_rep_lean': df['rep_lean'].max()
            })
        except Exception as e:
            logger.warning(f"Failed to process {file_path}: {e}")

    if final_stats:
        final_stats_df = pd.DataFrame(final_stats)
        final_stats_df.to_csv(OUTPUT_DIR / "final_dataset_stats_by_month.csv", index=False)

        logger.info(f"Final dataset statistics:")
        logger.info(f"  Total months: {len(final_stats_df)}")
        logger.info(f"  Total POI-month observations: {final_stats_df['poi_month_observations'].sum()}")

    logger.info(f"Step 6 complete: Diagnostic files saved to {OUTPUT_DIR}")
    return True


def main():
    """Run Step 6."""
    try:
        success = generate_diagnostics()

        if success:
            logger.info("Step 6 completed successfully!")
            return 0
        else:
            logger.error("Step 6 failed")
            return 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

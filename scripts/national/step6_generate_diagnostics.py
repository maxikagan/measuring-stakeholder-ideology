#!/usr/bin/env python3
"""
Step 6: Generate diagnostic reports for unmatched CBGs and data quality.
"""

import pandas as pd
from pathlib import Path

UNMATCHED_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/unmatched_cbgs")
OUTPUT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/outputs/location_partisan_lean/national_2024")
DIAGNOSTICS_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/outputs/diagnostics")


def main():
    print("=" * 60)
    print("STEP 6: GENERATE DIAGNOSTICS")
    print("=" * 60)

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n1. UNMATCHED CBG ANALYSIS")
    print("-" * 40)

    unmatched_files = list(UNMATCHED_DIR.glob("*_unmatched.parquet"))
    print(f"Found {len(unmatched_files)} unmatched CBG files")

    if unmatched_files:
        all_unmatched = []
        for uf in unmatched_files:
            df = pd.read_parquet(uf)
            all_unmatched.append(df)

        unmatched = pd.concat(all_unmatched, ignore_index=True)

        by_state = unmatched.groupby('state').agg({
            'cbg_geoid': 'nunique',
            'total_visitors': 'sum',
            'poi_count': 'sum'
        }).reset_index()
        by_state.columns = ['state', 'unique_cbgs', 'total_visitors', 'affected_pois']
        by_state = by_state.sort_values('total_visitors', ascending=False)

        by_state_file = DIAGNOSTICS_DIR / "unmatched_cbgs_by_state.csv"
        by_state.to_csv(by_state_file, index=False)
        print(f"  Saved: {by_state_file}")
        print(f"  Total unmatched CBGs: {unmatched['cbg_geoid'].nunique():,}")
        print(f"  Total unmatched visitors: {unmatched['total_visitors'].sum():,}")

        top_unmatched = unmatched.groupby('cbg_geoid').agg({
            'total_visitors': 'sum',
            'poi_count': 'sum',
            'state': 'first'
        }).reset_index()
        top_unmatched = top_unmatched.nlargest(100, 'total_visitors')

        top_file = DIAGNOSTICS_DIR / "top_unmatched_cbgs.csv"
        top_unmatched.to_csv(top_file, index=False)
        print(f"  Saved: {top_file}")
    else:
        print("  No unmatched CBG files found")

    print("\n2. FINAL DATASET QUALITY")
    print("-" * 40)

    monthly_files = list(OUTPUT_DIR.glob("*.parquet"))
    print(f"Found {len(monthly_files)} monthly output files")

    if monthly_files:
        stats = []
        for mf in sorted(monthly_files):
            df = pd.read_parquet(mf)
            stats.append({
                'month': mf.stem,
                'poi_count': len(df),
                'unique_pois': df['placekey'].nunique(),
                'mean_rep_lean': df['rep_lean'].mean(),
                'median_rep_lean': df['rep_lean'].median(),
                'std_rep_lean': df['rep_lean'].std(),
                'mean_visitors': df['total_visitors'].mean(),
                'mean_pct_matched': df['pct_visitors_matched'].mean(),
                'pois_below_90pct_matched': (df['pct_visitors_matched'] < 90).sum(),
            })

        stats_df = pd.DataFrame(stats)
        stats_file = DIAGNOSTICS_DIR / "monthly_data_quality.csv"
        stats_df.to_csv(stats_file, index=False)
        print(f"  Saved: {stats_file}")

        print("\n  Monthly Summary:")
        for _, row in stats_df.iterrows():
            print(f"    {row['month']}: {row['poi_count']:,} POIs, "
                  f"rep_lean={row['mean_rep_lean']:.3f}, "
                  f"matched={row['mean_pct_matched']:.1f}%")

        all_data = pd.concat([pd.read_parquet(f) for f in monthly_files], ignore_index=True)

        by_state_quality = all_data.groupby('region').agg({
            'placekey': 'nunique',
            'rep_lean': ['mean', 'std'],
            'pct_visitors_matched': 'mean',
            'total_visitors': 'sum'
        }).reset_index()
        by_state_quality.columns = ['state', 'unique_pois', 'mean_rep_lean', 'std_rep_lean',
                                     'mean_pct_matched', 'total_visitors']
        by_state_quality = by_state_quality.sort_values('unique_pois', ascending=False)

        state_file = DIAGNOSTICS_DIR / "quality_by_state.csv"
        by_state_quality.to_csv(state_file, index=False)
        print(f"\n  Saved: {state_file}")

    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)
    print(f"Output directory: {DIAGNOSTICS_DIR}")


if __name__ == "__main__":
    main()

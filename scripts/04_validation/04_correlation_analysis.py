#!/usr/bin/env python3
"""
Task 2.3: Correlation Analysis - Validate partisan lean against Schoenmueller.

Computes correlation between our foot traffic-based partisan lean and
Schoenmueller et al.'s Twitter-based brand ideology scores.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRATCH = Path('/global/scratch/users/maxkagan/measuring_stakeholder_ideology')
HOME = Path('/global/home/users/maxkagan/measuring_stakeholder_ideology')

BRAND_LEAN_PATH = SCRATCH / 'outputs' / 'brand_month_aggregated' / 'brand_month_partisan_lean.parquet'
SCHOENMUELLER_PATH = HOME / 'reference' / 'other_measures' / 'schoenmueller_et_al' / 'social-listening_PoliticalAffiliation_2022_Dec.csv'
LABELED_MATCHES_PATH = SCRATCH / 'outputs' / 'validation' / 'labeled_matches.csv'
OUTPUT_DIR = SCRATCH / 'outputs' / 'validation'


def load_data():
    """Load brand partisan lean, Schoenmueller data, and labeled matches."""
    print("=== Loading data ===")

    brand_lean = pd.read_parquet(BRAND_LEAN_PATH)
    print(f"Brand-month data: {len(brand_lean):,} rows, {brand_lean['brand_name'].nunique()} brands")

    schoen = pd.read_csv(SCHOENMUELLER_PATH)
    schoen = schoen.rename(columns={
        'Brand_Name': 'schoen_brand',
        'Proportion Republicans': 'schoen_rep_prop',
        'Proportion Democrats': 'schoen_dem_prop'
    })
    print(f"Schoenmueller data: {len(schoen):,} brands")

    labeled = pd.read_csv(LABELED_MATCHES_PATH)
    true_matches = labeled[labeled['is_match'] == True].copy()
    print(f"Labeled matches: {len(true_matches):,} TRUE matches across {true_matches['schoen_brand'].nunique()} Schoenmueller brands")

    return brand_lean, schoen, true_matches


def aggregate_brand_lean(brand_lean):
    """Aggregate brand-level partisan lean across all months."""
    print("\n=== Aggregating brand-level partisan lean ===")

    brand_agg = brand_lean.groupby(['safegraph_brand_id', 'brand_name']).agg({
        'brand_lean_2020': 'mean',
        'brand_lean_2016': 'mean',
        'total_normalized_visits': 'sum',
        'n_pois': 'max',
        'n_states': 'max'
    }).reset_index()

    print(f"Aggregated brands: {len(brand_agg):,}")
    return brand_agg


def merge_validation_data(brand_agg, schoen, true_matches):
    """Merge our brand lean with Schoenmueller data via labeled matches."""
    print("\n=== Merging validation data ===")

    merged = true_matches[['schoen_brand', 'advan_brand', 'advan_brand_id', 'schoen_rep_prop']].copy()
    merged = merged.rename(columns={'advan_brand_id': 'safegraph_brand_id'})

    merged = merged.merge(
        brand_agg[['safegraph_brand_id', 'brand_lean_2020', 'brand_lean_2016',
                   'total_normalized_visits', 'n_pois', 'n_states']],
        on='safegraph_brand_id',
        how='inner'
    )

    print(f"Merged records: {len(merged):,}")
    print(f"Unique Schoenmueller brands matched: {merged['schoen_brand'].nunique()}")

    schoen_agg = merged.groupby('schoen_brand').agg({
        'schoen_rep_prop': 'first',
        'brand_lean_2020': lambda x: np.average(x, weights=merged.loc[x.index, 'total_normalized_visits']),
        'brand_lean_2016': lambda x: np.average(x, weights=merged.loc[x.index, 'total_normalized_visits']),
        'total_normalized_visits': 'sum',
        'advan_brand': 'count'
    }).reset_index()
    schoen_agg = schoen_agg.rename(columns={'advan_brand': 'n_advan_matches'})

    schoen_agg = schoen_agg.dropna(subset=['brand_lean_2020', 'schoen_rep_prop'])
    print(f"Final validation sample: {len(schoen_agg):,} brands")

    return schoen_agg


def compute_correlations(validation_df):
    """Compute correlation statistics."""
    print("\n=== Correlation Analysis ===")

    our_lean = validation_df['brand_lean_2020'].values
    schoen_lean = validation_df['schoen_rep_prop'].values

    r_pearson, p_pearson = stats.pearsonr(our_lean, schoen_lean)
    r_spearman, p_spearman = stats.spearmanr(our_lean, schoen_lean)

    slope, intercept, r_value, p_value, std_err = stats.linregress(schoen_lean, our_lean)

    print(f"\n2020 Election Data:")
    print(f"  Pearson r:  {r_pearson:.4f} (p={p_pearson:.2e})")
    print(f"  Spearman ρ: {r_spearman:.4f} (p={p_spearman:.2e})")
    print(f"  R²:         {r_value**2:.4f}")
    print(f"  OLS slope:  {slope:.4f} (SE={std_err:.4f})")
    print(f"  OLS intercept: {intercept:.4f}")

    our_lean_2016 = validation_df['brand_lean_2016'].values
    r_pearson_2016, p_pearson_2016 = stats.pearsonr(our_lean_2016, schoen_lean)
    print(f"\n2016 Election Data:")
    print(f"  Pearson r:  {r_pearson_2016:.4f} (p={p_pearson_2016:.2e})")

    return {
        'pearson_r': r_pearson,
        'pearson_p': p_pearson,
        'spearman_r': r_spearman,
        'spearman_p': p_spearman,
        'r_squared': r_value**2,
        'slope': slope,
        'intercept': intercept,
        'std_err': std_err,
        'n_brands': len(validation_df),
        'pearson_r_2016': r_pearson_2016,
    }


def create_scatter_plot(validation_df, stats_dict, output_path):
    """Create scatter plot of validation comparison."""
    print("\n=== Creating scatter plot ===")

    fig, ax = plt.subplots(figsize=(10, 8))

    weights = np.log1p(validation_df['total_normalized_visits'])
    sizes = 20 + 80 * (weights - weights.min()) / (weights.max() - weights.min())

    scatter = ax.scatter(
        validation_df['schoen_rep_prop'],
        validation_df['brand_lean_2020'],
        s=sizes,
        alpha=0.6,
        c='steelblue',
        edgecolors='white',
        linewidths=0.5
    )

    x_line = np.array([0.2, 0.8])
    y_line = stats_dict['intercept'] + stats_dict['slope'] * x_line
    ax.plot(x_line, y_line, 'r-', linewidth=2, label='OLS fit')

    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='45° line')

    textstr = (f"n = {stats_dict['n_brands']} brands\n"
               f"r = {stats_dict['pearson_r']:.3f}\n"
               f"R² = {stats_dict['r_squared']:.3f}")
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=props)

    ax.set_xlabel('Schoenmueller Republican Proportion (Twitter-based)', fontsize=12)
    ax.set_ylabel('Our Republican Lean (Foot Traffic-based)', fontsize=12)
    ax.set_title('Validation: Foot Traffic vs Twitter Brand Ideology', fontsize=14)

    ax.set_xlim(0.15, 0.85)
    ax.set_ylim(0.35, 0.70)

    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved scatter plot to {output_path}")

    pdf_path = output_path.with_suffix('.pdf')
    plt.savefig(pdf_path, bbox_inches='tight')
    print(f"Saved PDF to {pdf_path}")

    plt.close()


def identify_divergent_brands(validation_df, n_top=20):
    """Identify brands where our measure diverges most from Schoenmueller."""
    print(f"\n=== Top {n_top} Divergent Brands ===")

    validation_df = validation_df.copy()
    validation_df['divergence'] = validation_df['brand_lean_2020'] - validation_df['schoen_rep_prop']
    validation_df['abs_divergence'] = validation_df['divergence'].abs()

    most_divergent = validation_df.nlargest(n_top, 'abs_divergence')

    print("\nMost divergent brands (our lean - Schoenmueller):")
    for _, row in most_divergent.iterrows():
        direction = "more R" if row['divergence'] > 0 else "more D"
        print(f"  {row['schoen_brand']:25} | Ours: {row['brand_lean_2020']:.3f} | "
              f"Schoen: {row['schoen_rep_prop']:.3f} | Diff: {row['divergence']:+.3f} ({direction})")

    return most_divergent


def main():
    print("=" * 60)
    print("Task 2.3: Correlation Analysis (Schoenmueller Validation)")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    brand_lean, schoen, true_matches = load_data()
    brand_agg = aggregate_brand_lean(brand_lean)
    validation_df = merge_validation_data(brand_agg, schoen, true_matches)

    correlation_stats = compute_correlations(validation_df)

    scatter_path = OUTPUT_DIR / 'validation_scatter.png'
    create_scatter_plot(validation_df, correlation_stats, scatter_path)

    divergent = identify_divergent_brands(validation_df)

    validation_df.to_csv(OUTPUT_DIR / 'validation_comparison.csv', index=False)
    divergent.to_csv(OUTPUT_DIR / 'divergent_brands.csv', index=False)

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Brands compared: {correlation_stats['n_brands']}")
    print(f"Pearson correlation: {correlation_stats['pearson_r']:.4f}")
    print(f"R-squared: {correlation_stats['r_squared']:.4f}")
    print(f"\nOutput files:")
    print(f"  {scatter_path}")
    print(f"  {OUTPUT_DIR / 'validation_comparison.csv'}")
    print(f"  {OUTPUT_DIR / 'divergent_brands.csv'}")


if __name__ == '__main__':
    main()

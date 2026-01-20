#!/usr/bin/env python3
"""
EPIC 2: Validation against Schoenmueller et al. (2022) Twitter-based brand ideology

This script:
1. Aggregates POI-level partisan lean to brand level using normalized_visits as weights
2. Matches Advan brands to Schoenmueller brands via fuzzy matching
3. Computes correlation between the two measures
4. Generates validation visualizations
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from rapidfuzz import fuzz, process
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

SCRATCH = Path('/global/scratch/users/maxkagan/measuring_stakeholder_ideology')
HOME = Path('/global/home/users/maxkagan/measuring_stakeholder_ideology')

PARTISAN_LEAN_DIR = SCRATCH / 'outputs' / 'national_with_normalized'
SCHOENMUELLER_PATH = HOME / 'reference' / 'other_measures' / 'schoenmueller_et_al' / 'social-listening_PoliticalAffiliation_2022_Dec.csv'
OUTPUT_DIR = SCRATCH / 'outputs' / 'validation'


def normalize_brand_name(name: str) -> str:
    """Normalize brand name for matching: lowercase, remove punctuation/spaces."""
    if pd.isna(name):
        return ''
    name = str(name).lower()
    name = re.sub(r"['\-\.\,\&\(\)]", '', name)
    name = re.sub(r'\s+', '', name)
    name = name.replace('the', '').replace('inc', '').replace('llc', '').replace('corp', '')
    return name.strip()


def aggregate_brand_lean() -> pd.DataFrame:
    """
    Aggregate POI-level partisan lean to brand level.
    Uses normalized_visits_by_state_scaling as weights.
    """
    print("=== Aggregating POI-level data to brand level ===")

    parquet_files = sorted(PARTISAN_LEAN_DIR.glob('partisan_lean_*.parquet'))
    print(f"Found {len(parquet_files)} monthly files")

    brand_agg = []

    for i, pf in enumerate(parquet_files):
        print(f"Processing {pf.name} ({i+1}/{len(parquet_files)})")

        df = pd.read_parquet(pf, columns=[
            'brand', 'rep_lean_2020', 'rep_lean_2016',
            'normalized_visits_by_state_scaling', 'year_month'
        ])

        df = df[df['brand'].notna() & (df['brand'] != '')]
        df = df[df['normalized_visits_by_state_scaling'].notna() & (df['normalized_visits_by_state_scaling'] > 0)]

        df['weighted_lean_2020'] = df['rep_lean_2020'] * df['normalized_visits_by_state_scaling']
        df['weighted_lean_2016'] = df['rep_lean_2016'] * df['normalized_visits_by_state_scaling']

        monthly_agg = df.groupby('brand').agg({
            'weighted_lean_2020': 'sum',
            'weighted_lean_2016': 'sum',
            'normalized_visits_by_state_scaling': 'sum',
            'year_month': 'first'
        }).reset_index()

        brand_agg.append(monthly_agg)

    print("Combining all months...")
    all_months = pd.concat(brand_agg, ignore_index=True)

    overall_agg = all_months.groupby('brand').agg({
        'weighted_lean_2020': 'sum',
        'weighted_lean_2016': 'sum',
        'normalized_visits_by_state_scaling': 'sum'
    }).reset_index()

    overall_agg['brand_rep_lean_2020'] = overall_agg['weighted_lean_2020'] / overall_agg['normalized_visits_by_state_scaling']
    overall_agg['brand_rep_lean_2016'] = overall_agg['weighted_lean_2016'] / overall_agg['normalized_visits_by_state_scaling']
    overall_agg['total_normalized_visits'] = overall_agg['normalized_visits_by_state_scaling']

    result = overall_agg[['brand', 'brand_rep_lean_2020', 'brand_rep_lean_2016', 'total_normalized_visits']]
    result['brand_normalized'] = result['brand'].apply(normalize_brand_name)

    print(f"Aggregated to {len(result)} unique brands")
    return result


def load_schoenmueller() -> pd.DataFrame:
    """Load and prepare Schoenmueller validation data."""
    print("\n=== Loading Schoenmueller data ===")
    schoen = pd.read_csv(SCHOENMUELLER_PATH)
    schoen = schoen.rename(columns={
        'Brand_Name': 'schoen_brand',
        'Proportion Republicans': 'schoen_rep_prop',
        'Proportion Democrats': 'schoen_dem_prop'
    })
    schoen['schoen_brand_normalized'] = schoen['schoen_brand'].apply(normalize_brand_name)
    print(f"Loaded {len(schoen)} Schoenmueller brands")
    return schoen


def match_brands(advan_brands: pd.DataFrame, schoen_brands: pd.DataFrame) -> pd.DataFrame:
    """
    Match Advan brands to Schoenmueller brands using fuzzy matching.
    Returns matched pairs with similarity scores.
    """
    print("\n=== Matching brands ===")

    advan_normalized = advan_brands['brand_normalized'].unique()
    schoen_normalized = schoen_brands['schoen_brand_normalized'].unique()

    exact_matches = set(advan_normalized) & set(schoen_normalized)
    print(f"Exact matches (normalized): {len(exact_matches)}")

    matches = []

    advan_lookup = advan_brands.set_index('brand_normalized')
    schoen_lookup = schoen_brands.set_index('schoen_brand_normalized')

    for schoen_norm in schoen_normalized:
        if schoen_norm in exact_matches:
            advan_row = advan_lookup.loc[schoen_norm]
            schoen_row = schoen_lookup.loc[schoen_norm]

            if isinstance(advan_row, pd.DataFrame):
                advan_row = advan_row.iloc[0]
            if isinstance(schoen_row, pd.DataFrame):
                schoen_row = schoen_row.iloc[0]

            matches.append({
                'advan_brand': advan_row['brand'],
                'schoen_brand': schoen_row['schoen_brand'],
                'match_score': 100,
                'match_type': 'exact',
                'brand_rep_lean_2020': advan_row['brand_rep_lean_2020'],
                'brand_rep_lean_2016': advan_row['brand_rep_lean_2016'],
                'total_normalized_visits': advan_row['total_normalized_visits'],
                'schoen_rep_prop': schoen_row['schoen_rep_prop']
            })
        else:
            result = process.extractOne(
                schoen_norm,
                advan_normalized,
                scorer=fuzz.ratio
            )

            if result and result[1] >= 80:
                advan_norm_match = result[0]
                advan_row = advan_lookup.loc[advan_norm_match]
                schoen_row = schoen_lookup.loc[schoen_norm]

                if isinstance(advan_row, pd.DataFrame):
                    advan_row = advan_row.iloc[0]
                if isinstance(schoen_row, pd.DataFrame):
                    schoen_row = schoen_row.iloc[0]

                matches.append({
                    'advan_brand': advan_row['brand'],
                    'schoen_brand': schoen_row['schoen_brand'],
                    'match_score': result[1],
                    'match_type': 'fuzzy',
                    'brand_rep_lean_2020': advan_row['brand_rep_lean_2020'],
                    'brand_rep_lean_2016': advan_row['brand_rep_lean_2016'],
                    'total_normalized_visits': advan_row['total_normalized_visits'],
                    'schoen_rep_prop': schoen_row['schoen_rep_prop']
                })

    matched_df = pd.DataFrame(matches)
    print(f"Total matches: {len(matched_df)}")
    print(f"  - Exact: {len(matched_df[matched_df['match_type'] == 'exact'])}")
    print(f"  - Fuzzy: {len(matched_df[matched_df['match_type'] == 'fuzzy'])}")

    return matched_df


def compute_validation_stats(matched: pd.DataFrame) -> dict:
    """Compute correlation and other validation statistics."""
    print("\n=== Validation Statistics ===")

    valid = matched.dropna(subset=['brand_rep_lean_2020', 'schoen_rep_prop'])

    corr_2020, p_2020 = stats.pearsonr(valid['brand_rep_lean_2020'], valid['schoen_rep_prop'])
    corr_2016, p_2016 = stats.pearsonr(valid['brand_rep_lean_2016'], valid['schoen_rep_prop'])

    spearman_2020, sp_p_2020 = stats.spearmanr(valid['brand_rep_lean_2020'], valid['schoen_rep_prop'])

    results = {
        'n_matched': len(valid),
        'pearson_2020': corr_2020,
        'pearson_2020_p': p_2020,
        'pearson_2016': corr_2016,
        'pearson_2016_p': p_2016,
        'spearman_2020': spearman_2020,
        'spearman_2020_p': sp_p_2020,
        'r_squared_2020': corr_2020 ** 2
    }

    print(f"N matched brands: {results['n_matched']}")
    print(f"\nCorrelation with 2020 election data:")
    print(f"  Pearson r = {corr_2020:.4f} (p = {p_2020:.2e})")
    print(f"  R-squared = {results['r_squared_2020']:.4f}")
    print(f"  Spearman ρ = {spearman_2020:.4f} (p = {sp_p_2020:.2e})")
    print(f"\nCorrelation with 2016 election data:")
    print(f"  Pearson r = {corr_2016:.4f} (p = {p_2016:.2e})")

    return results


def create_validation_plots(matched: pd.DataFrame, stats: dict, output_dir: Path):
    """Generate validation visualizations."""
    print("\n=== Creating visualizations ===")

    output_dir.mkdir(parents=True, exist_ok=True)

    valid = matched.dropna(subset=['brand_rep_lean_2020', 'schoen_rep_prop'])

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.scatter(
        valid['schoen_rep_prop'],
        valid['brand_rep_lean_2020'],
        alpha=0.6,
        s=50,
        c='steelblue'
    )

    z = np.polyfit(valid['schoen_rep_prop'], valid['brand_rep_lean_2020'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(valid['schoen_rep_prop'].min(), valid['schoen_rep_prop'].max(), 100)
    ax.plot(x_line, p(x_line), 'r-', linewidth=2, label=f'OLS fit')

    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='45° line')

    ax.set_xlabel('Schoenmueller Twitter-based Republican Share', fontsize=12)
    ax.set_ylabel('Advan Foot Traffic-based Republican Lean (2020)', fontsize=12)
    ax.set_title(f'Validation: Foot Traffic vs. Twitter Brand Ideology\n'
                 f'N={stats["n_matched"]} brands, r={stats["pearson_2020"]:.3f}, R²={stats["r_squared_2020"]:.3f}',
                 fontsize=14)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'validation_scatter.png', dpi=150, bbox_inches='tight')
    plt.savefig(output_dir / 'validation_scatter.pdf', bbox_inches='tight')
    print(f"Saved scatter plot to {output_dir / 'validation_scatter.png'}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].hist(valid['brand_rep_lean_2020'], bins=50, alpha=0.7, label='Advan (2020)', color='steelblue')
    axes[0].hist(valid['schoen_rep_prop'], bins=50, alpha=0.7, label='Schoenmueller', color='coral')
    axes[0].set_xlabel('Republican Share')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Distribution Comparison (Matched Brands)')
    axes[0].legend()

    valid['diff'] = valid['brand_rep_lean_2020'] - valid['schoen_rep_prop']
    axes[1].hist(valid['diff'], bins=50, color='purple', alpha=0.7)
    axes[1].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Advan - Schoenmueller')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title(f'Difference Distribution\n(Mean: {valid["diff"].mean():.3f}, Std: {valid["diff"].std():.3f})')

    plt.tight_layout()
    plt.savefig(output_dir / 'validation_distributions.png', dpi=150, bbox_inches='tight')
    print(f"Saved distribution plots to {output_dir / 'validation_distributions.png'}")

    plt.close('all')


def identify_divergent_brands(matched: pd.DataFrame, n_top: int = 20) -> pd.DataFrame:
    """Identify brands where our measure diverges most from Schoenmueller."""
    valid = matched.dropna(subset=['brand_rep_lean_2020', 'schoen_rep_prop']).copy()
    valid['difference'] = valid['brand_rep_lean_2020'] - valid['schoen_rep_prop']
    valid['abs_difference'] = valid['difference'].abs()

    divergent = valid.nlargest(n_top, 'abs_difference')

    print(f"\n=== Top {n_top} Divergent Brands ===")
    print(divergent[['advan_brand', 'schoen_brand', 'brand_rep_lean_2020',
                     'schoen_rep_prop', 'difference', 'total_normalized_visits']].to_string())

    return divergent


def main():
    print("=" * 60)
    print("EPIC 2: Schoenmueller Validation")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    advan_brands = aggregate_brand_lean()
    advan_brands.to_parquet(OUTPUT_DIR / 'advan_brand_level_lean.parquet', index=False)
    print(f"Saved brand-level aggregation to {OUTPUT_DIR / 'advan_brand_level_lean.parquet'}")

    schoen = load_schoenmueller()

    matched = match_brands(advan_brands, schoen)
    matched.to_parquet(OUTPUT_DIR / 'schoenmueller_matched_brands.parquet', index=False)
    matched.to_csv(OUTPUT_DIR / 'schoenmueller_matched_brands.csv', index=False)
    print(f"Saved matched brands to {OUTPUT_DIR}")

    validation_stats = compute_validation_stats(matched)

    create_validation_plots(matched, validation_stats, OUTPUT_DIR)

    divergent = identify_divergent_brands(matched)
    divergent.to_csv(OUTPUT_DIR / 'divergent_brands.csv', index=False)

    with open(OUTPUT_DIR / 'validation_summary.txt', 'w') as f:
        f.write("Schoenmueller Validation Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"N Schoenmueller brands: 1,289\n")
        f.write(f"N Advan brands: {len(advan_brands)}\n")
        f.write(f"N matched brands: {validation_stats['n_matched']}\n\n")
        f.write("Correlation Results:\n")
        f.write(f"  Pearson r (2020): {validation_stats['pearson_2020']:.4f}\n")
        f.write(f"  R-squared (2020): {validation_stats['r_squared_2020']:.4f}\n")
        f.write(f"  Spearman ρ (2020): {validation_stats['spearman_2020']:.4f}\n")
        f.write(f"  Pearson r (2016): {validation_stats['pearson_2016']:.4f}\n")

    print("\n" + "=" * 60)
    print("Validation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

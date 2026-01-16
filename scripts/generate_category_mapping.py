#!/usr/bin/env python3
"""Generate Advan category to NAICS mapping for manual review."""

import pandas as pd
import os

OUTPUT_DIR = '/global/home/users/maxkagan/measuring_stakeholder_ideology/reference'
DATA_PATH = '/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/national/partisan_lean_2023-06.parquet'

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading data...")
df = pd.read_parquet(DATA_PATH)
print(f"Loaded {len(df):,} rows")

# Detailed mapping: top_category → sub_category → naics_code
print("\nGenerating detailed mapping...")
mapping = df.groupby(['top_category', 'sub_category', 'naics_code']).size().reset_index(name='n_pois')
mapping['naics_2digit'] = mapping['naics_code'].str[:2]
mapping = mapping.sort_values(['top_category', 'sub_category', 'naics_code'])

mapping_path = f'{OUTPUT_DIR}/advan_category_naics_mapping.csv'
mapping.to_csv(mapping_path, index=False)
print(f"Saved: {mapping_path} ({len(mapping):,} combinations)")

# Summary by top_category
print("\nGenerating top_category summary...")
summary = df.groupby('top_category').agg({
    'naics_code': lambda x: ', '.join(sorted(x.unique())[:5]) + ('...' if x.nunique() > 5 else ''),
    'sub_category': 'nunique',
    'placekey': 'count',
    'brand': 'nunique'
}).reset_index()
summary.columns = ['top_category', 'sample_naics', 'n_subcategories', 'n_pois', 'n_brands']
summary = summary.sort_values('n_pois', ascending=False)

summary_path = f'{OUTPUT_DIR}/advan_top_category_summary.csv'
summary.to_csv(summary_path, index=False)
print(f"Saved: {summary_path}")

# Human-readable markdown
print("\nGenerating markdown summary...")
md_lines = ["# Advan Category → NAICS Mapping\n"]
md_lines.append(f"Generated from {len(df):,} POIs (June 2023)\n\n")
md_lines.append("## Top Categories by POI Count\n\n")
md_lines.append("| Top Category | POIs | Brands | SubCats | Sample NAICS |\n")
md_lines.append("|--------------|------|--------|---------|-------------|\n")

for _, row in summary.head(50).iterrows():
    md_lines.append(f"| {row['top_category']} | {row['n_pois']:,} | {row['n_brands']:,} | {row['n_subcategories']} | {row['sample_naics'][:30]}{'...' if len(row['sample_naics']) > 30 else ''} |\n")

md_path = f'{OUTPUT_DIR}/advan_category_mapping.md'
with open(md_path, 'w') as f:
    f.writelines(md_lines)
print(f"Saved: {md_path}")

print("\n=== Top 20 Categories ===")
print(summary.head(20).to_string(index=False))

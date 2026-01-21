#!/usr/bin/env python3
"""Estimate national embedding costs before running."""

import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
POI_DIR = PROJECT_DIR / "outputs" / "entity_resolution" / "unbranded_pois_by_msa"
PAW_FILE = PROJECT_DIR / "outputs" / "entity_resolution" / "paw_company_by_msa.parquet"

COST_PER_1M_TOKENS = 0.13  # text-embedding-3-large
AVG_TOKENS_PER_NAME = 6

print("=" * 70)
print("National Embedding Cost Estimate")
print("=" * 70)

# Load PAW data
print("\n[1] Loading PAW company data...")
paw = pd.read_parquet(PAW_FILE)
paw_by_msa = paw.groupby('msa')['company_name'].nunique().to_dict()
print(f"  Total MSAs in PAW: {len(paw_by_msa)}")
print(f"  Total unique company names: {paw['company_name'].nunique():,}")

# Count POI names per MSA
print("\n[2] Counting POI names per MSA...")
poi_files = [f for f in POI_DIR.glob("*.parquet") if not f.name.startswith('_')]
print(f"  Total MSA POI files: {len(poi_files)}")

msa_stats = []
total_poi_names = 0
total_company_names = 0

for f in poi_files:
    msa = f.stem
    poi_df = pd.read_parquet(f, columns=['location_name'])
    n_poi = poi_df['location_name'].nunique()
    n_company = paw_by_msa.get(msa, 0)

    total_poi_names += n_poi
    total_company_names += n_company

    msa_stats.append({
        'msa': msa,
        'n_poi_names': n_poi,
        'n_company_names': n_company,
        'total_names': n_poi + n_company
    })

msa_df = pd.DataFrame(msa_stats).sort_values('total_names', ascending=False)

print(f"\n[3] Summary:")
print(f"  Total unique POI names: {total_poi_names:,}")
print(f"  Total unique company names: {total_company_names:,}")
print(f"  Grand total names to embed: {total_poi_names + total_company_names:,}")

total_tokens = (total_poi_names + total_company_names) * AVG_TOKENS_PER_NAME
estimated_cost = (total_tokens / 1_000_000) * COST_PER_1M_TOKENS

print(f"\n[4] Cost Estimate:")
print(f"  Total tokens: {total_tokens:,}")
print(f"  Estimated cost: ${estimated_cost:.2f}")

print(f"\n[5] Top 20 MSAs by volume:")
print(msa_df.head(20).to_string(index=False))

print(f"\n[6] MSAs with no PAW companies (will have 0 matches):")
no_paw = msa_df[msa_df['n_company_names'] == 0]
print(f"  {len(no_paw)} MSAs have no PAW company data")
if len(no_paw) > 0:
    print(f"  Examples: {no_paw['msa'].head(5).tolist()}")

# Suggest batching
print(f"\n[7] Suggested batching:")
large = msa_df[msa_df['total_names'] >= 100000]
medium = msa_df[(msa_df['total_names'] >= 20000) & (msa_df['total_names'] < 100000)]
small = msa_df[msa_df['total_names'] < 20000]
print(f"  Large MSAs (>=100K names): {len(large)} - run individually")
print(f"  Medium MSAs (20K-100K names): {len(medium)} - batch 5-10 per job")
print(f"  Small MSAs (<20K names): {len(small)} - batch 20+ per job")

print("\n" + "=" * 70)

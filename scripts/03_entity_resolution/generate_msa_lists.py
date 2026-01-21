#!/usr/bin/env python3
"""Generate MSA lists for batched national processing."""

import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
POI_DIR = PROJECT_DIR / "outputs" / "entity_resolution" / "unbranded_pois_by_msa"
PAW_FILE = PROJECT_DIR / "outputs" / "entity_resolution" / "paw_company_by_msa.parquet"
OUTPUT_DIR = Path("/global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/03_entity_resolution/msa_lists")

LARGE_THRESHOLD = 100000
MEDIUM_THRESHOLD = 20000

print("Loading PAW company data...")
paw = pd.read_parquet(PAW_FILE)
paw_by_msa = paw.groupby('msa')['company_name'].nunique().to_dict()

print("Counting POI names per MSA...")
poi_files = [f for f in POI_DIR.glob("*.parquet") if not f.name.startswith('_')]

msa_stats = []
for f in poi_files:
    msa = f.stem
    poi_df = pd.read_parquet(f, columns=['location_name'])
    n_poi = poi_df['location_name'].nunique()
    n_company = paw_by_msa.get(msa, 0)
    total = n_poi + n_company

    if n_company > 0:  # Only include MSAs with PAW data
        msa_stats.append({
            'msa': msa,
            'n_poi': n_poi,
            'n_company': n_company,
            'total': total
        })

msa_df = pd.DataFrame(msa_stats).sort_values('total', ascending=False)

large = msa_df[msa_df['total'] >= LARGE_THRESHOLD]['msa'].tolist()
medium = msa_df[(msa_df['total'] >= MEDIUM_THRESHOLD) & (msa_df['total'] < LARGE_THRESHOLD)]['msa'].tolist()
small = msa_df[msa_df['total'] < MEDIUM_THRESHOLD]['msa'].tolist()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_DIR / "large_msas.txt", 'w') as f:
    f.write('\n'.join(large))

with open(OUTPUT_DIR / "medium_msas.txt", 'w') as f:
    f.write('\n'.join(medium))

with open(OUTPUT_DIR / "small_msas.txt", 'w') as f:
    f.write('\n'.join(small))

print(f"\nMSA Lists Generated:")
print(f"  Large (>={LARGE_THRESHOLD:,} names): {len(large)} MSAs")
print(f"  Medium ({MEDIUM_THRESHOLD:,}-{LARGE_THRESHOLD:,} names): {len(medium)} MSAs")
print(f"  Small (<{MEDIUM_THRESHOLD:,} names): {len(small)} MSAs")
print(f"  Total: {len(large) + len(medium) + len(small)} MSAs")
print(f"\nSaved to: {OUTPUT_DIR}")

# Estimate costs by tier
large_names = msa_df[msa_df['total'] >= LARGE_THRESHOLD]['total'].sum()
medium_names = msa_df[(msa_df['total'] >= MEDIUM_THRESHOLD) & (msa_df['total'] < LARGE_THRESHOLD)]['total'].sum()
small_names = msa_df[msa_df['total'] < MEDIUM_THRESHOLD]['total'].sum()

cost_per_name = 6 * 0.13 / 1_000_000  # 6 tokens/name, $0.13/1M tokens

print(f"\nEstimated costs by tier:")
print(f"  Large: {large_names:,} names = ${large_names * cost_per_name:.2f}")
print(f"  Medium: {medium_names:,} names = ${medium_names * cost_per_name:.2f}")
print(f"  Small: {small_names:,} names = ${small_names * cost_per_name:.2f}")
print(f"  Total: ${(large_names + medium_names + small_names) * cost_per_name:.2f}")

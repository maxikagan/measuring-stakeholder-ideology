#!/usr/bin/env python3
"""Analyze unmatched singleton POIs."""

import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
CANDIDATE_DIR = PROJECT_DIR / "outputs" / "singleton_matching"
CROSSWALK_DIR = CANDIDATE_DIR / "crosswalks"

msa = "columbus_oh"

print("=" * 70)
print(f"Analyzing Unmatched POIs - {msa}")
print("=" * 70)

# Load candidate pairs (has all POI names)
print("\n[1] Loading data...")
candidates = pd.read_parquet(CANDIDATE_DIR / f"{msa}_candidate_pairs.parquet")
crosswalk = pd.read_parquet(CROSSWALK_DIR / f"{msa}_singleton_crosswalk.parquet")

all_poi_names = set(candidates['location_name'].unique())
matched_poi_names = set(crosswalk['location_name'].unique())
unmatched_poi_names = all_poi_names - matched_poi_names

print(f"  Total unique POI names: {len(all_poi_names):,}")
print(f"  Matched: {len(matched_poi_names):,}")
print(f"  Unmatched: {len(unmatched_poi_names):,}")

# Get best candidate for each unmatched POI
print("\n[2] Finding best candidates for unmatched POIs...")
unmatched_df = candidates[candidates['location_name'].isin(unmatched_poi_names)].copy()

# Get best match per unmatched POI
best_unmatched = unmatched_df.sort_values('cos_sim', ascending=False).groupby('location_name').first().reset_index()

print(f"  Unmatched POIs with candidates: {len(best_unmatched):,}")

# Distribution of best match similarity
print("\n[3] Best match similarity distribution for UNMATCHED POIs:")
bins = [(0.0, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
for low, high in bins:
    count = len(best_unmatched[(best_unmatched['cos_sim'] >= low) & (best_unmatched['cos_sim'] < high)])
    pct = 100 * count / len(best_unmatched)
    print(f"  {low:.1f}-{high:.1f}: {count:,} ({pct:.1f}%)")

# Sample unmatched POIs by similarity range
print("\n[4] Sample UNMATCHED POIs (best candidate shown):")

print("\n  High similarity (0.7-0.9) but still unmatched - WHY?")
high_sim = best_unmatched[(best_unmatched['cos_sim'] >= 0.7) & (best_unmatched['cos_sim'] < 0.9)]
for _, r in high_sim.head(20).iterrows():
    print(f"    [{r['cos_sim']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

print("\n  Medium similarity (0.5-0.7) - partial matches:")
med_sim = best_unmatched[(best_unmatched['cos_sim'] >= 0.5) & (best_unmatched['cos_sim'] < 0.7)]
for _, r in med_sim.sample(min(15, len(med_sim)), random_state=42).iterrows():
    print(f"    [{r['cos_sim']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

print("\n  Low similarity (<0.5) - no good match in PAW:")
low_sim = best_unmatched[best_unmatched['cos_sim'] < 0.5]
for _, r in low_sim.sample(min(15, len(low_sim)), random_state=42).iterrows():
    print(f"    [{r['cos_sim']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

# Common patterns in unmatched names
print("\n[5] Common patterns in UNMATCHED POI names:")
unmatched_names = best_unmatched['location_name'].tolist()

# Check for keywords
patterns = {
    'Church/Religious': ['church', 'baptist', 'methodist', 'lutheran', 'catholic', 'temple', 'mosque', 'synagogue'],
    'School/Education': ['school', 'elementary', 'middle', 'high school', 'academy', 'university', 'college'],
    'Medical/Health': ['hospital', 'clinic', 'medical', 'dental', 'doctor', 'dr ', 'health'],
    'Restaurant/Food': ['restaurant', 'cafe', 'pizza', 'grill', 'kitchen', 'diner', 'bistro'],
    'Retail': ['store', 'shop', 'mart', 'outlet'],
    'Auto': ['auto', 'car', 'tire', 'motor', 'vehicle'],
    'Generic names': ['the ', 'a ', 'an '],
}

for category, keywords in patterns.items():
    count = sum(1 for name in unmatched_names if any(kw in name.lower() for kw in keywords))
    pct = 100 * count / len(unmatched_names)
    print(f"  {category}: {count:,} ({pct:.1f}%)")

# Compare matched vs unmatched characteristics
print("\n[6] Comparing MATCHED vs UNMATCHED POI name lengths:")
matched_names = list(matched_poi_names)
print(f"  Matched avg length: {sum(len(n) for n in matched_names) / len(matched_names):.1f} chars")
print(f"  Unmatched avg length: {sum(len(n) for n in unmatched_names) / len(unmatched_names):.1f} chars")

print("\n" + "=" * 70)
print("Done!")
print("=" * 70)

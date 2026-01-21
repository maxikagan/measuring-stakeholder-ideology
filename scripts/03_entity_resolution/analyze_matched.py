#!/usr/bin/env python3
"""Analyze matched singleton POIs."""

import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
CROSSWALK_DIR = PROJECT_DIR / "outputs" / "singleton_matching" / "crosswalks"

msa = "columbus_oh"

print("=" * 70)
print(f"Matched Singleton POIs - {msa}")
print("=" * 70)

crosswalk = pd.read_parquet(CROSSWALK_DIR / f"{msa}_singleton_crosswalk.parquet")

print(f"\nTotal POI-company links: {len(crosswalk):,}")
print(f"Unique POI names: {crosswalk['location_name'].nunique():,}")
print(f"Unique companies matched to: {crosswalk['company_name'].nunique():,}")

# Match probability distribution
print("\n[1] Match probability distribution:")
for thresh in [0.99, 0.95, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40]:
    count = len(crosswalk[crosswalk['match_probability'] >= thresh])
    pct = 100 * count / len(crosswalk)
    print(f"  >= {thresh:.2f}: {count:,} ({pct:.1f}%)")

# Sample matches at different confidence levels
print("\n[2] HIGH confidence matches (prob >= 0.95):")
high = crosswalk[crosswalk['match_probability'] >= 0.95].sample(min(20, len(crosswalk)), random_state=42)
for _, r in high.iterrows():
    print(f"  [{r['match_probability']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

print("\n[3] MEDIUM confidence matches (prob 0.60-0.80):")
med = crosswalk[(crosswalk['match_probability'] >= 0.60) & (crosswalk['match_probability'] < 0.80)]
if len(med) > 0:
    for _, r in med.sample(min(20, len(med)), random_state=42).iterrows():
        print(f"  [{r['match_probability']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

print("\n[4] LOWER confidence matches (prob 0.40-0.60):")
low = crosswalk[(crosswalk['match_probability'] >= 0.40) & (crosswalk['match_probability'] < 0.60)]
if len(low) > 0:
    for _, r in low.sample(min(20, len(low)), random_state=42).iterrows():
        print(f"  [{r['match_probability']:.2f}] '{r['location_name']}' → '{r['company_name']}'")

# Business type patterns
print("\n[5] Matched POI patterns:")
names = crosswalk['location_name'].unique().tolist()
patterns = {
    'Church/Religious': ['church', 'baptist', 'methodist', 'lutheran', 'catholic'],
    'School': ['school', 'elementary', 'academy'],
    'Medical': ['medical', 'dental', 'clinic', 'hospital', 'health'],
    'Restaurant': ['restaurant', 'cafe', 'pizza', 'grill'],
    'Auto': ['auto', 'car', 'tire', 'motor'],
}

for cat, keywords in patterns.items():
    count = sum(1 for n in names if any(kw in n.lower() for kw in keywords))
    print(f"  {cat}: {count:,}")

print("\n" + "=" * 70)

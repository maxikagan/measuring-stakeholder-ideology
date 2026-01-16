#!/usr/bin/env python3
"""
Steps 1-2: Unzip all state election data and build national CBG lookup.

Combines all 50 states' CBG-level election data into a single lookup table
for cross-state border visitor matching.
"""

import zipfile
import pandas as pd
from pathlib import Path
import os

ELECTION_ZIP_DIR = Path("/global/scratch/users/maxkagan/02_election_voter/election_results_geocoded")
EXTRACT_DIR = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/intermediate/election_unzipped")
OUTPUT_FILE = Path("/global/scratch/users/maxkagan/09_projects/project_oakland/inputs/cbg_partisan_lean_national.parquet")

STATE_FIPS = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
    'CO': '08', 'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12',
    'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18',
    'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23',
    'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28',
    'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33',
    'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38',
    'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
    'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49',
    'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56'
}

FIPS_TO_STATE = {v: k for k, v in STATE_FIPS.items()}


def find_and_unzip_states():
    """Find all state zip files and extract them."""
    print("=" * 60)
    print("STEP 1: UNZIP ALL STATE ELECTION DATA")
    print("=" * 60)

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = list(ELECTION_ZIP_DIR.glob("*.zip"))
    print(f"Found {len(zip_files)} zip files")

    state_dirs = {}

    for zip_path in sorted(zip_files):
        filename = zip_path.name

        if "Contiguous USA" in filename:
            print(f"  Skipping: {filename}")
            continue

        parts = filename.replace('.zip', '').split(' ')
        if len(parts) < 2:
            print(f"  Skipping (unexpected format): {filename}")
            continue

        fips_prefix = parts[0][:2]
        state_abbr = parts[1]

        if fips_prefix not in FIPS_TO_STATE and state_abbr not in STATE_FIPS:
            print(f"  Skipping (unknown state): {filename}")
            continue

        state = state_abbr if state_abbr in STATE_FIPS else FIPS_TO_STATE.get(fips_prefix)

        extract_to = EXTRACT_DIR / state

        if extract_to.exists():
            print(f"  Already extracted: {state}")
        else:
            print(f"  Extracting: {filename} -> {state}")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_to)

        state_dirs[state] = extract_to

    print(f"\nExtracted {len(state_dirs)} states")
    return state_dirs


def find_bg_file(state_dir: Path, state: str) -> Path:
    """Find the bg-2020-RLCR.csv file for a state."""
    fips = STATE_FIPS[state]

    patterns = [
        state_dir / f"{fips}0 {state}" / "Main Method" / "Block Groups" / "bg-2020-RLCR.csv",
        state_dir / "Main Method" / "Block Groups" / "bg-2020-RLCR.csv",
        state_dir / f"{fips}0 {state}" / "Main Method (RLCR)" / "Block Groups" / "bg-2020-RLCR.csv",
    ]

    for pattern in patterns:
        if pattern.exists():
            return pattern

    for csv_file in state_dir.rglob("bg-2020-RLCR.csv"):
        return csv_file

    return None


def build_national_lookup(state_dirs: dict):
    """Build national CBG lookup from all states."""
    print("\n" + "=" * 60)
    print("STEP 2: BUILD NATIONAL CBG LOOKUP")
    print("=" * 60)

    all_dfs = []
    missing_states = []

    for state, state_dir in sorted(state_dirs.items()):
        bg_file = find_bg_file(state_dir, state)

        if bg_file is None:
            print(f"  {state}: bg-2020-RLCR.csv NOT FOUND")
            missing_states.append(state)
            continue

        try:
            df = pd.read_csv(bg_file, dtype={'bg_GEOID': str})

            lookup = pd.DataFrame({
                'cbg_geoid': df['bg_GEOID'].astype(str).str.zfill(12),
                'state': state,
                'trump_2020': df['G20PRERTRU'],
                'biden_2020': df['G20PREDBID'],
                'population': df['bg_population'],
            })

            total_two_party = lookup['trump_2020'] + lookup['biden_2020']
            lookup['two_party_rep_share_2020'] = lookup['trump_2020'] / total_two_party
            lookup['two_party_rep_share_2020'] = lookup['two_party_rep_share_2020'].fillna(0.5)

            all_dfs.append(lookup)
            print(f"  {state}: {len(lookup):,} CBGs (mean R share: {lookup['two_party_rep_share_2020'].mean():.3f})")

        except Exception as e:
            print(f"  {state}: ERROR - {e}")
            missing_states.append(state)

    if missing_states:
        print(f"\nWARNING: Missing states: {missing_states}")

    print("\nCombining all states...")
    combined = pd.concat(all_dfs, ignore_index=True)

    print(f"\n{'=' * 60}")
    print("NATIONAL CBG LOOKUP SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total CBGs: {len(combined):,}")
    print(f"  States: {combined['state'].nunique()}")
    print(f"  Mean Rep share: {combined['two_party_rep_share_2020'].mean():.3f}")
    print(f"  Median Rep share: {combined['two_party_rep_share_2020'].median():.3f}")
    print(f"  Std Dev: {combined['two_party_rep_share_2020'].std():.3f}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUTPUT_FILE, index=False)
    print(f"\nSaved to: {OUTPUT_FILE}")

    return combined


def main():
    print("National CBG Lookup Builder")
    print("=" * 60)

    state_dirs = find_and_unzip_states()
    national_lookup = build_national_lookup(state_dirs)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

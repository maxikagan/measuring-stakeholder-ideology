#!/usr/bin/env python3
"""Step 0: Verify schema compatibility between old and new Advan data."""

import pyarrow.parquet as pq

OLD_PATH = "/global/scratch/users/maxkagan/01_foot_traffic_location/advan/monthly_patterns_foot_traffic/dewey_2024_08_27_parquet/DATE_RANGE_START=2019-01-01/part-0.parquet"
NEW_PATH = "/global/scratch/users/maxkagan/09_projects/project_oakland/advan_foot_traffic_2024_2026-01-12/foot-traffic-monthly-2024/2024-01--data_01c16721-0307-60f1-0042-fa0705144bba_008_0_0.snappy.parquet"

REQUIRED_COLUMNS = [
    'PLACEKEY', 'VISITOR_HOME_CBGS', 'DATE_RANGE_START', 'REGION',
    'BRANDS', 'TOP_CATEGORY', 'SUB_CATEGORY', 'NAICS_CODE',
    'CITY', 'PARENT_PLACEKEY', 'MEDIAN_DWELL', 'RAW_VISITOR_COUNTS'
]

def get_columns(path):
    schema = pq.read_schema(path)
    return set(name.upper() for name in schema.names)

print("=" * 60)
print("STEP 0: SCHEMA VERIFICATION")
print("=" * 60)

print("\nReading old schema...")
old_cols = get_columns(OLD_PATH)
print(f"Old data columns: {len(old_cols)}")

print("\nReading new schema...")
new_cols = get_columns(NEW_PATH)
print(f"New data columns: {len(new_cols)}")

print("\n" + "-" * 60)
print("COMPARISON")
print("-" * 60)

in_both = old_cols & new_cols
only_old = old_cols - new_cols
only_new = new_cols - old_cols

print(f"\nColumns in both: {len(in_both)}")
print(f"Only in old: {len(only_old)}")
if only_old:
    print(f"  {sorted(only_old)}")
print(f"Only in new: {len(only_new)}")
if only_new:
    print(f"  {sorted(only_new)}")

print("\n" + "-" * 60)
print("REQUIRED COLUMNS CHECK")
print("-" * 60)

missing = []
for col in REQUIRED_COLUMNS:
    status = "✓" if col in new_cols else "✗ MISSING"
    print(f"  {col}: {status}")
    if col not in new_cols:
        missing.append(col)

print("\n" + "=" * 60)
if missing:
    print(f"RESULT: FAILED - Missing columns: {missing}")
else:
    print("RESULT: PASSED - All required columns present")
print("=" * 60)

#!/usr/bin/env python3
"""Check raw Advan data for coordinate columns."""

import pyarrow.parquet as pq
from pathlib import Path
import pandas as pd

print("=" * 60)
print("Checking raw Advan data for coordinates")
print("=" * 60)

# Check raw parquet file
raw_dir = Path("/global/scratch/users/maxkagan/01_foot_traffic_location/advan/foot_traffic_monthly_complete_2026-01-12/Monthly Patterns/2023/01")
files = list(raw_dir.glob("*.parquet"))[:1]

if files:
    print(f"\nRaw Advan file: {files[0].name}")
    schema = pq.read_schema(files[0])

    print("\nAll columns:")
    for field in schema:
        print(f"  {field.name}")

    print("\nCoordinate columns:")
    coord_cols = [f.name for f in schema if 'lat' in f.name.lower() or 'lon' in f.name.lower()]
    print(f"  {coord_cols if coord_cols else 'NONE'}")
else:
    print("No parquet files found")

print("\n" + "=" * 60)

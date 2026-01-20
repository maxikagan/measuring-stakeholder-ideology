#!/bin/bash
#SBATCH --job-name=sample_data
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/sample_data_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/sample_data_%j.err

module load python

python3 << 'EOF'
import pandas as pd
import os

print("Loading full dataset...")
df = pd.read_parquet('/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data/poi_with_coords.parquet')
print(f"Full: {len(df):,} rows")

print("Creating sampled dataset (500k rows)...")
sampled = df.sample(n=500000, random_state=42)
print(f"Sampled: {len(sampled):,} rows")

output_path = '/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data/poi_sampled.parquet'
sampled.to_parquet(output_path, index=False)
print(f"Saved to: {output_path}")

size_mb = os.path.getsize(output_path) / 1024 / 1024
print(f"Size: {size_mb:.1f} MB")
EOF

#!/bin/bash
#SBATCH --job-name=convert_ce_combined
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --output=/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_combined_2026-01-12/convert_%j.log
#SBATCH --error=/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_combined_2026-01-12/convert_%j.err

module load python/3.11

echo "Starting CSV to Parquet conversion at $(date)"
echo "Input: consumer_edge_combined_2026-01-12/brand-and-geography-cohort-breakout (64 CSV.gz files, ~6.7GB)"
echo "Output: consumer_edge_combined_2026-01-12/parquet/consumer_edge_brand_geo_combined.parquet"
echo "Method: Streaming (low memory footprint)"
echo ""

python /global/home/users/maxkagan/project_oakland/scripts/consumer_edge/convert_combined_to_parquet.py

EXIT_CODE=$?
echo ""
echo "Conversion completed at $(date) with exit code $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "Output files:"
    ls -lh /global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_combined_2026-01-12/parquet/
fi

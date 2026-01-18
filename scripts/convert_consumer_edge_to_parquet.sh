#!/bin/bash
#SBATCH --job-name=csv_to_parquet
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --mem=128G
#SBATCH --output=/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_data_2026-01-12/convert_%j.log
#SBATCH --error=/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_data_2026-01-12/convert_%j.err

echo "Starting CSV to Parquet conversion at $(date)"

module load r/4.4.0

Rscript /global/home/users/maxkagan/project_oakland/scripts/convert_consumer_edge_to_parquet.R

EXIT_CODE=$?

echo "Conversion completed at $(date) with exit code ${EXIT_CODE}"

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "Output files:"
    ls -lh /global/scratch/users/maxkagan/consumer_edge_data_2026-01-12/parquet/
fi

exit ${EXIT_CODE}

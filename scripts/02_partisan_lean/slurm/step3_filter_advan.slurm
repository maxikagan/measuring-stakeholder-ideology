#!/bin/bash
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --time=06:00:00
#SBATCH --job-name=step3_filter
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step3_%a_%j.out
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step3_%a_%j.err
#SBATCH --array=1-51

STATES=(
  "AL" "AK" "AZ" "AR" "CA" "CO" "CT" "DE" "DC" "FL"
  "GA" "HI" "ID" "IL" "IN" "IA" "KS" "KY" "LA" "ME"
  "MD" "MA" "MI" "MN" "MS" "MO" "MT" "NE" "NV" "NH"
  "NJ" "NM" "NY" "NC" "ND" "OH" "OK" "OR" "PA" "RI"
  "SC" "SD" "TN" "TX" "UT" "VT" "VA" "WA" "WV" "WI"
  "WY"
)

STATE=${STATES[$((SLURM_ARRAY_TASK_ID - 1))]}

echo "Step 3: Filter Advan for ${STATE}"
echo "Job ID: $SLURM_JOB_ID, Array Task: $SLURM_ARRAY_TASK_ID"
echo "Start: $(date)"

module load python/3.11.6-gcc-11.4.0
cd /global/home/users/maxkagan/project_oakland/scripts
python3 -u 03_filter_advan_by_state.py ${STATE}

echo "Exit code: $?"
echo "End: $(date)"

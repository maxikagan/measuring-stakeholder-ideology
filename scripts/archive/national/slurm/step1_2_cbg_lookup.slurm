#!/bin/bash
#SBATCH --job-name=step1_2_cbg
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step1_2_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step1_2_%j.err

module load python/3.11

echo "Starting Step 1-2: Build National CBG Lookup"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

cd /global/home/users/maxkagan/project_oakland

python scripts/national/step1_2_build_national_cbg_lookup.py

echo "End time: $(date)"

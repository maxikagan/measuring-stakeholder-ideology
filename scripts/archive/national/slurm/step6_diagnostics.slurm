#!/bin/bash
#SBATCH --job-name=step6_diag
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step6_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step6_%j.err

module load python/3.11

echo "Starting Step 6: Generate Diagnostics"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

cd /global/home/users/maxkagan/project_oakland

python scripts/national/step6_generate_diagnostics.py

echo "End time: $(date)"

#!/bin/bash
#SBATCH --job-name=step4_lean
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=08:00:00
#SBATCH --array=0-50
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step4_%A_%a.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step4_%A_%a.err

module load python/3.11

echo "Starting Step 4: Compute Partisan Lean"
echo "Job ID: $SLURM_JOB_ID, Array Task: $SLURM_ARRAY_TASK_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

cd /global/home/users/maxkagan/project_oakland

python scripts/national/step4_compute_partisan_lean.py

echo "End time: $(date)"

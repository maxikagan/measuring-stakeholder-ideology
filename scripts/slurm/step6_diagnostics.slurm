#!/bin/bash
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=step6_diag
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step6_%j.out
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step6_%j.err

echo "Step 6: Generate Diagnostics"
echo "Job ID: $SLURM_JOB_ID"
echo "Start: $(date)"

module load python/3.11.6-gcc-11.4.0
cd /global/home/users/maxkagan/project_oakland/scripts
python3 -u 06_generate_diagnostics.py

echo "Exit code: $?"
echo "End: $(date)"

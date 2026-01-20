#!/bin/bash
#SBATCH --job-name=dashboard_prep
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/dashboard_prep_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/dashboard_prep_%j.err

echo "=========================================="
echo "Dashboard Data Preparation"
echo "Job ID: $SLURM_JOB_ID"
echo "Started: $(date)"
echo "=========================================="

module load python

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

python scripts/dashboard/01_prepare_dashboard_data.py

echo "=========================================="
echo "Finished: $(date)"
echo "=========================================="

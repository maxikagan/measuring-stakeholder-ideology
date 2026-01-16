#!/bin/bash
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --job-name=step1_2_election_setup
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step1_2_%j.out
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step1_2_%j.err

echo "=========================================="
echo "Step 1-2: Election Data Setup"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "=========================================="

module load python/3.11.6-gcc-11.4.0

echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"

cd /global/home/users/maxkagan/project_oakland/scripts

echo "Running election setup script..."
python3 -u 01_02_election_data_setup.py

EXIT_CODE=$?
echo "=========================================="
echo "Exit code: $EXIT_CODE"
echo "End: $(date)"
echo "=========================================="

exit $EXIT_CODE

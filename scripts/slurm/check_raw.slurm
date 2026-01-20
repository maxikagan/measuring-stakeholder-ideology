#!/bin/bash
#SBATCH --job-name=check_raw
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/slurm/logs/check_raw_%j.out

module load python/3.11
python3 -u /global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/diagnostics/check_raw_advan.py

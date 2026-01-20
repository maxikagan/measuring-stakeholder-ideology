#!/bin/bash
#SBATCH --job-name=join_normalized
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --exclude=n0008.savio3
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/join_normalized_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/join_normalized_%j.err

module load python/3.11

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

echo "Starting join at $(date)"
echo "Node: $(hostname)"

export PYTHONUNBUFFERED=1
stdbuf -oL -eL python3 -u scripts/02_partisan_lean/join_normalized_visits.py

echo "Completed at $(date)"

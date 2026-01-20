#!/bin/bash
#SBATCH --job-name=paw_msa_table
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/paw_msa_table_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/paw_msa_table_%j.err

module load python/3.11

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

echo "Starting at $(date)"
echo "Node: $(hostname)"

export PYTHONUNBUFFERED=1
stdbuf -oL -eL python3 -u scripts/03_entity_resolution/10_build_paw_company_msa_table.py

echo "Completed at $(date)"

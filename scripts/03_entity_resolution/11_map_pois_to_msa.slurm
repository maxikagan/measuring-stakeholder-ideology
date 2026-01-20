#!/bin/bash
#SBATCH --job-name=poi_to_msa
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --exclude=n0008.savio3
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/poi_to_msa_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/poi_to_msa_%j.err

module load python/3.11

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

echo "Starting at $(date)"
echo "Node: $(hostname)"

export PYTHONUNBUFFERED=1
stdbuf -oL -eL python3 -u scripts/03_entity_resolution/11_map_pois_to_msa.py

echo "Completed at $(date)"

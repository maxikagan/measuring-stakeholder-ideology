#!/bin/bash
#SBATCH --job-name=category_map
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:15:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/category_mapping_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/category_mapping_%j.err

module load python/3.11
python /global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/generate_category_mapping.py

#!/bin/bash
#SBATCH --job-name=tiered_entity_res
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/tiered_entity_res_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/tiered_entity_res_%j.err

module load python/3.11.6-gcc-11.4.0

source /global/home/users/maxkagan/measuring_stakeholder_ideology/.env

cd /global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/03_entity_resolution

python 20_tiered_entity_resolution.py

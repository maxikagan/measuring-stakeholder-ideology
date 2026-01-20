#!/bin/bash
#SBATCH --job-name=step0_schema
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/step0_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/step0_%j.err

module load python/3.11

cd /global/home/users/maxkagan/project_oakland

python scripts/step0_verify_schema.py

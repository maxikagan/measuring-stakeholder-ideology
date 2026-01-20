#!/bin/bash
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=step7_brand
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step7_%j.out
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step7_%j.err

echo "Step 7: Brand Heterogeneity Analysis"
echo "Job ID: $SLURM_JOB_ID"
echo "Start: $(date)"

module load python/3.11.6-gcc-11.4.0
cd /global/home/users/maxkagan/project_oakland/scripts
python3 -u 07_brand_heterogeneity.py

echo "Exit code: $?"
echo "End: $(date)"

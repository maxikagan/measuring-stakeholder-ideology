#!/bin/bash
#SBATCH --job-name=step5_combine
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step5_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step5_%j.err

module load python/3.11

echo "Starting Step 5: Combine and Partition by Month"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

cd /global/home/users/maxkagan/project_oakland

python scripts/national/step5_combine_and_partition.py

echo "End time: $(date)"

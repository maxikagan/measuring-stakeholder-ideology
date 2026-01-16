#!/bin/bash
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=step5_combine
#SBATCH --output=/global/home/users/maxkagan/project_oakland/logs/national/step5_%j.out
#SBATCH --error=/global/home/users/maxkagan/project_oakland/logs/national/step5_%j.err

echo "Step 5: Combine and Partition"
echo "Job ID: $SLURM_JOB_ID"
echo "Start: $(date)"

module load python/3.11.6-gcc-11.4.0
cd /global/home/users/maxkagan/project_oakland/scripts
python3 -u 05_combine_and_partition.py

echo "Exit code: $?"
echo "End: $(date)"

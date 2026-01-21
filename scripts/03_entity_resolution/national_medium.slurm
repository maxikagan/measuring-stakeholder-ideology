#!/bin/bash
#SBATCH --job-name=singleton_medium
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=1-12
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/singleton_medium_%A_%a.log

# Medium MSAs: batch 10 per task (~117 MSAs = 12 tasks)

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

source ~/.bashrc

module load gcc/11.4.0
module load python/3.10.12-gcc-11.4.0

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-11.4.0-nfcdl6bpyabpnhhasfzu6y4ge4kfskvl/lib64:$LD_LIBRARY_PATH

pip install --user rapidfuzz scikit-learn --quiet

MSA_FILE="scripts/03_entity_resolution/msa_lists/medium_msas.txt"
BATCH_SIZE=10

START=$(( (SLURM_ARRAY_TASK_ID - 1) * BATCH_SIZE + 1 ))
END=$(( SLURM_ARRAY_TASK_ID * BATCH_SIZE ))

MSAS=$(sed -n "${START},${END}p" $MSA_FILE | tr '\n' ' ')

echo "Task $SLURM_ARRAY_TASK_ID: Processing MSAs $START to $END"
echo "MSAs: $MSAS"
echo "Start: $(date)"

python3 -u scripts/03_entity_resolution/16_singleton_national.py $MSAS

echo "End: $(date)"

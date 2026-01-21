#!/bin/bash
#SBATCH --job-name=singleton_large
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --array=1-41
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/singleton_large_%A_%a.log

# Large MSAs: process one per task (41 MSAs)

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

source ~/.bashrc

module load gcc/11.4.0
module load python/3.10.12-gcc-11.4.0

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-11.4.0-nfcdl6bpyabpnhhasfzu6y4ge4kfskvl/lib64:$LD_LIBRARY_PATH

pip install --user rapidfuzz scikit-learn --quiet

MSA_FILE="scripts/03_entity_resolution/msa_lists/large_msas.txt"
MSA=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $MSA_FILE)

echo "Task $SLURM_ARRAY_TASK_ID: Processing $MSA"
echo "Start: $(date)"

python3 -u scripts/03_entity_resolution/16_singleton_national.py "$MSA"

echo "End: $(date)"

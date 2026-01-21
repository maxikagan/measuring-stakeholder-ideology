#!/bin/bash
#SBATCH --job-name=singleton_bigmem
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3_bigmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=06:00:00
#SBATCH --array=1-11
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/singleton_bigmem_%A_%a.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/singleton_bigmem_%A_%a.err

module load python/3.11.6-gcc-11.4.0

source /global/home/users/maxkagan/measuring_stakeholder_ideology/.env

MSA_LIST="/global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/03_entity_resolution/msa_lists/failed_large_msas.txt"
MSA=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$MSA_LIST")

if [ -z "$MSA" ]; then
    echo "No MSA found for array task $SLURM_ARRAY_TASK_ID"
    exit 1
fi

echo "Processing MSA: $MSA (task $SLURM_ARRAY_TASK_ID)"
echo "Partition: $SLURM_JOB_PARTITION"
echo "Memory available: savio3_bigmem (~386GB)"

cd /global/home/users/maxkagan/measuring_stakeholder_ideology/scripts/03_entity_resolution

python 16_singleton_national.py --msa "$MSA"

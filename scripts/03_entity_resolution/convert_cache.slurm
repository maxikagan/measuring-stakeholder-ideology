#!/bin/bash
#SBATCH --job-name=convert_cache
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/convert_cache_%j.log

echo "Converting Columbus cache to efficient format..."
echo "Start: $(date)"

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

module load gcc/11.4.0
module load python/3.10.12-gcc-11.4.0

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-11.4.0-nfcdl6bpyabpnhhasfzu6y4ge4kfskvl/lib64:$LD_LIBRARY_PATH

python3 -u scripts/03_entity_resolution/embedding_cache.py convert columbus_oh

echo ""
echo "Comparing sizes..."
echo "Old cache:"
ls -lh /global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/singleton_matching/embedding_cache/columbus_oh*.json

echo ""
echo "New cache:"
ls -lh /global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/singleton_matching/embedding_cache_v2/columbus_oh*

echo ""
echo "End: $(date)"

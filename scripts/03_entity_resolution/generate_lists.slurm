#!/bin/bash
#SBATCH --job-name=gen_msa_lists
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:15:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/gen_msa_lists_%j.log

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

module load gcc/11.4.0
module load python/3.10.12-gcc-11.4.0

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-11.4.0-nfcdl6bpyabpnhhasfzu6y4ge4kfskvl/lib64:$LD_LIBRARY_PATH

python3 -u scripts/03_entity_resolution/generate_msa_lists.py

#!/bin/bash
#SBATCH --job-name=singleton_test
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/logs/singleton_test_%j.log

# Test job: process 3 small MSAs to validate pipeline

cd /global/home/users/maxkagan/measuring_stakeholder_ideology

source ~/.bashrc

module load gcc/11.4.0
module load python/3.10.12-gcc-11.4.0

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-11.4.0-nfcdl6bpyabpnhhasfzu6y4ge4kfskvl/lib64:$LD_LIBRARY_PATH

pip install --user rapidfuzz scikit-learn --quiet

echo "Test run: 3 small MSAs"
echo "Start: $(date)"

python3 -u scripts/03_entity_resolution/16_singleton_national.py santa_cruz-watsonville_ca olympia_wa holland-grand_haven_mi

echo "End: $(date)"

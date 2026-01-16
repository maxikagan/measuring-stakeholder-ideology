#!/bin/bash
#SBATCH --job-name=dashboard
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=/global/home/users/maxkagan/measuring_stakeholder_ideology/dashboard/dashboard_%j.out
#SBATCH --error=/global/home/users/maxkagan/measuring_stakeholder_ideology/dashboard/dashboard_%j.err

echo "========================================"
echo "Stakeholder Ideology Dashboard"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"
echo "========================================"

module load python

pip install --user streamlit plotly pandas pyarrow --quiet

echo ""
echo "========================================"
echo "Dashboard starting on: $SLURMD_NODENAME:8501"
echo ""
echo "TO ACCESS FROM YOUR LAPTOP:"
echo "  ssh -L 8501:$SLURMD_NODENAME:8501 maxkagan@hpc.brc.berkeley.edu"
echo ""
echo "Then open: http://localhost:8501"
echo "========================================"
echo ""

cd /global/home/users/maxkagan/measuring_stakeholder_ideology/dashboard
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

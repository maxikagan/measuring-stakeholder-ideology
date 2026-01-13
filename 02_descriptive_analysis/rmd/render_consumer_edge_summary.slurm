#!/bin/bash
#SBATCH --job-name=render_ce_rmd
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/render_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/render_%j.err

module load r/4.4.0

RMD_FILE="/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/consumer_edge_summary.Rmd"
OUTPUT_DIR="/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd"

echo "Starting RMD render at $(date)"
echo "Input: $RMD_FILE"
echo "Output directory: $OUTPUT_DIR"
echo ""

cd "$OUTPUT_DIR"

Rscript -e "rmarkdown::render('$RMD_FILE', output_dir='$OUTPUT_DIR')"

EXIT_CODE=$?
echo ""
echo "Render completed at $(date) with exit code $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "Output files:"
    ls -lh "$OUTPUT_DIR"/*.html 2>/dev/null
fi

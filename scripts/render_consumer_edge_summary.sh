#!/bin/bash
#SBATCH --job-name=render_rmd
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --mem=32G
#SBATCH --output=/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/render_%j.log
#SBATCH --error=/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/render_%j.err

RMD_FILE="/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd/consumer_edge_summary.Rmd"
OUTPUT_DIR="/global/home/users/maxkagan/project_oakland/02_descriptive_analysis/rmd"

echo "Starting R Markdown render at $(date)"
echo "Input: ${RMD_FILE}"
echo "Output directory: ${OUTPUT_DIR}"

module load r/4.4.0

cd "${OUTPUT_DIR}" || { echo "ERROR: Failed to access ${OUTPUT_DIR}"; exit 1; }

Rscript -e "rmarkdown::render('${RMD_FILE}', output_dir = '${OUTPUT_DIR}')"

EXIT_CODE=$?

echo "Render completed at $(date) with exit code ${EXIT_CODE}"

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "Output files:"
    ls -lh "${OUTPUT_DIR}"/*.html 2>/dev/null || echo "No HTML files found"
fi

exit ${EXIT_CODE}

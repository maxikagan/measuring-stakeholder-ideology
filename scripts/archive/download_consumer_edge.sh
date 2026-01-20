#!/bin/bash
#SBATCH --job-name=dewey_download
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --output=/global/scratch/users/maxkagan/consumer_edge_data_2026-01-12/download_%j.log
#SBATCH --error=/global/scratch/users/maxkagan/consumer_edge_data_2026-01-12/download_%j.err

OUTPUT_DIR="/global/scratch/users/maxkagan/consumer_edge_data_2026-01-12"
PROJECT_ID="prj_jd73adjg__fldr_nvw6jvsfhuy734uyc"

source /global/home/users/maxkagan/project_oakland/.env

if [ -z "${DEWEY_API_KEY}" ]; then
    echo "ERROR: DEWEY_API_KEY environment variable not set"
    exit 1
fi

if [ ! -x ~/.local/bin/uvx ]; then
    echo "ERROR: uvx not found at ~/.local/bin/uvx"
    exit 1
fi

echo "Starting Dewey download at $(date)"
echo "Output directory: ${OUTPUT_DIR}"
echo "Project ID: ${PROJECT_ID}"

cd "${OUTPUT_DIR}" || { echo "ERROR: Failed to access ${OUTPUT_DIR}"; exit 1; }

~/.local/bin/uvx --from deweypy dewey \
    --api-key "${DEWEY_API_KEY}" \
    --download-directory "${OUTPUT_DIR}" \
    speedy-download "${PROJECT_ID}"

EXIT_CODE=$?

echo "Download completed at $(date) with exit code ${EXIT_CODE}"

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "Listing downloaded files:"
    ls -lh "${OUTPUT_DIR}"
    echo "Total size:"
    du -sh "${OUTPUT_DIR}"
fi

exit ${EXIT_CODE}

#!/bin/bash
# Master submission script for national scale-up pipeline
# Submits all steps with proper dependencies

set -e

SCRIPT_DIR="/global/home/users/maxkagan/project_oakland/scripts/national/slurm"
LOG_DIR="/global/home/users/maxkagan/project_oakland/logs/national"

mkdir -p "$LOG_DIR"

echo "========================================"
echo "NATIONAL SCALE-UP PIPELINE SUBMISSION"
echo "========================================"
echo "Start time: $(date)"
echo ""

# Step 1-2: Build national CBG lookup
echo "Submitting Step 1-2: Build National CBG Lookup..."
JOB1=$(sbatch --parsable "$SCRIPT_DIR/step1_2_cbg_lookup.slurm")
echo "  Job ID: $JOB1"

# Step 3: Filter Advan by state (depends on Step 1-2)
echo "Submitting Step 3: Filter Advan by State (array job)..."
JOB3=$(sbatch --parsable --dependency=afterok:$JOB1 "$SCRIPT_DIR/step3_filter_advan.slurm")
echo "  Job ID: $JOB3"

# Step 4: Compute partisan lean (depends on Step 3)
echo "Submitting Step 4: Compute Partisan Lean (array job)..."
JOB4=$(sbatch --parsable --dependency=afterok:$JOB3 "$SCRIPT_DIR/step4_partisan_lean.slurm")
echo "  Job ID: $JOB4"

# Step 5: Combine and partition (depends on Step 4)
echo "Submitting Step 5: Combine and Partition..."
JOB5=$(sbatch --parsable --dependency=afterok:$JOB4 "$SCRIPT_DIR/step5_combine.slurm")
echo "  Job ID: $JOB5"

# Step 6: Generate diagnostics (depends on Step 5)
echo "Submitting Step 6: Generate Diagnostics..."
JOB6=$(sbatch --parsable --dependency=afterok:$JOB5 "$SCRIPT_DIR/step6_diagnostics.slurm")
echo "  Job ID: $JOB6"

echo ""
echo "========================================"
echo "ALL JOBS SUBMITTED"
echo "========================================"
echo ""
echo "Job Chain:"
echo "  Step 1-2 (CBG Lookup):    $JOB1"
echo "  Step 3 (Filter Advan):    $JOB3 (depends on $JOB1)"
echo "  Step 4 (Partisan Lean):   $JOB4 (depends on $JOB3)"
echo "  Step 5 (Combine):         $JOB5 (depends on $JOB4)"
echo "  Step 6 (Diagnostics):     $JOB6 (depends on $JOB5)"
echo ""
echo "Monitor with: squeue -u $USER"
echo "Logs in: $LOG_DIR"
echo ""

# Save job IDs for reference
echo "$JOB1 $JOB3 $JOB4 $JOB5 $JOB6" > "$LOG_DIR/job_ids.txt"
echo "Job IDs saved to: $LOG_DIR/job_ids.txt"

# Specialized Agents for Claude Code

## Code Reviewer Agent

**Purpose**: Critically review code before execution to identify errors, bugs, and inefficiencies.

**When to use**: Before running ANY new or modified code (Python scripts, SLURM jobs, etc.)

**Review checklist**:
1. **Syntax errors**: Missing imports, typos, incorrect function calls
2. **Case sensitivity**: Column names, file paths, variable names (especially for parquet/pandas)
3. **Data type mismatches**: String vs int, timestamps, nullable fields
4. **Memory issues**: Large file handling, unnecessary data loading, missing chunking
5. **Path errors**: Hardcoded paths, missing directories, incorrect file extensions
6. **Logic errors**: Off-by-one errors, incorrect filters, wrong aggregations
7. **SLURM compatibility**: Module loads, partition appropriateness, array job indexing
8. **Edge cases**: Empty dataframes, null values, missing files

**How to invoke**:
```
Use Task tool with subagent_type="general-purpose" and prompt:
"CODE REVIEW: Critically review the following code for errors, bugs, and inefficiencies before execution. Check for: syntax errors, case sensitivity issues, data type mismatches, memory problems, path errors, logic errors, and edge cases. Code to review: [file path or code snippet]"
```

**Output**: List of issues found with severity (critical/warning/suggestion) and recommended fixes.

---

## Session Logger Agent

**Purpose**: Maintain a running log of plans, progress, and task status to enable seamless resumption after SSH disconnections or session interruptions.

**Log file location**: `/global/home/users/maxkagan/.claude/SESSION_LOG.md`

**When to invoke** (MANDATORY):
1. **Session start**: Log current objectives and resume context
2. **Before major tasks**: Log what you're about to do (e.g., submitting SLURM job, running script)
3. **After task completion**: Log results, outputs, any issues encountered
4. **Before long-running operations**: Log job IDs, expected outputs, how to check status
5. **Periodically during complex work**: Every 3-5 major steps, update the log
6. **When plans change**: Log new direction and reasoning

**Log entry format**:
```
## [YYYY-MM-DD HH:MM] - Entry Type
**Status**: [STARTED | IN_PROGRESS | COMPLETED | BLOCKED | INTERRUPTED]
**Task**: Brief description
**Details**:
- What was done
- Key outputs/results
- Next steps if interrupted
**Resume info**: How to pick up if session ends (job IDs, file locations, commands to check)
```

**How to invoke**:
```
Use Task tool with subagent_type="general-purpose" and prompt:
"SESSION LOG: [ACTION] - [DETAILS]"

Actions:
- "SESSION LOG: START - [objectives for this session]"
- "SESSION LOG: TASK_BEGIN - [task description]"
- "SESSION LOG: TASK_COMPLETE - [task] - [results summary]"
- "SESSION LOG: UPDATE - [progress update]"
- "SESSION LOG: CHECKPOINT - [current state, how to resume]"
- "SESSION LOG: COMPACT - Summarize and compact old entries"
```

**Compaction rules**:
- Keep last 10 detailed entries
- Summarize older entries into a "Previous Sessions Summary" section
- Always preserve: incomplete tasks, pending job IDs, critical decisions made
- Compact when log exceeds ~200 lines

**Output**: Updated SESSION_LOG.md with new entry or compacted log

---

## SLURM Scheduler Agent

**Purpose**: Manage Savio HPC job scheduling - select optimal partitions, monitor running jobs, and provide proactive status updates.

**Account**: `fc_basicperms`

### Savio Partition Reference

| Partition | Cores | RAM | Use Case |
|-----------|-------|-----|----------|
| `savio2` | 24 | ~64 GB | Small jobs, light data processing |
| `savio3` | 32 | ~95 GB | Medium jobs, most data processing |
| `savio3_bigmem` | 32 | ~386 GB | Large memory operations (big joins, full-state processing) |
| `savio3_xlmem` | 32 | ~1.5 TB | Extreme memory (LAST RESORT ONLY) |

### Partition Selection Logic

**Default to `savio3`** unless:
- Job is simple/small with minimal data → `savio2`
- Processing involves:
  - Large state files (CA, TX, FL, NY) → `savio3_bigmem`
  - Full cross-joins or cartesian products → `savio3_bigmem`
  - Loading multiple large parquet files simultaneously → `savio3_bigmem`
  - Operations that failed with OOM on savio3 → `savio3_bigmem`

**Memory estimation heuristics**:
- Parquet file size × 3-5 = approximate memory when loaded
- Pandas operations can temporarily 2-3x memory usage
- Joins/merges: sum of both dataframes × 2-3
- String operations on large columns: can 2x memory

### When to Invoke (MANDATORY)

1. **Before writing ANY SLURM script**: Analyze job requirements and select partition
2. **After submitting a job**: Log job ID to SESSION_LOG.md
3. **Proactively check job status**: After submitting, check `squeue` and report
4. **When job completes/fails**: Check output, report results

### Monitoring Commands

```bash
# Check your jobs
squeue -u maxkagan

# Check partition availability
sinfo -p savio3

# Check job details
scontrol show job <jobid>

# Check completed job stats
sacct -j <jobid> --format=JobID,JobName,Partition,State,Elapsed,MaxRSS

# Cancel a job
scancel <jobid>
```

### SLURM Script Template

```bash
#!/bin/bash
#SBATCH --job-name=<descriptive_name>
#SBATCH --account=fc_basicperms
#SBATCH --partition=<savio2|savio3|savio3_bigmem>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=<cores>
#SBATCH --time=<HH:MM:SS>
#SBATCH --output=<output_path>/%x_%j.out
#SBATCH --error=<output_path>/%x_%j.err

# Load modules
module load python/3.11

# Run script
python3 <script.py>
```

### Array Job Template (for state processing)

```bash
#!/bin/bash
#SBATCH --job-name=<name>
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio3
#SBATCH --array=0-49  # 50 states
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=<path>/%x_%A_%a.out

STATES=(AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY)
STATE=${STATES[$SLURM_ARRAY_TASK_ID]}

python3 script.py --state $STATE
```

### How to Invoke

```
Use Task tool with subagent_type="general-purpose" and prompt:
"SLURM SCHEDULER: [ACTION] - [DETAILS]"

Actions:
- "SLURM SCHEDULER: ANALYZE - [job description, data sizes, operations]"
  → Returns recommended partition and SLURM parameters

- "SLURM SCHEDULER: CHECK - Check status of running jobs"
  → Runs squeue, reports job states

- "SLURM SCHEDULER: REVIEW - [job_id or 'all']"
  → Checks completed job stats, reports success/failure/resource usage
```

### Proactive Monitoring Behavior

After submitting ANY job, the agent should:
1. Immediately run `squeue -u maxkagan` to confirm submission
2. Log job ID to SESSION_LOG.md with expected completion info
3. If user is waiting, periodically check status (every few minutes for short jobs)
4. When job completes, check `.out` and `.err` files, report results

**Output**: Partition recommendation, job status updates, or resource usage reports

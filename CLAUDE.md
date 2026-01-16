# Claude Code Instructions for Project Oakland

## General Rules
- Don't run jobs on the login node. Create a bash job with SLURM.
- Data fidelity is paramount - be transparent with everything, no unnecessary shortcuts.
- This is academic research - document all steps clearly.
- **Multi-stage analytics jobs**: Create validation checks at each step to ensure output is reasonable and as expected (e.g., row counts, value ranges, sample records, known-answer tests).

## Code Review Requirement (MANDATORY)
**Before running ANY new or modified code**, use the Code Reviewer agent to critically review it.
- See `AGENTS.md` for full agent description and checklist
- Review checks: syntax errors, case sensitivity, data types, memory issues, path errors, logic errors, edge cases
- This prevents wasted compute time from avoidable bugs (e.g., uppercase vs lowercase column names)
- Invoke via Task tool with subagent_type="general-purpose" and prompt starting with "CODE REVIEW:"

## Session Logging Requirement (MANDATORY)
**Log progress to enable resumption after SSH disconnections.**
- Log file: `~/.claude/SESSION_LOG.md`
- See `AGENTS.md` for full agent description
- **When to log**:
  - Session start (objectives, context)
  - Before/after major tasks (SLURM jobs, scripts, data processing)
  - Before long-running operations (include job IDs, how to check status)
  - When plans change
- Invoke via Task tool with subagent_type="general-purpose" and prompt starting with "SESSION LOG:"
- **Compact log periodically** to prevent file bloat (keep last 10 detailed entries)

## SLURM Scheduler Requirement (MANDATORY)
**Use SLURM Scheduler Agent for all job management.**
- See `AGENTS.md` for full partition specs and templates
- **Before writing SLURM scripts**: Invoke to analyze job and select optimal partition
- **After submitting jobs**: Check queue status, log job ID to SESSION_LOG.md
- **Proactively monitor**: Report job status without being asked
- Invoke via Task tool with subagent_type="general-purpose" and prompt starting with "SLURM SCHEDULER:"

## UC Berkeley Savio HPC Guidelines
- **Account**: fc_basicperms
- **Partitions**:
  - `savio2`: 24 cores, ~64 GB RAM - for small jobs without much data
  - `savio3`: 32 cores, ~95 GB RAM - for medium jobs
  - `savio3_bigmem`: 32 cores, ~386 GB RAM - only when needed for large memory operations
  - `savio3_xlmem`: only if absolutely necessary
- **Parallelization**: Use array jobs when processing by state or month
- **State groupings for array jobs**:
  - Large (individual jobs): CA, TX, FL, NY, PA, IL, OH, GA, NC, MI
  - Medium/small: group 2-3 states per job

## Project Oakland: Stakeholder Ideology from Foot Traffic

### Goal
Generate estimates of partisan lean of business visitors (proxy for consumers) by combining:
1. Advan foot traffic data (visitor_home_cbgs)
2. CBG-level election results (2020) from geocoded election data
3. Politics at Work employee ideology data

### Target
Fall 2026 job market paper for SMJ/Organization Science/Management Science/ASQ

### Key Data Sources
1. **Advan Monthly Patterns** (existing, no download needed):
   - Location: `/global/scratch/users/maxkagan/advan/monthly_patterns_foot_traffic/dewey_2024_08_27_parquet/`
   - Coverage: Jan 2019 - Jul 2024

2. **Advan Neighborhood Patterns** (available):
   - For Bartik IV and baseline visitor composition

3. **CBG-Level Election Results**:
   - Location: `/global/scratch/users/maxkagan/02_election_voter/election_results_geocoded/`
   - Files: `bg-2016-RLCR.csv` and `bg-2020-RLCR.csv` (in Main Method zip)
   - Format: Block Group level vote estimates for 2016 and 2020 elections

4. **Politics at Work**:
   - Full microdata: 45M individuals with work histories
   - Can aggregate by MSA × employer × year

### Key Decisions
- **Election data**: Include both 2016 and 2020 CBG-level election results for all POIs
  - Primary: `two_party_rep_share_2020` = Trump / (Biden + Trump)
  - Secondary/robustness: `two_party_rep_share_2016` = Trump / (Clinton + Trump)
- Output format: Long (placekey x month rows)
- CBG method: Main Method (RLCR)
- Entity resolution: Maximum coverage (public + private, branded + unbranded)
- API budget for FuzzyLink: $500-2000

### File Structure
- **Home** (`/global/home/users/maxkagan/measuring_stakeholder_ideology/`): scripts, references, small files
- **Scratch** (`/global/scratch/users/maxkagan/measuring_stakeholder_ideology/`): large data only
- **GitHub**: https://github.com/maxikagan/measuring-stakeholder-ideology

### Research Agenda
See `research_agenda_draft.md` for full details including:
- 12 research options (A-L)
- Prioritized action plan (5 phases)
- Identification strategies
- Data readiness tiers

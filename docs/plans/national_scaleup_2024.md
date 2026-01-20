# Plan: Scale Up Ohio Analysis to National 2024 Data

## Overview

Scale the Ohio 2023 pilot analysis to all 50 states using the 2024 Advan foot traffic data. Generate POI-level partisan lean estimates for the entire United States.

## Data Sources

### Input Data
1. **2024 Advan Foot Traffic** (just downloaded)
   - Location: `/global/scratch/users/maxkagan/project_oakland/advan_foot_traffic_2024_2026-01-12/foot-traffic-monthly-2024/`
   - Size: 177 GB, 438 parquet files
   - Coverage: Jan-Dec 2024, all US states

2. **2020 Election Results** (existing)
   - Location: `/global/scratch/users/maxkagan/election_results_geocoded/`
   - Format: Zipped state files with CBG-level vote estimates
   - All 50 states available
   - Method: Main Method (RLCR) Block Group level

### Output Data
- Location: `/global/scratch/users/maxkagan/project_oakland/outputs/location_partisan_lean/national_2024/`
- Format: Parquet files partitioned by month (12 files)
- Granularity: POI × month observations
- Expected size: ~15-20M POI-month observations

## Key Design Decisions

### 1. National CBG Lookup Table
Build a **single national CBG lookup table** combining all 50 states' election data. This handles cross-state border visitors (e.g., Kentucky visitors to Cincinnati POIs).

### 2. State-by-State Processing with National Lookup
- Process Advan data state-by-state for parallelization
- Join against the national CBG lookup (not state-specific)
- Enables efficient array job parallelization

### 3. Array Job Grouping by State Size
Per CLAUDE.md guidelines:
- **Large states (individual jobs)**: CA, TX, FL, NY, PA, IL, OH, GA, NC, MI
- **Medium/small states**: Group 2-3 per job

### 4. Edge Case Handling
- CBGs with zero votes: Set to 0.5 (neutral) - same as Ohio
- Unmatched CBGs: **Flag for investigation** rather than assume
- Generate diagnostic output tracking unmatched CBGs with counts

## Output Schema

| Column | Description |
|--------|-------------|
| placekey | Unique POI identifier |
| date_range_start | Month start date |
| brand | Brand name (if applicable) |
| top_category | Primary category |
| sub_category | Subcategory |
| naics_code | NAICS code |
| city | City |
| region | State abbreviation |
| parent_placekey | Parent location (NEW) |
| median_dwell | Median dwell time (NEW) |
| rep_lean | Two-party Republican share (weighted by visitors) |
| total_visitors | Total visitor count from matched CBGs |
| unmatched_visitors | Visitor count from unmatched CBGs (diagnostic) |
| pct_visitors_matched | Percentage of visitors successfully matched |

## Pipeline Steps

### Step 0: Schema Verification
Verify column name compatibility between:
- Old Advan path: `/global/scratch/users/maxkagan/advan/monthly_patterns_foot_traffic/dewey_2024_08_27_parquet/`
- New 2024 path: `/global/scratch/users/maxkagan/project_oakland/advan_foot_traffic_2024_2026-01-12/foot-traffic-monthly-2024/`

### Step 1: Unzip All State Election Data
- Extract all 50 state zip files from election_results_geocoded
- Output: Extracted directories with `bg-2020-RLCR.csv` files per state

### Step 2: Build National CBG Lookup Table
- Read all 50 states' `bg-2020-RLCR.csv` files
- Combine into single lookup table
- Calculate `two_party_rep_share_2020 = Trump / (Trump + Biden)`
- Handle zero-vote CBGs (set to 0.5)
- Output: `/global/scratch/users/maxkagan/project_oakland/inputs/cbg_partisan_lean_national.parquet`

### Step 3: Filter Advan Data by State
- Array job: Process by state groupings
- Filter 2024 Advan data by REGION
- Select relevant columns (same as Ohio + parent_placekey, median_dwell)
- Output: `/global/scratch/users/maxkagan/project_oakland/intermediate/advan_2024_filtered/{STATE}/`

### Step 4: Parse Visitor CBGs and Compute Partisan Lean
- Array job: Process by state groupings
- For each POI-month:
  - Parse visitor_home_cbgs JSON
  - Lookup CBGs in national partisan lean table
  - Calculate weighted average rep_lean
  - Track unmatched CBGs
- Output: State-level parquet files

### Step 5: Combine and Partition by Month
- Combine all state outputs
- Repartition by month
- Output: `/global/scratch/users/maxkagan/project_oakland/outputs/location_partisan_lean/national_2024/2024-{MM}.parquet`

### Step 6: Generate Diagnostic Report
- Unmatched CBG summary (by state, by frequency)
- Data quality metrics

### Step 7: Render National Analysis Report
- Adapt Ohio R Markdown report structure
- Sections: Executive Summary, Descriptive Stats, Brand Analysis, Geographic Patterns, Temporal Trends, Industry Deep-Dives, Measure Validation, Within-Neighborhood Variation
- Output: HTML report

## Compute Resources

| Step | Partition | Rationale |
|------|-----------|-----------|
| Schema verification | savio2 | Quick check |
| Unzip election data | savio2 | I/O bound |
| Build national CBG lookup | savio3 | 50 state files, moderate memory |
| Filter Advan by state | savio3_bigmem | Large files, array job |
| Parse visitor CBGs | savio3_bigmem | Memory-intensive aggregation |
| Combine & partition | savio3_bigmem | Large dataset |
| Render report | savio3 | R needs moderate memory |

## Storage

- **Intermediates**: Keep in scratch for debugging
  - `/global/scratch/users/maxkagan/project_oakland/intermediate/advan_2024_filtered/`
  - `/global/scratch/users/maxkagan/project_oakland/intermediate/election_unzipped/`

- **Final outputs**:
  - `/global/scratch/users/maxkagan/project_oakland/outputs/location_partisan_lean/national_2024/`
  - `/global/scratch/users/maxkagan/project_oakland/outputs/reports/national_2024_analysis.html`

## Success Criteria

1. All 50 states processed without errors
2. POI-month observations generated for all 12 months
3. >95% of visitors matched to CBG lookup (investigate if lower)
4. Report renders successfully with national scope
5. Ohio 2024 subset shows reasonable consistency with Ohio 2023 pilot (spot check in report)

# Singleton Aggregation Plan

**Task**: 1.7 - Aggregate unbranded POIs to name × MSA × month level
**Status**: Pending
**Last updated**: 2026-01-20

---

## Problem Statement

Advan foot traffic data contains ~6.3M POIs. Of these:
- **~1.5M POIs** belong to national brands (matched in Task 1.4)
- **~4.8M POIs** are "singletons" — unbranded local businesses

For national brands, we have a company identifier (brand_name, gvkey, rcid) to aggregate by. For singletons, we need to determine how to group POIs into company-level entities.

### The "Joe's Pizza" Problem

Multiple POIs may share the same name:
- "Joe's Pizza" in Columbus, OH
- "Joe's Pizza" in Cleveland, OH
- "Joe's Pizza" in Brooklyn, NY

Are these the same company? Probably not. But Advan provides no chain ID or parent company field for unbranded POIs.

---

## Approach: Name × MSA Aggregation

We aggregate unbranded POIs by `(poi_name, msa, year_month)`. This assumes:
- All POIs with the same name in the same MSA are the same company
- POIs with the same name in different MSAs are different companies (conservative)

### Why Not Use PAW Directly?

Politics at Work (PAW) could provide company identifiers, but:
1. **Coverage gap**: PAW only includes companies with employees who have voter registration records
2. **Systematic exclusion**: Sole proprietors, family businesses, very small businesses, businesses with unregistered employees
3. **Selection bias**: Missing certain types of businesses could bias our analysis

By using name × MSA, we get full coverage of all Advan POIs without PAW dependency.

---

## Two-Stage Aggregation with Preserved Weights

### Stage 1: POI → Name × MSA × Month (Task 1.7)

```python
# Group by (poi_name, msa, year_month)
# Output preserves total_normalized_visits for later rollup

output_schema = {
    'poi_name': str,           # Business name from Advan
    'msa': str,                # MSA name or CBSA code
    'year_month': str,         # e.g., "2023-06"
    'lean_2020': float,        # Weighted avg Republican lean (2020 election)
    'lean_2016': float,        # Weighted avg Republican lean (2016 election)
    'total_normalized_visits': float,  # SUM of weights — CRITICAL for later rollup
    'n_pois': int,             # Number of POIs contributing
    'top_category': str,       # Mode across POIs
    'naics_code': str,         # Mode across POIs
}
```

### Stage 2 (Optional): Name × MSA → Company (Task 6.3 / Epic 6)

If PAW identifies that "Joe's Pizza" in Columbus and "Joe's Pizza" in Cleveland are the same company (same rcid), we can re-aggregate:

```python
# Correct re-aggregation using preserved weights
company_lean = (
    (columbus_lean × columbus_visits) + (cleveland_lean × cleveland_visits)
) / (columbus_visits + cleveland_visits)
```

This is mathematically equivalent to aggregating directly from POI → company, as long as we preserve `total_normalized_visits` at Stage 1.

---

## Aggregation Formula

Same as national brands (Task 1.5a):

```
entity_lean = Σ(poi_lean_i × normalized_visits_i) / Σ(normalized_visits_i)
```

Where:
- `poi_lean_i` = `rep_lean_2020` or `rep_lean_2016` for POI i
- `normalized_visits_i` = `normalized_visits_by_state_scaling` for POI i

---

## Filters

| Filter | Threshold | Rationale |
|--------|-----------|-----------|
| `pct_visitors_matched` | ≥ 95% | Ensure partisan lean based on sufficient sample (same as Task 1.5a) |
| `brand` column | IS NULL | Only process unbranded POIs (singletons) |
| `normalized_visits` | > 0 | Exclude POIs with no visitor data |

---

## Output Location

```
/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/singleton_name_msa_aggregated/
└── singleton_name_msa_partisan_lean.parquet
```

---

## Expected Output Size

- ~4.8M singleton POIs
- Grouped by name × MSA: estimate 2-4M unique entities
- × 79 months = 150-300M rows (much larger than national brands)
- May need to partition by year or state

---

## Script Location

```
scripts/02_partisan_lean/aggregate_singleton_name_msa.py
```

---

## Relationship to Other Tasks

```
Task 1.1-1.3: POI-level partisan lean (input)
      ↓
Task 1.6: POI → MSA mapping (provides MSA for each POI)
      ↓
Task 1.7: Aggregate to name × MSA × month (THIS TASK)
      ↓
Task 6.3: (Optional) Link to PAW for cross-MSA rollup
      ↓
Task 6.5: Employee-consumer alignment analysis
```

---

## Open Questions

1. **Name normalization**: Should we normalize POI names (lowercase, strip punctuation) before grouping?
2. **Minimum POIs**: Should we require a minimum number of POIs per name × MSA entity?
3. **Partitioning**: Given large output size, partition by year? By state?

---

*See also: `RESEARCH_PLAN.md` Epic 1 Phase 3, Epic 6*

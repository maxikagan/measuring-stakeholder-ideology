# Stakeholder Ideology Dashboard - Design Plan

## Purpose
Interactive exploration tool for visualizing consumer partisan lean across brands, MSAs, and geography.

---

## Proposed Pages/Views

### 1. Overview Dashboard
**Goal**: High-level summary of the entire dataset

**Metrics displayed**:
- Total POIs, unique brands, MSAs covered, time range
- Distribution histogram of partisan lean (2020 and 2016 basis)
- Top categories by POI count

**Questions this answers**:
- What does the overall distribution of consumer ideology look like?
- How much of the data is branded vs unbranded?

---

### 2. Brand Explorer
**Goal**: Explore individual brands and compare them

**Features**:
- Searchable/filterable table of all brands
- Sort by: # locations, mean partisan lean, std deviation, # MSAs
- Click on brand to see detailed view:
  - Distribution of partisan lean across all locations
  - Map of locations colored by partisan lean
  - List of MSAs where brand operates
  - Time series of partisan lean (if meaningful)

**Key metrics per brand**:
| Field | Description |
|-------|-------------|
| `n_locations` | Number of unique POIs |
| `mean_rep_lean_2020` | Average Republican lean (2020 basis) |
| `std_rep_lean_2020` | Standard deviation - how much variation? |
| `median_rep_lean_2020` | Median (robust to outliers) |
| `n_msas` | Number of MSAs brand operates in |
| `n_states` | Geographic spread |

**Questions this answers**:
- Which brands are most Republican? Most Democratic?
- Which brands have the most variation across locations?
- How many markets does each brand serve?

---

### 3. MSA Explorer
**Goal**: Explore partisan lean by metropolitan area

**Features**:
- Searchable table of all MSAs
- Sort by: # POIs, mean partisan lean, within-MSA variation
- Click on MSA to see:
  - Distribution of partisan lean for all POIs in that MSA
  - Breakdown by brand within the MSA
  - Map of POIs within MSA

**Key metrics per MSA**:
| Field | Description |
|-------|-------------|
| `n_pois` | Number of POIs in MSA |
| `mean_rep_lean_2020` | Average across all POIs |
| `std_rep_lean_2020` | Within-MSA variation |
| `n_brands` | Number of unique brands |

**Questions this answers**:
- Which MSAs are most/least Republican?
- How much variation exists within each MSA?

---

### 4. Brand Comparison Tool
**Goal**: Side-by-side comparison of selected brands

**Features**:
- Multi-select brands (up to 10)
- Bar chart comparing mean partisan lean
- Bar chart comparing within-brand variation (std dev)
- Table with all metrics
- Optional: Scatter plot (x = national mean, y = variation)

**Questions this answers**:
- How does Starbucks compare to Dunkin?
- Which coffee chains have the most liberal/conservative customers?

---

### 5. Geographic Map View
**Goal**: Visualize partisan lean spatially

**Map types**:

#### a) National POI Map
- Scatter plot of all POIs, colored by partisan lean
- Red = Republican, Blue = Democratic
- Filter by brand, category, or MSA
- Zoom/pan interactivity

#### b) Choropleth Maps
- State-level average partisan lean
- MSA-level average partisan lean
- Option to show by brand

#### c) Brand-Specific Map
- Select a brand, see all locations on map
- Color intensity = partisan lean
- Hover for details (city, exact lean, visitor count)

**Questions this answers**:
- Where are the most Republican/Democratic consumers?
- How does Walmart's customer base vary geographically?
- Are there regional patterns?

---

### 6. Variance Decomposition View
**Goal**: Understand sources of variation

**Analyses**:
- Between-brand vs within-brand variance
- Between-MSA vs within-MSA variance (for same brand)
- ICC (Intraclass Correlation) - what % of variance is explained by geography vs brand?

**Visualization**:
- Stacked bar chart showing variance components
- Table with ICC for major brands
- Interpretation guide

**Questions this answers**:
- Is partisan lean driven more by brand or location?
- Do brands attract similar customers everywhere, or does geography dominate?

---

### 7. Time Series View (Optional)
**Goal**: Track changes over time

**Features**:
- Select brand(s) or MSA(s)
- Line chart of partisan lean over time (2019-2024)
- Highlight key events (elections, COVID, etc.)

**Note**: Partisan lean is based on 2020 election data, so changes over time reflect visitor composition shifts, not election result changes.

---

## Data Fields Available

From our partisan lean output:

| Field | Type | Use in Dashboard |
|-------|------|------------------|
| `brand` | string | Primary grouping variable |
| `placekey` | string | Unique POI identifier |
| `city` | string | Location detail |
| `region` | string | State (for state-level analysis) |
| `cbsa_title` | string | MSA name (for MSA analysis) |
| `top_category` | string | Industry category |
| `sub_category` | string | Detailed category |
| `naics_code` | string | NAICS code |
| `rep_lean_2020` | float | **Primary measure** - Republican lean (2020) |
| `rep_lean_2016` | float | **Secondary measure** - Republican lean (2016) |
| `total_visitors` | int | Weighting for aggregations |
| `pct_visitors_matched` | float | Data quality indicator |
| `year_month` | string | Time dimension |

**Missing but could add**:
- `latitude`, `longitude` - needed for maps (can derive from placekey)
- `poi_cbg` - CBG where POI is located (have this)

---

## Visual Design Preferences

**Questions for you**:

1. **Color scheme**:
   - Political colors (Red/Blue gradient)?
   - Neutral colors?
   - Custom palette?

2. **Layout**:
   - Sidebar navigation (like current draft)?
   - Top navigation tabs?
   - Single scrolling page?

3. **Interactivity priority**:
   - Which views are most important?
   - What questions do you want to answer first?

4. **Data scope**:
   - Show all 79 months, or default to recent?
   - Pre-compute summaries for speed, or always compute live?

5. **Map style**:
   - Light/dark base map?
   - Focus on national view or MSA-level zoom?

---

## Technical Notes

**Data size considerations**:
- Full dataset: 29GB, 596M rows
- Per month: ~7.5M rows
- For responsive UI, will need to:
  - Pre-compute brand/MSA summaries
  - Sample data for map views
  - Use caching aggressively

**Coordinates**:
- Current data lacks lat/lon
- Can derive from placekey using `placekey` Python library
- Should pre-compute and add to dataset

---

## Priority Ranking (Suggested)

| Priority | View | Rationale |
|----------|------|-----------|
| 1 | Brand Explorer | Core use case - which brands are partisan? |
| 2 | Brand Comparison | Direct comparison answers key questions |
| 3 | Geographic Map | Visual appeal, validates methodology |
| 4 | MSA Explorer | Secondary grouping, useful for within-market analysis |
| 5 | Variance Decomposition | Academic analysis, important but less exploratory |
| 6 | Overview | Context, but less actionable |
| 7 | Time Series | Lower priority unless temporal dynamics matter |

---

## Next Steps

1. **Review this plan** - What would you add/remove/change?
2. **Decide on coordinate extraction** - Do we want maps? If so, need to add lat/lon
3. **Build MVP** - Start with Brand Explorer + Comparison
4. **Iterate** - Add features based on what's useful

What aspects would you like to prioritize or modify?

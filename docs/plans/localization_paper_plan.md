# Localization and Store Performance: A Strategy Paper

## Core Research Question

**Do stores that better match their employee composition to local customer preferences perform better?**

This is fundamentally a question about multi-unit strategy and organizational adaptation. Firms operating across diverse geographic markets face a localization challenge: should they impose a uniform organizational culture, or adapt to local conditions?

---

## Theoretical Framing

### The Localization Trade-off
- **Standardization benefits**: Consistent brand experience, economies of scale in training/HR, strong organizational culture
- **Localization benefits**: Better customer-employee fit, local trust, cultural resonance

### Why Employee-Customer Match Might Matter
1. **Service interaction quality**: Employees who share customers' values may provide more authentic, comfortable interactions
2. **Trust and in-group dynamics**: Customers may prefer transacting with ideologically similar employees
3. **Word-of-mouth and community embeddedness**: Locally-matched employees are embedded in local networks
4. **Employee motivation**: Employees serving customers they identify with may be more engaged

### Boundary Conditions
- Effect should be stronger for:
  - High-touch service industries (restaurants, retail) vs. low-touch (gas stations)
  - Locally-rooted brands vs. national chains
  - Politically salient categories (e.g., outdoor/gun retailers, organic grocers)

---

## Causal Structure

```
                    ┌─────────────────────────┐
                    │   Local Labor Market    │
                    │      Ideology           │
                    └───────────┬─────────────┘
                                │ (instrument)
                                ▼
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  HQ / Company   │───▶│  Store Employee     │───▶│ Store Performance│
│   Ideology      │    │     Ideology        │    │  (Foot Traffic)  │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
                                │                          ▲
                                │                          │
                                ▼                          │
                    ┌─────────────────────────┐            │
                    │  Employee-Customer      │────────────┘
                    │  Ideological Alignment  │
                    └─────────────────────────┘
                                ▲
                                │
                    ┌─────────────────────────┐
                    │   Local Customer        │
                    │      Ideology           │
                    │  (from neighborhood)    │
                    └─────────────────────────┘
```

### Key Variables

| Role | Variable | Measurement | Source |
|------|----------|-------------|--------|
| **DV** | Store performance | Monthly foot traffic; spending per visit | Advan Monthly Patterns; SafeGraph Spend |
| **Key IV** | Employee-customer alignment | Absolute distance between employee and customer ideology at store level | Computed (see below) |
| **Instrument** | Local labor market ideology | MSA-level or zip-level worker ideology | Politics at Work aggregated |
| **Instrument** | HQ ideology | Employee ideology at HQ location | Politics at Work |
| **Control** | Local customer ideology | Visitor home CBG partisan lean | Advan + Election data |
| **Control** | Store characteristics | Category, chain, age, size | Advan POI data |
| **Control** | Local market characteristics | Population, income, competition density | Census, Advan |

---

## Empirical Strategy

### Baseline Specification

```
Performance_ijt = β₁(Alignment_ijt) + β₂(X_ijt) + α_i + γ_t + μ_j + ε_ijt
```

Where:
- `i` = store
- `j` = firm/brand
- `t` = month
- `α_i` = store fixed effects
- `γ_t` = time fixed effects
- `μ_j` = firm fixed effects
- `X` = controls

### Identification Concerns

| Concern | Problem | Solution |
|---------|---------|----------|
| **Reverse causality** | Successful stores attract certain customers/employees | Use lagged alignment; instrument with pre-period labor market ideology |
| **Omitted variables** | Good managers do everything well | Firm fixed effects; within-firm variation |
| **Selection into locations** | Firms choose where to open stores | Focus on within-store variation over time; new store openings |
| **Measurement error** | Ideology measures are noisy | Multiple measures; sensitivity analysis |

### Instrumental Variables Approach

**First stage**: Local labor market ideology → Store employee ideology
- Firms hire from local labor markets
- They can't perfectly screen for ideology
- Local labor market composition is exogenous to individual store performance

**Exclusion restriction**: Local labor market ideology affects store performance *only* through employee composition, not directly
- Plausible if we control for local customer ideology separately
- Customer base is measured directly from visitor patterns, not assumed from location

### Alternative: New Store Openings

Natural experiment setup:
1. Identify new store openings
2. Measure pre-opening neighborhood ideology (customers) from Neighborhood Patterns
3. Measure initial employee cohort ideology
4. Track performance trajectory
5. Compare stores with good vs. poor initial match

---

## Data Requirements

### Already Have
- [ ] Advan Monthly Patterns (foot traffic, visitor home CBGs) ✓
- [ ] CBG-level election results (2016, 2020) ✓
- [ ] Politics at Work (employee ideology by employer × MSA) ✓

### Need to Construct
- [ ] Store-level customer ideology (aggregate visitor CBGs → partisan lean)
- [ ] Store-level employee ideology (link POIs to employers in Politics at Work)
- [ ] Alignment measure (distance between employee and customer ideology)
- [ ] MSA-level labor market ideology (for instrument)
- [ ] HQ location identification for chains

### Entity Resolution Challenge
Critical step: Link Advan POIs (stores) to Politics at Work employers
- Use brand names, addresses, parent companies
- May need fuzzy matching or manual verification for major chains
- Start with large national chains where match is clearer

---

## Analysis Plan

### Phase 1: Measurement & Validation
1. Construct store-level customer ideology from Advan + election data
2. Link stores to employers in Politics at Work
3. Construct store-level employee ideology
4. Compute alignment measures
5. Validate: Do measures behave sensibly? (e.g., Whole Foods vs. Cracker Barrel)

### Phase 2: Descriptive Analysis
1. How much within-firm variation exists in employee ideology across locations?
2. How much within-firm variation exists in customer ideology?
3. What predicts alignment? (firm size, industry, HQ location, franchising)
4. Maps and visualizations

### Phase 3: Main Analysis
1. Baseline OLS: Alignment → Performance
2. Add fixed effects progressively
3. IV specification with labor market instrument
4. Robustness checks

### Phase 4: Heterogeneity & Mechanisms
1. By industry (high-touch vs. low-touch service)
2. By brand positioning (local vs. national)
3. By political salience of category
4. Franchise vs. corporate-owned

### Phase 5: Extensions
1. New store openings analysis
2. Does alignment affect which customers come? (composition vs. volume)
3. Does alignment affect employee turnover?

---

## Open Questions

1. **Unit of analysis**: Store-month? Store-quarter? Need sufficient variation.

2. **Which alignment measure?**
   - Absolute distance: |Employee ideology - Customer ideology|
   - Match to local market: Does employee match the local customer base better than HQ average would?
   - Directional: Does liberal employee + liberal customer differ from conservative + conservative?

3. **Employee level**:
   - Politics at Work gives employer × MSA
   - Can we get store-level? Or assume MSA-level = store-level for chains in that MSA?

4. **Spending data**:
   - SafeGraph Spend would strengthen the DV
   - Need to check data access

5. **Time horizon**:
   - When does alignment "pay off"? Immediately or over time?
   - New store openings allow cleaner trajectory analysis

---

## Contribution

1. **Novel measurement**: First paper to measure employee-customer ideological alignment at the store level using revealed preference data

2. **Within-firm strategy**: Moves beyond firm-level analysis to understand geographic adaptation

3. **Performance DV**: Unlike political economy papers, this is about business outcomes

4. **Causal identification**: IV strategy using labor market composition provides traction on causality

---

## Target Outlets

- **Strategic Management Journal** (multi-unit strategy, organizational adaptation)
- **Management Science** (empirical rigor, novel data)
- **Organization Science** (if we emphasize employee-organization fit angle)

---

## Timeline (Rough)

| Phase | Tasks |
|-------|-------|
| **1** | Entity resolution; construct measures |
| **2** | Descriptive statistics; validate measures |
| **3** | Main analysis; IV specifications |
| **4** | Heterogeneity; robustness |
| **5** | Write up; circulate |

---

## Notes

- This reframes the project from "political" to "strategy" — the ideology is just a measurable dimension of employee-customer fit
- The same framework could apply to other dimensions (age, education, lifestyle) if we had data
- Ideology is salient and measurable, making it a good test case for the broader localization question

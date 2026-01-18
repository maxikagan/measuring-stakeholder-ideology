# Corporate Activism Events Dataset: Methodology Plan

## Overview

This document outlines a methodology for creating a comprehensive dataset of corporate activism events from 2019-2025, combining approaches from two leading papers:

1. **Mkrtchyan, Sandvik, & Zhu (2024)** - "CEO Activism and Firm Value" (Management Science)
2. **Conway & Boxell (2024)** - "Consuming Values" (SSRN)

**Primary research question:** When firms take political stances, is it driven more by employee composition or customer composition?

**Use case:** Activism events as a **dependent variable** - predicting which firms speak out based on employee and customer ideology measures.

---

## Scope Decisions

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| **Firm universe** | 1000+ brands from Advan data | Ensures linkage to foot traffic outcomes |
| **Time period** | 2019-2025 | Extends existing datasets, captures recent events |
| **Attribution level** | Firm-level | CEO-specific attribution not required for DV use case |
| **Event detail** | Topic + ideology coding | Full Mkrtchyan coding (vividness, action level) not needed |
| **Ideology coverage** | Both liberal AND conservative | Explicitly capture right-leaning stances |
| **Explicit neutrality** | Yes - as separate category | Firms explicitly stating "we won't take a stance" |
| **Timeline** | Flexible (quality over speed) | ~4-5 weeks estimated |
| **Budget** | $200-500 | GDELT is free; LLM costs moderate |

---

## Source Methodology Comparison

| Dimension | Mkrtchyan et al. | Conway & Boxell |
|-----------|-----------------|-----------------|
| **Goal** | Comprehensive CEO activism | High-salience consumer events |
| **Sample** | S&P 500 CEOs | Top 10,000 US firms by revenue |
| **Events found** | 1,402 | 117 |
| **Time period** | 2010-2019 | 2010-2022 |
| **Identification** | Keyword scraping (News + Twitter) | Multi-method triangulation |
| **Filtering** | RA manual coding (1-5 scale) | Manual verification + awareness measurement |
| **Coding** | Ideology, action, vividness, relatedness | Topic, ideology, consumer awareness |

### What We Take From Each

**From Mkrtchyan et al.:**
- Comprehensive keyword-based identification
- Ideology coding approach

**From Conway & Boxell:**
- Multi-method triangulation (Google Trends + news + LLM)
- Salience measurement via search/news spikes
- LLM-assisted event generation

---

## Step 1: Firm List

**Source:** Extract unique brand names from Advan monthly patterns data

**Process:**
1. Pull distinct `brands` or `location_name` values from Advan
2. Standardize names (remove Inc., LLC, etc.)
3. Filter to brands with sufficient foot traffic volume
4. Target: 1000+ brands

**Why Advan-based:** Ensures every firm in the activism dataset can be linked to customer ideology (via visitor_home_cbgs) and foot traffic outcomes.

---

## Step 2: Keyword List

### Liberal-Leaning Topics

| Category | Keywords |
|----------|----------|
| **LGBT/Trans** | gay, gay marriage, homosexual, lesbian, LGBT, same-sex, transgender, trans rights, gender-affirming, queer, lgbtq, lgbtq+, lgbtqia, bathroom bill, drag, pronoun |
| **Racial Justice** | BLM, Black Lives Matter, George Floyd, Juneteenth, systemic racism, police, defund, racial, discrimination, inclusion |
| **Environment** | climate change, global warming, carbon tax, Paris accord, renewable, clean energy, environment, pollution, ESG |
| **Immigration (pro)** | dreamers, daca, refugee, immigration rights, #keepfamiliestogether |
| **Reproductive (pro-choice)** | reproductive rights, abortion access, pro-choice, Roe |
| **DEI** | DEI, diversity equity inclusion, diversity initiative |

### Conservative-Leaning Topics

| Category | Keywords |
|----------|----------|
| **Trump/MAGA** | Trump, MAGA, Trump endorsement, Mar-a-Lago |
| **Anti-DEI** | anti-woke, woke, anti-DEI, DEI rollback, meritocracy |
| **Anti-ESG** | anti-ESG, ESG backlash |
| **Immigration (restrictionist)** | border security, illegal immigration, travel ban |
| **Reproductive (pro-life)** | pro-life, abortion ban |
| **Trade/Tariffs** | tariffs, trade war, protectionism, Buy American |
| **Second Amendment** | gun rights, second amendment, NRA |

### Neutral/Contested Topics

| Category | Keywords |
|----------|----------|
| **Israel/Gaza** | Israel, Gaza, Hamas, ceasefire, antisemitism |
| **COVID** | vaccine, vaccine mandate, mask, mask mandate, pandemic, lockdown, remote work |
| **AI Ethics** | AI ethics, artificial intelligence, responsible AI, AI safety |
| **Explicit Neutrality** | not taking a stance, staying neutral, won't comment, staying out of, no political position |

### From Original Papers (Retained)

| Category | Keywords |
|----------|----------|
| **Politics (general)** | Democrat, Republican, political, voting, controversy, boycott, buycott |
| **Other Social** | equal pay, pay gap, healthcare, human rights, indigenous people, poverty, gun control |

---

## Step 3: Event Identification Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. GET FIRM LIST FROM ADVAN                                     │
│    - Extract unique brand names from Advan data                 │
│    - Clean/standardize names                                    │
│    - ~1000+ firms                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. LLM-GENERATED CANDIDATE EVENTS                               │
│    - Query Claude/GPT-4 for known activism events               │
│    - Cover all topics (liberal + conservative + neutral)        │
│    - Explicitly ask for conservative-leaning events             │
│    - ~200-500 high-confidence events                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. GDELT NEWS SCRAPING (BigQuery)                               │
│    - Query firm names + keywords                                │
│    - Identify news spikes (28-day forward vs. backward MA)      │
│    - Additional candidates beyond LLM recall                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. GOOGLE TRENDS VALIDATION                                     │
│    - Confirm candidate events show search interest spikes       │
│    - Measure salience                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. LLM CODING                                                   │
│    - Is this activism? (binary filter)                          │
│    - Topic category                                             │
│    - Ideology (Liberal / Neutral / Conservative)                │
│    - Is this explicit neutrality? (firm saying "no stance")     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. MANUAL SPOT-CHECK                                            │
│    - Review ~100 events for accuracy                            │
│    - Fix any systematic errors                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. MERGE WITH EMPLOYEE/CUSTOMER IDEOLOGY                        │
│    - Join to PAW data (employee ideology by firm)               │
│    - Join to Advan + CBG voting (customer ideology by brand)    │
│    - Ready for analysis                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 4: Method Details

### Method A: LLM-Generated Candidate Events

**Prompts:**

```
PROMPT 1 (Liberal stances):
"List 50 of the most notable events in which U.S. companies took
LIBERAL-LEANING stances on social/political issues between
January 2019 and December 2025.

Include: LGBT/trans rights, BLM/racial justice, climate/environment,
pro-immigration, reproductive rights, DEI initiatives.

For each event, provide:
- company: company name
- date: start date (MM/DD/YY)
- topic: main topic category
- description: brief (2-6 word) description

Order by notability. Output as CSV."

PROMPT 2 (Conservative stances):
"List 50 of the most notable events in which U.S. companies took
CONSERVATIVE-LEANING stances on social/political issues between
January 2019 and December 2025.

Include: Trump endorsements/support, anti-DEI/anti-woke rollbacks,
anti-ESG statements, restrictionist immigration stances, pro-life
positions, tariff/protectionism support, Second Amendment support.

For each event, provide:
- company: company name
- date: start date (MM/DD/YY)
- topic: main topic category
- description: brief (2-6 word) description

Order by notability. Output as CSV."

PROMPT 3 (Explicit neutrality):
"List 30 notable instances where U.S. companies EXPLICITLY STATED
they would not take a political stance or were 'staying neutral'
on controversial issues between 2019-2025.

This must be an EXPLICIT statement (e.g., 'we don't take political
positions', 'we're staying out of this debate'), NOT simply the
absence of a statement.

For each, provide:
- company: company name
- date: date of neutrality statement (MM/DD/YY)
- context: what issue they declined to take a stance on
- description: brief description

Output as CSV."

PROMPT 4 (Contested topics):
"List 30 notable corporate stances on Israel/Gaza, COVID policies,
or AI ethics between 2019-2025. Include stances from both political
perspectives. Same format as above."
```

**Run multiple prompts to ensure coverage across ideological spectrum.**

---

### Method B: GDELT + BigQuery

**Why GDELT:** Free, comprehensive news archive accessible via BigQuery.

**Query approach:**

```sql
-- Example GDELT query for firm + keyword mentions
SELECT
  DATE(TIMESTAMP_SECONDS(DATEADDED)) as date,
  SourceCommonName as source,
  DocumentIdentifier as url,
  V2Themes,
  V2Tone
FROM `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE
  DATE(_PARTITIONTIME) BETWEEN '2019-01-01' AND '2025-12-31'
  AND (
    REGEXP_CONTAINS(LOWER(V2Themes), r'company_name')
    AND REGEXP_CONTAINS(LOWER(V2Themes), r'keyword')
  )
```

**Process:**
1. Query GDELT for each firm × keyword combination
2. Count articles per firm-day
3. Calculate spike index (28-day forward vs. backward moving average)
4. Flag firm-dates with largest spikes as candidates

---

### Method C: Google Trends Validation

**Purpose:** Confirm candidate events and measure salience

```python
from pytrends.request import TrendReq

def validate_event_salience(firm, date, keyword):
    pytrends = TrendReq()

    # Get daily data around event date
    start = date - timedelta(days=135)
    end = date + timedelta(days=135)

    pytrends.build_payload(
        [f"{firm} {keyword}"],
        timeframe=f'{start.strftime("%Y-%m-%d")} {end.strftime("%Y-%m-%d")}'
    )
    data = pytrends.interest_over_time()

    # Calculate spike magnitude
    pre_event = data.loc[:date-timedelta(days=1)].mean()
    post_event = data.loc[date:date+timedelta(days=28)].max()

    return {
        'salience': post_event - pre_event,
        'peak_value': post_event
    }
```

---

## Step 5: LLM Coding

### Simplified Coding Schema

For DV use case, we only need:

| Field | Values | Description |
|-------|--------|-------------|
| `is_activism` | TRUE/FALSE | Is this actually a corporate stance? |
| `topic` | See list below | Primary topic category |
| `ideology` | L / N / C | Liberal, Neutral, or Conservative |
| `is_explicit_neutrality` | TRUE/FALSE | Firm explicitly saying "we won't take a stance" |

**Topic categories:**
- `lgbt` - LGBT/trans rights
- `racial_justice` - BLM, racial discrimination
- `environment` - Climate, ESG
- `immigration` - Pro or anti
- `abortion` - Reproductive rights
- `dei` - DEI initiatives or anti-DEI
- `trump` - Trump endorsements/opposition
- `tariffs` - Trade policy
- `guns` - Gun control or rights
- `israel_gaza` - Middle East
- `covid` - Pandemic policies
- `ai` - AI ethics
- `other` - Other topics

### Coding Prompt

```
You are coding corporate activism events for academic research.

For the following news headline/article about a company, determine:

1. IS_ACTIVISM: Is this an actual corporate political/social stance?
   - TRUE if the company or its leadership took a public position
   - FALSE if this is a false positive (e.g., shooting at store,
     executive scandal unrelated to company stance)

2. TOPIC: What is the primary topic? Choose from:
   lgbt, racial_justice, environment, immigration, abortion, dei,
   trump, tariffs, guns, israel_gaza, covid, ai, other

3. IDEOLOGY: What is the ideological direction?
   - L = Liberal-leaning
   - N = Neutral or unclear
   - C = Conservative-leaning

4. IS_EXPLICIT_NEUTRALITY: Is this a company EXPLICITLY stating
   they will not take a political position?
   - TRUE only if company explicitly says "we're not taking a stance"
     or similar
   - FALSE for actual stances OR for companies that simply didn't speak

---
HEADLINE/ARTICLE:
{content}

COMPANY: {company_name}
DATE: {date}

Respond in JSON:
{
  "is_activism": true/false,
  "topic": "<category>",
  "ideology": "L"/"N"/"C",
  "is_explicit_neutrality": true/false,
  "reasoning": "<brief explanation>"
}
```

---

## Step 6: Output Schema

| Field | Description |
|-------|-------------|
| `brand_name` | Standardized brand name (from Advan) |
| `event_date` | Date of stance |
| `topic` | Topic category |
| `ideology` | L / N / C |
| `is_explicit_neutrality` | TRUE if firm explicitly declined to take stance |
| `salience_google` | Google Trends spike magnitude |
| `salience_news` | News article count (from GDELT) |
| `source_url` | Link to source article |
| `description` | Brief description of stance |

**Expected output:** 500-2,000 events for 2019-2025

---

## Step 7: Validation

### Manual Spot-Check Protocol

1. Randomly sample 100 coded events
2. Review each for accuracy on:
   - Is this actually activism? (not false positive)
   - Is the topic correct?
   - Is the ideology coding correct?
3. Calculate accuracy rates
4. If <90% accuracy, refine LLM prompts and re-code
5. Document any systematic errors

---

## Timeline & Costs

| Phase | Tasks | Time | Cost |
|-------|-------|------|------|
| Firm list extraction | Pull brands from Advan | 1 day | $0 |
| LLM candidate generation | Run prompts for all topics | 2-3 days | $20-50 |
| GDELT BigQuery setup | Configure queries | 1-2 days | $0 |
| GDELT scraping | Run queries for all firms | 1 week | $0 (free tier) |
| Google Trends validation | Validate candidates | 1 week | $0 |
| LLM coding | Code all candidates | 1 week | $50-100 |
| Manual spot-check | Review ~100 events | 2-3 days | $0 |
| Merge with ideology | Join to PAW + Advan | 1 day | $0 |

**Total: ~4-5 weeks, ~$100-200**

---

## Integration with Project Oakland

Once complete, merge activism dataset with:

1. **Employee ideology** (Politics at Work)
   - Aggregate to firm level
   - Measure: mean/median employee partisan lean

2. **Customer ideology** (Advan + CBG voting)
   - Weight visitor_home_cbgs by visit share
   - Merge with CBG-level 2020 election results
   - Measure: visitor-weighted partisan lean

**Analysis:**
```
Activism_i = β₁(Employee_Ideology_i) + β₂(Customer_Ideology_i) + Controls + ε
```

Test: Is β₁ > β₂ (employees matter more) or β₂ > β₁ (customers matter more)?

---

## References

- Mkrtchyan, A., Sandvik, J., & Zhu, V. Z. (2024). CEO Activism and Firm Value. *Management Science*, 70(10), 6519-6549.
- Conway, J., & Boxell, L. (2024). Consuming Values. *SSRN Working Paper*.

---

## Appendix: Full Keyword List (Consolidated)

### All Keywords by Category

**LGBT/Trans:** gay, gay marriage, homosexual, lesbian, LGBT, same-sex, transgender, trans rights, gender-affirming, queer, lgbtq, lgbtq+, lgbtqia, bathroom bill, drag, pronoun

**Racial Justice:** BLM, Black Lives Matter, George Floyd, Juneteenth, systemic racism, police, defund, racial, discrimination, inclusion, Nazi, white supremacists

**Environment:** climate change, global warming, carbon tax, Paris accord, renewable, clean energy, environment, pollution, clean air, clean water, land conservation

**Immigration:** immigration, dreamers, daca, refugee, #keepfamiliestogether, border security, illegal immigration, travel ban

**Abortion:** abortion, reproductive rights, Roe, Dobbs, abortion access, abortion ban, pro-choice, pro-life

**DEI/Anti-DEI:** DEI, diversity equity inclusion, diversity initiative, anti-woke, woke, anti-DEI, DEI rollback, meritocracy

**ESG/Anti-ESG:** ESG, anti-ESG, ESG backlash, sustainable investing

**Trump/Politics:** Trump, MAGA, Trump endorsement, Mar-a-Lago, Democrat, Republican, Clinton, Obama, Biden, Capitol, insurrection, January 6, election integrity, election fraud

**Trade/Tariffs:** tariffs, trade war, protectionism, Buy American

**Guns:** gun, gun control, guns, second amendment, gun rights, NRA

**Israel/Gaza:** Israel, Gaza, Hamas, ceasefire, antisemitism

**COVID:** vaccine, vaccine mandate, mask, mask mandate, pandemic, lockdown, remote work

**AI Ethics:** AI ethics, artificial intelligence, responsible AI, AI safety

**Explicit Neutrality:** not taking a stance, staying neutral, won't comment, staying out of, no political position, apolitical

**Other:** equal pay, pay gap, healthcare, human rights, indigenous people, poverty, controversy, boycott, buycott, social issue

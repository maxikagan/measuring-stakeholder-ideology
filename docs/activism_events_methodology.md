# Corporate Activism Events Dataset: Methodology Plan

## Overview

This document outlines a methodology for creating a comprehensive dataset of corporate activism events from 2019-2025, combining approaches from two leading papers:

1. **Mkrtchyan, Sandvik, & Zhu (2024)** - "CEO Activism and Firm Value" (Management Science)
2. **Conway & Boxell (2024)** - "Consuming Values" (SSRN)

The goal is to identify when firms or their CEOs take public stances on social/political issues, code these events, and measure their salience.

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

### Combined Approach: Best of Both Worlds

**From Mkrtchyan et al.:**
- Comprehensive keyword-based scraping
- Detailed event coding (ideology, action level, vividness)
- CEO-level attribution

**From Conway & Boxell:**
- Multi-method triangulation (reduces false negatives)
- Salience filtering via Google Trends + news spikes
- GPT-4 assisted event identification
- Consumer awareness measurement

---

## Step 1: Merged Keyword List

### Mkrtchyan et al. Keywords (50 keywords)

| Category | Keywords |
|----------|----------|
| **Diversity** | discrimination, ethnicity, glass ceiling, harassment, inclusion, racial, religion, gay marriage, homosexual, lesbian, LGBT, same-sex |
| **Environment** | clean air, clean water, environment, pollution, renewable, carbon tax, climate change, global warming, land conservation, Paris accord |
| **Politics** | debt ceiling, Democrat, fiscal cliff, government shutdown, Republican, tariffs, taxes, Brexit, Clinton, Obama, travel ban, Trump |
| **Other** | abortion, dreamers, equal pay, gun, healthcare, human rights, immigration, indigenous people, Nazi, Obamacare, pay gap, poverty, prison, refugee, violence, war, white supremacists, #keepfamiliestogether |

### Conway & Boxell Keywords

| Source | Keywords |
|--------|----------|
| **Google Trends** | gay, transgender, immigration, political contributions, political, voting, controversy, buycott, boycott, gun control, abortion |
| **ProQuest (additional)** | racial, social issue, lesbian, queer, lgbtq, lgbtq+, lgbtqia, daca, guns, second amendment, reproductive rights |

### New Keywords for 2019-2025

| Category | New Keywords |
|----------|-------------|
| **Racial Justice (2020)** | BLM, Black Lives Matter, George Floyd, Juneteenth, systemic racism, police, defund |
| **COVID (2020-2022)** | vaccine, vaccine mandate, mask, mask mandate, pandemic, lockdown, remote work |
| **Democracy (2021+)** | Capitol, insurrection, January 6, election integrity, election fraud, Stop the Steal |
| **Abortion (2022+)** | Roe, Dobbs, reproductive rights, abortion access, abortion ban, pro-choice, pro-life |
| **Trans Rights (2022+)** | transgender, trans rights, gender-affirming, bathroom bill, drag, pronoun |
| **DEI/Anti-DEI (2023+)** | DEI, diversity equity inclusion, anti-woke, woke, ESG, anti-ESG |
| **Geopolitics** | Ukraine, Russia, Israel, Gaza, Hamas, ceasefire |
| **AI (2023+)** | AI ethics, artificial intelligence, responsible AI, AI safety |
| **Specific events** | Bud Light, Dylan Mulvaney, Target Pride, Disney, Ron DeSantis |

---

## Step 2: Multi-Source Event Identification Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVENT IDENTIFICATION SOURCES                          │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
     │   METHOD 1   │    │   METHOD 2   │    │   METHOD 3   │    │   METHOD 4   │
     │Google Trends │    │News Scraping │    │Twitter/X     │    │  LLM Query   │
     │  (Conway)    │    │(Both papers) │    │(Mkrtchyan)   │    │  (Conway)    │
     └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
            │                   │                   │                   │
            ▼                   ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CANDIDATE EVENT POOL                                 │
│                    (Union of all methods - high recall)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM-ASSISTED FILTERING                               │
│           "Is this actually a corporate social/political stance?"            │
│                        (Replaces RA manual coding)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LLM-ASSISTED CODING                                │
│  • Ideology (liberal/neutral/conservative)                                   │
│  • Action level (statement only / low-moderate / high cashflow)              │
│  • Vividness (1-3)                                                           │
│  • Business relatedness (1-3)                                                │
│  • Topic category                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SALIENCE MEASUREMENT                                 │
│  • Google Trends spike magnitude                                             │
│  • News article count                                                        │
│  • (Optional) BrandIndex if available                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FINAL EVENT DATASET                                 │
│            Firm × Date × Topic × Ideology × Salience × Coding                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 3: Detailed Implementation

### Method 1: Google Trends Identification (Conway approach)

**Input:** Firm list × Keyword list × Date range (2019-2025)

**Procedure:**
1. Get firm list (S&P 500 + top brands from Advan data)
2. Query `pytrends` for each firm × keyword combination
3. Calculate spike index (28-day forward vs. backward moving average)
4. Flag firm-dates with largest spikes as candidates

**Technical notes:**
- `pytrends` has rate limits; need to throttle queries
- Monthly pulls first, then daily for candidate months
- Normalize using rolling window z-scores (6, 12, 24 months)

```python
# Pseudocode
from pytrends.request import TrendReq

def get_trends_candidates(firms, keywords, start_date, end_date):
    pytrends = TrendReq()
    candidates = []

    for firm in firms:
        for keyword in keywords:
            query = f"{firm} {keyword}"
            pytrends.build_payload([query], timeframe=f'{start_date} {end_date}')
            data = pytrends.interest_over_time()

            # Calculate spike index
            data['forward_ma'] = data[query].rolling(28).mean().shift(-28)
            data['backward_ma'] = data[query].rolling(28).mean()
            data['spike'] = data['forward_ma'] - data['backward_ma']

            # Flag large spikes
            threshold = data['spike'].quantile(0.99)
            spikes = data[data['spike'] > threshold]
            candidates.extend([(firm, date, keyword) for date in spikes.index])

    return candidates
```

---

### Method 2: News Scraping (Both papers)

**Option A: ProQuest/LexisNexis (if academic access)**
- Query: Firm as subject + social keywords in text
- Count articles per firm-day
- Flag dates with largest spikes

**Option B: Google News (Mkrtchyan approach)**
- Query: CEO name + firm name + keyword
- Use `googlenews` or `newspaper3k` Python packages
- Extract headlines, dates, URLs

**Option C: NewsAPI or GDELT (alternative)**
- NewsAPI: 500 requests/day free tier, $449/mo for unlimited
- GDELT: Free, comprehensive, but requires BigQuery

**Query templates (from Mkrtchyan):**
```
<"CEO first name" AND "CEO last name" AND keyword>
<"CEO first name" AND "CEO last name" AND "firm name" AND keyword>
<"firm name" AND CEO AND keyword>
<"firm name" AND chief AND keyword>
```

---

### Method 3: Twitter/X Extraction

**Challenge:** Musk restricted free API access in 2023

**Options:**

| Option | Cost | Coverage | Feasibility |
|--------|------|----------|-------------|
| X API Basic | $100/mo | 10K tweets/mo | Low volume |
| X API Pro | $5,000/mo | 1M tweets/mo | Expensive |
| Internet Archive | Free | Historical only (pre-2023) | Partial |
| Scrape news about tweets | Free | Indirect | Reasonable |
| Skip Twitter entirely | Free | - | Fallback |

**Recommendation:** Focus on news coverage of CEO tweets rather than direct Twitter scraping. Most newsworthy tweets get media coverage anyway.

---

### Method 4: LLM-Assisted Event Generation (Conway approach, extended)

**Prompts for 2019-2025:**

```
PROMPT 1 (Initial):
"List 50 of the most notable and widely covered events in which
individual companies took partisan stances on controversial
social/political issues in the U.S. between January 2019 and
December 2025, inclusive.

Include events related to: BLM/racial justice, COVID policies,
January 6, Dobbs/abortion, trans rights, DEI initiatives,
ESG controversies, and any other partisan corporate stances.

For each event, provide:
- company: company name
- date: start date (MM/DD/YY)
- ideology: liberal, conservative, or neutral
- topic: main topic category
- description: brief (2-6 word) description

Order by notability (descending). Output as CSV."

PROMPT 2 (Extension):
"Extend this list with 50 more events. Avoid duplicates.
Focus on events that received significant media coverage
or consumer backlash."

PROMPT 3 (Specific topics):
"List 30 notable corporate stances specifically related to
[TOPIC: e.g., "trans rights and bathroom bills"] between
2019-2025. Same format as above."
```

**Run this for each major topic area to ensure coverage.**

---

## Step 4: LLM-Assisted Coding (Replacing RAs)

### Coding Prompt Template

```
You are coding corporate activism events for academic research.

For the following news article/tweet about a corporate stance,
provide ratings on these dimensions:

1. IS_ACTIVISM (1-5): Is this actually a corporate political/social
   stance, or a false positive?
   1 = Definitely not activism
   5 = Definitely activism

2. IDEOLOGY (L/N/C): Is the stance liberal-leaning, neutral, or
   conservative-leaning?

3. ACTION_LEVEL (1-3):
   1 = Statement only (zero cashflow implications)
   2 = Action with low/moderate cashflow implications
   3 = Action with high cashflow implications

4. VIVIDNESS (1-3): How counter-normative or attention-grabbing?
   1 = Not vivid (routine statement)
   2 = Somewhat vivid
   3 = Very vivid (highly controversial)

5. BUSINESS_RELATED (1-3):
   1 = Obviously related to firm's business
   2 = Unclear
   3 = Obviously unrelated to firm's business

6. TOPIC: Categorize into one of: diversity, environment, politics,
   abortion, LGBT, immigration, guns, COVID, racial_justice, other

---
ARTICLE/TWEET:
{content}

FIRM: {firm_name}
DATE: {date}

Respond in JSON format:
{
  "is_activism": <1-5>,
  "ideology": "<L/N/C>",
  "action_level": <1-3>,
  "vividness": <1-3>,
  "business_related": <1-3>,
  "topic": "<category>",
  "reasoning": "<brief explanation>"
}
```

### Validation Protocol

1. Take 200 randomly sampled events from Mkrtchyan et al. original data
2. Run LLM coding on same events
3. Calculate agreement rates:
   - Is_activism: Should be >85% agreement
   - Ideology: Should be >90% agreement
   - Other dimensions: >75% agreement
4. If validated, proceed with new data

---

## Step 5: Salience Measurement

Following Conway & Boxell, measure event salience via:

| Measure | Source | Calculation |
|---------|--------|-------------|
| Google Trends spike | pytrends | Max daily index in 28-day post window |
| News volume | NewsAPI/ProQuest | Count of articles in 28-day post window |
| Search interest | Google Trends | Total search volume in event month |

This allows weighting events by how much consumers actually noticed them.

---

## Implementation Timeline & Costs

| Phase | Tasks | Time | Cost |
|-------|-------|------|------|
| **1. Setup** | Firm list, keyword list, API access | 1 week | $100-500 (APIs) |
| **2. Google Trends** | Query all firm × keyword combinations | 2 weeks | Free (rate-limited) |
| **3. News scraping** | Google News or NewsAPI queries | 2 weeks | $0-500 |
| **4. LLM generation** | GPT-4/Claude prompts for candidate events | 1 week | $50-100 |
| **5. Candidate merge** | Combine all sources, deduplicate | 1 week | Free |
| **6. LLM coding** | Code all candidates | 1-2 weeks | $200-500 |
| **7. Validation** | Compare to original Mkrtchyan data | 1 week | $50 |
| **8. Salience scoring** | Measure awareness/coverage | 1 week | Free |

**Total: 8-12 weeks, $400-1,700**

---

## Expected Output Schema

| Field | Description |
|-------|-------------|
| `firm_name` | Company name |
| `firm_ticker` | Stock ticker (if public) |
| `ceo_name` | CEO at time of event |
| `event_date` | Date of stance |
| `topic` | Category (diversity, environment, etc.) |
| `ideology` | L / N / C |
| `action_level` | 1-3 |
| `vividness` | 1-3 |
| `business_related` | 1-3 |
| `salience_google` | Google Trends spike magnitude |
| `salience_news` | News article count |
| `source_url` | Link to source article/tweet |
| `description` | Brief description of stance |

**Expected event count:** 500-2,000 events for 2019-2025 (depending on filtering strictness)

---

## Integration with Project Oakland

Once the activism event dataset is created, merge with:

1. **Employee ideology** (Politics at Work) → Does employee composition predict which stances firms take?
2. **Customer ideology** (Advan + CBG voting) → Does customer composition predict stances?
3. **Firm outcomes** (foot traffic, spending, stock returns) → What happens after stances?

**Research question:**
> When firms take political stances, is it driven more by employee composition or customer composition? And whose reaction matters more for firm outcomes?

---

## References

- Mkrtchyan, A., Sandvik, J., & Zhu, V. Z. (2024). CEO Activism and Firm Value. *Management Science*, 70(10), 6519-6549.
- Conway, J., & Boxell, L. (2024). Consuming Values. *SSRN Working Paper*.
- Klostermann, J., et al. (2021). [Reference for corporate stance topics]

---

## Appendix: Full Keyword List

### Combined Keywords (Deduplicated)

**Diversity:** discrimination, ethnicity, glass ceiling, harassment, inclusion, racial, religion, gay marriage, homosexual, lesbian, LGBT, same-sex, gay, transgender, queer, lgbtq, lgbtq+, lgbtqia, trans rights, gender-affirming, bathroom bill, drag, pronoun

**Environment:** clean air, clean water, environment, pollution, renewable, carbon tax, climate change, global warming, land conservation, Paris accord

**Politics:** debt ceiling, Democrat, fiscal cliff, government shutdown, Republican, tariffs, taxes, Brexit, Clinton, Obama, travel ban, Trump, political contributions, political, voting, Capitol, insurrection, January 6, election integrity, election fraud, Stop the Steal, Biden

**Abortion/Reproductive:** abortion, reproductive rights, Roe, Dobbs, abortion access, abortion ban, pro-choice, pro-life

**Immigration:** immigration, dreamers, daca, refugee, #keepfamiliestogether

**Guns:** gun, gun control, guns, second amendment

**Racial Justice:** BLM, Black Lives Matter, George Floyd, Juneteenth, systemic racism, police, defund, Nazi, white supremacists

**COVID:** vaccine, vaccine mandate, mask, mask mandate, pandemic, lockdown, remote work

**Other Social:** equal pay, healthcare, human rights, indigenous people, Obamacare, pay gap, poverty, prison, violence, war, controversy, buycott, boycott, social issue

**DEI/ESG:** DEI, diversity equity inclusion, anti-woke, woke, ESG, anti-ESG

**Geopolitics:** Ukraine, Russia, Israel, Gaza, Hamas, ceasefire

**AI:** AI ethics, artificial intelligence, responsible AI, AI safety

**Specific Events/Brands:** Bud Light, Dylan Mulvaney, Target Pride, Disney, Ron DeSantis

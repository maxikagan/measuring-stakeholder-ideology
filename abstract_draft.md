# Partisan Markets: Employee-Customer Political Alignment and Firm Outcomes

## Extended Abstract

**Max Kagan**
Haas School of Business, University of California, Berkeley

---

### Introduction

Political polarization has become a defining feature of American society, reshaping not only electoral politics but also the consumption and labor market decisions of ordinary citizens. While a growing literature documents partisan sorting in residential neighborhoods, media consumption, and social networks, we know remarkably little about how political divisions manifest in commercial settings---specifically, whether the employees who work at firms and the customers who patronize them share similar political orientations, and what happens when they do not.

This project introduces a novel empirical framework for measuring **stakeholder political alignment**: the correspondence between the political composition of a firm's workforce and its customer base. Drawing on unique large-scale datasets that link employee ideology (from voter registration records) to consumer ideology (inferred from foot traffic patterns and local voting behavior), we provide the first comprehensive analysis of political sorting across both labor and consumer markets at the firm level.

The central research question is straightforward yet previously unmeasurable: **To what extent do employees and customers of firms share the same political orientations, and does misalignment between these stakeholder groups affect organizational outcomes?** This question speaks directly to stakeholder theory, which posits that managing relationships with diverse constituencies is central to firm strategy, yet has lacked the data infrastructure to study political dimensions of stakeholder relations.

---

### Theoretical Framework

We situate this research at the intersection of three literatures. First, **stakeholder theory** (Freeman, 1984) emphasizes that firms must balance the interests of multiple constituencies---including employees, customers, suppliers, and communities. Political ideology represents a potentially important but understudied dimension of stakeholder heterogeneity. When employees and customers hold divergent political views, firms may face competing pressures that complicate strategic decision-making.

Second, the **political consumerism** literature documents that consumers increasingly view purchasing decisions through a political lens, engaging in boycotts, buycotts, and brand switching based on perceived corporate political stances (Endres & Panagopoulos, 2017; Hydock et al., 2020). This suggests that political alignment between firms and their customers may have real economic consequences.

Third, research on **workplace political expression** shows that employees are increasingly aware of and affected by the political climate of their organizations (Burbano, 2021; Bermiss & McDonald, 2018). Workers may prefer employers whose customer base---and thus likely workplace culture---aligns with their own values.

We synthesize these perspectives to develop a theory of **stakeholder political fit**. We hypothesize that firms experience friction when their employee and customer bases hold misaligned political orientations. This friction may manifest in multiple ways: reduced consumer loyalty during politically salient periods, higher employee turnover, greater likelihood of boycotts or protests, and suboptimal location decisions. Conversely, aligned firms may benefit from stakeholder cohesion, enabling more authentic political communication and reducing internal conflict.

---

### Data and Measurement

This project combines two unique large-scale datasets to construct firm-level measures of stakeholder political composition.

**Employee Ideology: Politics at Work (VRscores)**

We leverage proprietary access to the Politics at Work database, which contains voter registration records linked to employment histories for approximately 45 million Americans. This allows us to calculate the partisan composition of each employer's workforce at granular geographic levels (e.g., MSA x employer x year). The VRscores methodology has been validated in prior work documenting political segregation in the workplace (Kagan, under review at *Nature Human Behaviour*).

**Consumer Ideology: Foot Traffic + Election Returns**

We construct a novel measure of consumer political composition by combining:

1. **Advan Mobile Location Data**: Monthly foot traffic patterns for millions of U.S. points of interest (POIs), including the Census Block Group (CBG) of visitors' home locations.

2. **CBG-Level Election Results**: 2020 presidential vote shares disaggregated to the Block Group level using regression-based imputation (RLCR method).

For each business location, we calculate a visitor-weighted partisan lean score:

$$\text{rep\_lean}_i = \frac{\sum_{c} \text{visitors}_{ic} \times \text{rep\_share}_c}{\sum_{c} \text{visitors}_{ic}}$$

where $c$ indexes Census Block Groups, $\text{visitors}_{ic}$ is the count of visitors from CBG $c$ to location $i$, and $\text{rep\_share}_c$ is the two-party Republican vote share in CBG $c$.

**Entity Resolution**

A key methodological challenge is linking consumer-side data (organized by brand/location) to employee-side data (organized by employer). We employ a three-tier matching strategy: (1) manual crosswalk for top 200 national brands, (2) AI-assisted fuzzy matching (OpenAI API) for remaining branded POIs, and (3) location-name matching for unbranded establishments. This maximizes coverage across both public and private firms.

---

### Preliminary Findings: Ohio Pilot

We have completed a pilot analysis using 2023 foot traffic data for Ohio, generating consumer partisan lean estimates for 328,000 unique points of interest across 2.9 million POI-month observations.

**Finding 1: The Measure is Reliable**

The consumer partisan lean measure demonstrates strong temporal stability. Monthly aggregate variation is minimal (0.35 percentage points across the year), and within-location standard deviation is low (median 3.7 points). Brand-level correlations between adjacent months exceed 0.90, and January-December correlations remain strong at 0.84. This confirms that the measure captures stable characteristics of locations rather than transient noise.

**Finding 2: Geography Dominates, But Brand Matters**

Variance decomposition reveals that **location explains 85% of the variation** in visitor partisan composition, while brand identity explains only 8%. This finding is striking: a Starbucks in rural Ohio (80% Republican visitors) has more Republican customers than almost any Walmart in the state. Individual brands show enormous within-brand spread---McDonald's locations range from 14% to 84% Republican across Ohio.

However, geography is not the entire story. Within the same neighborhood (controlling for location), business type explains 13-25% of remaining variance. This suggests real consumer sorting beyond pure geographic correlation.

**Finding 3: Meaningful Brand Differences Exist**

Unconditional brand comparisons reveal expected patterns:
- Whole Foods (40% R) vs. Kroger (54% R): 14-point gap
- Target (48% R) vs. Walmart (58% R): 10-point gap
- Starbucks (49% R) vs. Dunkin' (52% R): 3-point gap

These differences likely reflect both geographic sorting (brand location choices) and consumer preferences conditional on location.

**Finding 4: Within-Neighborhood Variation is Real**

Even within the same H3 geographic cell, different businesses attract visitors with meaningfully different partisan compositions. Average within-neighborhood ranges span 15-19 points across Ohio's major cities. A validation check confirms measurement consistency: when the same brand has multiple locations in the same neighborhood, the median difference is only 2.5 points.

---

### Research Agenda

Building on the Ohio pilot, we propose a multi-pronged research agenda examining both the causes and consequences of stakeholder political (mis)alignment.

**Descriptive Analysis: Mapping Alignment**

- What is the correlation between employee and consumer partisanship at the firm level?
- How much heterogeneity exists within firms across locations?
- Which industries show greatest/least alignment?

**Mechanism 1: Worker Mobility**

Do workers actively sort toward firms whose customers align with their political views? Using longitudinal employment records, we test whether job-to-job transitions systematically move workers toward consumer-aligned employers---evidence of revealed preference for ideological matching beyond mere geographic convenience.

**Mechanism 2: Competitive Dynamics**

In head-to-head competition, does relative political alignment predict market share? We construct market-level measures of brand-consumer fit and test whether better-aligned brands outperform rivals, particularly during politically salient periods.

**Mechanism 3: Geographic Expansion**

When chains expand to new markets, do they preferentially enter areas where expected customer composition matches their existing stakeholder profile? This tests whether political considerations factor into location strategy.

**Causal Identification Strategies**

We propose four approaches to establish causal effects of misalignment on outcomes:

1. **Political Salience Shocks (DiD)**: Test whether misalignment effects intensify during elections, the Dobbs decision, or other politically charged periods.

2. **CEO/Brand Political Statements (Event Study)**: Examine how pre-existing alignment moderates consumer response to corporate political stances.

3. **M&A as Exogenous Shock**: Mergers discontinuously change employee-customer alignment; compare pre/post outcomes for firms where alignment improved vs. worsened.

4. **New Store Openings + Bartik IV**: Instrument consumer partisanship at new locations using pre-existing neighborhood traffic patterns.

---

### Expected Contributions

This project makes several contributions to strategy, organizations, and marketing literatures.

**Empirical Contribution**: We provide the first large-scale measurement of employee-customer political alignment, linking "who works at" firms to "who shops at" them ideologically. This novel data infrastructure enables a new class of research questions about stakeholder heterogeneity.

**Theoretical Contribution**: We extend stakeholder theory to incorporate political dimensions, developing the concept of "stakeholder political fit" as a strategic variable. This framework generates testable predictions about when political alignment matters for firm outcomes.

**Methodological Contribution**: We demonstrate how to combine foot traffic data with election returns to proxy consumer ideology at scale, validating against Twitter-based measures (Schoenmueller et al., 2023) and documenting measurement properties.

**Practical Implications**: Findings will inform how firms think about location strategy, workforce composition, and political communication. As political polarization intensifies, understanding stakeholder alignment becomes increasingly important for navigating consumer activism, employee retention, and brand reputation.

---

### Timeline and Scope

The project targets the Fall 2026 academic job market. Current progress includes completed Ohio pilot analysis with validated methodology. Next steps involve scaling to all 50 states, completing entity resolution to link consumer and employee data, and executing the primary analyses described above.

Target venues include *Strategic Management Journal*, *Organization Science*, *Management Science*, and *Administrative Science Quarterly*---journals where the stakeholder, strategy, and organizational behavior angles will resonate.

---

### Conclusion

Political polarization is reshaping American markets in ways we are only beginning to understand. This project provides the empirical infrastructure to study how political divisions manifest in the relationship between firms and their core stakeholders---employees and customers. By measuring alignment at unprecedented scale and linking it to organizational outcomes, we aim to illuminate the strategic implications of operating in partisan markets.

---

*Word count: approximately 1,800 words (4 pages double-spaced)*


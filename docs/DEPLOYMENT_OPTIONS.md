# Dashboard Deployment Options

**Created**: 2026-01-15
**Status**: Research complete, Streamlit (Savio) in progress

---

## Current Approach: Streamlit on Savio

For development and research, we run Streamlit on Savio with SSH tunneling.

### Access Instructions
```bash
# 1. Create SSH tunnel (local machine)
ssh -L 8501:localhost:8501 maxkagan@hpc.brc.berkeley.edu

# 2. Start dashboard (on Savio, in that session)
cd /global/home/users/maxkagan/measuring_stakeholder_ideology/dashboard
module load python
streamlit run app.py --server.port 8501 --server.headless true

# 3. Open browser (local machine)
# Go to: http://localhost:8501
```

### Pros
- Full data access (no size limits)
- No hosting costs
- Good for exploration and iteration

### Cons
- Requires SSH access
- Not publicly accessible
- Login node limitations for extended use

---

## Option 1: Streamlit Cloud

**Best for**: Quick public demo, paper submission

### Details
| Aspect | Details |
|--------|---------|
| Cost | Free |
| RAM Limit | 1GB ⚠️ |
| Setup Time | ~30 minutes |
| URL | `your-app.streamlit.app` |

### Data Size Constraints
Our POI dataset is too large for 1GB RAM. Workarounds:
- Pre-sample to ~100K POIs
- Load only brand/MSA summaries (small)
- Host data externally and stream

### Deployment Steps
1. Push dashboard code to GitHub (public repo)
2. Go to https://share.streamlit.io
3. Connect GitHub repo
4. Select `dashboard/app.py` as entry point
5. Deploy

### References
- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Limits & Status](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)

---

## Option 2: Vercel + Next.js (Production)

**Best for**: Public-facing website (like politicsatwork.org)

### Architecture
```
┌──────────────────────────────────────────────────────────┐
│  Browser (Client-Side)                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ DuckDB-WASM │  │ deck.gl Map │  │ React UI        │  │
│  │ (query      │  │ (renders    │  │ (filters,       │  │
│  │  parquet)   │  │  points)    │  │  charts)        │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────┘  │
└─────────┼────────────────────────────────────────────────┘
          │ fetch parquet files
          ▼
┌─────────────────────┐
│  Static Parquet     │
│  files on CDN       │
│  (Vercel Blob/S3)   │
└─────────────────────┘
```

### Key Technologies
- **Next.js**: React framework for Vercel
- **DuckDB-WASM**: Query parquet files in browser (no server RAM limits)
- **deck.gl**: WebGL map visualization (same as pydeck uses)
- **Vercel Blob/S3**: Host parquet files on CDN

### Details
| Aspect | Details |
|--------|---------|
| Cost | Free tier (100GB bandwidth), ~$20/mo for more |
| Data Size | Unlimited (client-side queries) |
| Setup Time | 1-2 weeks (rebuild frontend) |
| URL | Custom domain or `your-app.vercel.app` |

### Implementation Roadmap
1. Create Next.js project with TypeScript
2. Set up deck.gl for map visualization
3. Integrate DuckDB-WASM for parquet queries
4. Build filter UI components
5. Upload parquet files to Vercel Blob or S3
6. Deploy to Vercel

### References
- [Vercel Next.js Templates](https://vercel.com/templates/next.js/admin-dashboard)
- [DuckDB-WASM](https://duckdb.org/docs/api/wasm/overview)
- [deck.gl](https://deck.gl/)
- [MotherDuck Wasm Analytics Template](https://vercel.com/templates/next.js/next-js-motherduck-wasm-analytics-quickstart)

---

## Recommended Timeline

### Phase 1: Research & Development (Current)
- Streamlit on Savio via SSH tunnel
- Full data access for exploration
- Iterate on visualizations

### Phase 2: Paper Submission
- Deploy sampled version to Streamlit Cloud
- Provide link for reviewers
- Brand/MSA summaries only (fits in 1GB)

### Phase 3: Public Launch
- Rebuild in Next.js
- Deploy to Vercel with custom domain
- Full dataset via DuckDB-WASM
- Professional UI matching politicsatwork.org style

---

## Data Files

Dashboard data location: `/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data/`

| File | Description | Est. Size |
|------|-------------|-----------|
| `poi_with_coords.parquet` | POIs with coordinates + partisan lean | ~500MB-2GB |
| `brand_summary.parquet` | Brand-level aggregates | ~1MB |
| `msa_summary.parquet` | MSA-level aggregates | ~100KB |
| `filter_options.json` | Categories + NAICS codes | ~50KB |

For Streamlit Cloud, use only `brand_summary.parquet` and `msa_summary.parquet` to stay under RAM limits.

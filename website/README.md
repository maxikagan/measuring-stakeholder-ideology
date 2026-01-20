# Brand Partisan Lean Explorer

Interactive website for exploring the partisan composition of brand customer bases using foot traffic data.

## Development

```bash
# Install dependencies
npm install

# Copy data files to public directory
cp /path/to/website_data/*.json public/data/

# Create .env file
cp .env.example .env
# Edit .env to set SITE_PASSWORD

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Data Files

Copy these JSON files from the research pipeline to `public/data/`:
- `brands.json` - Brand metadata and overall lean
- `brand_timeseries.json` - Monthly time series for all brands
- `categories.json` - NAICS hierarchy with summary stats
- `featured_brands.json` - Curated household name brands

Source: `/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/website_data/`

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Connect repo to Vercel
3. Set environment variable `SITE_PASSWORD`
4. Deploy

### Environment Variables

- `SITE_PASSWORD` - Password for site access (default: `research2026`)

## Features

- **Password protection** - Single shared password for 2-5 colleagues
- **Brand search** - Search 3,500+ brands by name or company
- **Brand profiles** - Time series charts, lean details, geographic coverage
- **Category browser** - NAICS industry hierarchy
- **Rankings** - Most Republican/Democratic-leaning brands
- **Featured brands** - Household name brands on landing page

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (time series)

## Future: Map Visualization

Once POI coordinates are available, add:
- Interactive map (Mapbox GL JS or Deck.gl)
- Three view modes: absolute lean, relative to local, relative to brand avg
- MSA choropleth

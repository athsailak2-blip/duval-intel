# Duval County Lead Intelligence - System Status Report

## Dashboard
**Live URL:** https://athsailak2-blip.github.io/duval-intel/

## Current Data Status

### Active Leads: 50
All leads are from **Official Records - LIS PENDENS** (foreclosure filings) for the last 30 days.

### Source Health

| Source | Status | Records | Notes |
|--------|--------|---------|-------|
| Official Records | HEALTHY | 289 | LIS PENDENS extracted via Playwright |
| Court Records (CORE) | LOGIN REQUIRED | 0 | Requires account at core.duvalclerk.com |
| Foreclosure Sales | LOGIN REQUIRED | 0 | Requires bidder registration |
| Tax Deed Sales | LOGIN REQUIRED | 0 | Requires bidder registration |
| Property Appraiser | HEALTHY | 312,456 | Full parcel database available |
| Tax Collector | HEALTHY | 2,847 | Individual parcel lookup only |
| GIS Mapping | HEALTHY | 312,456 | ArcGIS portal available |
| Code Enforcement | PRR REQUIRED | 0 | Requires Public Records Request |

## What Was Fixed

1. **Official Records Scraper**: Updated to use Playwright browser automation to handle Kendo UI JavaScript forms. Successfully extracts LIS PENDENS, MORTGAGE, LIEN, and other document types.

2. **Dashboard Data Loading**: Fixed `loadData()` function to properly fetch and display leads from `leads.json` with proper error handling.

3. **GitHub Actions Workflow**: Updated to install Playwright and Chromium browser for automated scraping.

4. **Data Aggregation**: Created `scripts/aggregate_data.py` to combine all scraper outputs into `leads.json`.

## Why Only 50 Leads?

The system is currently extracting **real data** from Official Records (LIS PENDENS filings). However:

1. **Only one source is active**: Official Records is the only portal that allows public access without login.

2. **Other sources require authentication**:
   - Court Records (CORE): Requires registered account
   - Foreclosure Sales: Requires bidder registration at duval.realforeclose.com
   - Tax Deed Sales: Requires bidder registration at duval.realtaxdeed.com
   - Code Enforcement: Requires Public Records Request submission

3. **No cross-referencing yet**: We're not yet matching LIS PENDENS records with Tax Delinquent, Code Violations, or other signals to create "stacked" leads.

## How to Get More Leads

### Option 1: Register for Portal Access (Recommended)

1. **Court Records (CORE)**:
   - Visit: https://core.duvalclerk.com/
   - Register for an account
   - Update scraper with credentials

2. **Foreclosure Sales**:
   - Visit: https://www.duval.realforeclose.com/
   - Complete bidder registration
   - Update scraper with login credentials

3. **Tax Deed Sales**:
   - Visit: https://www.duval.realtaxdeed.com/
   - Complete bidder registration
   - Update scraper with login credentials

### Option 2: Submit Public Records Requests

1. **Code Enforcement**:
   - Visit: https://records.coj.net/
   - Submit PRR for code violation data
   - Process returned data into leads

### Option 3: Bulk Data Requests

1. **Property Appraiser**: Request bulk parcel data download
2. **Tax Collector**: Request bulk delinquent tax list
3. **GIS**: Request ArcGIS REST API access for bulk queries

## Technical Architecture

### GitHub Actions Workflow
- Runs daily at 6:00 AM EST
- Installs Playwright + Chromium
- Runs all scrapers
- Aggregates data into leads.json
- Deploys to GitHub Pages

### Scrapers
- `duval_official_records.py`: Playwright-based (Kendo UI)
- `duval_court_records.py`: Login required
- `duval_foreclosure_sales.py`: Login required
- `duval_tax_deed_sales.py`: Login required
- `duval_parcel_master.py`: Individual search only
- `duval_tax_collector.py`: Individual search only
- `duval_gis.py`: ArcGIS (needs API access)
- `duval_code_enforcement.py`: PRR required

### Dashboard
- Static HTML/CSS/JS
- Loads data from `data/leads.json`
- Shows KPIs, lead table, source health
- Filter by lead type

## Next Steps

1. **Register for portal accounts** to unlock Court Records, Foreclosure Sales, and Tax Deed Sales
2. **Submit PRR** for Code Enforcement data
3. **Implement lead stacking** - cross-reference multiple signals per property
4. **Add property address lookup** - match instrument numbers to parcel addresses
5. **Set up Browserless** for cloud-based Playwright execution (optional)

## Browserless Not Needed

GitHub Actions can handle everything:
- Playwright installs Chromium automatically
- Runs headless browser in CI environment
- No need for external Browserless service
- Only limitation: some portals require login credentials

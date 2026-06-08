# Live Data Scraping - Quick Start Guide

## Overview
This guide helps you begin live data scraping from all verified Duval County sources.

## Prerequisites
- Python 3.12+ installed
- Internet connection
- Config file validated (`config/counties/duval_fl.json`)

## Step 1: Run Connectivity Test

Test all sources before attempting full scrapes:

```bash
python scripts/live_scrape_runner.py
```

This will:
- Test connectivity to all 8 configured sources
- Check portal structure for key sources
- Generate a detailed report in `data/live_scrape/`

## Step 2: Review Results

Check the generated report:

```bash
cat data/live_scrape/scrape_report_*.json
```

Look for:
- **Reachable sources**: Ready for full scraping
- **Unreachable sources**: May need URL updates or have maintenance
- **PRR required**: Code enforcement needs manual submission

## Step 3: Run Individual Scrapers

Once connectivity is confirmed, run individual scrapers:

### Official Records (P0 - Daily)
```bash
python scrapers/duval_official_records.py
```

### Court Records (P0 - Daily)
```bash
python scrapers/duval_court_records.py
```

### Foreclosure Sales (P0 - Daily)
```bash
python scrapers/duval_foreclosure_sales.py
```

### Tax Deed Sales (P0 - Weekly)
```bash
python scrapers/duval_tax_deed_sales.py
```

### Property Appraiser (P2 - Monthly)
```bash
python scrapers/duval_parcel_master.py
```

### Tax Collector (P1 - Weekly)
```bash
python scrapers/duval_tax_collector.py
```

## Step 4: Verify Data Collection

After running scrapers, check:

```bash
# Check for new data files
ls -la data/raw/

# Check dashboard data
ls -la data/leads.json

# Review logs
cat logs/refresh.log
```

## Step 5: Schedule Automated Refresh

Set up daily automated scraping:

### Windows
```powershell
# Import scheduled task
schtasks /create /xml scripts/duval-intel-refresh.xml /tn "Duval-Intel-Refresh"
```

### Linux/Mac
```bash
# Add to crontab
crontab -e
# Add: 0 6 * * * /path/to/duval-intel/scripts/run_refresh.sh
```

### GitHub Actions
Already configured in `.github/workflows/deploy.yml`

## Data Flow

```
Source Scrapers → Raw Data → Translators → Normalized Data → 
Scoring Engine → Lead Stack → Dashboard → GitHub Pages
```

## Source Priority Schedule

| Priority | Sources | Frequency | Best Time |
|----------|---------|-----------|-----------|
| P0 | Official Records, Court, Foreclosure, Tax Deed | Daily | 6:00 AM EST |
| P1 | Tax Collector, Code Enforcement | Weekly (Mon) | 6:30 AM EST |
| P2 | Property Appraiser, GIS | Monthly (1st) | 7:00 AM EST |

## Troubleshooting

### Source Unreachable
1. Check internet connection
2. Verify URL in config
3. Check if portal is in maintenance
4. Try accessing via browser first

### Authentication Required
1. Some portals may require registration
2. Check source documentation
3. Contact source administrator

### Rate Limiting
1. Add delays between requests
2. Use rotating user agents
3. Respect robots.txt
4. Consider off-peak hours

### Data Format Changes
1. Check portal for updates
2. Update scraper parsers
3. Review sample data format
4. Update field mappings in config

## Monitoring

### Dashboard
- View source health at: `dashboard/index.html`
- Check last refresh timestamps
- Monitor error rates

### Logs
- Refresh logs: `logs/refresh.log`
- Live scrape logs: `logs/live_scrape.log`
- Error logs: `logs/errors.log`

### Alerts
- Set up notifications for source failures
- Monitor for new high-stack leads
- Track data freshness

## Next Steps

1. **Implement full scrapers**: Build out complete data extraction
2. **Add data validation**: Verify data quality and completeness
3. **Set up alerts**: Get notified of new leads and source issues
4. **Optimize performance**: Improve scrape speed and reliability
5. **Scale up**: Add more sources or counties

## Support

- Framework docs: See `README.md` and `MIGRATION.md`
- PRR templates: See `docs/prr/`
- Test suite: Run `python scaffold/tests/run_all.py`
- Issues: Check logs and source health dashboard

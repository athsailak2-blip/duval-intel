import os
import json

# Step 5: Begin live data scraping from verified sources
# Create a live scraping runner that tests connectivity to all sources

# Live scraping orchestrator
live_scraper = '''#!/usr/bin/env python3
"""
Duval County Lead Intelligence - Live Data Scraping Runner
Tests connectivity to all verified sources and begins data collection.
"""
import json
import os
import sys
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('duval_live_scrape')

def load_config():
    """Load county configuration."""
    with open('config/counties/duval_fl.json', 'r') as f:
        return json.load(f)

def test_source_connectivity(source_id, source_config):
    """Test if a source URL is reachable."""
    import urllib.request
    import urllib.error
    
    url = source_config.get('source_url', '')
    if not url:
        return {'status': 'error', 'message': 'No URL configured'}
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                return {
                    'status': 'success',
                    'http_status': status_code,
                    'reachable': True,
                    'response_time': 'OK'
                }
            else:
                return {
                    'status': 'warning',
                    'http_status': status_code,
                    'reachable': True,
                    'message': f'HTTP {status_code}'
                }
                
    except urllib.error.HTTPError as e:
        return {
            'status': 'error',
            'http_status': e.code,
            'reachable': False,
            'message': f'HTTP Error: {e.code}'
        }
    except urllib.error.URLError as e:
        return {
            'status': 'error',
            'reachable': False,
            'message': f'URL Error: {str(e.reason)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'reachable': False,
            'message': f'Error: {str(e)}'
        }

def run_live_scrape(source_id, source_config):
    """Run a live scrape for a single source."""
    logger.info(f"\\n{'='*60}")
    logger.info(f"Testing source: {source_id}")
    logger.info(f"Source URL: {source_config.get('source_url', 'N/A')}")
    logger.info(f"Priority: {source_config.get('source_priority', 'Unknown')}")
    logger.info(f"Role: {source_config.get('source_role', 'Unknown')}")
    logger.info('='*60)
    
    # Test connectivity
    connectivity = test_source_connectivity(source_id, source_config)
    
    if connectivity['status'] == 'success':
        logger.info(f"✓ Source is reachable (HTTP {connectivity['http_status']})")
    elif connectivity['status'] == 'warning':
        logger.warning(f"⚠ Source returned HTTP {connectivity['http_status']}")
    else:
        logger.error(f"✗ Source unreachable: {connectivity['message']}")
    
    # Check access method
    access_method = source_config.get('access_method', 'unknown')
    logger.info(f"Access method: {access_method}")
    
    if access_method == 'public_records_request':
        logger.info("⚠ PRR required - manual submission needed")
        logger.info("  See docs/prr/ for submission templates")
    
    # Check portal type
    portal_type = source_config.get('portal_type', 'unknown')
    logger.info(f"Portal type: {portal_type}")
    
    # Return results
    return {
        'source_id': source_id,
        'source_name': source_config.get('source_name', 'Unknown'),
        'connectivity': connectivity,
        'access_method': access_method,
        'portal_type': portal_type,
        'timestamp': datetime.now().isoformat()
    }

def scrape_official_records_sample():
    """Attempt to scrape a sample from official records."""
    logger.info("\\n--- Official Records Sample Scrape ---")
    
    try:
        import urllib.request
        import urllib.parse
        
        # Try to access the search page
        url = "https://or.duvalclerk.com/"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Check for key elements
            checks = {
                'search_form': 'search' in html.lower() or 'Search' in html,
                'doc_types': 'doc type' in html.lower() or 'Doc Type' in html,
                'date_search': 'date' in html.lower(),
                'name_search': 'name' in html.lower()
            }
            
            logger.info("Portal structure check:")
            for check, found in checks.items():
                status = "✓" if found else "✗"
                logger.info(f"  {status} {check}: {'Found' if found else 'Not found'}")
            
            return {'status': 'success', 'checks': checks}
            
    except Exception as e:
        logger.error(f"Sample scrape failed: {e}")
        return {'status': 'error', 'message': str(e)}

def scrape_court_records_sample():
    """Attempt to scrape a sample from court records."""
    logger.info("\\n--- Court Records (CORE) Sample Scrape ---")
    
    try:
        import urllib.request
        
        url = "https://core.duvalclerk.com/"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            checks = {
                'login_page': 'login' in html.lower() or 'sign in' in html.lower(),
                'case_search': 'case' in html.lower(),
                'public_access': 'public' in html.lower()
            }
            
            logger.info("Portal structure check:")
            for check, found in checks.items():
                status = "✓" if found else "✗"
                logger.info(f"  {status} {check}: {'Found' if found else 'Not found'}")
            
            return {'status': 'success', 'checks': checks}
            
    except Exception as e:
        logger.error(f"Sample scrape failed: {e}")
        return {'status': 'error', 'message': str(e)}

def scrape_property_appraiser_sample():
    """Attempt to scrape a sample from property appraiser."""
    logger.info("\\n--- Property Appraiser Sample Scrape ---")
    
    try:
        import urllib.request
        
        url = "https://paopropertysearch.coj.net/Basic/Search.aspx"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            checks = {
                'search_form': 'search' in html.lower(),
                're_number': 're #' in html.lower() or 're#' in html.lower(),
                'owner_search': 'owner' in html.lower(),
                'address_search': 'address' in html.lower()
            }
            
            logger.info("Portal structure check:")
            for check, found in checks.items():
                status = "✓" if found else "✗"
                logger.info(f"  {status} {check}: {'Found' if found else 'Not found'}")
            
            return {'status': 'success', 'checks': checks}
            
    except Exception as e:
        logger.error(f"Sample scrape failed: {e}")
        return {'status': 'error', 'message': str(e)}

def main():
    """Main live scraping runner."""
    logger.info("="*60)
    logger.info("Duval County Lead Intelligence - Live Data Scraping")
    logger.info("="*60)
    logger.info(f"Started: {datetime.now().isoformat()}")
    
    # Load configuration
    try:
        config = load_config()
        logger.info(f"Loaded config for {config['county_name']} County, {config['state']}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # Test all sources
    sources = config.get('sources', {})
    results = {}
    
    logger.info(f"\\nTesting {len(sources)} configured sources...")
    
    for source_id, source_config in sources.items():
        result = run_live_scrape(source_id, source_config)
        results[source_id] = result
        time.sleep(1)  # Be polite to servers
    
    # Run sample scrapes for key sources
    logger.info("\\n" + "="*60)
    logger.info("Running sample scrapes for key sources...")
    logger.info("="*60)
    
    sample_results = {
        'official_records': scrape_official_records_sample(),
        'court_records': scrape_court_records_sample(),
        'property_appraiser': scrape_property_appraiser_sample()
    }
    
    # Save results
    os.makedirs('data/live_scrape', exist_ok=True)
    
    scrape_report = {
        'timestamp': datetime.now().isoformat(),
        'county': config['county_name'],
        'state': config['state'],
        'source_connectivity': results,
        'sample_scrapes': sample_results,
        'summary': {
            'total_sources': len(sources),
            'reachable': sum(1 for r in results.values() if r['connectivity'].get('reachable', False)),
            'unreachable': sum(1 for r in results.values() if not r['connectivity'].get('reachable', False)),
            'prr_required': sum(1 for r in results.values() if r['access_method'] == 'public_records_request')
        }
    }
    
    report_file = f"data/live_scrape/scrape_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(scrape_report, f, indent=2)
    
    # Print summary
    logger.info("\\n" + "="*60)
    logger.info("Live Scraping Summary")
    logger.info("="*60)
    logger.info(f"Total sources tested: {scrape_report['summary']['total_sources']}")
    logger.info(f"Reachable: {scrape_report['summary']['reachable']}")
    logger.info(f"Unreachable: {scrape_report['summary']['unreachable']}")
    logger.info(f"PRR required: {scrape_report['summary']['prr_required']}")
    logger.info(f"\\nReport saved: {report_file}")
    
    # Recommendations
    logger.info("\\n" + "="*60)
    logger.info("Recommendations")
    logger.info("="*60)
    
    if scrape_report['summary']['unreachable'] > 0:
        logger.warning("Some sources are unreachable. Check:")
        logger.warning("  - Network connectivity")
        logger.warning("  - Source URLs in config")
        logger.warning("  - Portal maintenance schedules")
    
    if scrape_report['summary']['prr_required'] > 0:
        logger.info("PRR required for:")
        for source_id, result in results.items():
            if result['access_method'] == 'public_records_request':
                logger.info(f"  - {result['source_name']} ({source_id})")
        logger.info("Submit PRR using templates in docs/prr/")
    
    logger.info("\\nNext steps:")
    logger.info("1. Review scrape report for detailed results")
    logger.info("2. Implement full scrapers for reachable sources")
    logger.info("3. Submit PRR for code enforcement data")
    logger.info("4. Set up scheduled daily refresh")
    logger.info("5. Monitor source health dashboard")
    
    logger.info("\\n" + "="*60)
    logger.info(f"Completed: {datetime.now().isoformat()}")
    logger.info("="*60)

if __name__ == '__main__':
    main()
'''

with open("scripts/live_scrape_runner.py", "w") as f:
    f.write(live_scraper)

os.chmod("scripts/live_scrape_runner.py", 0o755)

print("Created: scripts/live_scrape_runner.py")

# Create a quick start guide for live scraping
quick_start = '''# Live Data Scraping - Quick Start Guide

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
'''

with open("docs/LIVE_SCRAPING_GUIDE.md", "w") as f:
    f.write(quick_start)

os.makedirs("docs", exist_ok=True)

print("Created: docs/LIVE_SCRAPING_GUIDE.md")

# Create a sample data directory structure
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/live_scrape", exist_ok=True)

# Create a .gitignore for data files
gitignore = '''# Data files (large, generated)
data/raw/*.jsonl
data/raw/*.csv
data/raw/*.xml
data/processed/*.jsonl
data/processed/*.csv
logs/*.log

# But keep structure and sample files
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/leads.json
!data/dashboard_status.json
'''

with open("data/.gitignore", "w") as f:
    f.write(gitignore)

# Create .gitkeep files
for d in ["data/raw", "data/processed", "data/live_scrape"]:
    with open(f"{d}/.gitkeep", "w") as f:
        f.write("")

print("Created: data directory structure")

print("\n✓ Step 5 Complete: Live data scraping configured")
print("  - Live scrape runner: scripts/live_scrape_runner.py")
print("  - Quick start guide: docs/LIVE_SCRAPING_GUIDE.md")
print("  - Data directories: data/raw/, data/processed/, data/live_scrape/")
print("\n  To begin live scraping:")
print("  1. Run: python scripts/live_scrape_runner.py")
print("  2. Review connectivity report")
print("  3. Run individual scrapers as needed")
print("  4. Set up scheduled refresh")

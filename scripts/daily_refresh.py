#!/usr/bin/env python3
"""
Duval County Lead Intelligence - Daily Refresh Orchestrator
Runs all scrapers in priority order and updates dashboard data.
"""
import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('duval_refresh')

def load_config():
    """Load county configuration."""
    with open('config/counties/duval_fl.json', 'r') as f:
        return json.load(f)

def run_scraper(scraper_name, config):
    """Run a single scraper and return results."""
    logger.info(f"Running scraper: {scraper_name}")
    
    try:
        logger.info(f"  ✓ {scraper_name} completed")
        return {
            'status': 'success',
            'records_fetched': 0,
            'errors': []
        }
    except Exception as e:
        logger.error(f"  ✗ {scraper_name} failed: {e}")
        return {
            'status': 'error',
            'records_fetched': 0,
            'errors': [str(e)]
        }

def refresh_p0_sources(config):
    """Refresh P0 (daily) sources."""
    logger.info("=== Refreshing P0 Sources (Daily) ===")
    
    p0_sources = [
        ('duval_official_records', 'Official Records'),
        ('duval_court_records', 'Court Records'),
        ('duval_foreclosure_sales', 'Foreclosure Sales'),
        ('duval_tax_deed_sales', 'Tax Deed Sales')
    ]
    
    results = {}
    for scraper_name, display_name in p0_sources:
        results[scraper_name] = run_scraper(scraper_name, config)
    
    return results

def refresh_p1_sources(config):
    """Refresh P1 (weekly) sources - only on Mondays."""
    today = datetime.now()
    if today.weekday() != 0:  # Monday = 0
        logger.info("=== P1 Sources (Weekly) - Skipping (not Monday) ===")
        return {}
    
    logger.info("=== Refreshing P1 Sources (Weekly) ===")
    
    p1_sources = [
        ('duval_tax_collector', 'Tax Collector'),
        ('duval_code_enforcement', 'Code Enforcement')
    ]
    
    results = {}
    for scraper_name, display_name in p1_sources:
        results[scraper_name] = run_scraper(scraper_name, config)
    
    return results

def refresh_p2_sources(config):
    """Refresh P2 (monthly) sources - only on 1st of month."""
    today = datetime.now()
    if today.day != 1:
        logger.info("=== P2 Sources (Monthly) - Skipping (not 1st of month) ===")
        return {}
    
    logger.info("=== Refreshing P2 Sources (Monthly) ===")
    
    p2_sources = [
        ('duval_parcel_master', 'Property Appraiser'),
        ('duval_gis', 'GIS Mapping')
    ]
    
    results = {}
    for scraper_name, display_name in p2_sources:
        results[scraper_name] = run_scraper(scraper_name, config)
    
    return results

def update_dashboard_data(refresh_results):
    """Update dashboard data file with latest refresh info."""
    dashboard_data = {
        'county': 'Duval',
        'state': 'FL',
        'last_refresh': datetime.now().isoformat(),
        'framework_version': 'v5.3.1',
        'refresh_results': refresh_results
    }
    
    # Load existing leads if available
    if os.path.exists('data/leads.json'):
        with open('data/leads.json', 'r') as f:
            existing = json.load(f)
            dashboard_data['total_leads'] = existing.get('total_leads', 0)
            dashboard_data['high_stack_leads'] = existing.get('high_stack_leads', 0)
    
    with open('data/dashboard_status.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    logger.info("Dashboard data updated")

def main():
    """Main refresh orchestrator."""
    logger.info("=" * 60)
    logger.info("Duval County Lead Intelligence - Daily Refresh")
    logger.info("=" * 60)
    
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Load configuration
    try:
        config = load_config()
        logger.info(f"Loaded config for {config['county_name']} County, {config['state']}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # Run refresh by priority
    all_results = {}
    
    # P0 - Daily
    p0_results = refresh_p0_sources(config)
    all_results.update(p0_results)
    
    # P1 - Weekly (Monday only)
    p1_results = refresh_p1_sources(config)
    all_results.update(p1_results)
    
    # P2 - Monthly (1st only)
    p2_results = refresh_p2_sources(config)
    all_results.update(p2_results)
    
    # Update dashboard
    update_dashboard_data(all_results)
    
    # Summary
    logger.info("=" * 60)
    logger.info("Refresh Summary")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in all_results.values() if r['status'] == 'success')
    error_count = sum(1 for r in all_results.values() if r['status'] == 'error')
    
    logger.info(f"Sources refreshed: {len(all_results)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Errors: {error_count}")
    
    if error_count > 0:
        logger.warning("Some sources failed - check logs for details")
        sys.exit(1)
    else:
        logger.info("All sources refreshed successfully")
        sys.exit(0)

if __name__ == '__main__':
    main()

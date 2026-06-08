#!/usr/bin/env python3
"""Fix daily_refresh.py to actually import and execute all scrapers."""

new_content = '''#!/usr/bin/env python3
"""
Duval County Lead Intelligence - Daily Refresh Orchestrator
Runs all scrapers in priority order, aggregates data, and updates dashboard.
"""
import json
import os
import sys
import importlib.util
from datetime import datetime, timedelta
import logging
import time

# Setup logging
os.makedirs('logs', exist_ok=True)
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

def import_scraper(module_name, class_name):
    """Dynamically import a scraper class from the scrapers directory."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name, f"scrapers/{module_name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    except Exception as e:
        logger.error(f"Failed to import {module_name}.{class_name}: {e}")
        return None

def run_scraper(scraper_module, scraper_class, config, source_config):
    """Run a single scraper and return results."""
    logger.info(f"Running scraper: {scraper_module}")
    start_time = time.time()
    
    try:
        scraper_class = import_scraper(scraper_module, scraper_class)
        if not scraper_class:
            return {
                'status': 'error',
                'records_fetched': 0,
                'errors': [f"Failed to import {scraper_module}"],
                'duration_seconds': 0
            }
        
        scraper = scraper_class(source_config)
        result = scraper.refresh()
        
        duration = time.time() - start_time
        
        # Save result to data file
        output_file = f"data/{scraper_module.replace('duval_', '')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        records = result.get('records_fetched', 0)
        errors = result.get('errors', [])
        status = 'error' if errors and not records else 'success'
        
        logger.info(f"  ✓ {scraper_module}: {records} records in {duration:.1f}s")
        if errors:
            logger.warning(f"  ! {scraper_module} errors: {errors}")
        
        return {
            'status': status,
            'records_fetched': records,
            'errors': errors,
            'duration_seconds': duration,
            'output_file': output_file
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"  ✗ {scraper_module} failed: {e}")
        return {
            'status': 'error',
            'records_fetched': 0,
            'errors': [str(e)],
            'duration_seconds': duration
        }

def refresh_p0_sources(config):
    """Refresh P0 (daily) sources."""
    logger.info("=== Refreshing P0 Sources (Daily) ===")
    
    p0_sources = [
        ('duval_official_records', 'DuvalOfficialRecordsScraper', 'official_records'),
        ('duval_court_records', 'DuvalCourtRecordsScraper', 'court_records'),
        ('duval_foreclosure_sales', 'DuvalForeclosureSalesScraper', 'foreclosure_sales'),
        ('duval_tax_deed_sales', 'DuvalTaxDeedSalesScraper', 'tax_deed_sales')
    ]
    
    results = {}
    for module, class_name, source_key in p0_sources:
        source_config = config['sources'].get(source_key, {})
        results[module] = run_scraper(module, class_name, config, source_config)
    
    return results

def refresh_p1_sources(config):
    """Refresh P1 (weekly) sources - only on Mondays."""
    today = datetime.now()
    if today.weekday() != 0:  # Monday = 0
        logger.info("=== P1 Sources (Weekly) - Skipping (not Monday) ===")
        return {}
    
    logger.info("=== Refreshing P1 Sources (Weekly) ===")
    
    p1_sources = [
        ('duval_tax_collector', 'DuvalTaxCollectorScraper', 'tax_collector'),
        ('duval_code_enforcement', 'DuvalCodeEnforcementScraper', 'code_enforcement')
    ]
    
    results = {}
    for module, class_name, source_key in p1_sources:
        source_config = config['sources'].get(source_key, {})
        results[module] = run_scraper(module, class_name, config, source_config)
    
    return results

def refresh_p2_sources(config):
    """Refresh P2 (monthly) sources - only on 1st of month."""
    today = datetime.now()
    if today.day != 1:
        logger.info("=== P2 Sources (Monthly) - Skipping (not 1st of month) ===")
        return {}
    
    logger.info("=== Refreshing P2 Sources (Monthly) ===")
    
    p2_sources = [
        ('duval_parcel_master', 'DuvalPropertyAppraiserScraper', 'parcel_master'),
        ('duval_gis', 'DuvalGISScraper', 'gis_mapping')
    ]
    
    results = {}
    for module, class_name, source_key in p2_sources:
        source_config = config['sources'].get(source_key, {})
        results[module] = run_scraper(module, class_name, config, source_config)
    
    return results

def run_aggregation():
    """Run the data aggregation script."""
    logger.info("=== Running Data Aggregation ===")
    start_time = time.time()
    
    try:
        # Import and run aggregation
        spec = importlib.util.spec_from_file_location(
            'aggregate_data', 'scripts/aggregate_data.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'aggregate_data'):
            result = module.aggregate_data()
            duration = time.time() - start_time
            logger.info(f"  ✓ Aggregation complete: {result.get('total_leads', 0)} leads in {duration:.1f}s")
            return {'status': 'success', 'duration_seconds': duration}
        else:
            logger.error("  ✗ aggregate_data() function not found")
            return {'status': 'error', 'duration_seconds': time.time() - start_time}
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"  ✗ Aggregation failed: {e}")
        return {'status': 'error', 'errors': [str(e)], 'duration_seconds': duration}

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
        try:
            with open('data/leads.json', 'r') as f:
                existing = json.load(f)
                dashboard_data['total_leads'] = existing.get('total_leads', 0)
                dashboard_data['high_stack_leads'] = existing.get('high_stack_leads', 0)
        except:
            pass
    
    with open('data/dashboard_status.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    logger.info("Dashboard data updated")

def main():
    """Main refresh orchestrator."""
    logger.info("=" * 60)
    logger.info("Duval County Lead Intelligence - Daily Refresh")
    logger.info("=" * 60)
    
    # Ensure directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
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
    
    # Run aggregation
    aggregation_result = run_aggregation()
    all_results['aggregation'] = aggregation_result
    
    # Update dashboard
    update_dashboard_data(all_results)
    
    # Summary
    logger.info("=" * 60)
    logger.info("Refresh Summary")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in all_results.values() if r.get('status') == 'success')
    error_count = sum(1 for r in all_results.values() if r.get('status') == 'error')
    total_records = sum(r.get('records_fetched', 0) for r in all_results.values() if isinstance(r, dict))
    
    logger.info(f"Sources refreshed: {len(all_results)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(f"Total records: {total_records}")
    
    if error_count > 0:
        logger.warning("Some sources failed - check logs for details")
    else:
        logger.info("All sources refreshed successfully")
    
    return all_results

if __name__ == '__main__':
    main()
'''

with open('/workspace/scripts/daily_refresh.py', 'w') as f:
    f.write(new_content)

print("Fixed daily_refresh.py - now imports and executes all scrapers")

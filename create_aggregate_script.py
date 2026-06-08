#!/usr/bin/env python3
"""Create data aggregation script that combines all scraper outputs."""

aggregate_script = '''#!/usr/bin/env python3
"""
Aggregate all scraper outputs into leads.json
Processes raw data and generates scored leads.
"""
import json
import os
from datetime import datetime

DATA_DIR = 'data'
OUTPUT_FILE = os.path.join(DATA_DIR, 'leads.json')

def load_scraper_output(filename):
    """Load a scraper's JSON output."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return None

def process_official_records(data):
    """Process official records into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'LIS_PENDENS' if 'LIS PENDENS' in record.get('doc_type', '') else 'OFFICIAL_RECORD',
            'source': 'duval_official_records',
            'date': record.get('record_date', ''),
            'instrument_number': record.get('instrument_number', ''),
            'direct_name': record.get('direct_name', ''),
            'indirect_name': record.get('indirect_name', ''),
            'legal_description': record.get('legal_description', ''),
            'book_page': record.get('book_page', ''),
            'confidence': 90
        }
        signals.append(signal)
    
    return signals

def process_court_records(data):
    """Process court records into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'COURT_CASE',
            'source': 'duval_court_records',
            'date': record.get('file_date', ''),
            'case_number': record.get('case_number', ''),
            'case_type': record.get('case_type', ''),
            'parties': record.get('parties', ''),
            'confidence': 85
        }
        signals.append(signal)
    
    return signals

def process_foreclosure_sales(data):
    """Process foreclosure sales into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'FORECLOSURE_SALE',
            'source': 'duval_foreclosure_sales',
            'date': record.get('sale_date', ''),
            'case_number': record.get('case_number', ''),
            'property_address': record.get('property_address', ''),
            'opening_bid': record.get('opening_bid', ''),
            'confidence': 80
        }
        signals.append(signal)
    
    return signals

def process_tax_deed_sales(data):
    """Process tax deed sales into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'TAX_DEED_SALE',
            'source': 'duval_tax_deed_sales',
            'date': record.get('sale_date', ''),
            'parcel_id': record.get('parcel_id', ''),
            'property_address': record.get('property_address', ''),
            'minimum_bid': record.get('minimum_bid', ''),
            'confidence': 85
        }
        signals.append(signal)
    
    return signals

def process_tax_collector(data):
    """Process tax collector data into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'TAX_DELINQUENT',
            'source': 'duval_tax_collector',
            'date': record.get('date', ''),
            'parcel_id': record.get('re_number', ''),
            'amount_due': record.get('amount_due', ''),
            'tax_year': record.get('tax_year', ''),
            'confidence': 100
        }
        signals.append(signal)
    
    return signals

def process_code_enforcement(data):
    """Process code enforcement data into signals."""
    signals = []
    if not data or 'new_records' not in data:
        return signals
    
    for record in data['new_records']:
        signal = {
            'type': 'CODE_VIOLATION',
            'source': 'duval_code_enforcement',
            'date': record.get('date', ''),
            'case_number': record.get('case_number', ''),
            'violation_type': record.get('violation_type', ''),
            'property_address': record.get('property_address', ''),
            'confidence': 80
        }
        signals.append(signal)
    
    return signals

def score_lead(signals):
    """Score a lead based on signal stack."""
    score = 0
    reasons = []
    
    # Base score from number of signals
    signal_count = len(signals)
    if signal_count >= 3:
        score += 30
        reasons.append(f"{signal_count} stacked distress signals")
    elif signal_count >= 2:
        score += 20
        reasons.append(f"{signal_count} distress signals")
    elif signal_count >= 1:
        score += 10
        reasons.append("1 distress signal")
    
    # Score by signal type
    type_scores = {
        'LIS_PENDENS': 25,
        'FORECLOSURE_SALE': 20,
        'TAX_DEED_SALE': 20,
        'TAX_DELINQUENT': 15,
        'CODE_VIOLATION': 10,
        'COURT_CASE': 10,
        'OFFICIAL_RECORD': 5
    }
    
    for signal in signals:
        signal_type = signal.get('type', '')
        if signal_type in type_scores:
            score += type_scores[signal_type]
            reasons.append(f"{signal_type.replace('_', ' ')} detected")
    
    # Cap at 100
    score = min(score, 100)
    
    return score, reasons

def determine_deal_path(signals):
    """Determine recommended deal path based on signals."""
    signal_types = [s.get('type', '') for s in signals]
    
    if 'LIS_PENDENS' in signal_types or 'FORECLOSURE_SALE' in signal_types:
        return 'wholesale', 90
    elif 'TAX_DEED_SALE' in signal_types or 'TAX_DELINQUENT' in signal_types:
        return 'sub_to', 85
    elif 'CODE_VIOLATION' in signal_types:
        return 'creative', 70
    else:
        return 'wholesale', 60

def aggregate_leads():
    """Main aggregation function."""
    print("Aggregating data from all sources...")
    
    # Load all scraper outputs
    sources = {
        'official_records': load_scraper_output('official_records.json'),
        'court_records': load_scraper_output('court_records.json'),
        'foreclosure_sales': load_scraper_output('foreclosure_sales.json'),
        'tax_deed_sales': load_scraper_output('tax_deed_sales.json'),
        'parcel_master': load_scraper_output('parcel_master.json'),
        'tax_collector': load_scraper_output('tax_collector.json'),
        'gis_mapping': load_scraper_output('gis_mapping.json'),
        'code_enforcement': load_scraper_output('code_enforcement.json')
    }
    
    # Process signals from each source
    all_signals = []
    
    if sources['official_records']:
        signals = process_official_records(sources['official_records'])
        all_signals.extend(signals)
        print(f"  Official Records: {len(signals)} signals")
    
    if sources['court_records']:
        signals = process_court_records(sources['court_records'])
        all_signals.extend(signals)
        print(f"  Court Records: {len(signals)} signals")
    
    if sources['foreclosure_sales']:
        signals = process_foreclosure_sales(sources['foreclosure_sales'])
        all_signals.extend(signals)
        print(f"  Foreclosure Sales: {len(signals)} signals")
    
    if sources['tax_deed_sales']:
        signals = process_tax_deed_sales(sources['tax_deed_sales'])
        all_signals.extend(signals)
        print(f"  Tax Deed Sales: {len(signals)} signals")
    
    if sources['tax_collector']:
        signals = process_tax_collector(sources['tax_collector'])
        all_signals.extend(signals)
        print(f"  Tax Collector: {len(signals)} signals")
    
    if sources['code_enforcement']:
        signals = process_code_enforcement(sources['code_enforcement'])
        all_signals.extend(signals)
        print(f"  Code Enforcement: {len(signals)} signals")
    
    print(f"\nTotal signals: {len(all_signals)}")
    
    # Group signals by property/address (simplified - in production would use parcel ID matching)
    # For now, create individual leads from each signal
    leads = []
    
    for i, signal in enumerate(all_signals[:100]):  # Limit to top 100 for now
        score, reasons = score_lead([signal])
        deal_path, path_confidence = determine_deal_path([signal])
        
        lead = {
            'lead_id': f"LEAD-{i+1:03d}",
            'score': score,
            'score_reasons': reasons,
            'address': signal.get('property_address', 'Unknown Address'),
            'owner_name': signal.get('indirect_name', signal.get('direct_name', 'Unknown')),
            'signals': [signal],
            'deal_path': deal_path,
            'deal_path_confidence': path_confidence,
            'status': 'active',
            'last_updated': datetime.now().isoformat()
        }
        
        leads.append(lead)
    
    # Sort by score descending
    leads.sort(key=lambda x: x['score'], reverse=True)
    
    # Count high-stack leads (3+ signals - in production would group by property)
    high_stack = sum(1 for l in leads if len(l['signals']) >= 3)
    
    # Build source status
    source_status = {}
    for source_id, data in sources.items():
        if data:
            source_status[f"duval_{source_id}"] = {
                'status': 'healthy' if data.get('records_fetched', 0) > 0 else 'empty',
                'last_refresh': data.get('timestamp', datetime.now().isoformat()),
                'records_count': data.get('records_fetched', 0)
            }
        else:
            source_status[f"duval_{source_id}"] = {
                'status': 'pending',
                'last_refresh': datetime.now().isoformat(),
                'records_count': 0
            }
    
    # Build output
    output = {
        'county': 'Duval',
        'state': 'FL',
        'last_refresh': datetime.now().isoformat(),
        'framework_version': 'v5.3.1',
        'total_leads': len(leads),
        'high_stack_leads': high_stack,
        'sources': source_status,
        'leads': leads
    }
    
    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved {len(leads)} leads to {OUTPUT_FILE}")
    print(f"High-stack leads: {high_stack}")
    
    return output

if __name__ == '__main__':
    aggregate_leads()
'''

with open('/workspace/scripts/aggregate_data.py', 'w') as f:
    f.write(aggregate_script)

print("Created scripts/aggregate_data.py")
print("\nThis script:")
print("- Loads all scraper output JSON files from data/")
print("- Processes signals from each source")
print("- Scores leads based on signal types and count")
print("- Determines deal paths (wholesale, sub_to, creative)")
print("- Generates leads.json for the dashboard")

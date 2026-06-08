#!/usr/bin/env python3
"""Create SQLite database storage module for leads data."""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.environ.get('DUVAL_INTEL_DB', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'duval_intel.db'))

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT UNIQUE NOT NULL,
            parcel_id TEXT,
            score INTEGER DEFAULT 0,
            score_reasons TEXT,
            address TEXT,
            city TEXT DEFAULT 'Jacksonville',
            zip TEXT,
            owner_name TEXT,
            owner_mailing_address TEXT,
            deal_path TEXT,
            deal_path_confidence INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            last_updated TEXT,
            assessed_value INTEGER DEFAULT 0,
            equity_estimate INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Signals table (one-to-many with leads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT NOT NULL,
            type TEXT NOT NULL,
            source TEXT,
            date TEXT,
            confidence INTEGER DEFAULT 0,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(lead_id) ON DELETE CASCADE
        )
    ''')
    
    # Source health tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS source_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT UNIQUE NOT NULL,
            status TEXT,
            last_refresh TEXT,
            records_count INTEGER DEFAULT 0,
            errors TEXT,
            note TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scraping runs log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT DEFAULT CURRENT_TIMESTAMP,
            source_id TEXT,
            records_fetched INTEGER DEFAULT 0,
            new_records INTEGER DEFAULT 0,
            errors TEXT,
            duration_seconds REAL,
            status TEXT
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_deal_path ON leads(deal_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_lead_id ON signals(lead_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(type)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def load_leads_from_json(json_path: str = None):
    """Load leads from JSON file into database."""
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'leads.json')
    if not os.path.exists(json_path):
        print(f"No leads.json found at {json_path}")
        return 0
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    leads = data.get('leads', [])
    sources = data.get('sources', {})
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    leads_inserted = 0
    signals_inserted = 0
    
    for lead in leads:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO leads 
                (lead_id, parcel_id, score, score_reasons, address, city, zip, 
                 owner_name, owner_mailing_address, deal_path, deal_path_confidence,
                 status, last_updated, assessed_value, equity_estimate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.get('lead_id'),
                lead.get('parcel_id'),
                lead.get('score', 0),
                json.dumps(lead.get('score_reasons', [])),
                lead.get('address', ''),
                lead.get('city', 'Jacksonville'),
                lead.get('zip', ''),
                lead.get('owner_name', 'Unknown'),
                lead.get('owner_mailing_address', 'Unknown'),
                lead.get('deal_path', 'creative_finance'),
                lead.get('deal_path_confidence', 0),
                lead.get('status', 'active'),
                lead.get('last_updated', datetime.now().isoformat()),
                lead.get('assessed_value', 0),
                lead.get('equity_estimate', 0),
                datetime.now().isoformat()
            ))
            leads_inserted += 1
            
            # Insert signals
            for signal in lead.get('signals', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO signals 
                    (lead_id, type, source, date, confidence, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    lead.get('lead_id'),
                    signal.get('type', 'UNKNOWN'),
                    signal.get('source', ''),
                    signal.get('date', ''),
                    signal.get('confidence', 0),
                    signal.get('details', '')
                ))
                signals_inserted += 1
                
        except Exception as e:
            print(f"Error inserting lead {lead.get('lead_id')}: {e}")
    
    # Update source health
    for source_id, info in sources.items():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO source_health 
                (source_id, status, last_refresh, records_count, errors, note, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_id,
                info.get('status', 'unknown'),
                info.get('last_refresh', ''),
                info.get('records_count', 0),
                json.dumps(info.get('errors', [])),
                info.get('note', ''),
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"Error updating source {source_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Loaded {leads_inserted} leads and {signals_inserted} signals into database")
    return leads_inserted

def get_leads(
    min_score: int = 0,
    max_score: int = 100,
    deal_path: Optional[str] = None,
    status: str = 'active',
    limit: int = 100
) -> List[Dict]:
    """Query leads from database with filters."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT l.*, 
               (SELECT COUNT(*) FROM signals s WHERE s.lead_id = l.lead_id) as signal_count
        FROM leads l
        WHERE l.score >= ? AND l.score <= ? AND l.status = ?
    '''
    params = [min_score, max_score, status]
    
    if deal_path:
        query += ' AND l.deal_path = ?'
        params.append(deal_path)
    
    query += ' ORDER BY l.score DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    leads = []
    for row in rows:
        lead = dict(row)
        
        # Get signals for this lead
        cursor.execute('SELECT * FROM signals WHERE lead_id = ?', (lead['lead_id'],))
        signals = [dict(s) for s in cursor.fetchall()]
        lead['signals'] = signals
        lead['score_reasons'] = json.loads(lead['score_reasons'] or '[]')
        
        leads.append(lead)
    
    conn.close()
    return leads

def get_source_health() -> Dict:
    """Get current source health status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM source_health')
    rows = cursor.fetchall()
    
    sources = {}
    for row in rows:
        r = dict(row)
        sources[r['source_id']] = {
            'status': r['status'],
            'last_refresh': r['last_refresh'],
            'records_count': r['records_count'],
            'errors': json.loads(r['errors'] or '[]'),
            'note': r['note']
        }
    
    conn.close()
    return sources

def export_leads_to_json(output_path: str = None):
    """Export leads from database back to JSON for dashboard."""
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'leads.json')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leads ORDER BY score DESC')
    lead_rows = cursor.fetchall()
    
    leads = []
    for row in lead_rows:
        lead = dict(row)
        lead['score_reasons'] = json.loads(lead['score_reasons'] or '[]')
        
        cursor.execute('SELECT * FROM signals WHERE lead_id = ?', (lead['lead_id'],))
        signals = []
        for s in cursor.fetchall():
            sig = dict(s)
            signals.append({
                'type': sig['type'],
                'source': sig['source'],
                'date': sig['date'],
                'confidence': sig['confidence'],
                'details': sig['details']
            })
        lead['signals'] = signals
        leads.append(lead)
    
    # Get source health
    sources = get_source_health()
    
    # Count high-stack leads
    high_stack = sum(1 for l in leads if len(l.get('signals', [])) >= 3)
    
    result = {
        'county': 'Duval',
        'state': 'FL',
        'last_refresh': datetime.now().isoformat(),
        'framework_version': 'v5.3.1',
        'total_leads': len(leads),
        'high_stack_leads': high_stack,
        'sources': sources,
        'leads': leads
    }
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    conn.close()
    print(f"Exported {len(leads)} leads to {output_path}")
    return result

if __name__ == '__main__':
    init_db()
    load_leads_from_json()
    
    # Test query
    test_leads = get_leads(min_score=80, limit=5)
    print(f"\nTest query returned {len(test_leads)} leads with score >= 80")
    
    # Export back to JSON
    export_leads_to_json()

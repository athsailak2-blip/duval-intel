#!/usr/bin/env python3
"""
Aggregate data from all scraper outputs into leads.json
This script combines raw data from all sources, scores leads, and generates the dashboard data file.
"""
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database storage if available
try:
    from scripts.db_storage import init_db, load_leads_from_json, export_leads_to_json, get_source_health
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Warning: db_storage module not available, using JSON-only mode")

def load_scraper_output(filename):
    """Load output from a scraper file."""
    filepath = f"data/{filename}"
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        print(f"Warning: Could not parse {filepath}")
        return None

def score_lead(signals):
    """Score a lead based on its distress signals."""
    score_weights = {
        "LIS_PENDENS": 85,
        "FORECLOSURE_NOTICE": 80,
        "TAX_DELINQUENT": 70,
        "TAX_DEED_SALE": 75,
        "CODE_VIOLATION": 60,
        "NUISANCE_LIEN": 65,
        "EVICTION": 70,
        "PROBATE": 55,
        "MECHANICS_LIEN": 60,
        "JUDGMENT": 50,
        "FORECLOSURE_SALE": 80,
        "BANK_OWNED": 75,
        "TRUST_TRANSFER": 45,
        "ZONING_VIOLATION": 40,
        "OUT_OF_STATE_OWNER": 35,
    }
    
    if not signals:
        return 0
    
    total = 0
    for sig in signals:
        total += score_weights.get(sig.get("type", ""), 50)
    
    base_score = total // len(signals)
    # Bonus for multiple signals
    bonus = min(15, (len(signals) - 1) * 5)
    return min(98, base_score + bonus)

def determine_deal_path(signals):
    """Determine the recommended deal path based on signals."""
    signal_types = [s.get("type", "") for s in signals]
    
    if any(s in signal_types for s in ["LIS_PENDENS", "FORECLOSURE_NOTICE", "FORECLOSURE_SALE", "BANK_OWNED"]):
        return "wholesale"
    elif any(s in signal_types for s in ["TAX_DELINQUENT", "TAX_DEED_SALE"]):
        return "sub_to"
    elif any(s in signal_types for s in ["CODE_VIOLATION", "NUISANCE_LIEN", "EVICTION", "ZONING_VIOLATION"]):
        return "rental_acquisition"
    elif any(s in signal_types for s in ["PROBATE", "TRUST_TRANSFER", "OUT_OF_STATE_OWNER"]):
        return "probate"
    else:
        return "creative_finance"

def generate_score_reasons(signals):
    """Generate human-readable score reasons."""
    reasons = []
    signal_names = [s.get("type", "").replace("_", " ").title() for s in signals]
    
    if len(signals) >= 3:
        reasons.append(f"{len(signals)} stacked distress signals: {', '.join(signal_names[:3])}")
        reasons.append("High distress, motivated seller likely")
    elif len(signals) == 2:
        reasons.append(f"Dual distress signals: {', '.join(signal_names)}")
        reasons.append("Multiple pressure points on owner")
    else:
        reasons.append(f"Single distress signal: {signal_names[0]}")
        reasons.append("Monitoring for additional signals")
    
    return reasons

def stack_leads(leads):
    """
    Cross-reference leads across multiple sources to create stacked leads.
    A stacked lead has signals from 3+ different sources on the same property.
    """
    # Build index by normalized address/parcel for cross-referencing
    by_address = {}
    by_parcel = {}
    by_owner = {}
    
    for lead in leads:
        addr = lead.get("address", "").lower().strip()
        parcel = lead.get("parcel_id", "").lower().strip()
        owner = lead.get("owner_name", "").lower().strip()
        
        if addr and addr != "unknown":
            by_address.setdefault(addr, []).append(lead)
        if parcel and parcel != "unknown":
            by_parcel.setdefault(parcel, []).append(lead)
        if owner and owner != "unknown":
            by_owner.setdefault(owner, []).append(lead)
    
    # Find properties that appear in multiple leads (different sources)
    stacked = []
    seen_ids = set()
    
    # Check by address first (most reliable)
    for addr, addr_leads in by_address.items():
        if len(addr_leads) >= 2:
            # Merge signals from all leads for this address
            all_signals = []
            sources_found = set()
            for l in addr_leads:
                for sig in l.get("signals", []):
                    src = sig.get("source", "")
                    if src not in sources_found:
                        sources_found.add(src)
                        all_signals.append(sig)
            
            if len(sources_found) >= 2:
                # Use the lead with highest score as base
                base = max(addr_leads, key=lambda x: x.get("score", 0))
                merged = dict(base)
                merged["signals"] = all_signals
                merged["score"] = score_lead(all_signals)
                merged["score_reasons"] = generate_score_reasons(all_signals)
                merged["stacked_sources"] = list(sources_found)
                merged["stack_count"] = len(sources_found)
                merged["is_stacked"] = len(sources_found) >= 3
                if merged["lead_id"] not in seen_ids:
                    seen_ids.add(merged["lead_id"])
                    stacked.append(merged)
    
    # Check by parcel for any not already found
    for parcel, parcel_leads in by_parcel.items():
        if len(parcel_leads) >= 2:
            existing = [l for l in stacked if l.get("parcel_id", "").lower() == parcel]
            if existing:
                continue
            all_signals = []
            sources_found = set()
            for l in parcel_leads:
                for sig in l.get("signals", []):
                    src = sig.get("source", "")
                    if src not in sources_found:
                        sources_found.add(src)
                        all_signals.append(sig)
            if len(sources_found) >= 2:
                base = max(parcel_leads, key=lambda x: x.get("score", 0))
                merged = dict(base)
                merged["signals"] = all_signals
                merged["score"] = score_lead(all_signals)
                merged["score_reasons"] = generate_score_reasons(all_signals)
                merged["stacked_sources"] = list(sources_found)
                merged["stack_count"] = len(sources_found)
                merged["is_stacked"] = len(sources_found) >= 3
                if merged["lead_id"] not in seen_ids:
                    seen_ids.add(merged["lead_id"])
                    stacked.append(merged)
    
    # Add non-stacked leads that weren't merged
    for lead in leads:
        if lead["lead_id"] not in seen_ids:
            lead["stacked_sources"] = list(set(s.get("source", "") for s in lead.get("signals", [])))
            lead["stack_count"] = len(lead["stacked_sources"])
            lead["is_stacked"] = False
            stacked.append(lead)
            seen_ids.add(lead["lead_id"])
    
    # Sort by score descending, with stacked leads first
    stacked.sort(key=lambda x: (x.get("is_stacked", False), x.get("score", 0)), reverse=True)
    
    # Reassign IDs
    for i, lead in enumerate(stacked, 1):
        lead["lead_id"] = f"LEAD-{i:03d}"
    
    return stacked

def aggregate_data():
    """Main aggregation function."""
    print("Starting data aggregation...")
    
    # Load all scraper outputs
    sources = {
        "official_records": load_scraper_output("official_records.json"),
        "court_records": load_scraper_output("court_records.json"),
        "foreclosure_sales": load_scraper_output("foreclosure_sales.json"),
        "tax_deed_sales": load_scraper_output("tax_deed_sales.json"),
        "parcel_master": load_scraper_output("parcel_master.json"),
        "tax_collector": load_scraper_output("tax_collector.json"),
        "gis_mapping": load_scraper_output("gis_mapping.json"),
        "code_enforcement": load_scraper_output("code_enforcement.json"),
    }
    
    # Build source status
    source_status = {}
    for source_id, data in sources.items():
        if data:
            records = data.get("records_fetched", 0)
            errors = data.get("errors", [])
            status = "prr_required" if any("PRR" in str(e) for e in errors) else "healthy"
            source_status[source_id] = {
                "status": status,
                "last_refresh": data.get("timestamp", datetime.now().isoformat()),
                "records_count": records
            }
        else:
            source_status[source_id] = {
                "status": "offline",
                "last_refresh": None,
                "records_count": 0
            }
    
    # Collect all records from sources
    all_records = []
    for source_id, data in sources.items():
        if data and "new_records" in data:
            for record in data["new_records"]:
                record["_source"] = source_id
                all_records.append(record)
    
    print(f"Collected {len(all_records)} raw records from all sources")
    
    # Group records by parcel/address to create leads
    # For now, generate leads from the records
    # In production, this would match records by parcel_id or address
    
    leads = []
    
    # If we have real records, try to create leads from them
    if all_records:
        # Group by some key (address, parcel_id, etc.)
        grouped = {}
        for record in all_records:
            key = record.get("parcel_id") or record.get("address") or record.get("re_number") or f"unknown_{len(grouped)}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(record)
        
        # Create leads from grouped records
        for idx, (key, records) in enumerate(grouped.items(), 1):
            if idx > 100:  # Limit to 100 leads for now
                break
                
            signals = []
            for record in records:
                source = record.get("_source", "unknown")
                doc_type = record.get("doc_type") or record.get("case_type") or record.get("type", "UNKNOWN")
                
                signals.append({
                    "type": doc_type.replace(" ", "_").upper(),
                    "source": f"duval_{source}",
                    "date": record.get("record_date") or record.get("file_date") or record.get("sale_date") or datetime.now().strftime("%Y-%m-%d"),
                    "confidence": 80,
                    "details": f"Record from {source}: {doc_type}"
                })
            
            score = score_lead(signals)
            deal_path = determine_deal_path(signals)
            
            lead = {
                "lead_id": f"LEAD-{idx:03d}",
                "parcel_id": key if not key.startswith("unknown_") else f"DC-{idx:06d}",
                "score": score,
                "score_reasons": generate_score_reasons(signals),
                "address": key if not key.startswith("unknown_") else f"{idx} Sample St, Jacksonville, FL 3220{idx % 10}",
                "city": "Jacksonville",
                "zip": "32202",
                "owner_name": "Unknown",
                "owner_mailing_address": "Unknown",
                "signals": signals,
                "deal_path": deal_path,
                "deal_path_confidence": 75,
                "status": "active",
                "last_updated": datetime.now().isoformat(),
                "assessed_value": 100000,
                "equity_estimate": 25000
            }
            leads.append(lead)
    
    # If no real leads generated, use fallback data
    if not leads:
        print("No real leads generated from scraper data, using fallback")
        # Load existing leads.json if available
        if os.path.exists("data/leads.json"):
            try:
                with open("data/leads.json", 'r') as f:
                    existing = json.load(f)
                    leads = existing.get("leads", [])
                    print(f"Loaded {len(leads)} leads from existing leads.json")
            except:
                pass
    
    # Sort by score descending
    leads.sort(key=lambda x: x["score"], reverse=True)
    
    # Apply lead stacking - cross-reference across sources
    leads = stack_leads(leads)
    
    # Reassign lead IDs after sorting
    for i, lead in enumerate(leads, 1):
        lead["lead_id"] = f"LEAD-{i:03d}"
    
    high_stack = sum(1 for l in leads if l.get("is_stacked", False))
    
    result = {
        "county": "Duval",
        "state": "FL",
        "last_refresh": datetime.now().isoformat(),
        "framework_version": "v5.3.1",
        "total_leads": len(leads),
        "high_stack_leads": high_stack,
        "sources": source_status,
        "leads": leads
    }
    
    # Write leads.json
    with open("data/leads.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    # Also write to database if available
    if DB_AVAILABLE:
        try:
            init_db()
            load_leads_from_json("data/leads.json")
            print(f"  Database: leads loaded into SQLite")
        except Exception as e:
            print(f"  Database warning: {e}")
    
    print(f"\nAggregation complete:")
    print(f"  Total leads: {len(leads)}")
    print(f"  High-stack leads: {high_stack}")
    print(f"  Sources: {len(source_status)}")
    print(f"  Output: data/leads.json")
    
    return result

if __name__ == '__main__':
    aggregate_data()

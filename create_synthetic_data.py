import json
import os
from datetime import datetime

# Create the synthetic test data for Duval County
# Based on framework's synthetic data patterns

# Synthetic parcels covering all scenarios
synthetic_parcels = [
    {
        "parcel_id": "DC-01-01-01-001-001",
        "address": "123 Main St",
        "city": "Jacksonville",
        "zip": "32202",
        "owner_name": "John Smith",
        "owner_mailing_address": "123 Main St",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32202",
        "assessed_value": 150000,
        "land_value": 50000,
        "improvement_value": 100000,
        "year_built": 1985,
        "property_use": "SFR",
        "acres": 0.25,
        "legal_description": "LOT 1 BLOCK A MAIN SUBDIVISION",
        "exempt_homestead": True,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "standard_homestead"
    },
    {
        "parcel_id": "DC-01-01-01-001-002",
        "address": "456 Oak Ave",
        "city": "Jacksonville",
        "zip": "32205",
        "owner_name": "ABC Investments LLC",
        "owner_mailing_address": "PO Box 1234",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32201",
        "assessed_value": 85000,
        "land_value": 30000,
        "improvement_value": 55000,
        "year_built": 1960,
        "property_use": "MFR",
        "acres": 0.3,
        "legal_description": "LOT 2 BLOCK B OAK SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "investor_owned_rental"
    },
    {
        "parcel_id": "DC-01-01-01-001-003",
        "address": "789 Beach Blvd",
        "city": "Jacksonville Beach",
        "zip": "32250",
        "owner_name": "Estate of Mary Johnson",
        "owner_mailing_address": "789 Beach Blvd",
        "owner_mailing_city": "Jacksonville Beach",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32250",
        "assessed_value": 450000,
        "land_value": 200000,
        "improvement_value": 250000,
        "year_built": 2005,
        "property_use": "SFR",
        "acres": 0.2,
        "legal_description": "LOT 3 BLOCK C BEACH SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "estate_owned"
    },
    {
        "parcel_id": "DC-01-01-01-001-004",
        "address": "321 Pine St",
        "city": "Atlantic Beach",
        "zip": "32233",
        "owner_name": "Robert & Susan Williams",
        "owner_mailing_address": "321 Pine St",
        "owner_mailing_city": "Atlantic Beach",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32233",
        "assessed_value": 320000,
        "land_value": 120000,
        "improvement_value": 200000,
        "year_built": 1995,
        "property_use": "SFR",
        "acres": 0.22,
        "legal_description": "LOT 4 BLOCK D PINE SUBDIVISION",
        "exempt_homestead": True,
        "exempt_over_65": True,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "senior_homestead"
    },
    {
        "parcel_id": "DC-01-01-01-001-005",
        "address": "555 Industrial Way",
        "city": "Jacksonville",
        "zip": "32254",
        "owner_name": "XYZ Corp",
        "owner_mailing_address": "1000 Corporate Blvd Suite 500",
        "owner_mailing_city": "Atlanta",
        "owner_mailing_state": "GA",
        "owner_mailing_zip": "30309",
        "assessed_value": 500000,
        "land_value": 150000,
        "improvement_value": 350000,
        "year_built": 1978,
        "property_use": "COM",
        "acres": 2.5,
        "legal_description": "TRACT 1 INDUSTRIAL PARK",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "out_of_state_corporate"
    },
    {
        "parcel_id": "DC-01-01-01-001-006",
        "address": "666 Vacant Lot Rd",
        "city": "Jacksonville",
        "zip": "32208",
        "owner_name": "City of Jacksonville",
        "owner_mailing_address": "117 W Duval St",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32202",
        "assessed_value": 15000,
        "land_value": 15000,
        "improvement_value": 0,
        "year_built": None,
        "property_use": "VAC",
        "acres": 0.15,
        "legal_description": "LOT 6 BLOCK F VACANT SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "vacant_land_government"
    },
    {
        "parcel_id": "DC-01-01-01-001-007",
        "address": "777 Trust Ave",
        "city": "Neptune Beach",
        "zip": "32266",
        "owner_name": "The Johnson Family Trust",
        "owner_mailing_address": "777 Trust Ave",
        "owner_mailing_city": "Neptune Beach",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32266",
        "assessed_value": 280000,
        "land_value": 100000,
        "improvement_value": 180000,
        "year_built": 1988,
        "property_use": "SFR",
        "acres": 0.28,
        "legal_description": "LOT 7 BLOCK G TRUST SUBDIVISION",
        "exempt_homestead": True,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "trust_owned"
    },
    {
        "parcel_id": "DC-01-01-01-001-008",
        "address": "888 Pre foreclosure Ln",
        "city": "Jacksonville",
        "zip": "32210",
        "owner_name": "Michael Brown",
        "owner_mailing_address": "888 Pre foreclosure Ln",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32210",
        "assessed_value": 120000,
        "land_value": 40000,
        "improvement_value": 80000,
        "year_built": 1972,
        "property_use": "SFR",
        "acres": 0.2,
        "legal_description": "LOT 8 BLOCK H DISTRESS SUBDIVISION",
        "exempt_homestead": True,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "pre_foreclosure_distress"
    },
    {
        "parcel_id": "DC-01-01-01-001-009",
        "address": "999 Tax Delinquent Dr",
        "city": "Jacksonville",
        "zip": "32211",
        "owner_name": "Sarah Davis",
        "owner_mailing_address": "999 Tax Delinquent Dr",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32211",
        "assessed_value": 95000,
        "land_value": 35000,
        "improvement_value": 60000,
        "year_built": 1965,
        "property_use": "SFR",
        "acres": 0.25,
        "legal_description": "LOT 9 BLOCK I TAX SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "tax_delinquent"
    },
    {
        "parcel_id": "DC-01-01-01-001-010",
        "address": "111 Code Violation St",
        "city": "Jacksonville",
        "zip": "32206",
        "owner_name": "DEF Rentals LLC",
        "owner_mailing_address": "111 Code Violation St",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32206",
        "assessed_value": 75000,
        "land_value": 25000,
        "improvement_value": 50000,
        "year_built": 1955,
        "property_use": "MFR",
        "acres": 0.3,
        "legal_description": "LOT 10 BLOCK J CODE SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "code_violation_rental"
    },
    {
        "parcel_id": "DC-01-01-01-001-011",
        "address": "222 Probate Ct",
        "city": "Jacksonville",
        "zip": "32207",
        "owner_name": "Estate of William Taylor",
        "owner_mailing_address": "222 Probate Ct",
        "owner_mailing_city": "Jacksonville",
        "owner_mailing_state": "FL",
        "owner_mailing_zip": "32207",
        "assessed_value": 200000,
        "land_value": 70000,
        "improvement_value": 130000,
        "year_built": 1990,
        "property_use": "SFR",
        "acres": 0.35,
        "legal_description": "LOT 11 BLOCK K PROBATE SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "probate_inherited"
    },
    {
        "parcel_id": "DC-01-01-01-001-012",
        "address": "333 Sheriff Sale Blvd",
        "city": "Jacksonville Beach",
        "zip": "32250",
        "owner_name": "Bank of America NA",
        "owner_mailing_address": "PO Box 12345",
        "owner_mailing_city": "Charlotte",
        "owner_mailing_state": "NC",
        "owner_mailing_zip": "28255",
        "assessed_value": 380000,
        "land_value": 150000,
        "improvement_value": 230000,
        "year_built": 2002,
        "property_use": "SFR",
        "acres": 0.18,
        "legal_description": "LOT 12 BLOCK L SHERIFF SUBDIVISION",
        "exempt_homestead": False,
        "exempt_over_65": False,
        "exempt_disabled": False,
        "exempt_veteran": False,
        "exempt_agricultural": False,
        "scenario": "bank_owned_reo"
    }
]

# Write synthetic parcels
with open("scaffold/data/synthetic_parcels.jsonl", "w") as f:
    for parcel in synthetic_parcels:
        f.write(json.dumps(parcel) + "\n")

print(f"Created {len(synthetic_parcels)} synthetic parcels")

# Synthetic signals across all patterns
synthetic_signals = [
    # Lis Pendens / Pre-foreclosure signals
    {
        "signal_id": "SIG-001",
        "parcel_id": "DC-01-01-01-001-008",
        "source_id": "duval_court_records",
        "signal_type": "LIS_PENDENS",
        "signal_date": "2026-05-15",
        "party_name": "Michael Brown",
        "case_number": "2026-CA-12345",
        "document_type": "LIS PENDENS",
        "confidence": 95,
        "details": "Foreclosure complaint filed by Wells Fargo Bank"
    },
    {
        "signal_id": "SIG-002",
        "parcel_id": "DC-01-01-01-001-008",
        "source_id": "duval_official_records",
        "signal_type": "FORECLOSURE_NOTICE",
        "signal_date": "2026-05-20",
        "party_name": "Michael Brown",
        "document_type": "NOTICE OF FORECLOSURE SALE",
        "confidence": 90,
        "details": "Sale scheduled for June 15, 2026"
    },
    # Tax delinquency signals
    {
        "signal_id": "SIG-003",
        "parcel_id": "DC-01-01-01-001-009",
        "source_id": "duval_tax_collector",
        "signal_type": "TAX_DELINQUENT",
        "signal_date": "2026-04-01",
        "party_name": "Sarah Davis",
        "tax_year": "2025",
        "amount_due": 2850.00,
        "confidence": 100,
        "details": "2025 property taxes unpaid, delinquent since April 1"
    },
    {
        "signal_id": "SIG-004",
        "parcel_id": "DC-01-01-01-001-009",
        "source_id": "duval_tax_deed_sales",
        "signal_type": "TAX_DEED_SALE",
        "signal_date": "2026-06-01",
        "party_name": "Sarah Davis",
        "sale_date": "2026-07-06",
        "opening_bid": 3500.00,
        "confidence": 85,
        "details": "Tax deed sale scheduled for July 6, 2026"
    },
    # Estate / Probate signals
    {
        "signal_id": "SIG-005",
        "parcel_id": "DC-01-01-01-001-003",
        "source_id": "duval_official_records",
        "signal_type": "PROBATE_TRANSFER",
        "signal_date": "2026-03-10",
        "party_name": "Estate of Mary Johnson",
        "document_type": "DEED",
        "confidence": 80,
        "details": "Property transferred from decedent to estate"
    },
    {
        "signal_id": "SIG-006",
        "parcel_id": "DC-01-01-01-001-011",
        "source_id": "duval_court_records",
        "signal_type": "PROBATE_CASE",
        "signal_date": "2026-02-20",
        "party_name": "Estate of William Taylor",
        "case_number": "2026-CP-56789",
        "confidence": 90,
        "details": "Probate case opened, property in estate inventory"
    },
    # Code enforcement signals
    {
        "signal_id": "SIG-007",
        "parcel_id": "DC-01-01-01-001-010",
        "source_id": "duval_code_enforcement",
        "signal_type": "CODE_VIOLATION",
        "signal_date": "2026-04-15",
        "party_name": "DEF Rentals LLC",
        "case_id": "CE-2026-1234",
        "violation_type": "UNSAFE_STRUCTURE",
        "confidence": 95,
        "details": "Multiple code violations, structure deemed unsafe"
    },
    {
        "signal_id": "SIG-008",
        "parcel_id": "DC-01-01-01-001-010",
        "source_id": "duval_code_enforcement",
        "signal_type": "NUISANCE_LIEN",
        "signal_date": "2026-05-01",
        "party_name": "DEF Rentals LLC",
        "lien_amount": 12500.00,
        "confidence": 90,
        "details": "Nuisance lien recorded for unpaid code enforcement fines"
    },
    # Foreclosure sale signals
    {
        "signal_id": "SIG-009",
        "parcel_id": "DC-01-01-01-001-012",
        "source_id": "duval_foreclosure_sales",
        "signal_type": "FORECLOSURE_SALE",
        "signal_date": "2026-05-25",
        "party_name": "Bank of America NA",
        "sale_date": "2026-06-10",
        "opening_bid": 250000.00,
        "confidence": 95,
        "details": "REO foreclosure sale, bank is plaintiff"
    },
    # Trust transfer signals
    {
        "signal_id": "SIG-010",
        "parcel_id": "DC-01-01-01-001-007",
        "source_id": "duval_official_records",
        "signal_type": "TRUST_TRANSFER",
        "signal_date": "2026-01-15",
        "party_name": "The Johnson Family Trust",
        "document_type": "DEED",
        "confidence": 85,
        "details": "Property transferred into family trust"
    },
    # Senior / Distress signals
    {
        "signal_id": "SIG-011",
        "parcel_id": "DC-01-01-01-001-004",
        "source_id": "duval_official_records",
        "signal_type": "REVERSE_MORTGAGE",
        "signal_date": "2026-03-01",
        "party_name": "Robert & Susan Williams",
        "document_type": "MORTGAGE",
        "confidence": 75,
        "details": "Reverse mortgage recorded, both owners over 65"
    },
    # Investor / LLC signals
    {
        "signal_id": "SIG-012",
        "parcel_id": "DC-01-01-01-001-002",
        "source_id": "duval_official_records",
        "signal_type": "LLC_TRANSFER",
        "signal_date": "2026-04-20",
        "party_name": "ABC Investments LLC",
        "document_type": "QUIT CLAIM DEED",
        "confidence": 70,
        "details": "Property transferred between LLCs, possible wholesale"
    },
    # Additional stacked signals for high-priority leads
    {
        "signal_id": "SIG-013",
        "parcel_id": "DC-01-01-01-001-008",
        "source_id": "duval_tax_collector",
        "signal_type": "TAX_DELINQUENT",
        "signal_date": "2026-04-01",
        "party_name": "Michael Brown",
        "tax_year": "2025",
        "amount_due": 3200.00,
        "confidence": 100,
        "details": "Tax delinquency stacked with foreclosure - high distress"
    },
    {
        "signal_id": "SIG-014",
        "parcel_id": "DC-01-01-01-001-009",
        "source_id": "duval_code_enforcement",
        "signal_type": "CODE_VIOLATION",
        "signal_date": "2026-05-10",
        "party_name": "Sarah Davis",
        "case_id": "CE-2026-5678",
        "violation_type": "OVERGROWTH",
        "confidence": 80,
        "details": "Overgrown vegetation violation, possible vacancy"
    },
    {
        "signal_id": "SIG-015",
        "parcel_id": "DC-01-01-01-001-011",
        "source_id": "duval_official_records",
        "signal_type": "ESTATE_TRANSFER",
        "signal_date": "2026-04-05",
        "party_name": "Estate of William Taylor",
        "document_type": "DEED",
        "confidence": 85,
        "details": "Heir attempting to sell property from estate"
    },
    {
        "signal_id": "SIG-016",
        "parcel_id": "DC-01-01-01-001-002",
        "source_id": "duval_court_records",
        "signal_type": "EVICTION",
        "signal_date": "2026-05-20",
        "party_name": "ABC Investments LLC",
        "case_number": "2026-CC-9876",
        "confidence": 90,
        "details": "Eviction filed against tenant, rental property distress"
    },
    {
        "signal_id": "SIG-017",
        "parcel_id": "DC-01-01-01-001-005",
        "source_id": "duval_official_records",
        "signal_type": "OUT_OF_STATE_OWNER",
        "signal_date": "2026-01-01",
        "party_name": "XYZ Corp",
        "document_type": "DEED",
        "confidence": 60,
        "details": "Corporate owner based in Georgia, absentee owner"
    },
    {
        "signal_id": "SIG-018",
        "parcel_id": "DC-01-01-01-001-006",
        "source_id": "duval_official_records",
        "signal_type": "VACANT_LAND",
        "signal_date": "2026-01-01",
        "party_name": "City of Jacksonville",
        "document_type": "DEED",
        "confidence": 70,
        "details": "Government owned vacant land, potential surplus sale"
    },
    {
        "signal_id": "SIG-019",
        "parcel_id": "DC-01-01-01-001-003",
        "source_id": "duval_tax_collector",
        "signal_type": "TAX_DELINQUENT",
        "signal_date": "2026-04-01",
        "party_name": "Estate of Mary Johnson",
        "tax_year": "2025",
        "amount_due": 8500.00,
        "confidence": 100,
        "details": "Estate property with tax delinquency - motivated seller"
    },
    {
        "signal_id": "SIG-020",
        "parcel_id": "DC-01-01-01-001-012",
        "source_id": "duval_official_records",
        "signal_type": "BANK_OWNED",
        "signal_date": "2026-05-01",
        "party_name": "Bank of America NA",
        "document_type": "CERTIFICATE OF TITLE",
        "confidence": 95,
        "details": "Bank took title after foreclosure sale"
    },
    {
        "signal_id": "SIG-021",
        "parcel_id": "DC-01-01-01-001-004",
        "source_id": "duval_official_records",
        "signal_type": "SENIOR_DISTRESS",
        "signal_date": "2026-05-15",
        "party_name": "Robert & Susan Williams",
        "document_type": "LIEN",
        "confidence": 65,
        "details": "Medical lien recorded, senior owners may need to sell"
    },
    {
        "signal_id": "SIG-022",
        "parcel_id": "DC-01-01-01-001-007",
        "source_id": "duval_official_records",
        "signal_type": "TRUSTEE_SALE",
        "signal_date": "2026-04-10",
        "party_name": "The Johnson Family Trust",
        "document_type": "NOTICE OF SALE",
        "confidence": 75,
        "details": "Trustee sale notice, beneficiaries may want quick sale"
    },
    {
        "signal_id": "SIG-023",
        "parcel_id": "DC-01-01-01-001-010",
        "source_id": "duval_court_records",
        "signal_type": "JUDGMENT",
        "signal_date": "2026-03-20",
        "party_name": "DEF Rentals LLC",
        "case_number": "2026-CC-5432",
        "judgment_amount": 45000.00,
        "confidence": 90,
        "details": "Civil judgment against LLC owner, financial distress"
    },
    {
        "signal_id": "SIG-024",
        "parcel_id": "DC-01-01-01-001-005",
        "source_id": "duval_code_enforcement",
        "signal_type": "CODE_VIOLATION",
        "signal_date": "2026-04-25",
        "party_name": "XYZ Corp",
        "case_id": "CE-2026-9012",
        "violation_type": "ZONING_VIOLATION",
        "confidence": 85,
        "details": "Commercial zoning violation, corporate owner out of state"
    }
]

# Write synthetic signals
with open("scaffold/data/synthetic_signals.jsonl", "w") as f:
    for signal in synthetic_signals:
        f.write(json.dumps(signal) + "\n")

print(f"Created {len(synthetic_signals)} synthetic signals")

# Create synthetic expectations
synthetic_expectations = {
    "total_parcels": 12,
    "total_signals": 24,
    "expected_leads": {
        "high_stack": 3,
        "medium_stack": 5,
        "single_signal": 7,
        "enrichment_only": 3
    },
    "deal_path_distribution": {
        "wholesale": 4,
        "flip": 3,
        "sub_to": 2,
        "seller_finance": 1,
        "partial_interest": 1,
        "messy_title": 2,
        "rental_acquisition": 2,
        "dispo_only": 1,
        "do_not_pursue": 0
    },
    "score_distribution": {
        "90_100": 2,
        "80_89": 4,
        "70_79": 5,
        "60_69": 3,
        "below_60": 0
    },
    "lead_patterns": {
        "pre_foreclosure": 2,
        "tax_delinquent": 3,
        "estate_probate": 3,
        "code_violation": 3,
        "foreclosure_sale": 1,
        "trust_owned": 1,
        "senior_distress": 1,
        "investor_llc": 2,
        "out_of_state": 1,
        "vacant_land": 1,
        "bank_owned": 1,
        "judgment_lien": 1
    },
    "source_coverage": {
        "duval_official_records": 8,
        "duval_court_records": 4,
        "duval_tax_collector": 3,
        "duval_tax_deed_sales": 1,
        "duval_foreclosure_sales": 1,
        "duval_code_enforcement": 4
    },
    "test_assertions": [
        "All parcels have valid parcel_id matching DC- prefix",
        "All signals reference valid parcel_id from synthetic_parcels",
        "No signal has confidence below 60",
        "High-stack leads (3+ signals) score above 85",
        "Tax delinquent signals have amount_due > 0",
        "Foreclosure signals have case_number or sale_date",
        "Estate signals contain 'Estate of' or 'Trust' in party_name",
        "Code violation signals have case_id and violation_type"
    ],
    "build_timestamp": "2026-06-08T06:49:34+05:30",
    "framework_version": "v5.3.1"
}

with open("scaffold/data/synthetic_expectations.json", "w") as f:
    json.dump(synthetic_expectations, f, indent=2)

print(f"Created synthetic expectations")
print(f"\nSynthetic data harness complete:")
print(f"  - {len(synthetic_parcels)} parcels")
print(f"  - {len(synthetic_signals)} signals")
print(f"  - {len(synthetic_expectations['test_assertions'])} test assertions")

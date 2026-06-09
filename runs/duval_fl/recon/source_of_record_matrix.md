# Source-of-Record Matrix — duval_fl

Framework v5.4.0 · Generated 2026-06-09T06:47Z · State rule family `FL_judicial_foreclosure`

Legend:  ✅ live · 🔒 needs login · 🚧 stub / extractor missing · 📨 PRR required · ⚪ N/A in state · ❓ not found

| # | Lead type | State applicability | Selected source | Status |
|---|---|---|---|---|
| 1 | Foreclosure | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 2 | Trustee Sale | NOT_APPLICABLE_IN_STATE | — | ⚪ |
| 3 | Notice of Trustee Sale | NOT_APPLICABLE_IN_STATE | — | ⚪ |
| 4 | Notice of Substitute Trustee Sale | NOT_APPLICABLE_IN_STATE | — | ⚪ |
| 5 | Sheriff Sale | APPLICABLE | duval_foreclosure_sales_scrappey | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 6 | Tax Lien Foreclosure | APPLICABLE | duval_tax_deed_sales | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 7 | Tax Sale | APPLICABLE | duval_tax_deed_sales | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 8 | Tax Sale Certificate | APPLICABLE | duval_tax_collector | 🚧 NEEDS_OPERATOR_REVIEW |
| 9 | Tax Delinquency | APPLICABLE | duval_tax_collector | 🚧 NEEDS_OPERATOR_REVIEW |
| 10 | Lis Pendens | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 11 | Civil Judgment | APPLICABLE | duval_court_records | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 12 | Abstract of Judgment | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 13 | Mechanic Lien | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 14 | Construction Lien | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 15 | Federal Tax Lien | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 16 | State Tax Lien | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 17 | Probate | APPLICABLE | duval_official_records (+ court_records limited) | ✅ LIVE_SOURCE_FOUND_LIMITED_COVERAGE |
| 18 | Affidavit of Heirship | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 19 | Executor Deed | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 20 | Administrator Deed | APPLICABLE | duval_official_records | ✅ LIVE_SOURCE_FOUND |
| 21 | Code Lien | APPLICABLE | duval_official_records (+ code_enforcement) | ✅ LIVE_SOURCE_FOUND_LIMITED_COVERAGE |
| 22 | Demolition | APPLICABLE | duval_code_enforcement | 📨 NEEDS_OPERATOR_REVIEW |
| 23 | Condemnation | APPLICABLE | duval_code_enforcement | 📨 NEEDS_OPERATOR_REVIEW |
| 24 | Eviction | APPLICABLE | duval_court_records | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 25 | Divorce | APPLICABLE | duval_court_records | 🔒 SOURCE_FOUND_NEEDS_LOGIN |
| 26 | Bankruptcy | APPLICABLE (federal) | — | ❓ SOURCE_NOT_FOUND (PACER out of county scope) |
| 27 | Surplus | APPLICABLE | duval_court_records | 🔒 SOURCE_FOUND_NEEDS_LOGIN |

## Headline

* **11 of 24 in-scope lead types are live today**, all routed through `duval_official_records` (county clerk recordings via GridResults API).
* **3 lead types** are not applicable in Florida (non-judicial-state trustee-sale concepts).
* **8 lead types** are blocked behind login walls on clerk court / RealAuction portals, pending credential rotation + Stage B unblock.
* **3 lead types** are stubbed (tax collector / code enforcement) and need Stage C work or a PRR.
* **1 lead type** (Bankruptcy) is federal and not addressable at the county scope.

Full schema-validated detail in `source_of_record_matrix.json`.

# Source coverage map — duval_fl

Framework v5.4.0 · Generated 2026-06-09T06:47Z

## live_sources

* `duval_official_records` — verified `OPEN_PUBLIC` access, `FULL_COUNTY_BULK` extractability via GridResults API. Carries 11 lead types directly and supplements 2 more.

## blocked_sources

* `duval_court_records` — `LOGIN_REQUIRED`. Existing scraper uses hardcoded operator credentials; rotation pending. Carries 5 lead types (Civil Judgment, Probate-court, Eviction, Divorce, Surplus, Foreclosure-court).
* `duval_tax_deed_sales` — `LOGIN_REQUIRED`. Same credential rotation gating. Carries Tax Lien Foreclosure, Tax Sale.
* `duval_foreclosure_sales_scrappey` — `LOGIN_REQUIRED` plus missing `SCRAPPEY_API_KEY`. Carries Sheriff Sale.
* `duval_code_enforcement` — `BLOCKED` pending operator-submitted public-records request. Carries Demolition, Condemnation, primary Code-Lien path.

## limited_coverage_sources

* `duval_official_records` for Probate and Code Lien — surfaces recorded documents only; companion court / code-enforcement signals required for full enrichment.

## not_found_lead_types

* Bankruptcy — federal jurisdiction (US Bankruptcy Court, Middle District of FL via PACER). Out of county scope.

## operator_review_required

* `duval_tax_collector` (Tax Sale Certificate, Tax Delinquency) — portal open, no working extractor.
* `duval_parcel_master` (enrichment) — portal open, scraper is a stub. Required for parcel-ID resolution but not lead-generating.
* `duval_gis` (enrichment) — portal open, current scraper is a deceptive stub returning zero records without a request (§4.33 violation).

## Stage B unblock list (post Review Gate 1)

1. Rotate `Heyheyhey@1`, add as repo secrets, scrub from `scrapers/duval_court_records.py`, `scrapers/duval_tax_deed_sales.py`, `scrapers/duval_foreclosure_sales_scrappey.py`.
2. Rotate Browserless token, add as repo secret, scrub from the five scrapers that hardcode it today.
3. Decide per source whether to use operator-credentialed-login posture (§4.16 Partial Build Contract permits it under recorded operator override) or the public no-login path.
4. Build & ship the `duval_official_records` v5.4.0 thin slice first; everything else sequenced behind it.

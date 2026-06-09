# API discovery report — duval_fl

Framework v5.4.0 · Generated 2026-06-09T06:47Z

v5.3.0 introduced a mandatory documented-API search for every candidate source. Each source's base domain plus `/api`, `/swagger`, `/docs`, `/api-docs`, `/openapi.json`, plus public Postman and GitHub searches are required.

## Searches attempted

| Source | base + /api | /swagger | /docs | /api-docs | /openapi.json | Postman | GitHub |
|---|---|---|---|---|---|---|---|
| duval_official_records | inspected (GridResults endpoint) | — | — | — | — | not found | not found |
| duval_court_records | not attempted (login wall) | not attempted | not attempted | not attempted | not attempted | not attempted | not attempted |
| duval_foreclosure_sales_scrappey | not attempted (vendor) | — | — | — | — | not attempted | not attempted |
| duval_tax_deed_sales | not attempted (vendor) | — | — | — | — | not attempted | not attempted |
| duval_parcel_master | not attempted | — | — | — | — | not attempted | not attempted |
| duval_tax_collector | not attempted | — | — | — | — | not attempted | not attempted |
| duval_gis | ArcGIS REST conventions plausible at `services.arcgis.com/<org>/...` — not yet probed | n/a | n/a | n/a | n/a | not attempted | not attempted |
| duval_code_enforcement | n/a (PRR path) | — | — | — | — | — | — |

## Found APIs

### `duval_official_records` — GridResults endpoint

* **Endpoint family:** `https://or.duvalclerk.com/.../GridResults` (Tyler/CivilServe-style)
* **API type:** REST (JSON over HTTPS)
* **Documentation:** none public — discovered via network inspection of the portal search UI
* **Auth required:** false (public portal)
* **Rate limited:** unknown; treat as best-effort, throttle to ~1 request / 2 seconds in Stage B
* **Source role:** PRIMARY_EVENT_SOURCE
* **Notes:** Returns paginated record arrays with `record_date`, `doc_type`, `party_name`, `instrument_number`, `book/page`, `consideration`, `case_number`. This is the de facto API powering the Stage B thin slice.

## Backlog (Stage B / Stage C)

* Probe `services.arcgis.com` for a Duval property service that exposes parcels + zoning + flood layers as REST feature services. ArcGIS REST is documented and rate-limited but usually open.
* Inspect `core.duvalclerk.com` and `paopropertysearch.coj.net` network traffic for hidden JSON endpoints once an exploratory budget is approved.
* Inspect `realtaxdeed.com` and `realforeclose.com` for any unauthenticated calendar / sale-list endpoints.

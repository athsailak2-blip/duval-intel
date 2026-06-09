# duval_fl backlog

Deferred follow-ups not in Phase 0 PR1. These are tracked here rather than as TODO comments in code, to keep the framework-patch backlog auditable.

## P0 — must clear before Stage B begins

* **Rotate `Heyheyhey@1` password** used in `scrapers/duval_court_records.py`, `scrapers/duval_tax_deed_sales.py`, `scrapers/duval_foreclosure_sales_scrappey.py`. Add as repo secrets. Scrub literals.
* **Rotate Browserless API token** used in five duval scrapers. Add as repo secret. Scrub literal.

## P1 — Stage B scope (separate PR set)

* Schema-compliance rewrite of `config/counties/duval_fl.json`. The current shape is invalid against `config/counties/_schema.json` in several ways and PR1 only patched the verdict + recon blocks:
  * Top-level: `county_id` is `"12031"` but schema pattern requires `^[a-z][a-z0-9_]+$` (use `duval_fl`).
  * Top-level: `framework_version`, `slug`, `state_full` are not in the schema's allowed top-level properties (`additionalProperties: false`). Move `state_full` to `subject_state_full`; drop `slug` (use `county_id`); drop `framework_version` (canonical home is `FRAMEWORK_VERSION.json`).
  * Per-source required fields missing: `category`, `subtype`, `access_pattern`, `scraper_module`, `refresh_cadence`. Note `refresh_frequency` is currently used but schema requires `refresh_cadence`.
  * Per-source enum drift: `lead_value: "PRIMARY"` → `LEAD_GENERATING`; `source_role: "TIER_1"` → `PRIMARY_LEAD_SOURCE`; `access_method: "web_portal"` → `OPEN_PUBLIC_PORTAL`; `public_access_status: "FULLY_OPEN"` → `FULL_PUBLIC_ACCESS`; `document_access_status: "FULL_TEXT"` → `DOCUMENTS_PUBLIC`; `verification_confidence: "VERIFIED"` → `HIGH`; `verification_method: "LIVE_PORTAL"` → `manual_operator_verified`; `build_priority: <integer>` → string enum (`mvp_required` etc.).
  * `dashboard` requires top-level `primary_color` + `accent_color` (currently nested under `theme`).
  * `deployment` requires `github_org` (currently only `github_repo`).
  * This rewrite must be done with `scaffold/ops/write_county_config.py` per §4.28; the writer is local-Python only, so the Stage B PR should add a workflow step that runs the writer (or document the manual operator step).
* Replace `duval_gis.py` deceptive stub with a real ArcGIS REST query, or disable the source until implemented.
* Switch dashboard primary entry point from `dashboard/index.html` (legacy schema) to `dashboard/dashboard.js` (v5.4.0 record schema), and add the "new since yesterday's run" default chip per acceptance criteria.
* Resolve pipeline duplication: today `scripts/aggregate_data.py` (legacy) and `scaffold/pipeline/build_leads.py` (v5.4.0) both target `data/leads.json`. Pick one (build_leads.py), retire the other.
* Replace `.github/workflows/deploy.yml` silent `||` fallbacks with explicit job-level error surfacing (§4.33 hard rule: no silent stubs).
* Rewrite `scrapers/duval_official_records.py` to the §4.32 wrapped raw-record shape; emit to `data/raw/duval_official_records.jsonl`.
* Add the §4.39 semantic verifier specialized for duval_fl.

## P2 — Stage C scope (one PR per source)

* Court records, tax deed sales, foreclosure sales, parcel master, tax collector, GIS, code enforcement — each sequenced behind its own approval gate.

## P3 — exploratory

* Bankruptcy enrichment via PACER, if operator authorizes a federal-scope addition.
* `services.arcgis.com` probe for documented ArcGIS REST endpoints that could replace per-source web-scraping.

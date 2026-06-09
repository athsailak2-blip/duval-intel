# Operator notes — duval_fl

This file is an append-only operator notebook. New entries go at the bottom of the relevant section with an ISO timestamp. Do not edit historical entries — add corrections as new entries instead.

---

## general

* **2026-06-09T06:47Z** — Phase 0 redo initiated under framework v5.4.0. Original recon was older and missing all v5.4.0-mandated artifacts.
* **2026-06-09T06:47Z** — Operator (Sai, `athsailak2-blip`) confirms the GitHub personal access token that was previously pasted in chat has been **revoked**. No secret value is recorded in this file. All future GitHub writes use the MCP-mediated authentication path, not that PAT.
* **2026-06-09T06:47Z** — Operator commits to **rotating the password** that appears hardcoded in three duval scrapers (`scrapers/duval_court_records.py`, `scrapers/duval_tax_deed_sales.py`, `scrapers/duval_foreclosure_sales_scrappey.py`) **before Stage B begins**, and to supplying the new credentials only as GitHub repository secrets. The hardcoded literal must be removed from those files in the Stage B PR. No password value is recorded here.
* **2026-06-09T06:47Z** — Operator commits to **rotating the Browserless API token** currently hardcoded in five scrapers and supplying the new token as a repo secret before Stage B. No token value is recorded here.
* **2026-06-09T06:47Z** — Operator on free GitHub plan; repo is acceptable as public. License/proprietary concerns explicitly de-scoped by operator for this engagement.
* **2026-06-09T06:47Z** — Acceptance criteria stated by operator: "Every day the investor should see all the leads that were there in the last day, and it should have all the information." Interpreted as: dashboard default view filters to records with `first_seen_at >= now - 24h`; row content satisfies the §4.17 Evidence-First Row Contract. Captured in `LAUNCH_DUVAL_FL.md` §6.

## duval_official_records

* **2026-06-09T06:47Z** — Verified live. `or.duvalclerk.com` GridResults API responds to date-range queries and returns ~534 records on a typical weekday. This is the one source that satisfies all five verification layers under §4.7 today.
* **2026-06-09T06:47Z** — Current scraper (`scrapers/duval_official_records.py`) works but emits unwrapped records. Stage B must rewrite to the §4.32 wrapped raw-record shape emitting to `data/raw/duval_official_records.jsonl`.

## duval_court_records

* **2026-06-09T06:47Z** — `core.duvalclerk.com` portal exists and is functionally accessible to humans, but the operator's scraper is currently configured to use a personal username/password rather than going through the public search path. Source posture is reclassified `DOCUMENTS_LOGIN_REQUIRED` until either (a) the public no-login path is verified to expose the same records, or (b) operator credentials are rotated and added as repo secrets and §4.16 operator-credentialed-login posture is explicitly logged.
* **Open question:** does the public no-login path on CORE return the same docket records as the logged-in path? Recon could not confirm without operator approval to exercise the login.

## duval_tax_deed_sales

* **2026-06-09T06:47Z** — `www.duval.realtaxdeed.com` (RealAuction). Same hardcoded-credentials posture as court_records. Public sale calendar and List of Lands Available may be viewable without registration — to be confirmed in Stage B recon.

## duval_foreclosure_sales_scrappey

* **2026-06-09T06:47Z** — `www.duval.realforeclose.com` (RealAuction). Scraper uses Scrappey vendor and the same hardcoded credentials. Missing `SCRAPPEY_API_KEY` env var. Public sale calendar may be viewable without registration — to be confirmed.

## duval_parcel_master

* **2026-06-09T06:47Z** — `paopropertysearch.coj.net` (Duval Property Appraiser). Portal is fully public, searchable by RE#, owner, address. Current scraper is a stub that does not query the portal. Stage C work item.

## duval_tax_collector

* **2026-06-09T06:47Z** — `tclieninfo.coj.net`. Portal is public. Current scraper is a stub. Bulk parcel lien data availability is unconfirmed — see open question in source-of-record matrix.

## duval_gis

* **2026-06-09T06:47Z** — `maps.coj.net/duvalproperty/`. ArcGIS-based. Current scraper returns `status: "healthy"` and `records_fetched: 0` without making a request to the portal — this is a §4.33 hard-rule violation (deceptive stub) and must be replaced with either a real ArcGIS REST query in Stage C or removed from the active source list.

## duval_code_enforcement

* **2026-06-09T06:47Z** — `www.jacksonville.gov/.../municipal-code-compliance`. Case detail requires a public-records request (PRR) via `records.coj.net`. Falls under §4.23 manual-assisted-pull pattern. Not blocking the Stage B partial build; sequence after operator submits a PRR in Stage C.

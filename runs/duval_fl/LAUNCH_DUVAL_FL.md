# Phase 0 Recon Launch — Duval County, FL

| Field | Value |
|---|---|
| County slug | `duval_fl` |
| County name | Duval |
| State | FL (Florida) |
| FIPS | 12031 |
| State rule family | `FL_judicial_foreclosure` |
| Framework version target | v5.4.0 |
| Target county config | `config/counties/duval_fl.json` |
| Recon launched | 2026-06-09 |
| Operator | Sai (`athsailak2-blip`) |
| Build verdict (current) | `PARTIALLY_RESOLVED_BUILDABLE` |

---

## 1. Why this Phase 0 redo exists

The original recon for duval_fl was performed under an older framework cycle. The county config was marked `READY_TO_BUILD` despite seven of the eight declared sources being non-functional, and none of the v5.4.0-mandated recon artifacts (source-of-record matrix, source coverage map, API discovery report, build eligibility report, per-source fingerprints, operator-verified sources index) were present in the repository.

This PR re-runs Phase 0 honestly and produces those artifacts. It does **not** change any scraper, pipeline, dashboard, or workflow code. The intent is to lock in the truth about what the county actually has, surface the gaps to the operator, and gate the next implementation slice behind an explicit Review Gate 1 sign-off.

## 2. Scope of this PR (PR1)

* **In scope (docs + honest config only):**
  * `runs/duval_fl/LAUNCH_DUVAL_FL.md` (this file)
  * `runs/duval_fl/operator_notes.md` (operator-facing notebook, seeded)
  * `runs/duval_fl/recon/source_of_record_matrix.{json,md}` (27-lead-type sweep)
  * `runs/duval_fl/recon/source_coverage_map.md` (live vs blocked vs limited)
  * `runs/duval_fl/recon/api_discovery_report.md` (documented-API search log)
  * `runs/duval_fl/recon/build_eligibility_report.md` (verdict justification)
  * `runs/duval_fl/recon/operator_verified_sources.yml` (8 URLs the operator surfaced)
  * `runs/duval_fl/recon/fingerprints/*.json` (per-source vendor/access fingerprints)
  * `runs/duval_fl/gates/REVIEW_GATE_1.signoff.json` (in `pending` state)
  * `runs/duval_fl/backlog/README.md` (deferred follow-ups, including the full schema-compliance config rewrite)
  * `config/counties/duval_fl.json` (minimal honest update — verdict, recon blocks, state_rule_family)

* **Out of scope (deferred to subsequent stages):**
  * Any change to scraper code under `scrapers/`
  * Any change to pipeline code under `scaffold/pipeline/` or `scripts/`
  * Any change to dashboard code under `dashboard/`
  * Any change to `.github/workflows/`
  * Full schema-compliance rewrite of `config/counties/duval_fl.json` — see `runs/duval_fl/backlog/README.md` for the deferred surgery list
  * Credential rotation (`Heyheyhey@1`, Browserless token) — operator action item, then Stage B

## 3. Five-layer source verification (v5.4.0)

For every candidate source per lead type, recon must satisfy five independent checks:

1. **Authority** — Is the entity behind this source the lawful authority for this lead type in this jurisdiction? (clerk for recordings, court for cases, sheriff/clerk for sales, etc.)
2. **Lead-type relevance** — Does this source actually carry records of this specific lead type today? (verified against a live record, not just a homepage description)
3. **Access** — Is the source publicly accessible without paid subscription, login, or captcha that cannot be programmatically traversed under the locked framework rules?
4. **Extractability** — Can records be programmatically extracted at scale (API, CSV, structured HTML), or only viewed per-record?
5. **Refresh provenance** — Can we determine when a given record was added or last changed, so we can drive a daily-delta pipeline?

A source is `LIVE_SOURCE_FOUND` only when all five layers are green. Partial green produces `LIVE_SOURCE_FOUND_LIMITED_COVERAGE` or one of the blocked states.

## 4. Build Mode Approval Gate format

Per framework §4.15, no scraper, translator, pipeline, or dashboard change may be made under the duval_fl banner until the operator signs `runs/duval_fl/gates/REVIEW_GATE_1.signoff.json`. The signoff file is committed in `pending` state by this PR; the operator flips it to `accepted` (with name + timestamp) in a separate commit after reviewing the recon outputs.

Do Not Proceed Matrix (§4.11) — the following conditions in the matrix are currently triggered for duval_fl and must remain blocking until cleared:

* Sources marked `DOCUMENTS_LOGIN_REQUIRED` while their corresponding scraper carries leaked credentials → blocked (rotate credentials, add as repo secrets, re-verify).
* Sources marked as `LIVE_SOURCE_FOUND` only by an unverified scraper that returns `records_fetched: 0` without making a request → blocked (§4.33 hard rule: no deceptive stubs).
* `state_rule_family` unset or wrong → blocked (this PR fixes it).
* Framework version drift between `FRAMEWORK_VERSION.json` and `config/counties/duval_fl.json` → blocked (this PR fixes it).

## 5. Honest build verdict (§4.10, §4.16)

Applying the §4.10 verdict enum and the §4.16 Partial Build Contract:

* **One verified primary source:** `duval_official_records` — full county bulk via GridResults API on `or.duvalclerk.com`, refreshable daily, evidence of recording back to 1988.
* **Seven blocked or stubbed sources:** see `build_eligibility_report.md` for the per-source justification.
* **Verdict:** `PARTIALLY_RESOLVED_BUILDABLE` — the county can ship a Partial Build labeled "Official Records live" (Stage B), with other sources sequenced behind their unblockers.

This verdict explicitly does NOT authorize a Full Build dashboard. Any dashboard rendered while only `duval_official_records` is live must carry the `PARTIAL_BUILD` label per §4.16, and must clearly communicate to the investor which lead types are sourced and which are not yet covered.

## 6. Acceptance criteria captured from operator

Operator stated 2026-06-09: "Every day the investor should see all the leads that were there in the last day, and it should have all the information."

Resolution: in Stage B the dashboard's default view will filter `records[]` to those with `first_seen_at >= now - 24h` (i.e. new since yesterday's pipeline run). Cumulative views remain accessible via chip switcher. "All the information" is interpreted as the full §4.17 Evidence-First Row Contract: address, owner, parcel ID, signal type, doc number, recording/file date, source, source URL, source reliability grade, score breakdown, and evidence-ledger pointer.

## 7. Next gates

* **Review Gate 1 (this PR + signoff):** operator reviews the recon outputs, flips `REVIEW_GATE_1.signoff.json` to `accepted`.
* **Stage B (separate PR set):** rotate `Heyheyhey@1` and Browserless token; add as repo secrets; rewrite `duval_official_records.py` to the §4.32 wrapped raw-record shape; build the official-records translator per §4.36 debtor party rules; switch the dashboard to v5.4.0 record shape; add the "last 24h" default chip; ship `PARTIAL_BUILD — Official Records live`.
* **Stage C (separate PR set per source):** sequence court_records → tax_deed_sales → foreclosure_sales → parcel_master → tax_collector → gis_mapping → code_enforcement (PRR), each behind its own approval gate.

---

*Generated by Phase 0 redo, 2026-06-09. Framework v5.4.0. No code changes in this PR.*

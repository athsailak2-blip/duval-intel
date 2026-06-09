# Build eligibility report — duval_fl

Framework v5.4.0 · Generated 2026-06-09T06:47Z

## Verdict

**`PARTIALLY_RESOLVED_BUILDABLE`** under §4.10 + §4.16.

## Justification

### Counts

* Declared sources: **8**
* Verified live (all 5 layers green): **1** (`duval_official_records`)
* Verified live with limited coverage: **0** (the 2 limited-coverage entries reuse the live source)
* Blocked on credentials / login: **3** (court_records, tax_deed_sales, foreclosure_sales_scrappey)
* Blocked on stub / no extractor: **3** (parcel_master, tax_collector, gis)
* Blocked on public-records request: **1** (code_enforcement)

### §4.16 Partial Build Contract check

A Partial Build is shippable if and only if **at least one P0 distress source is verified live and produces records satisfying the §4.17 Evidence-First Row Contract**. `duval_official_records` satisfies that requirement for Lis Pendens, Construction Lien, Mechanic Lien, Federal/State Tax Lien, Abstract of Judgment, Affidavit of Heirship, Executor Deed, Administrator Deed, Probate-recorded, and Code-Lien-recorded leads. ✅

### §4.11 Do Not Proceed Matrix check (current state)

| Matrix condition | Triggered? | Resolution |
|---|---|---|
| No P0 distress source unblocked | ❌ no | `duval_official_records` is unblocked |
| Deceptive stub returning `status: healthy, records_fetched: 0` | ⚠️ yes (`duval_gis`) | Disable from active list or replace in Stage C; not blocking partial build |
| Hardcoded credentials in repo | ⚠️ yes (3 scrapers) | Operator committed to rotate before Stage B begins |
| `state_rule_family` unset / wrong | ✅ resolved by this PR (now `FL_judicial_foreclosure`) | — |
| Framework version drift | ✅ will resolve by Stage B (v5.4.0 stamp aligned) | — |
| Schema-invalid county config | ⚠️ yes (top-level + per-source enum drift) | Deferred to follow-up PR, logged in backlog |
| Recon artifacts missing | ✅ resolved by this PR | — |

### Honesty notes (§4.5 Autonomous First-Run guardrails)

* No source was upgraded from BLOCKED to LIVE without an in-session verification.
* No "likely works" claims appear in the matrix — every PASS is keyed to an observed behavior or a recorded historical observation.
* `duval_gis` was deliberately NOT graded LIVE despite the existing scraper claiming `status: healthy`; the scraper does not make a request and therefore has no honest evidence.

## Build label

When Stage B ships, the dashboard must carry `build_label: PARTIAL_BUILD` with reason `Official Records live; 7 other sources sequenced behind credential rotation, stub replacement, and PRR.` This label is mandatory until the source coverage map shows ≥4 live sources spanning ≥2 source families (recordings + court at minimum).

## Next gate

Operator signs `runs/duval_fl/gates/REVIEW_GATE_1.signoff.json` (`status: pending` → `status: accepted`) after reviewing this report and the source-of-record matrix. Stage B may not begin before that signoff is committed to `main`.

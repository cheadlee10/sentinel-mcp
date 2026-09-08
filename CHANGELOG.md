# Changelog

## 1.5.1 — current production release

- Added the source-backed `wa_research_packet` workflow and immutable captured
  permit-history tool `wa_property_changes`; the keyed catalog now contains
  fourteen tools while the no-key catalog remains three deterministic calculators.
- Added environmental `wa_site_context`, aggregate housing/transit/school-program
  `wa_local_context`, and bounded `wa_permit_history` coverage with source-specific
  dates, qualifications and unavailable states.
- Added shared customer answer caps, explicit field evidence and data-quality
  states, and kept unavailable research and validation failures unmetered.
- Added the current guided setup, synthetic evidence demo and offline starter
  validator. The $250 one-time 30-day integration pilot is unchanged.

See the hosted [API changelog](https://sentineliq.net/docs/api-changelog.md) for
the complete 1.3.0–1.5.1 contract history.

## 1.2.0 — API and MCP workflow release

- Added seller scenarios, offer comparison, monthly-payment estimates and a
  seller packet with structured output and report text.
- Added the 2026-07-28 MCP discovery/request format while retaining the supported
  2025-03-26 and 2025-06-18 initialize paths; no legacy SSE endpoint.
- Made account quota reservation atomic and exposed the actual trial/daily
  allowance. Failed answers and identity/discovery probes are unmetered.
- Added a developer-only account and console journey, an actual calculator
  preview and a $250 one-time, 30-day pilot for one account/five integration keys.
  Checkout appears only when configured; manual setup remains available.
- Limited listing output to the licensed cached subset. Null means no licensed
  listing on file; links, photos and portal valuations remain excluded.
- Added explicit provenance status and notes for legacy building attributes.
  Cached values may include earlier enrichment and are not independently
  verified field by field. Known portal backfills are omitted; current listing
  overrides are replaced with cached values. This corrects the earlier claim
  below that every physical attribute was a verified county original.
- Omitted payoff and seller credits now mean unknown. Scenario differences
  carry a comparable flag and nullable amount. Offer comparisons identify when
  differences are before an unknown shared mortgage payoff.


Version numbers match `info.version` in the public OpenAPI document at
`GET https://app.sentineliq.net/api/v1/agent-api/openapi.json`, and the
`serverInfo.version` returned by both MCP transports.

Seeded from the service's internal `docs/API_CHANGELOG.md`; the two are kept in
step.

---

## 1.1.0 — 2026-09-01

**Breaking for callers written against 1.0.** Everything below ships in one
deploy; there is no 1.0 compatibility window for the removed fields.

### Added

- `POST /api/v1/mcp/public` — the three calculators (`wa_reet`, `wa_net_sheet`,
  `nwmls_deadlines`) with no key, no account, 60/min and 500/day per IP.
- `GET /api/v1/agent-api/openapi.json` — public, cacheable OpenAPI 3.1 document
  for the whole developer surface.
- `POST /api/v1/public/net-sheet` — keyless seller net sheet.
- Headers on every response: `X-Request-Id`, `X-RateLimit-Remaining`, and
  `X-Quota-Remaining` on keyed routes (`0` on 402 and quota 429).
- `coverage_note` on property responses, naming the fields a county extract
  lacks.
- **413 PAYLOAD_TOO_LARGE** on both JSON-RPC transports for bodies over 64 KB.

### Removed from `GET /v1/property` and the `wa_property_lookup` MCP tool

The initial 1.1.0 contract removed the following fields from the `property`
object. Version 1.2.0 restores a licensed listing subset and corrects the
original county-only provenance claim; see the current README for the contract.

| Field | Why |
|---|---|
| `list_price` | Listing-portal content — Zillow ToU §5 bars redistribution; Apify licenses nothing. |
| `listing_status` | same |
| `dom` | same |
| `listing_url` | same |
| `photo_url` | same |
| `listing_source` | same |
| `listing_last_seen` | same |
| `avm_value` | Portal automated valuation — same terms. |
| `county_beds` | Folded into `beds`; historical field provenance was not recorded. |
| `county_baths` | Folded into `baths`. |
| `county_sqft` | Folded into `sqft`. |

The 1.1.0 implementation attempted to isolate cached building attributes from
listing overrides. These historical attributes cannot all be represented as
verified assessor values. The current contract exposes that limitation through
`interior_provenance_status` and `provenance_note`, and suppresses known portal
backfills.

Owner identity fields (owner or taxpayer name, mailing address, owner-status
classification) and equity estimates are not included in this version.

### Changed

- `property.source` is a prose county attribution label (for example
  `King County GIS Center parcel data and King County Assessor records, as of
  2026-08-01`) instead of the `county (YYYY-MM-DD)` string 1.0 returned.
- `whoami.requests_today` no longer counts the current request — `GET /v1/whoami`
  is free and unmetered, and runs on its own burst-only rate-limit bucket, so
  polling it can never drain the metered endpoints' per-key budget.
- A valid key on a lapsed plan with the free answers spent now returns
  **402 PLAN_REQUIRED** (with `upgrade_url`) instead of 401. Keys are never
  revoked by plan state: the same key answers again as soon as a plan is active.
- **404 NOT_FOUND** and **422 VALIDATION** answers are never metered.
- Burst rate-limit 429s return `{"detail": {"code": "RATE_LIMITED", "message": …}}`
  — an object, where 1.0 returned a bare string in `detail`.
- `attributions[]` is present on every response. Entries with `"required": true`
  must be reproduced wherever the data is shown.
- `POST /public/reet` and `POST /public/deadlines` now return the same payload
  as their keyed and MCP counterparts: the existing keys are unchanged, with
  `disclaimer` and `attributions[]` added.

### Error envelope

Every 4xx on this surface is `{"detail": {"code", "message", "upgrade_url"?}}`.
Codes: `VALIDATION`, `NOT_FOUND`, `AMBIGUOUS_ADDRESS`, `INVALID_KEY`,
`PLAN_REQUIRED`, `TRIAL_QUOTA_EXHAUSTED`, `QUOTA_EXCEEDED`, `RATE_LIMITED`,
`PAYLOAD_TOO_LARGE`. FastAPI's default `HTTPValidationError` list shape is not
returned anywhere and no longer appears in the OpenAPI document.

`operationId`s are stable camelCase names (`agentApiProperty`, `publicReet`, …)
rather than generated Python function/path mashups, so a regenerated client
keeps its method names.

---

## 1.0.0

Predates this changelog. It is the version running in production until the
1.1.0 deploy.

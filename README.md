# SENTINEL Washington Real Estate MCP

Source-dated Washington property evidence and transaction math for software and
compatible AI assistants. One REST and MCP service combines supported county
facts, permit and site context, REET, seller calculations and bounded research
packets. It complements licensed MLS data; it does not replace an MLS feed.

[Developer guide](https://sentineliq.net/developers?utm_source=github&utm_medium=referral&utm_campaign=sentinel_api_launch_202609&utm_content=github_readme) ·
[Console](https://sentineliq.net/developers/console) ·
[OpenAPI](https://app.sentineliq.net/api/v1/agent-api/openapi.json) ·
[Developer terms](https://sentineliq.net/developers/terms)

## Try without an account

```bash
curl -s https://app.sentineliq.net/api/v1/public/reet \
  -H 'Content-Type: application/json' \
  -d '{"sale_price":750000,"county":"king"}'
```

Worked example: $8,655 state REET + $3,750 county-level local REET + $5 technology
fee = **$12,410 estimated total**. The full response includes the tax bands,
scope, assumptions, disclaimer and attribution. This is an estimate for a
standard residential transfer; verify the location code and applicable rules.

## Tools

| MCP name | Keyed REST path after /api/v1/agent-api/v1 | Access |
|---|---|---|
| wa_research_packet | POST /research-packet | Key |
| wa_property_changes | POST /property-changes | Key |
| wa_local_context | GET /local-context | Key |
| wa_site_context | GET /site-context | Key |
| wa_reet | POST /reet | Public or key |
| wa_net_sheet | POST /net-sheet | Public or key |
| nwmls_deadlines | POST /deadlines | Public or key |
| wa_property_lookup | GET /property | Key |
| wa_permit_history | GET /permit-history | Key |
| wa_market_snapshot | GET /market | Key |
| wa_compare_seller_scenarios | POST /seller-scenarios | Key |
| wa_compare_offers | POST /offers/compare | Key |
| wa_monthly_payment | POST /monthly-payment | Key |
| wa_seller_packet | POST /seller-packet | Key |

The three public REST calculators use /api/v1/public/ instead. Tools do not
create deals, change CRM records or send messages. Successful keyed calls
update the account's usage ledger.

REST field names use snake_case. MCP arguments use camelCase; inspect tools/list
for the exact schema. MCP output retains the REST response's field names.

## Connect

Public URL: https://app.sentineliq.net/api/v1/mcp/public
Keyed URL: https://app.sentineliq.net/api/v1/mcp

The public connection exposes three calculators. The keyed connection exposes
all fourteen tools. Configure Authorization: Bearer agk_... using your client's
protected credential settings. There is no OAuth sign-in flow. Keys belong on
a server or in secure local configuration, never shared source files.

### Cursor

Use .cursor/mcp.json:

```json
{
  "mcpServers": {
    "sentinel": {
      "url": "https://app.sentineliq.net/api/v1/mcp/public"
    }
  }
}
```

### VS Code

Use .vscode/mcp.json. VS Code uses servers and an explicit transport type:

```json
{
  "servers": {
    "sentinel": {
      "type": "http",
      "url": "https://app.sentineliq.net/api/v1/mcp/public"
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport http sentinel https://app.sentineliq.net/api/v1/mcp/public
```

Other clients must support a remote HTTP MCP server. Availability and protected
header configuration vary by client and plan. No universal compatibility claim
is made. The optional Claude Desktop example uses a third-party stdio bridge;
review that dependency before using it.

### Protocol behavior

Server version: 1.5.1. Supported protocol revisions are 2026-07-28,
2025-06-18 and 2025-03-26. Transport is stateless HTTP POST with JSON responses;
a legacy HTTP+SSE server is not provided.

Current 2026-07-28 clients use server/discover. Requests include the
MCP-Protocol-Version and Mcp-Method headers; tools/call also includes Mcp-Name.
The body params._meta must carry io.modelcontextprotocol/protocolVersion and
io.modelcontextprotocol/clientCapabilities. Header and body values must agree.

Legacy 2025-03-26 and 2025-06-18 clients use initialize and send the negotiated
MCP-Protocol-Version header thereafter. The supported structured-result
revisions return structuredContent and outputSchema alongside text content.
Inspect the negotiated capabilities rather than assuming a client version.

Initialize, discovery and notifications do not consume successful-call quota.
Business failures appear as result.isError with a text error; protocol errors
use JSON-RPC errors. Preserve X-Request-Id when contacting support.

## Research one property with evidence

The `wa_research_packet` tool resolves one supported Washington property and
returns source-backed facts, calculations, conflicts, unknowns, follow-up
questions and field-level references in a single bounded response. Compact and
full projections preserve the same claims, qualifications and required notices.
Optional coordinate context remains a separate point observation; it is never
treated as proof of a parcel match. A useful partial packet counts as one
successful call, while unavailable or ambiguous research does not.

`wa_property_changes` reads the permit versions Sentinel has actually captured.
It distinguishes agency event dates from Sentinel observation times and treats
the first capture as a baseline, not as a newly observed change. History begins
at that first immutable capture and can be incomplete.

## Build a seller packet

A data-independent first request compares two prices with a known payoff and
explicitly no seller credits:

```json
{
  "county": "king",
  "scenarios": [
    {"label": "Conservative", "sale_price": 725000, "mortgage_balance": 420000, "concessions": 0},
    {"label": "Target", "sale_price": 750000, "mortgage_balance": 420000, "concessions": 0}
  ]
}
```

POST this body to /api/v1/agent-api/v1/seller-packet with your bearer key.
The response includes report_markdown, structured scenarios, section statuses,
gaps, generation time and provenance. Property and market inputs are optional.
The packet is not an appraisal or CMA and does not fetch comparable sales.

Omitted or null mortgage_balance and concessions mean unknown. Explicit 0
means no payoff or seller credits. Preserve each proceeds label and its
mortgage_payoff_known and concessions_known flags. Scenario deltas include
comparable and a nullable amount; a null difference is not zero. The response's
fully_comparable flag tells you whether every scenario has a known payoff and
known seller credits.

Offer comparisons share a single payoff. When credits are known for every
offer, differences can still be compared without that payoff, but
comparison_basis is before_mortgage_payoff rather than net_proceeds. Unknown
credits suppress the offer spread and highest-proceeds labels. Do not present
a proceeds amount before unknown costs as final seller cash.

The Python and curl examples demonstrate calls without sending messages or
changing customer records. They will make network requests when you run them.

## Coverage and data interpretation

- County property records cover King, Pierce, Snohomish and Whatcom only.
- REET local-rate assumptions cover eleven counties; that is not eleven-county
  property coverage.
- Historical cached building attributes may include earlier enrichment and
  are not independently verified field by field. interior_provenance_status
  is not_recorded when historical source tracking was not recorded; preserve
  provenance_note alongside the attributes. A county attribution is not proof
  of each building attribute's source.
- Known portal backfills are omitted (portal_suppressed). Current listing
  overrides are replaced with cached property values, which carry the same
  historical provenance limitation. Missing or unavailable facts stay null.
- Listing status, price and related fields are included only for a matched
  licensed listing already on file. Null means no licensed listing on file,
  not that a property is off market.
- Listing links, photos and portal automated valuations are not returned.
- Owner identity, mailing addresses, absentee classifications and equity
  estimates are excluded. No list export, bulk enumeration or lead feed exists.
- Market snapshots carry source dates and freshness warnings. A stale snapshot
  is historical context, not a current observation.
- Carry through attribution entries marked required and all relevant assumptions
  and disclaimers. The [developer terms](https://sentineliq.net/developers/terms)
  apply to source data and API use; the example-code license does not grant
  additional data redistribution rights.

## Access and limits

Public calculators: 60 requests/minute and 500/day per public client IP.
Keyed tools: 60 requests/minute per key; 2,000 successful calls per rolling
24 hours per account, shared across REST and MCP. Five active keys per account.
The trial includes 25 lifetime successful calls. Failed requests, validation
failures, not-found misses and whoami checks do not consume that allowance.
GET /api/v1/agent-api/v1/whoami is an unmetered identity/usage check.

Existing paid accounts retain their API access and published account allowance.
The current entry points are a trial key and a directly arranged integration pilot.

The optional **$250, 30-day integration pilot** covers one agreed workflow,
one developer account with up to five integration keys, setup help and a
success check. It is a one-time payment with no automatic renewal. Checkout is
shown only when payment setup is available; otherwise contact the founder
before the pilot starts. These are integration keys, not user seats; published
per-account limits still apply. Contact hello@sentineliq.net.

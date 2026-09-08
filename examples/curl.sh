#!/usr/bin/env bash
# SENTINEL developer API / MCP — runnable examples.
#
#   ./curl.sh              run the no-key examples
#   SENTINEL_API_KEY=agk_... ./curl.sh    also run the keyed examples
#
# Requires: curl. `jq` is optional and only used to pretty-print.
set -u

BASE="${SENTINEL_BASE_URL:-https://app.sentineliq.net}"
KEY="${SENTINEL_API_KEY:-}"

pretty() { if command -v jq >/dev/null 2>&1; then jq .; else cat; fi; }
hr() { printf '\n=== %s ===\n' "$1"; }

# --------------------------------------------------------------------------
# 1. REET — no key. Graduated RCW 82.45 state brackets + county local portion
#    + the $5 DOR technology fee.
#    $750,000 in King County -> total_reet 12405, estimated_total_due 12410.
# --------------------------------------------------------------------------
hr "POST /api/v1/public/reet  (no key)"
curl -s "$BASE/api/v1/public/reet" \
  -H 'Content-Type: application/json' \
  -d '{"sale_price":750000,"county":"king"}' | pretty

# --------------------------------------------------------------------------
# 2. Deadlines — no key. Mutual acceptance on Friday 2026-01-16.
#    Earnest money lands 2026-01-21: two BUSINESS days, skipping Sat, Sun and
#    MLK Monday 2026-01-19 (RCW 1.16.050). The 10-day inspection is a CALENDAR
#    count and lands 2026-01-26 without skipping the holiday.
#    financing_days on this public route accepts 14, 21 or 30 only.
# --------------------------------------------------------------------------
hr "POST /api/v1/public/deadlines  (no key)"
curl -s "$BASE/api/v1/public/deadlines" \
  -H 'Content-Type: application/json' \
  -d '{"mutual_acceptance":"2026-01-16","financing_days":21,"closing":"2026-02-28"}' | pretty

# --------------------------------------------------------------------------
# 3. Seller net sheet — no key.
#    750k / King / 5% / 300k payoff / HOA / 1200 proration -> net_proceeds 395840.
# --------------------------------------------------------------------------
hr "POST /api/v1/public/net-sheet  (no key)"
curl -s "$BASE/api/v1/public/net-sheet" \
  -H 'Content-Type: application/json' \
  -d '{"sale_price":750000,"county":"king","commission_rate":0.05,"mortgage_balance":300000,"has_hoa":true,"property_tax_proration":1200}' | pretty

# --------------------------------------------------------------------------
# 4. Authless MCP — JSON-RPC 2.0, no key, no account.
#    Three tools only: wa_reet, wa_net_sheet, nwmls_deadlines.
# --------------------------------------------------------------------------
hr "POST /api/v1/mcp/public  tools/list  (no key)"
curl -s "$BASE/api/v1/mcp/public" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | pretty

# $1.5M in Snohomish -> state_reet 18255, local_reet 7500, total_reet 25755.
hr "POST /api/v1/mcp/public  tools/call wa_reet  (no key)"
curl -s "$BASE/api/v1/mcp/public" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"wa_reet","arguments":{"salePrice":1500000,"county":"snohomish"}}}' | pretty

# --------------------------------------------------------------------------
# Everything below needs a key. Mint one in the developer console at
# https://app.sentineliq.net/developers/console. New accounts have a trial of
# 25 lifetime successful calls; paid API access uses the account allowance.
# --------------------------------------------------------------------------
if [ -z "$KEY" ]; then
  printf '\nSENTINEL_API_KEY not set — skipping the keyed examples.\n'
  exit 0
fi

AUTH="Authorization: Bearer $KEY"

# whoami is FREE: never metered, never spends the 25 lifetime trial answers,
# and runs on its own burst-only rate-limit bucket.
hr "GET /api/v1/agent-api/v1/whoami  (keyed, free)"
curl -s "$BASE/api/v1/agent-api/v1/whoami" -H "$AUTH" | pretty

# Property lookup — King, Pierce, Snohomish and Whatcom only. Per address.
# No owner identity or equity. Legacy building attributes have unrecorded
# field-level provenance and may include earlier enrichment; preserve the
# interior_provenance_status and provenance_note. Known portal backfills are
# omitted. Listing fields require a matched licensed listing already on file;
# null does not mean off market. Listing links, photos and portal AVMs are absent.
# A 404 miss and a 422 validation failure are not metered.
hr "GET /api/v1/agent-api/v1/property  (keyed, metered on a hit)"
curl -s -G "$BASE/api/v1/agent-api/v1/property" \
  -H "$AUTH" \
  --data-urlencode 'address=1600 Bell St' \
  --data-urlencode 'city=Seattle' \
  --data-urlencode 'zip_code=98121' | pretty

# Market snapshot — Redfin aggregates. Read market.freshness before you use a
# number: a snapshot older than 45 days is flagged status:"stale".
hr "GET /api/v1/agent-api/v1/market  (keyed, metered on a hit)"
curl -s -G "$BASE/api/v1/agent-api/v1/market" \
  -H "$AUTH" \
  --data-urlencode 'area=98103' \
  --data-urlencode 'region_type=zip' | pretty

# Keyed MCP — all fourteen tools.
hr "POST /api/v1/mcp  tools/list  (keyed)"
curl -s "$BASE/api/v1/mcp" \
  -H 'Content-Type: application/json' \
  -H "$AUTH" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/list"}' | pretty

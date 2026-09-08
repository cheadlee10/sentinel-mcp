"""SENTINEL developer API — minimal Python example. Standard library only.

Run with no arguments for the keyless calls:

    python example.py

Set SENTINEL_API_KEY to also run the keyed property lookup:

    SENTINEL_API_KEY=agk_... python example.py

Create a key at https://app.sentineliq.net/developers/console. New accounts have
25 lifetime successful trial calls; paid API access uses the account allowance.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("SENTINEL_BASE_URL", "https://app.sentineliq.net")
API_KEY = os.environ.get("SENTINEL_API_KEY")


def _request(method: str, path: str, *, body: dict | None = None, key: str | None = None) -> dict:
    """One request. Returns the parsed body for both 2xx and 4xx.

    Every 4xx on this surface is {"detail": {"code", "message", "upgrade_url"?}},
    so an error is worth reading rather than raising through.
    """
    headers = {"Accept": "application/json"}
    if path.startswith("/api/v1/mcp"):
        headers["Accept"] = "application/json, text/event-stream"
        headers["MCP-Protocol-Version"] = "2025-06-18"
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if key:
        headers["Authorization"] = f"Bearer {key}"

    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read() or b"{}")
            # Quote X-Request-Id in any support request.
            payload.setdefault("_request_id", resp.headers.get("X-Request-Id"))
            return payload
    except urllib.error.HTTPError as exc:
        return {"_status": exc.code, "_request_id": exc.headers.get("X-Request-Id"),
                **json.loads(exc.read() or b"{}")}


def reet(sale_price: int, county: str) -> dict:
    """Graduated WA state REET + county local portion + the $5 DOR fee. No key."""
    return _request("POST", "/api/v1/public/reet",
                    body={"sale_price": sale_price, "county": county})


def deadlines(mutual_acceptance: str, financing_days: int = 21, closing: str | None = None) -> dict:
    """NWMLS-default deadline set. No key. verify the supplied values against the published schema."""
    body: dict = {"mutual_acceptance": mutual_acceptance, "financing_days": financing_days}
    if closing:
        body["closing"] = closing
    return _request("POST", "/api/v1/public/deadlines", body=body)


def mcp_call(tool: str, arguments: dict, *, key: str | None = None) -> dict:
    """Call one MCP tool over JSON-RPC.

    Without a key this hits the authless transport, which serves the three
    calculators. With a key it hits the full fourteen-tool transport.

    Tool failures are NOT JSON-RPC errors: they arrive as result.isError = true
    with a {"code", "message"} text block.
    """
    path = "/api/v1/mcp" if key else "/api/v1/mcp/public"
    envelope = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    response = _request("POST", path, body=envelope, key=key)
    result = response.get("result")
    if not result:
        return response  # JSON-RPC error: malformed envelope or unknown tool.
    text = result["content"][0]["text"]
    return {"isError": result.get("isError", False), "data": json.loads(text)}


def property_lookup(address: str, *, city: str | None = None, zip_code: str | None = None,
                    key: str) -> dict:
    """Property record for one address. King, Pierce, Snohomish, Whatcom.

    Owner identity and equity are excluded. Legacy building attributes may
    include earlier enrichment and lack independent field-level verification;
    preserve interior_provenance_status and provenance_note when presenting
    them. Known portal backfills are omitted. A matched licensed listing on
    file may supply listing fields; null does not mean the property is off
    market. Listing links, photos and portal AVMs are absent.
    A 404 NOT_FOUND miss and a 422 VALIDATION failure are not metered.
    """
    params = {"address": address}
    if city:
        params["city"] = city
    if zip_code:
        params["zip_code"] = zip_code
    query = urllib.parse.urlencode(params)
    return _request("GET", f"/api/v1/agent-api/v1/property?{query}", key=key)


if __name__ == "__main__":
    # $750,000 in King County: total_reet 12405, estimated_total_due 12410.
    tax = reet(750_000, "king")
    print(f"REET  total {tax['total_reet']}  + ${tax['technology_fee']} DOR fee "
          f"= {tax['estimated_total_due']}  ({tax['effective_rate_pct']}% effective)")

    # Mutual acceptance Friday 2026-01-16. Earnest money is two BUSINESS days and
    # lands 2026-01-21, skipping Sat, Sun and MLK Monday. The 10-day inspection is
    # a CALENDAR count and lands 2026-01-26.
    plan = deadlines("2026-01-16", financing_days=21, closing="2026-02-28")
    for row in plan["deadlines"]:
        flag = "  <- weekend/holiday" if row.get("lands_on_non_business_day") else ""
        print(f"{row['date']}  {row['label']:<24} {row['basis']:<8} {row['rule']}{flag}")

    # Authless MCP: $1.5M in Snohomish -> state 18255, local 7500, total 25755.
    call = mcp_call("wa_reet", {"salePrice": 1_500_000, "county": "snohomish"})
    print("MCP wa_reet:", call["data"]["total_reet"] if not call["isError"] else call["data"])

    if API_KEY:
        record = property_lookup("1600 Bell St", city="Seattle", zip_code="98121", key=API_KEY)
        if "property" in record:
            prop = record["property"]
            print(f"{prop['address']} — {prop['sqft']} sqft, built {prop['year_built']}, "
                  f"assessed {prop['assessed_value']}")
            if prop.get("coverage_note"):
                print("  coverage:", prop["coverage_note"])
            # Reproduce every attribution marked required wherever you show the data.
            for entry in record["attributions"]:
                if entry["required"]:
                    print("  REQUIRED ATTRIBUTION:", entry["text"])
        else:
            print("lookup:", record.get("detail", record))
    else:
        print("SENTINEL_API_KEY not set — skipped the keyed property lookup.")

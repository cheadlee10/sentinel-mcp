# Security

Please report suspected vulnerabilities privately to `hello@sentineliq.net`.
Do not open a public issue containing credentials, private property inputs,
customer data or an unredacted request body.

Include the affected endpoint or example, the observed behavior, reproduction
steps that use synthetic data, and the `X-Request-Id` response header when one
is available. Never send an API key. Sentinel will acknowledge a complete report
and coordinate a safe disclosure timeline directly with the reporter.

API keys use the `agk_` prefix and belong in protected server or local-client
configuration. The examples in this repository contain no credentials.

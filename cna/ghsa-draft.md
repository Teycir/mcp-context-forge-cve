# GHSA draft — paste into `IBM/mcp-context-forge` → Security → Advisories → New draft

Requires private vulnerability reporting enabled, or a maintainer-created draft with the reporter
added as collaborator.

| Form field | Value |
|---|---|
| Ecosystem | pip |
| Package name | `mcp-contextforge-gateway` |
| Affected versions | `>= 1.0.0-RC2, <= 1.1.1` (rebinding); `0.9.0` and `>= 1.0.0-BETA-1, <= 1.0.0-RC1` (direct SSRF) |
| Patched versions | `1.1.2` |
| Severity | High |
| CVSS 3.1 vector | `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N` (8.2) |
| CWE | CWE-918 Server-Side Request Forgery (SSRF) |
| Credits | Teycir (https://github.com/Teycir) |

## Summary

`POST /llmchat/connect` validates the user-supplied MCP server URL once, then the streamable-HTTP
transport resolves the hostname a second time with no IP pinning. A DNS name that answers with a
public address on the validation lookup and `127.0.0.1` on the transport lookup (TTL 0) passes the
check and connects to loopback. The response lists the internal server's tools and
`POST /llmchat/chat` invokes them.

## Details

- `mcpgateway/routers/llmchat_router.py:1083-1087` (1.1.1) calls `SecurityValidator.validate_url()`
  and keeps the hostname.
- `mcpgateway/services/mcp_client_chat_service.py:105` builds the streamable-HTTP client with that
  URL; the hostname is resolved again at connect time.
- Pinning helpers exist and are used by other services — `validate_url_for_connection_pinning()` /
  `pin_url_to_resolved_ip()` (`mcpgateway/common/validators.py:76,1651`),
  `resolve_pinned_target()` (`mcpgateway/utils/ssrf_pinning.py`), used in `dcr_service.py`,
  `a2a_protocol.py`, `tool_service.py`. `llmchat_router.py` never calls them.

Prerequisite: authenticated account with the default `developer` role (`llm.invoke` seeded into
that role). An admin must have configured an LLM provider; the attacker does not control it.

Verified on 1.1.1 at commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` in an isolated lab:
`/llmchat/connect` returned `["internal_only_secret_tool_7f3a"]`, `/llmchat/chat` returned
`INTERNAL_ONLY_TOOL_REACHED_7f3a`; a write-only loopback tool produced `WRITE_PROOF_7f3a`.

## Impact

A low-privileged authenticated user can reach MCP servers bound to loopback or otherwise
unreachable from the internet, enumerate their tools and invoke them with attacker-controlled
arguments, bypassing the gateway's SSRF check. Confidentiality and integrity impact depend on the
internal servers present. Arbitrary-path write or code execution is not claimed.

## Remediation

Use the existing pinned-connection path in `llmchat_router.py`. Defence in depth: verify
`getpeername()` after connect, restrict `llm.invoke`, optional host allowlist.

## References

- https://cwe.mitre.org/data/definitions/918.html
- https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N
- Not a duplicate of CVE-2026-110194 (DCR SSRF, fixed in `dcr_service.py`):
  https://www.ibm.com/support/pages/node/7296696

# HackerOne submission — IBM program

Paste each field below. Plain text, no attachments (offer the pack on request). Link needed from the
PSIRT reply; the reply did not include it in the forwarded text.

| Field | Value |
|---|---|
| Program | IBM (Vulnerability Disclosure Program) |
| Title | SSRF (DNS rebinding) in `/llmchat/connect` allows a low-privileged user to invoke loopback MCP tools |
| Severity | High (CVSS 3.1 8.2, `AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`) |
| Weakness | CWE-918 Server-Side Request Forgery (SSRF) |
| Asset | `github.com/IBM/mcp-context-forge`, PyPI `mcp-contextforge-gateway` |
| Affected | 1.0.0-RC2 – 1.1.1 (rebinding); 0.9.0 and 1.0.0-BETA-1 – 1.0.0-RC1 (direct SSRF) |
| Tested | 1.1.1 at commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17) |
| Reporter | Teycir (`github.com/Teycir`) |

## Description

`POST /llmchat/connect` validates the user-supplied MCP server URL once
(`mcpgateway/routers/llmchat_router.py:1083-1087` in 1.1.1) but passes the hostname to the
streamable-HTTP transport, which resolves it again
(`mcpgateway/services/mcp_client_chat_service.py:105`). Nothing pins the validated address. A DNS
name that answers with a public IP on the validation lookup and `127.0.0.1` on the transport
lookup (TTL 0) passes the check and connects to loopback. The response lists the internal
server's tools and `POST /llmchat/chat` invokes them.

Prerequisite: an authenticated account with the default `developer` role (`llm.invoke` is seeded
into that role). An admin must have configured any LLM provider; the attacker does not need to
control it.

## Impact

A low-privileged authenticated user can reach MCP servers bound to loopback or otherwise
unreachable from the internet, enumerate their tools and invoke them with attacker-controlled
arguments. The URL check that exists to block this is bypassed, so the gateway is usable as a
confused deputy into its own host namespace. Confidentiality and integrity impact depend on the
internal MCP servers present; with a write-capable tool the gateway wrote `WRITE_PROOF_7f3a` to
`/tmp/internal_write_proof.txt` in its loopback namespace. Not claimed: arbitrary-path write or
code execution.

## Steps to reproduce

1. Isolated Docker lab: gateway 10.77.0.2:4444, attacker DNS 10.77.0.3, loopback MCP servers
   127.0.0.1:19000 (read) and 127.0.0.1:19001 (write-only).
2. Point `rebind.test` at 93.184.216.34, create provider `api_base=http://rebind.test:8081/v1`,
   model, user, team-scoped `developer` role.
3. Switch the name to TTL 0 rebinding: first answer public, later answers 127.0.0.1.
4. `POST /llmchat/connect` `{"server":{"url":"http://rebind.test:19000/mcp"}}` -> 200,
   `tools: ["internal_only_secret_tool_7f3a"]`.
5. `POST /llmchat/chat` -> 200, `tool_used: true`,
   `output: "INTERNAL_ONLY_TOOL_REACHED_7f3a"`.
6. Variant A, no attacker-controlled provider: same two calls against a real public
   OpenAI-compatible provider -> connect 200 with both tools, chat returns the canary.

Negative controls: direct `http://127.0.0.1:19000/mcp` -> 400 `Invalid server URL`; cached public
answer TTL 300 -> 500 with zero internal tool calls; attacker container cannot reach
10.77.0.2:19000 or 127.0.0.1:19000; provider `api_base` loopback/private -> 422 SSRF block.

Raw request/response captures, per-release range derivation and sha256 manifest available on
request.

## Remediation

Use the existing pinned-connection helpers in `llmchat_router.py`, as DCR/A2A/tool services
already do: `SecurityValidator.validate_url_for_connection_pinning()` then connect to
`pin_url_to_resolved_ip()` (`mcpgateway/common/validators.py:76,1651`). Defence in depth: verify
`getpeername()` after connect, restrict `llm.invoke`, optional host allowlist.

## References

- CWE-918: https://cwe.mitre.org/data/definitions/918.html
- CVSS: https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N
- Not a duplicate of CVE-2026-110194 (DCR SSRF, fixed v1.1.0 in `dcr_service.py`):
  https://www.ibm.com/support/pages/node/7296696

## Disclosure

Vendor notice sent 2026-11-19T13:49:49Z to `psirt@us.ibm.com`; PSIRT replied directing this
submission to HackerOne. The fix shipped in v1.1.2 on 2026-11-25; publication is no longer gated.
agreed. IBM's stated policy asks for no disclosure until a fix is public plus 30 days; that
conflicts with the stated date and needs a decision before submitting.

# DNS-rebinding SSRF in ContextForge LLM Chat (`/llmchat/connect`) reaches loopback MCP tools

**Severity:** High — CVSS 3.1 **8.2**
`CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`
(calculator: https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Conservative alternative if `S:C` is rejected: **7.1** `AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N`.

**CWE:** CWE-918 (Server-Side Request Forgery), CWE-367-adjacent TOCTOU (validate-then-resolve).

**Vendor / product:** IBM — ContextForge MCP Gateway, PyPI `mcp-contextforge-gateway`
(repository `IBM/mcp-context-forge`).

**Affected:** `1.0.0-RC2` – `1.1.1` (DNS rebinding); `0.9.0` – `1.0.0-RC1` (direct SSRF — the
endpoint had no outbound URL validation; `0.9.0` also lacked an auth dependency).
**Fixed:** `1.1.2` (2026-11-25), fix commit `a1c3293b4`, PR #7658.
**Tested:** `1.1.1`, commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17), exact PyPI
release, built and run locally.

## Summary

`POST /llmchat/connect` takes an MCP server URL from the request body, calls
`SecurityValidator.validate_url()` on it, and then passes the **hostname** — not the validated IP —
to the streamable-HTTP MCP transport. The transport resolves the hostname again when it connects.
An attacker-controlled DNS name with TTL 0 can answer with a public address for the validation
lookup and `127.0.0.1` for the transport lookup. The gateway then speaks MCP to a loopback server:
the connect response returns that server's tool list, and `POST /llmchat/chat` invokes a tool and
returns its output. Only an authenticated account with the default `developer` role is needed; that
role is seeded with `llm.invoke`.

## Root cause

- `mcpgateway/routers/llmchat_router.py:1083-1087` (1.1.1; `:803` in 1.0.0-RC2+):

  ```python
  input_data.server.url = SecurityValidator.validate_url(
      str(input_data.server.url), "MCP server URL"
  )
  ```

  The call returns a URL string with the same hostname. No resolved IP is carried forward.
- `mcpgateway/services/mcp_client_chat_service.py:105` builds the streamable-HTTP client with that
  URL. `httpx`/`anyio` resolve the hostname at connect time — a second, independent lookup.
- The codebase already ships the missing primitive: `pin_url_to_resolved_ip` /
  `validate_url_for_connection_pinning` (`mcpgateway/common/validators.py:76,1651`) and
  `resolve_pinned_target` (`mcpgateway/utils/ssrf_pinning.py`), used by `dcr_service.py:100,116`,
  `a2a_protocol.py:199,217` and `tool_service.py:6049,6076`. `llmchat_router.py` never calls them.
- Default grant: `developer` is seeded with `llm.invoke`
  (`alembic/versions/9f5d93ced2b3_*.py:36-37`, `bootstrap_db.py:396,445`, `db.py:1383`).

## Prerequisites

- Gateway reachable over HTTP with authentication enabled.
- Any authenticated account with the default `developer` role (`llm.invoke`).
- An LLM provider/model already configured (provider creation needs `admin.system_config`; the
  attacker does not need to create or control it — any existing public OpenAI-compatible model
  works).
- Attacker controls an authoritative DNS name and can point the gateway's resolver at it, or can
  otherwise answer the two lookups differently (classic rebinding, TTL 0).

## Reproduction (verified live)

Lab: two Docker containers on `labnet` 10.77.0.0/24.

1. Attacker container: authoritative DNS for `rebind.test` (UDP 5353) plus control endpoint
   (8082). Mode `public` answers `93.184.216.34`; mode `rebind` answers public first, then
   `127.0.0.1`. TTL 0. Gateway uses a TTL-honouring cache on `127.0.0.1:53`.
2. Gateway container: vulnerable app on `0.0.0.0:4444`, internal MCP server on
   `127.0.0.1:19000` (tool `internal_only_secret_tool_7f3a`, output
   `INTERNAL_ONLY_TOOL_REACHED_7f3a`), OpenAI-compatible stub on `0.0.0.0:8081`.
3. `mode=public`; create provider `api_base=http://rebind.test:8081/v1`, model `stub-model`,
   user `dev@example.com`, team-scoped role `developer`.
4. `mode=rebind`, TTL 0, reset counter.
5. `POST /llmchat/connect`:

   ```json
   {"user_id":"dev@example.com","server":{"url":"http://rebind.test:19000/mcp"},
    "llm":{"model":"stub-model"},"streaming":false}
   ```

6. `POST /llmchat/chat`:

   ```json
   {"user_id":"dev@example.com","message":"use the internal tool"}
   ```

Observed (2026-11-19T12:46:06Z):

```
connect 200  tools=["internal_only_secret_tool_7f3a"]
chat    200  tool_used=true, tool_invocations[1].output="INTERNAL_ONLY_TOOL_REACHED_7f3a"
```

Variant A repeats the chain with a real public provider (`text.pollinations.ai`, function calling
enabled) — the attacker-controlled hostname is needed only for the MCP URL, not for the LLM
endpoint. Result: 200, tools include `internal_only_secret_tool_7f3a` and
`internal_write_proof_7f3a`; the write-only tool returned `WRITE_PROOF_7f3a`.

### Negative controls

- Direct loopback URL `http://127.0.0.1:19000/mcp` → 400 `{"detail":"Invalid server URL"}`.
- Cached public answer, TTL 300 → 500 `Service initialization failed`, 0 internal tool calls.
- Attacker container cannot reach `10.77.0.2:19000` or `127.0.0.1:19000` (ConnectionRefused).
- Provider `api_base` private/loopback → 422 SSRF rejection; `10.77.0.2.nip.io` → 422 DNS failure.

## Impact

An authenticated low-privileged user (`developer`, no admin) can make the gateway connect to
loopback or link-local services that are not exposed to the network, enumerate their MCP tool
lists, and invoke tools with the gateway's network position and any credentials those services
trust. This bypasses the gateway's own SSRF control, which is the security boundary between a
tenant user and internal infrastructure. Confidentiality and integrity of internal MCP services
are both exposed; the loopback service sees the gateway as a trusted local client.

## Fix

Shipped in `1.1.2`: `_build_transport()` now calls `resolve_pinned_target()` and
`build_pinned_httpx_client_factory()` (with `SniPinningTransport`, `follow_redirects=False`), so the
transport dials only validated addresses and never re-resolves DNS. Release notes list PR #7658,
"Apply outbound URL checks and DNS pinning to MCP connections from LLM Chat". Verified in the 1.1.2
sdist: `mcpgateway/services/mcp_client_chat_service.py:2177` calls `resolve_pinned_target()`,
`:2180` builds the pinned factory.

## References

- Upstream: https://github.com/IBM/mcp-context-forge
- Fix PR: https://github.com/IBM/mcp-context-forge/pull/7658
- Release: https://github.com/IBM/mcp-context-forge/releases/tag/v1.1.2
- PyPI: https://pypi.org/project/mcp-contextforge-gateway/1.1.2/
- CWE-918: https://cwe.mitre.org/data/definitions/918.html
- Prior related issue, not a duplicate: CVE-2026-110194 (DCR endpoint SSRF, fixed in 1.1.0 by
  pinning `dcr_service.py`; `/llmchat/connect` remained unpinned in 1.1.1).
- Reproduction package: https://github.com/Teycir/mcp-context-forge-cve

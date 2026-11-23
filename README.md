# mcp-context-forge — DNS-rebinding SSRF reaches loopback MCP tools via `/llmchat/connect`

`/llmchat/connect` validates the user-supplied MCP server URL once (`validate_url`), then the
streamable-HTTP transport resolves the hostname again when it opens the connection. A hostname
whose DNS answer changes between the two lookups (TTL 0) passes the public-IP check and connects
to `127.0.0.1`. The response lists the internal server's tools, and `/llmchat/chat` invokes them.

| | |
|---|---|
| Package | `mcp-contextforge-gateway` (PyPI) |
| Source | `github.com/IBM/mcp-context-forge` |
| Audited | 1.1.1, commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17) |
| Affected | `1.0.0-RC2` – `1.1.1` (rebinding); `0.9.0` and `1.0.0-BETA-1` – `1.0.0-RC1` (direct SSRF) |
| Fixed in | commit `a1c3293b4` (2026-11-23), on `main` and `release/1.1.2`; not yet tagged/released |
| Severity | High — CVSS 3.1 **8.2** `AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N` |
| Conservative scoring | 7.1 High with `S:U` if scope change is rejected |
| CWE | CWE-918 (Server-Side Request Forgery) |
| CVE | pending — submission pack in `cve-submission/`, `cna/` |
| Reported by | Teycir ([github.com/Teycir](https://github.com/Teycir)) |
| Status | Vendor notified 2026-11-19T13:49:49Z; IBM PSIRT ticket **ADV0400680** opened. Fix committed 2026-11-23 (commit `a1c3293b4`) on **main** and **release/1.1.2**, not yet tagged. HackerOne declined. Disclosure: bounded 30-days-after-fix proposed, outer bound 2026-12-19. |

## Issue

- `mcpgateway/routers/llmchat_router.py:803` (v1.0.0-RC2+) and `:1083-1087` (1.1.1) call
  `SecurityValidator.validate_url()` on `input_data.server.url` and keep the hostname.
- `mcpgateway/services/mcp_client_chat_service.py:105` builds a streamable-HTTP client with that
  URL; `httpx`/`anyio` resolve `rebind.test` a second time. Nothing pins the validated IP.
- A DNS server that answers `93.184.216.34` on the validation lookup and `127.0.0.1` on the
  transport lookup (TTL 0, `mode=rebind`) defeats the check.
- The gateway then speaks MCP to loopback (`127.0.0.1:19000`) and returns the internal server's
  tool list. `POST /llmchat/chat` executes a tool through the stub LLM and returns its output.

Pinning helpers exist in 1.1.1 — `pin_url_to_resolved_ip` / `validate_url_for_connection_pinning`
(`mcpgateway/common/validators.py:76,1651`) and `resolve_pinned_target`
(`mcpgateway/utils/ssrf_pinning.py`) — and are used by `dcr_service.py:100,116`,
`a2a_protocol.py:199,217` and `tool_service.py:6049,6076`. `llmchat_router.py` never calls them.

Prerequisite: an authenticated account with the default `developer` role, which is seeded with
`llm.invoke` (`alembic/versions/9f5d93ced2b3_*.py:36-37`, `bootstrap_db.py:396,445`). No admin
rights, no non-default configuration.

## Reproduce

Lab: `pocs/run_lab.sh up` starts gateway (10.77.0.2:4444), attacker DNS (10.77.0.3:5353) and
loopback MCP server; `pocs/exploit.py` drives the rebind.

1. `ctl_set(ttl=0, reset=1, mode=public)` — `rebind.test` → `93.184.216.34`.
2. Create provider `api_base=http://rebind.test:8081/v1`, model `stub-model`, user `dev@example.com`,
   team-scoped role `developer`.
3. `ctl_set(ttl=0, reset=1, mode=rebind)` — first answer public, later answers `127.0.0.1`.
4. `POST /llmchat/connect` with `server.url=http://rebind.test:19000/mcp`.
5. `POST /llmchat/chat` — response contains `INTERNAL_ONLY_TOOL_REACHED_7f3a`.

Expected (verified 2026-11-19T12:46:06Z):

```
poc_connect_status   200  tools=["internal_only_secret_tool_7f3a"]
poc_chat_status      200  tool_used=true
tool_invocations[1]  output=INTERNAL_ONLY_TOOL_REACHED_7f3a
neg1 direct loopback 400  {"detail":"Invalid server URL"}
neg2 cached ttl=300  500  {"detail":"Service initialization failed"}, 0 internal calls
isolation control    BLOCKED from attacker container to 10.77.0.2:19000 and 127.0.0.1:19000
```

## Scope

- **Affected:** 0.9.0 – 1.1.1.
  - 0.9.0 – 1.0.0-RC1: `/connect` had **no** URL validation and (0.9.0) no auth dependency —
    plain SSRF to loopback, no rebinding required.
  - 1.0.0-RC2 – 1.1.1: `validate_url` added, no pinning — rebinding required.
- **Not affected:** < 0.9.0 — `llmchat_router.py` does not exist.
- **Not affected:** deployments that cannot resolve attacker-controlled names (egress DNS
  allowlist) or that set `SSRF_PROTECTION_ENABLED=false` only if they also block egress.

## Fix

1. Use the existing pinned-connection path in `llmchat_router.py`, as DCR/A2A/tool services do:
   `validated_target = await SecurityValidator.validate_url_for_connection_pinning(url, "MCP server URL")`
   then connect to `pin_url_to_resolved_ip(url, validated_target.resolved_ip)` (Host header keeps TLS SNI).
2. Defence in depth: resolve once at the socket layer and reject private/loopback/link-local IPs
   after connect (`getpeername`), not only pre-connect; restrict `llm.invoke` to roles that need it;
   optional host allowlist for `/llmchat/connect`.

## Disclosure status

- Notified: **2026-11-19T13:49:49Z** to `psirt@us.ibm.com` (Proton, text body, no attachments).
- Message-ID: `<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>`
- Sent copy: `cna/sent/20261119T134949Z-vendor-notice-psirt.eml` (sha256 `4810b310669a7eb33be499ed0ff4e211543d01f2e737d7850c619b200573dde2`)
- Log: `cna/contact-log.md` row 1.
- Deadline: **2026-11-26** (7 calendar days). Escalation: T+2 nudge (2026-11-21), T+4 MITRE (2026-11-23), T+7 publish.

## Evidence

| Path | Contents |
|---|---|
| `cve-submission/advisory.md` | Full advisory: metadata, description, PoC, impact, fix |
| `cve-submission/range-verification.txt` | Per-release derivation of the affected range |
| `report_20261119_120219.md` | Full assessment report (PTES, CVSS, negative controls) |
| `evidence/lab-20261119T124614Z/` | 32 raw artifacts + `sha256sums.txt` |
| `evidence/lab-20261119T124614Z/poc-chat-tool-invoke.json` | Tool output with canary |
| `evidence/lab-20261119T124614Z/neg1-direct-loopback.json` | Direct loopback rejected |
| `evidence/lab-20261119T124614Z/neg2-cached-public-ttl300.json` | Cached public answer rejected |
| `evidence/lab-20261119T124614Z/isolation-control.txt` | Attacker cannot reach loopback |
| `pocs/` | Lab: DNS auth+cache, internal MCP, LLM stub, exploit driver |
| `evidence/lab-20261119T131956Z/` | Exact-tag v1.1.1 rerun (PASS) + `sha256sums.txt` |
| `evidence/variantA-20261119T132238Z/` | Real public provider, read canary |
| `evidence/variantA-writeonly-20261119T132736Z/` | Write-only internal tool proof (`WRITE_PROOF_7f3a`) |
| `cna/sent/20261119T134949Z-vendor-notice-psirt.eml` | Sent vendor notice with headers |
| `cna/contact-log.md` | Contact ledger (row 1 sent, Message-ID) |
| `cve-submission/MANIFEST.txt` | sha256 of the submission pack |

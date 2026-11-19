# Vendor notice — email draft

**To:** psirt@us.ibm.com
**Cc:** (maintainer address from `pyproject.toml`, if public)
**Subject:** SSRF (DNS rebinding) in mcp-context-forge `/llmchat/connect` — low-privileged user reaches loopback MCP tools

---

Hello IBM PSIRT,

I am reporting a server-side request forgery in ContextForge MCP Gateway
(`mcp-contextforge-gateway`, repository `github.com/IBM/mcp-context-forge`) that lets any
authenticated user with the default `developer` role make the gateway connect to loopback MCP
servers and invoke their tools.

**Summary.** `POST /llmchat/connect` validates the user-supplied MCP server URL once
(`mcpgateway/routers/llmchat_router.py:1083-1087`, 1.1.1) but passes the hostname to the
streamable-HTTP transport, which resolves it again (`mcpgateway/services/mcp_client_chat_service.py:105`).
Nothing pins the validated IP. A DNS name that answers with a public address during validation and
`127.0.0.1` during the transport lookup passes the check and connects to loopback. The response
lists the internal server's tools; `POST /llmchat/chat` invokes them.

**Affected.** Primary: `1.0.0-RC2` – `1.1.1` (rebinding SSRF), tested at commit
`85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17). Secondary, same endpoint, worth separate
IDs: `0.9.0` had no auth dependency and no URL validation (unauthenticated direct SSRF);
`1.0.0-BETA-1` – `1.0.0-RC1` had auth but no URL validation (direct SSRF).

**Proof.** Isolated Docker lab, no production systems. With a TTL-0 rebinding name:

```
POST /llmchat/connect  -> 200, tools: ["internal_only_secret_tool_7f3a"]
POST /llmchat/chat     -> 200, tool_used: true,
                          output: "INTERNAL_ONLY_TOOL_REACHED_7f3a"
```

Prerequisite: an admin must have configured an LLM provider/model; the attacker does not need to
control it. Verified with a real public OpenAI-compatible provider (Variant A): connect returned
both tools, chat returned the canary, and a write-only internal MCP tool produced
`WRITE_PROOF_7f3a` in `/tmp/internal_write_proof.txt` inside the gateway's loopback namespace.

Negative controls: direct `http://127.0.0.1:19000/mcp` → 400 `Invalid server URL`; cached public
answer (TTL 300) → 500, zero internal tool calls; attacker container cannot reach either
`10.77.0.2:19000` or `127.0.0.1:19000`; provider `api_base` loopback/private → 422 SSRF block.

**Fix.** The pinning helpers already exist and are used by DCR/A2A/tool services:
`SecurityValidator.validate_url_for_connection_pinning()` +
`pin_url_to_resolved_ip()` (`mcpgateway/common/validators.py:76,1651`). `/llmchat/connect` does not
call them. Applying the same pattern closes the rebinding window. Suggested hardening: check
`getpeername()` after connect, restrict `llm.invoke`, optional host allowlist.

Full advisory, per-tag range derivation, raw request/response captures and sha256 manifest are
available on request; I can attach them to this thread or a private advisory.

**Disclosure.** I intend to publish after a fix ships or 90 days from this notice, whichever comes
first. Please confirm receipt and whether IBM PSIRT will assign a CVE.

Regards,
Teycir
github.com/Teycir

---

## Send checklist

- [ ] Body only — no attachments (repo is private; share details only on request)
- [ ] Save the sent message with full headers to `cna/vendor-notice-<date>.eml`
- [ ] Record Date, Message-ID, recipients in `cna/contact-log.md`
- [ ] Do not attach the Docker images or credentials

# MITRE CVE request — form fields

Submit at `https://cveform.mitre.org/` only after the PSIRT window elapses
(see `cna/playbook.md`, T+4 days). One request per vulnerability.

## Request type

`Create a new CVE ID`

## Fields

**Vulnerability type**

```
Server-Side Request Forgery (SSRF) — CWE-918
```

**Vendor / project**

```
IBM — mcp-context-forge (ContextForge MCP Gateway), PyPI mcp-contextforge-gateway
```

**Version(s) affected**

```
>=0.9.0, <=1.1.1
```

**Version(s) fixed**

```
None as of 2026-11-19.
```

**Description**

```
ContextForge MCP Gateway's POST /llmchat/connect validates a user-supplied MCP server URL once
with SecurityValidator.validate_url() and then passes the hostname to the streamable-HTTP
transport, which resolves it again (mcpgateway/routers/llmchat_router.py:1083-1087 and
mcpgateway/services/mcp_client_chat_service.py:105 in 1.1.1). The validated IP is not pinned.
A DNS name with TTL 0 that answers with a public address during validation and 127.0.0.1 during
the transport lookup passes the check and connects to loopback. The response exposes the internal
MCP server's tool list, and POST /llmchat/chat invokes those tools with attacker-controlled
arguments. Any authenticated user holding the default developer role (which carries llm.invoke)
can exploit this. In 0.9.0 the same route also lacked an authentication dependency and any URL
validation.
```

**Impact**

```
An authenticated low-privileged user makes the gateway act as a proxy into its own loopback and
private network: enumerate and invoke internal MCP tools, reach sidecars, and access internal
services that trust the gateway's network position. Verified in an isolated lab: the gateway
returned the internal tool list and executed a tool whose output was the canary string
INTERNAL_ONLY_TOOL_REACHED_7f3a.
```

**References**

```
https://github.com/IBM/mcp-context-forge
https://github.com/IBM/mcp-context-forge/blob/main/mcpgateway/routers/llmchat_router.py
https://github.com/IBM/mcp-context-forge/blob/main/mcpgateway/services/mcp_client_chat_service.py
https://cwe.mitre.org/data/definitions/918.html
```

**Reporter**

```
Teycir — https://github.com/Teycir
```

**Contact evidence**

Attach or paste:

- `cna/vendor-notice-<date>.eml` (full headers)
- PSIRT incident/ticket number, if assigned
- Follow-up message in the same thread
- This repository's `cve-submission/advisory.md`

## Notes

- MITRE may forward to IBM PSIRT; reference the existing thread so it is not treated as a new case.
- Do not submit a second request for the same issue to VulDB if MITRE assigns.
- If MITRE requests a CVSS vector, supply
  `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N` (8.2) and the conservative `S:U` variant (7.1).

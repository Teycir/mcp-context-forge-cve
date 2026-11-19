# VulDB submission — fields

Submit at `https://vuldb.com/?submit` only as the single CNA if PSIRT and MITRE are both
unresponsive (see `cna/playbook.md`). VulDB is a CNA and can assign unilaterally.

## Category

`SSRF (Server-Side Request Forgery)` — CWE-918

## Product

```
IBM mcp-context-forge (ContextForge MCP Gateway)
```

Version string: `1.1.1` (tested commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63`).

## Affected versions

```
0.9.0 to 1.1.1
```

## Title

```
IBM mcp-context-forge /llmchat/connect DNS rebinding SSRF exposes loopback MCP tools
```

## Description

```
The POST /llmchat/connect endpoint validates the user-supplied MCP server URL once via
SecurityValidator.validate_url() and then passes the hostname to the streamable-HTTP transport,
which resolves it a second time (mcpgateway/routers/llmchat_router.py:1083-1087,
mcpgateway/services/mcp_client_chat_service.py:105 in 1.1.1). The validated IP is not pinned.
A TTL-0 DNS name answering with a public address on the first lookup and 127.0.0.1 on the second
passes validation and connects the gateway to loopback. The response lists the internal MCP
server's tools; POST /llmchat/chat invokes them with attacker-controlled arguments. The default
developer role carries llm.invoke, so any authenticated user can exploit it. Version 0.9.0 also
lacked an auth dependency on the route and had no URL validation.
```

## Impact

```
Authenticated low-privileged user reaches loopback/private MCP servers through the gateway,
enumerates their tools, and executes them. Verified in an isolated lab: tool list returned and
tool output INTERNAL_ONLY_TOOL_REACHED_7f3a captured in the chat response.
```

## CVSS

`8.2` — `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

## References

```
https://github.com/IBM/mcp-context-forge
https://cwe.mitre.org/data/definitions/918.html
```

## Proof / attachments

- `cve-submission/advisory.md`
- `cve-submission/attack-path-simple.md`
- `evidence/lab-20261119T124614Z/` (32 artifacts, sha256 manifest included)
- `pocs/` (lab: DNS flip, internal MCP, LLM stub, exploit driver)

## Notes

- VulDB may ask for the vendor's response. Supply the PSIRT thread and state that the vendor was
  notified on `<date>` with no fix at submission time.
- If VulDB assigns, stop. Do not file MITRE afterwards.
- VulDB entries are public at submission time — confirm the 7-day window has elapsed.

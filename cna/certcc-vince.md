# CERT/CC VINCE — case fields

Use only if IBM PSIRT engages and the disclosure timeline stalls (see `cna/playbook.md`).
CERT/CC coordinates with the vendor and can assign a CVE if the vendor does not.

Submit at `https://kb.cert.org/vince/`.

## Vulnerability information

**Vendor**

```
IBM
```

**Product**

```
mcp-context-forge (ContextForge MCP Gateway), PyPI mcp-contextforge-gateway
```

**Version**

```
1.1.1 tested (commit 85474a7c0eefc8c5d0e958400af7bc0ce59dfe63); affected 0.9.0 through 1.1.1
```

**Vulnerability type**

```
Server-Side Request Forgery (CWE-918), DNS rebinding
```

**Public**

```
No
```

**Description**

```
POST /llmchat/connect validates an attacker-supplied MCP server URL once and then passes the
hostname to the streamable-HTTP transport, which re-resolves it. With TTL 0 and a DNS answer that
changes between lookups, the gateway connects to 127.0.0.1. The connect response exposes the
internal MCP server's tool list, and POST /llmchat/chat invokes the tools. The default developer
role carries llm.invoke, so no elevated rights are needed. Version 0.9.0 additionally lacked
authentication on the route.
```

**Impact**

```
Authenticated user reaches loopback/private MCP servers through the gateway and executes their
tools. Lab-verified canary output: INTERNAL_ONLY_TOOL_REACHED_7f3a.
```

**References**

```
https://github.com/IBM/mcp-context-forge
https://cwe.mitre.org/data/definitions/918.html
```

## Coordination

- Vendor notified: `<date>`, PSIRT case `<id>`, Message-ID `<id>`
- Requested disclosure date: 90 days from notice
- Requested CVE: yes (IBM PSIRT preferred; CERT/CC if PSIRT declines or stalls)
- Attachments: `cve-submission/advisory.md`, `cve-submission/range-verification.txt`,
  `evidence/lab-20261119T124614Z/sha256sums.txt`

## Notes

- State clearly that the reporter is willing to delay publication for coordination, but not
  indefinitely.
- VINCE prefers a single point of contact; keep the PSIRT thread as the vendor channel.
- Do not open a VINCE case and a MITRE request simultaneously.

# VulnCheck web form — field values

Form: <https://vulncheck.com/advisories/report>. Captcha is user-filled; every value below is
paste-ready. One finding per submission: **MCF-2026-01 only**.

## Shared fields

| Field | Value |
|---|---|
| Name to Credit | `Teycir` |
| Email | `teycir@users.noreply.github.com` |
| GitHub Username | `Teycir` |
| On behalf of someone else? | No — I discovered this myself |
| Vendor name | `IBM` |
| Product name | ContextForge MCP Gateway (`mcp-contextforge-gateway`) — LLM Chat MCP client (`/llmchat/connect`) |
| Product URL | https://github.com/IBM/mcp-context-forge |
| Tested Version(s) | `mcp-contextforge-gateway` 1.1.1, commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17), exact PyPI release; built and run locally. Also reproduced on 1.0.0-RC2. |
| Vulnerability Details | paste `details-MCF-2026-01.md` |
| Coordinate disclosure? | **No** — vendor coordinated directly; fix already released in v1.1.2 (2026-11-25) |
| Already reported to supplier? | **Yes.** Email to `psirt@us.ibm.com` 2026-11-19T13:49:49Z, Message-ID `<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>`; IBM PSIRT ticket **ADV0400680**. PSIRT redirected to HackerOne; declined (third-party identity/NDA). Fix commit `a1c3293b4`, PR #7658; released v1.1.2 2026-11-25T09:38:04Z (PyPI 09:55:46Z). |
| Previously requested CVE from MITRE w/o response? | No |
| Already publicly disclosed? | No prior disclosure. Reproduction repo is made public at submission time: https://github.com/Teycir/mcp-context-forge-cve |
| Generated with AI? | Yes — LLM assistance for source analysis and drafting. Reporter built the lab, executed the exploit, and verified every claim live. |
| Validated on production code? | Yes — exact PyPI release 1.1.1, built and run in Docker; not a mock. |
| Shodan / Fofa query | N/A — self-hosted gateway, no internet-wide fingerprint |
| Plan to publish on/after coordinated date? | Yes — repo public now; full report publishes with this submission |

## Finding MCF-2026-01

- **Title:** DNS-rebinding SSRF in ContextForge LLM Chat `/llmchat/connect` reaches loopback MCP tools
- **Severity:** High, CVSS 3.1 **8.2** `AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`
  (conservative 7.1 with `S:U`)
- **CWE:** CWE-918
- **Affected:** `1.0.0-RC2` – `1.1.1` (rebinding); `0.9.0` – `1.0.0-RC1` (direct SSRF)
- **Fixed:** `1.1.2`
- **Privileges:** authenticated account with default `developer` role (`llm.invoke`); no admin
- **Details file:** `details-MCF-2026-01.md`
- **Repro package:** https://github.com/Teycir/mcp-context-forge-cve (go public before submit)
- **VulnCheck case ID:** _record after submit_

## Wording to use for vendor contact

"Reported to IBM PSIRT on 2026-11-19T13:49:49Z (ticket ADV0400680). The vendor fixed the issue in
commit `a1c3293b4` (PR #7658) and released v1.1.2 on 2026-11-25T09:38:04Z (PyPI 09:55:46Z).
Verified fixed in the 1.1.2 sdist. A CVE has not been assigned by IBM."

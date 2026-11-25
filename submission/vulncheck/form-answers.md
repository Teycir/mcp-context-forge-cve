# VulnCheck web form — field values

Form: <https://vulncheck.com/advisories/report> (live field names/options checked 2026-11-25).
Captcha is user-filled. One finding per submission: **MCF-2026-01 only**.

## Top section

| HTML name | Field | Value |
|---|---|---|
| `name` | Name to Credit | `Teycir` |
| `email` | Email | `teycir@users.noreply.github.com` |
| `githubUsername` | GitHub Username | `Teycir` |
| `submissionBehalf` | On behalf of someone else? | **`self`** — No, I discovered this vulnerability myself |
| `affectedSoftwareVendor` | Vendor name | `IBM` |
| `affectedSoftwareProduct` | Product name | `ContextForge MCP Gateway (mcp-contextforge-gateway) — LLM Chat MCP client (/llmchat/connect)` |
| `affectedSoftwareUrl` | Product URL | `https://github.com/IBM/mcp-context-forge` |
| `testedVersions` | Tested Version(s) | `mcp-contextforge-gateway` 1.1.1, commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63` (2026-11-17), exact PyPI release; built and run locally. Also reproduced on 1.0.0-RC2. |
| `vulnerabilityDetails` | Vulnerability Details | paste **`PASTE-DETAILS.txt`** (same content as `details-MCF-2026-01.md`) |

## Disclosure questions

| HTML name | Field | Select |
|---|---|---|
| `disclosureCoordination` | VulnCheck coordinate disclosure? | **`cve_only_self_handle`** — "No, I only want VulnCheck to help me get a CVE ID; I will handle vendor disclosure myself." Vendor fix already released; coordination is done. |
| `reportedToSupplier` | Already reported to supplier? | **`yes`** |
| `previousCveRequested` | Previously requested CVE from MITRE w/o response? | **leave unchecked** (False) |
| `publiclyDisclosed` | Already publicly disclosed? | **`yes`** — reproduction repo public 2026-11-25T11:45:49Z; no prior advisory |
| `aiGenerated` | Generated with AI? | **checked** (True) |
| `validatedOnProduction` | Validated on production code? | **`yes`** — exact PyPI release 1.1.1 built and run in Docker |
| `shodanOrFofaQuery` | Shodan/Fofa query | `N/A — self-hosted gateway, no internet-wide fingerprint` |
| `planToPublish` | Publish on/after coordinated date? | **`yes`** — already public |

## Supplier-report wording (for any free-text follow-up)

"Reported to IBM PSIRT on 2026-11-19T13:49:49Z (ticket ADV0400680), Message-ID
`<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>`.
PSIRT redirected to HackerOne; declined (third-party identity/NDA). Fix commit `a1c3293b4`
(PR #7658) released in v1.1.2 on 2026-11-25T09:38:04Z (PyPI 09:55:46Z). Verified fixed in the
1.1.2 sdist. IBM has not assigned a CVE."

## Finding summary (if a separate severity/CWE field appears)

- Title: DNS-rebinding SSRF in ContextForge LLM Chat `/llmchat/connect` reaches loopback MCP tools
- Severity: High, CVSS 3.1 **8.2** `AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N` (conservative 7.1 with `S:U`)
- CWE: CWE-918
- Affected: `1.0.0-RC2` – `1.1.1` (rebinding); `0.9.0` – `1.0.0-RC1` (direct SSRF)
- Fixed: `1.1.2`
- Privileges: authenticated `developer` role (`llm.invoke`); no admin
- Package: https://github.com/Teycir/mcp-context-forge-cve
- VulnCheck case ID: _record after submit_

# Contact log

Status as of 2026-11-25: row 1 sent; PSIRT replied (row 2) redirecting to HackerOne (row 2a). Fix committed 2026-11-23 (commit `a1c3293b4657140cd801ecc4873a96919ed7dd95`, PR #7658) and **released in v1.1.2** 2026-11-25T09:38:04Z (PyPI 09:55:46Z). Embargo over.

| # | Channel | Address / URL | Purpose | Status | Date (UTC) | Message-ID / ticket |
|---|---|---|---|---|---|---|
| 1 | IBM PSIRT | psirt@us.ibm.com | Vendor notice + CVE request | sent | 2026-11-19T13:49:49Z | `<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>` |
| 2 | IBM PSIRT (reply) | psirt@us.ibm.com | Acknowledgement + disclosure terms | replied — in review, ticket ADV0400680 | 2026-11-19 (exact time pending `.eml`) | ADV0400680 |
| 2a | HackerOne (IBM program) | link from PSIRT reply | Complete submission | declined — third-party ID/NDA not acceptable; reply sent 2026-11-19 (time pending `.eml`) | — | pending |
| 2c | IBM PSIRT (ticket) | psirt@us.ibm.com / ADV0400680 | Agree disclosure window, request fix ETA + CVE | reply drafted — bounded 30-days-after-fix (outer bound 2026-12-19); fix committed 2026-11-23, awaiting tag | — | ADV0400680 |

| 2d | Vendor fix (verified in clone) | github.com/IBM/mcp-context-forge @ commit `a1c3293b4657140cd801ecc4873a96919ed7dd95` | Fix: `_build_transport()` calls `resolve_pinned_target()`, `build_pinned_httpx_client_factory()` with `SniPinningTransport`, `follow_redirects=False` | shipped in v1.1.2 (2026-11-25T09:38:04Z) | 2026-11-23T13:03:00Z | `a1c3293b4657140cd801ecc4873a96919ed7dd95` |
| 2b | GitHub GHSA (IBM/mcp-context-forge) | repo Security → advisories/new | Private report, no third-party ID | requested 2026-11-19 (time pending `.eml`) — PVR disabled (`cna/ghsa-pvr-check.txt`); PSIRT asked to enable or add me to a draft | — | pending |
| 3 | GitHub private advisory | `IBM/mcp-context-forge` → Security | Courtesy copy to maintainers | not opened | — | — |
| 4 | MITRE | cveform.mitre.org | CNA of last resort at T+4 days | not sent | — | — |
| 5 | VulDB | vuldb.com/?submit | Alternative CNA (only if MITRE/PSIRT fail) | not sent | — | — |
| 6 | CERT/CC | kb.cert.org/vince | Coordination if vendor engages and stalls | not sent | — | — |

## When each row is filled

- Row 1: immediately after sending, paste the full `.eml` headers into
  `cna/vendor-notice-<YYYYMMDD>.eml` and record Date + Message-ID here.
- Row 2: only in the same thread; record the reply Date.
- Row 3: record the GHSA URL and whether private reporting was enabled.
- Row 4/5/6: only after the playbook timers elapse; never two CNAs in parallel.

## Evidence to keep

- Raw sent messages with headers (`.eml`).
- PSIRT ticket number in the acknowledgement.
- Screenshots of submission confirmations.
- Any vendor reply, verbatim, in this directory.

## Reminders

- 7-day disclosure clock (deadline 2026-11-26) started at the row 1 send time; moot once v1.1.2
  shipped on 2026-11-25.
- If PSIRT assigns a CVE, stop and update `README.md` + `cve-submission/advisory.md` with the ID.
- If the vendor ships a fix, verify it against `pocs/` before publishing.

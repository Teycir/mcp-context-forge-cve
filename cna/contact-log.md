# Contact log

Status as of 2026-11-19: row 1 sent; PSIRT replied (row 2) redirecting to HackerOne (row 2a). HackerOne link and reply headers pending from reporter.

| # | Channel | Address / URL | Purpose | Status | Date (UTC) | Message-ID / ticket |
|---|---|---|---|---|---|---|
| 1 | IBM PSIRT | psirt@us.ibm.com | Vendor notice + CVE request | sent | 2026-11-19T13:49:49Z | `<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>` |
| 2 | IBM PSIRT (reply) | psirt@us.ibm.com | Acknowledgement — redirect to HackerOne | replied | 2026-11-19 (exact time pending `.eml`) | reply Message-ID pending |
| 2a | HackerOne (IBM program) | link from PSIRT reply | Complete submission | declined — third-party ID/NDA not acceptable | — | — |
| 2b | GitHub GHSA (IBM/mcp-context-forge) | repo Security → advisories/new | Private report, no third-party ID | blocked — PVR disabled (`cna/ghsa-pvr-check.txt`); asked PSIRT to enable or add me to a draft | — | — |
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

- 7-day disclosure clock (deadline 2026-11-26) starts at the row 1 send time, not at PoC verification.
- If PSIRT assigns a CVE, stop and update `README.md` + `cve-submission/advisory.md` with the ID.
- If the vendor ships a fix, verify it against `pocs/` before publishing.

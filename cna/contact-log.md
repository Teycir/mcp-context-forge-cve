# Contact log

Status as of 2026-11-19: **no channel contacted**. Pack prepared, nothing sent.

| # | Channel | Address / URL | Purpose | Status | Date (UTC) | Message-ID / ticket |
|---|---|---|---|---|---|---|
| 1 | IBM PSIRT | psirt@us.ibm.com | Vendor notice + CVE request | not sent | — | — |
| 2 | IBM PSIRT (follow-up) | same thread | Nudge at T+2 business days | not sent | — | — |
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

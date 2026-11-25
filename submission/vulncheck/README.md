# VulnCheck submission — MCF-2026-01

Status: **SUBMITTED 2026-11-25T11:55:37Z** — VulnCheck case `87e8faaf-6087-4a84-b57b-a998778122ea`. Repo public since 2026-11-25T11:45:49Z. One finding, one form submission.

## Files

| File | Purpose |
|---|---|
| `form-answers.md` | Paste-ready value for every field on vulncheck.com/advisories/report |
| `details-MCF-2026-01.md` | Full "Vulnerability Details" text (root cause, repro, impact, fix) |
| `PASTE-DETAILS.txt` | Byte-identical paste copy for the form textarea |
| `MCF-2026-01.cve.json` | CVE 5.1 record draft; IDs/orgId are placeholders for VulnCheck |
| `email-to-disclosure.txt` | Fallback email body (`disclosure@vulncheck.com`) |
| `timeline.md` | UTC disclosure timeline; add VulnCheck case ID here |
| `SHA256SUMS` | Integrity of this directory |

## Send gate

- [x] Vendor notified 2026-11-19T13:49:49Z (PSIRT ADV0400680); >72 h elapsed
- [x] Fix released: v1.1.2, 2026-11-25T09:38:04Z; verified in sdist
- [x] Reproduction repo public since 2026-11-25T11:45:49Z — https://github.com/Teycir/mcp-context-forge-cve
- [x] `submission/vulncheck/` committed and pushed
- [x] Submitted 2026-11-25T11:55:37Z — VulnCheck case `87e8faaf-6087-4a84-b57b-a998778122ea`
- [ ] `sha256sum -c SHA256SUMS`

## Notes

- Public repo URL used in form: https://github.com/Teycir/mcp-context-forge-cve
- Not a duplicate of CVE-2026-110194 (DCR SSRF, fixed 1.1.0); `/llmchat/connect` stayed unpinned.

# VulDB — form walkthrough

Only after the 7-day window (see `cna/playbook.md`). VulDB publishes on submission.

## Steps

1. Open `https://vuldb.com/?submit`.
2. **Vendor** — `IBM`. **Product** — `mcp-context-forge`. If the product is not listed, choose
   "new product" and use `mcp-context-forge (ContextForge MCP Gateway)`.
3. **Version** — `1.1.1`. Leave "fixed version" empty and note "no fix as of <date>" in the
   description.
4. **Vulnerability type** — `SSRF` (CWE-918). If a free-text field exists, write
   `DNS rebinding SSRF via /llmchat/connect`.
5. **Title** — `IBM mcp-context-forge /llmchat/connect DNS rebinding SSRF exposes loopback MCP tools`.
6. **Description** — paste the block from `cna/vuldb-submission.md` §Description.
7. **Impact** — paste §Impact from the same file.
8. **CVSS** — `8.2`, vector `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`. If the form rejects
   `S:C`, use the conservative `7.1` with `S:U` and say so in the notes.
9. **References** — repository URL and CWE URL. Do not link this repository before publication.
10. **Proof** — upload `cve-submission/advisory.md` and
    `evidence/lab-20261119T124614Z/sha256sums.txt`. Do not upload the whole lab.
11. **Vendor contact** — PSIRT email date and Message-ID; state "no fix, no CVE assigned at
    submission time".
12. **Reporter** — name `Teycir`, URL `https://github.com/Teycir`. Choose credit, not anonymity.
13. Submit. Save the confirmation page and the assigned VulDB entry ID into
    `cna/contact-log.md`.

## After submission

- VulDB may email the vendor; reply with the PSIRT thread if asked.
- If VulDB assigns a CVE, update `README.md`, `cve-submission/advisory.md`, and stop all other CNA
  routes.
- If VulDB rejects (duplicate/insufficient), fall back to MITRE with the rejection text attached.

## Do not

- Submit before the vendor window closes.
- Submit to VulDB and MITRE simultaneously.
- Include live credentials, internal hostnames, or client data in the description.

# CNA playbook — getting a CVE for an IBM-hosted open-source project

## Why the GitHub advisory is not the plan

A private GitHub advisory only becomes a CVE when the **maintainer publishes** it. If the
maintainer is unresponsive, the advisory sits unpublished and no record exists. Maintainer action
must never be the critical path.

> Always pair the vendor notice with a CNA that can assign unilaterally.

## Routes

| Route | Assigns unilaterally | P(CVE) if vendor silent | Typical time | Cost |
|---|---|---|---|---|
| **IBM PSIRT** (`psirt@us.ibm.com`) | Yes — IBM is a CNA for its products | ~0.95 | 1–4 weeks | free |
| **MITRE** (`cveform.mitre.org`) | Yes — CNA of last resort | ~0.90 with contact evidence | 3 weeks – 4 months | free |
| **VulDB** (`vuldb.com/?submit`) | Yes — VulDB is a CNA | ~0.85 | 3 days – 3 weeks | free |
| **CERT/CC** (`kb.cert.org/vince`) | Yes — coordinator + CNA | ~0.80 | 45 days + | free |
| **GitHub advisory** (private) | No — needs maintainer publish | ~0.30 given ghosting | indefinite | free |

IBM PSIRT is the fast lane here because the repository is under the `IBM` org and
`mcp-contextforge-gateway` is published as an IBM project. MITRE is the guaranteed fallback.
VulDB is a parallel-free alternative if PSIRT does not answer. CERT/CC only if PSIRT engages and
negotiations drag.

## Sequence (do not run two CNAs in parallel)

**T0 — vendor notice + PSIRT submission.**

1. Check `IBM/mcp-context-forge` → Security tab. If private reporting is enabled, open a private
   advisory with `cve-submission/advisory.md` **and** email PSIRT. If it is disabled, email only.
2. Email `psirt@us.ibm.com` using `cna/vendor-notice.md`. Cc the maintainer listed in
   `pyproject.toml` if a public address exists. Keep the sent copy and Message-ID.
3. Do **not** submit to VulDB or MITRE yet.

**T+2 business days — no acknowledgement.**

4. Resend once, reply in the same thread, reference the Message-ID. No new channel.

**T+4 calendar days — no substantive reply.**

5. File MITRE (`cna/mitre-submission.md`) and reference the PSIRT thread. Do not file VulDB at the
   same time.

**T+7 calendar days — no fix.**

6. Publish this repository (README + advisory + evidence). Redact nothing: the PoC uses dummy
   credentials and a loopback canary.

## What counts as contact evidence for MITRE

- Full headers of the vendor email (Date, Message-ID, To, Cc).
- Any PSIRT ticket/incident number.
- GitHub advisory URL if one was opened.
- A second follow-up in the same thread.

Save each as a file under `cna/` and reference it in the MITRE form.

## Rules

- One CNA at a time. Duplicate submissions produce duplicate CVEs and get rejected.
- Never publish before a fix or 7 calendar days, whichever comes first (window shortened deliberately:
  AI-assisted patching makes a 90-day embargo disproportionate for a pinned-IP bug with a one-line fix).
- Keep the advisory's affected range derived from tags (`cve-submission/range-verification.txt`),
  not from release notes.
- If PSIRT disputes the severity, do not argue scope in the first reply; supply the raw evidence
  (`evidence/lab-20261119T124614Z/`) and let them re-score.

# Disclosure timeline (UTC)

| When | Event |
|---|---|
| 2026-11-17 | Audited `1.1.1`, commit `85474a7c0eefc8c5d0e958400af7bc0ce59dfe63`. |
| 2026-11-19T12:46:06Z | Exploit verified in isolated lab: connect 200 (internal tool list), chat 200, canary `INTERNAL_ONLY_TOOL_REACHED_7f3a`; negative controls recorded. |
| 2026-11-19T13:49:49Z | Vendor notice to `psirt@us.ibm.com`. Message-ID `<s8T9ua3GH9FcqhYhjnImvhnsNQUefeogz5799X90-ejFiYsAzhfGbs9h5xbpOrwOGASdSDUM3t3vIDE2XBWcHDeDnelOg-L3wdwJLqMCi_k=@protonmail.com>`. |
| 2026-11-19 | IBM PSIRT opened **ADV0400680**; redirected to HackerOne. HackerOne declined (third-party identity/NDA). |
| 2026-11-23T13:03:58Z | Fix committed `a1c3293b4657140cd801ecc4873a96919ed7dd95` (PR #7658): pinned transport in LLM Chat. |
| 2026-11-25T09:38:04Z | **v1.1.2 released** (GitHub). PyPI upload 09:55:46Z. Fix verified in sdist sha256 `4c7248d17ea73f6d5f5443b943aab2386f09afdffc5d8da02e5ebafb45aa213c`. |
| 2026-11-25T11:45:49Z | Reproduction repo made public (https://github.com/Teycir/mcp-context-forge-cve); VulnCheck submission ready. |
| 2026-11-25T11:55:37Z | Submitted to VulnCheck; case ID `87e8faaf-6087-4a84-b57b-a998778122ea`. CVE assignment pending. |

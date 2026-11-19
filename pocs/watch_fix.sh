#!/usr/bin/env bash
# Poll IBM/mcp-context-forge for a fix to the /llmchat/connect SSRF.
# Exits 0 when llmchat_router.py references the pinning helpers, 1 otherwise.
set -uo pipefail
REPO=IBM/mcp-context-forge
F=mcpgateway/routers/llmchat_router.py
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
raw=$(curl -fsSL "https://raw.githubusercontent.com/$REPO/main/$F") || { echo "$ts FETCH_FAIL"; exit 2; }
sha=$(printf '%s' "$raw" | sha256sum | cut -d' ' -f1)
if printf '%s' "$raw" | grep -qE 'pin_url_to_resolved_ip|validate_url_for_connection_pinning'; then
  echo "$ts FIXED sha256=$sha"; exit 0
fi
echo "$ts UNFIXED sha256=$sha"

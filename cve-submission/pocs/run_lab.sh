#!/usr/bin/env bash
# Two-container lab for the /llmchat/connect DNS-rebinding SSRF.
#   gw  (10.77.0.2): gateway + internal MCP on its loopback + TTL cache
#   atk (10.77.0.3): attacker authoritative DNS + LLM stub
# Host runs the exploit driver against 10.77.0.2:4444.
set -euo pipefail

LAB="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$LAB/bin"
EV="$LAB/ev"
ENG="/home/teycir/BugBounty/mcp-context-forge/20261119/120219"
REPO="/home/teycir/ResearchAIRedTeam/mcp-context-forge"
PY="$LAB/venv/bin/python"
IMG=ubuntu:24.04
NET=labnet
GW=gw
ATK=atk

down() {
  docker rm -f "$GW" "$ATK" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}

up() {
  down
  mkdir -p "$EV" "$LAB/etc"
  printf 'nameserver 127.0.0.1\noptions ndots:1 timeout:2 attempts:1\n' > "$LAB/etc/resolv.conf"
  docker network create --subnet 10.77.0.0/24 "$NET" >/dev/null

  for pair in "$GW:10.77.0.2" "$ATK:10.77.0.3"; do
    name="${pair%%:*}"; ip="${pair##*:}"
    docker run -d --name "$name" --network "$NET" --ip "$ip" \
      --mount type=bind,src=/home/teycir,dst=/home/teycir \
      --mount type=bind,src="$LAB/etc/resolv.conf",dst=/etc/resolv.conf,readonly \
      -w "$LAB" "$IMG" sleep infinity >/dev/null
  done

  # attacker side: authoritative DNS
  docker exec -d "$ATK" "$PY" -u "$BIN/dns_auth.py"

  # gateway side: TTL cache, LLM stub (loopback), internal MCP, gateway
  docker exec -d "$GW" "$PY" -u "$BIN/dns_cache.py"
  docker exec -d "$GW" env LLM_LOG=/tmp/llm_stub.log "$PY" -u "$BIN/llm_stub.py"
  docker exec -d "$GW" env MCP_LOG=/tmp/internal.log "$PY" -u "$BIN/internal_mcp.py"
  docker exec -d "$GW" env \
    JWT_SECRET_KEY=6f1b7c2d9a4e8f3b5c0d2a7e9f1b3c5d7a9e0f2b4c6d8a1e3f5b7c9d0a2e4f6b \
    AUTH_ENCRYPTION_SECRET=8a2c4e6f0b1d3f5a7c9e1b3d5f7a9c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d1f3a \
    CSRF_SECRET_KEY=1f3b5d7a9c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d1f3a5c7e9b0d2f4a6c8e1b3d \
    BASIC_AUTH_PASSWORD='Str0ng-Pass-R4ndom-9281!' \
    PLATFORM_ADMIN_PASSWORD='Str0ng-Pass-R4ndom-9281!' \
    DEFAULT_USER_PASSWORD='Str0ng-Pass-R4ndom-9281!' \
    PLATFORM_ADMIN_EMAIL=admin@example.com \
    DATABASE_URL=sqlite:////tmp/gw.db \
    HOST=0.0.0.0 PORT=4444 \
    MCPGATEWAY_UI_ENABLED=true MCPGATEWAY_ADMIN_API_ENABLED=true \
    MCPGATEWAY_STDIO_TRANSPORT_ENABLED=false \
    SSRF_PROTECTION_ENABLED=true LLMCHAT_ENABLED=true \
    LOG_LEVEL=INFO REQUIRE_STRONG_SECRETS=true AUTH_REQUIRED=true \
    ALLOWED_ORIGINS='*' \
    HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
    sh -c "cd $REPO && exec $PY -m uvicorn mcpgateway.main:app --host 0.0.0.0 --port 4444 > /tmp/gw.log 2>&1"

  for i in $(seq 1 120); do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 http://10.77.0.2:4444/health || true)
    [ "$code" = "200" ] && { echo "gateway healthy after ${i}s"; return 0; }
    sleep 1
  done
  echo "gateway did not become healthy" >&2
  docker exec "$GW" tail -40 /tmp/gw.log >&2 || true
  return 1
}

collect() {
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  d="$ENG/evidence/lab-$ts"
  mkdir -p "$d"
  docker exec "$GW" cat /tmp/gw.log > "$d/gw.log" 2>/dev/null || true
  docker exec "$GW" cat /tmp/dns_cache.log > "$d/dns_cache.log" 2>/dev/null || true
  docker exec "$GW" cat /tmp/internal.log > "$d/internal.log" 2>/dev/null || true
  docker exec "$GW" cat /etc/resolv.conf > "$d/gw_resolv.conf" 2>/dev/null || true
  docker exec "$ATK" cat /tmp/dns.log > "$d/dns_authoritative.log" 2>/dev/null || true
  docker exec "$GW" cat /tmp/llm_stub.log > "$d/llm_stub.log" 2>/dev/null || true
  cp "$EV"/*.json "$EV"/*.txt "$EV"/*.http "$d"/ 2>/dev/null || true
  ( cd "$d" && sha256sum * > sha256sums.txt )
  echo "collected -> $d"
}

case "${1:-all}" in
  up) up ;;
  down) down ;;
  collect) collect ;;
  all) up; "$PY" "$BIN/exploit.py" --out "$EV"; collect ;;
  *) echo "usage: $0 {up|down|collect|all}"; exit 1 ;;
esac

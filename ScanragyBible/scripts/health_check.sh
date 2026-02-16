#!/usr/bin/env bash
# ============================================
# Scarnergy Health Check
# ============================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
  local name="$1" url="$2"
  if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} $name"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} $name — $url"
    ((FAIL++))
  fi
}

check_port() {
  local name="$1" port="$2"
  if nc -z localhost "$port" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} $name (port $port)"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} $name (port $port)"
    ((FAIL++))
  fi
}

echo ""
echo "═══════════════════════════════════════"
echo " Scarnergy v2.0 — Health Check"
echo "═══════════════════════════════════════"
echo ""

echo "Database Layer:"
check_port "PostgreSQL + TimescaleDB" 5432
check_port "Redis" 6379

echo ""
echo "Supabase Services:"
check "PostgREST API" "http://localhost:3001/"
check_port "GoTrue Auth" 9999
check_port "Realtime" 4000
check "Supabase Studio" "http://localhost:3000/"

echo ""
echo "IoT Layer:"
check_port "MQTT Broker" 1883
check_port "MQTT WebSocket" 9001
check_port "BLE Bridge WebSocket" 8765

echo ""
echo "AI & Reporting:"
check "AI Engine" "http://localhost:8500/health"
check_port "Report Engine" 8600

echo ""
echo "Dashboards:"
check "Metabase" "http://localhost:3003/api/health"
check "Grafana" "http://localhost:3030/api/health"

echo ""
echo "═══════════════════════════════════════"
echo -e " Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}"
echo "═══════════════════════════════════════"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo -e "${YELLOW}Tip: Run 'docker compose logs <service>' to debug failures${NC}"
  exit 1
fi

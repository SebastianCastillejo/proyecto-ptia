#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
python -m uvicorn app.main:app --reload --port 8000 & API_PID=$!
cd "$ROOT/frontend"
npm run dev -- --host 127.0.0.1 & FRONT_PID=$!
trap 'kill "$API_PID" "$FRONT_PID" 2>/dev/null || true' EXIT INT TERM
echo "API: http://localhost:8000/api/salud | Front: http://localhost:5173"
wait

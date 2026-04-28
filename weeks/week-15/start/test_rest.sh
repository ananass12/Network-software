#!/usr/bin/env bash
set -euo pipefail

CONCURRENCY="${1:-}"
DURATION="${DURATION:-15s}"
THREADS="${THREADS:-2}"
URL="${URL:-http://127.0.0.1:8080/api/likes}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_once() {
  local c="$1"
  local t="${THREADS}"
  if [[ "${c}" -lt "${t}" ]]; then
    t="${c}"
  fi
  echo "=== REST benchmark: concurrency=${c} ==="
  wrk --latency -t"${t}" -c"${c}" -d"${DURATION}" -s "${SCRIPT_DIR}/post.lua" "${URL}"
  echo
}

if [[ -n "${CONCURRENCY}" ]]; then
  run_once "${CONCURRENCY}"
else
  for c in 1 10 100; do
    run_once "${c}"
  done
fi
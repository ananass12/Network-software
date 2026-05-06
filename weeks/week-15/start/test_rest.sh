#!/usr/bin/env bash
set -euo pipefail

CONCURRENCY="${1:-}"
DURATION="${DURATION:-15s}"
THREADS="${THREADS:-2}"
URL="${URL:-http://127.0.0.1:8080/api/likes}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${OUT_DIR:-results}"

mkdir -p "${OUT_DIR}"

run_once() {
  local c="$1"
  local out_file="${OUT_DIR}/rest_c${c}.txt"
  local t="${THREADS}"
  if [[ "${c}" -lt "${t}" ]]; then
    t="${c}"
  fi
  echo "    REST benchmark: concurrency=${c}    "
  wrk --latency -t"${t}" -c"${c}" -d"${DURATION}" -s "${SCRIPT_DIR}/post.lua" "${URL}" | tee "${out_file}"
  echo
}

if [[ -n "${CONCURRENCY}" ]]; then
  run_once "${CONCURRENCY}"
else
  for c in 1 10 100 200 500; do
    run_once "${c}"
  done
fi
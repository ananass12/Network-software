#!/usr/bin/env bash
set -euo pipefail

CONCURRENCY="${1:-}"
DURATION="${DURATION:-15s}"
TARGET="${TARGET:-127.0.0.1:8174}"
PROTO="${PROTO:-../proto/service.proto}"
CALL="${CALL:-likes.v2.LikesService.CreateLike}"
OUT_DIR="${OUT_DIR:-results}"

mkdir -p "${OUT_DIR}"

run_once() {
  local c="$1"
  local out_file="${OUT_DIR}/grpc_c${c}.txt"
  echo "=== gRPC benchmark: concurrency=${c} ==="
  ghz --insecure \
    --proto "${PROTO}" \
    --call "${CALL}" \
    --data '{"target":"post_123"}' \
    --connections "${c}" \
    --concurrency "${c}" \
    --duration "${DURATION}" \
    "${TARGET}" | tee "${out_file}"
  echo
}

if [[ -n "${CONCURRENCY}" ]]; then
  run_once "${CONCURRENCY}"
else
  for c in 1 10 100; do
    run_once "${c}"
  done
fi
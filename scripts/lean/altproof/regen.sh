#!/usr/bin/env bash
# Advisory elegance-suite regeneration gate (v0.5.0).
# - regenerates route-table.json from route_definitions.py
# - optionally re-mines cross-theorem have-clusters over LEAN_SRC_DIR if provided
# - runs the AltProof route-table pytest gate
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

python3 "$SCRIPT_DIR/gen_route_table.py"

if [[ -n "${LEAN_SRC_DIR:-}" && -d "${LEAN_SRC_DIR}" ]]; then
  OUT_MD="${HAVE_CLUSTERS_OUT:-$ROOT/.cache/HAVE_CLUSTERS.md}"
  mkdir -p "$(dirname "$OUT_MD")"
  python3 "$SCRIPT_DIR/have_cluster.py" "$LEAN_SRC_DIR" "$OUT_MD"
fi

python3 -m pytest "$ROOT/tests/lean/test_altproof_route_table.py" -q

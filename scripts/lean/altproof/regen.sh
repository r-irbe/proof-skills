#!/usr/bin/env bash
# Advisory elegance-suite regeneration gate (S8 v1).
# - re-mines cross-theorem have-clusters over the current corpus
# - updates HAVE_CLUSTERS.md
# - tracks the cluster count as the elegance-drift metric
# - runs the tools test suite
# Advisory: exits 0 even on drift; the numbers are for the ledger.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="$ROOT/docs/investigation-garden/altproof/.elegance-drift.json"
python3 "$ROOT/tools/altproof/have_cluster.py" \
  "$ROOT/docs/easci/lean/EASCI" \
  "$ROOT/docs/investigation-garden/altproof/HAVE_CLUSTERS.md"
NOW=$(python3 -c "import json;print(json.load(open('$STATE'))['current'] if __import__('pathlib').Path('$STATE').exists() else 'first-run')" 2>/dev/null || echo first-run)
NEW=$(grep -c '^|' "$ROOT/docs/investigation-garden/altproof/HAVE_CLUSTERS.md")
python3 - "$STATE" "$NOW" "$NEW" <<'PYEOF'
import json, sys
state, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
rec = {"previous": None if old == "first-run" else int(old), "current": int(new) - 2}
json.dump(rec, open(state, "w"), indent=2)
print(f"elegance-drift: {rec['previous']} -> {rec['current']}")
PYEOF
python3 -m pytest "$ROOT/tests/tools/" -q 2>&1 | tail -1

#!/usr/bin/env bash
# Replay verification for a Lean 4 corpus - R1 + R2 of the
# lean-replay-verification skill.
#
# Usage: replay_verify.sh [axiom_audit flags...]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== R1: fresh kernel replay (cold state) =="
lake clean || exit 1
lake build > /tmp/replay_verify_build.log 2>&1
rc=$?
tail -3 /tmp/replay_verify_build.log
if [ $rc -ne 0 ]; then
  echo "R1 FAIL: lake build rc=$rc (log: /tmp/replay_verify_build.log)"
  exit 1
fi
jobs=$(grep -c "info: .*Building\|info: .*Compiling" /tmp/replay_verify_build.log 2>/dev/null || echo "?")
echo "R1 PASS: full rebuild from cold state (rc=0, ~${jobs} build steps)"
echo ""

echo "== R2: axiom-closure audit =="
if [ -f "scripts/axiom_audit.py" ]; then
  python3 scripts/axiom_audit.py "$@"
else
  python3 "$SCRIPT_DIR/axiom_audit.py" "$@"
fi
rc2=$?
if [ $rc2 -eq 0 ]; then
  echo "R2 PASS: axiom closure matches the expected-axioms allowlist"
else
  echo "R2 FAIL: axiom audit rc=$rc2"
fi
exit $rc2

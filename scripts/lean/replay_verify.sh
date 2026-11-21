#!/usr/bin/env bash
# Replay verification for a Lean 4 corpus - R1 + R2 of the
# lean-replay-verification skill.
#
# Usage: replay_verify.sh [axiom_audit flags...]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/cold_kernel_replay.lean" ]; then
  echo "R3 FAIL: required cold kernel replay driver missing: $SCRIPT_DIR/cold_kernel_replay.lean" >&2
  exit 1
fi
REPLAY_LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/proof-skills-replay.XXXXXX")" || exit 1
REPLAY_BUILD_LOG="$REPLAY_LOG_DIR/build.log"

echo "== R1: cold source rebuild =="
lake clean || exit 1
lake build > "$REPLAY_BUILD_LOG" 2>&1
rc=$?
tail -3 "$REPLAY_BUILD_LOG"
if [ $rc -ne 0 ]; then
  echo "R1 FAIL: lake build rc=$rc (log: $REPLAY_BUILD_LOG)"
  exit 1
fi
echo "R1 PASS: full rebuild from cold state (rc=0, log: $REPLAY_BUILD_LOG)"
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
  exit $rc2
fi
echo ""

echo "== R3: cold in-process Lean.Kernel.Environment.replay =="
if [ -d ".lake/build/lib/lean" ]; then
  COLD_REPLAY_LIB_DIR=".lake/build/lib/lean" lake env lean "$SCRIPT_DIR/cold_kernel_replay.lean"
  rc3=$?
  if [ $rc3 -eq 0 ]; then
    echo "R3 PASS: cold Lean.Kernel.Environment.replay + Lean.collectAxioms passed across all slice constants"
  else
    echo "R3 FAIL: cold kernel replay rc=$rc3"
    exit $rc3
  fi
else
  echo "R3 FAIL: compiled library directory .lake/build/lib/lean is missing" >&2
  exit 1
fi
exit 0

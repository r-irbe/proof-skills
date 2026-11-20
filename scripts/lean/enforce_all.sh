#!/usr/bin/env bash
# Full Enforcement Pipeline (Two-Tier: Tier 1 lean-rules + Tier 2 Audit & Gate Checks)
# Runs declarative AST/regex lint rules followed by structural, axiom, and quality gates.
#
# Usage:
#   ./enforce_all.sh [LEAN_DIR] [--strict]
# Environment overrides:
#   LEAN_RULES_PROFILE=core|default|kernel|fluid-pde|p2m|all (default: core)

set -uo pipefail

LEAN_DIR="${1:-src}"
STRICT="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CALLER_SCRIPTS="${ENFORCE_SCRIPTS_DIR:-scripts}"
TRACKING_DIR="${TRACKING_DIR:-docs/tracking}"
LEAN_RULES_PROFILE="${LEAN_RULES_PROFILE:-core}"
LEAN_RULES_BIN="$SKILLS_ROOT/tools/lean-lsp-mcp/bin/lean-rules.js"
EXIT_CODE=0

mkdir -p "$TRACKING_DIR"

run_py() {
    local name="$1"
    shift
    if [ -f "$CALLER_SCRIPTS/$name" ]; then
        python3 "$CALLER_SCRIPTS/$name" "$@"
    else
        python3 "$SCRIPT_DIR/$name" "$@"
    fi
}

run_sh() {
    local name="$1"
    shift
    if [ -f "$CALLER_SCRIPTS/$name" ]; then
        bash "$CALLER_SCRIPTS/$name" "$@"
    else
        bash "$SCRIPT_DIR/$name" "$@"
    fi
}

echo "=========================================="
echo "       LEAN ENFORCEMENT PIPELINE          "
echo "=========================================="
echo ""
echo "Lean directory: $LEAN_DIR"
echo "Rules profile:  $LEAN_RULES_PROFILE"
echo "Tracking output: $TRACKING_DIR"
echo ""

# Phase 1: Build
echo "=== Phase 1: Build Check ==="
if lake build 2>&1 | tail -5; then
    echo "[PASS] Build: PASS"
    echo ""
else
    echo "[FAIL] Build: FAIL -- aborting pipeline"
    exit 2
fi

# Phase 2: Tier 1 Declarative Rules (lean-rules) + Tier 2 Static Analysis
echo "=== Phase 2: Tier 1 Declarative Lint Rules & Tier 2 Static Analysis ==="

echo "--- Tier 1: lean-rules (--profile=$LEAN_RULES_PROFILE) ---"
if command -v node >/dev/null 2>&1 && [ -f "$LEAN_RULES_BIN" ]; then
    if node "$LEAN_RULES_BIN" --profile="$LEAN_RULES_PROFILE" "$LEAN_DIR" 2>&1; then
        echo "[PASS] lean-rules ($LEAN_RULES_PROFILE): PASS"
    else
        echo "[WARN] lean-rules ($LEAN_RULES_PROFILE): findings reported"
        EXIT_CODE=1
    fi
else
    echo "[INFO] node or lean-rules.js unavailable -- falling back to shell council_precheck.sh"
fi
echo ""

echo "--- Council Pre-Check ---"
if run_sh council_precheck.sh "$LEAN_DIR" 2>&1; then
    echo "[PASS] Council pre-check: PASS"
else
    echo "[WARN] Council pre-check: issues found"
    EXIT_CODE=1
fi
echo ""

echo "--- Axiom Audit ---"
if run_py axiom_audit.py --lean-dir "$LEAN_DIR" --output "$TRACKING_DIR/axiom_audit.md" --generate-script 2>&1; then
    echo "[PASS] Axiom audit: generated"
else
    echo "[WARN] Axiom audit: failed"
    EXIT_CODE=1
fi
echo ""

echo "--- Proof Quality Analysis ---"
if run_py proof_quality.py --lean-dir "$LEAN_DIR" --output "$TRACKING_DIR/proof_quality.md" 2>&1; then
    echo "[PASS] Proof quality: PASS"
else
    echo "[WARN] Proof quality: issues found"
    EXIT_CODE=1
fi
echo ""

# Phase 3: Reconnaissance
echo "=== Phase 3: Reconnaissance ==="

echo "--- RETRO Reconnaissance ---"
if run_py retro_recon.py --lean-dir "$LEAN_DIR" --output "$TRACKING_DIR/recon_report.md" 2>&1; then
    echo "[PASS] Reconnaissance: complete"
else
    echo "[WARN] Reconnaissance: failed"
    EXIT_CODE=1
fi
echo ""

# Phase 4: Cross-module validation
echo "=== Phase 4: Cross-Module Validation ==="

echo "--- Bridge Validator ---"
if run_py bridge_validator.py --lean-dir "$LEAN_DIR" 2>&1; then
    echo "[PASS] Bridge validation: PASS"
else
    echo "[WARN] Bridge validation: issues found"
    EXIT_CODE=1
fi
echo ""

echo "--- Metric Sync ---"
if run_py metric_sync.py --lean-dir "$LEAN_DIR" 2>&1; then
    echo "[PASS] Metric sync: PASS"
else
    echo "[WARN] Metric sync: out of sync"
    EXIT_CODE=1
fi
echo ""

# Phase 5: Knowledge base
echo "=== Phase 5: Knowledge Base ==="

echo "--- Zettelkasten Lint ---"
if run_py zettelkasten_lint.py 2>&1; then
    echo "[PASS] Zettelkasten: healthy"
else
    echo "[WARN] Zettelkasten: issues found"
    EXIT_CODE=1
fi
echo ""

# Phase 6: Ecosystem
echo "=== Phase 6: Ecosystem Health ==="

echo "--- Ecosystem Health ---"
if run_py ecosystem_health.py 2>&1; then
    echo "[PASS] Ecosystem: healthy"
else
    echo "[WARN] Ecosystem: issues found"
    EXIT_CODE=1
fi
echo ""

# Phase 7: Build Timing
echo "=== Phase 7: Build Timing ==="

TIMING_JSON="${LAKE_TIMING_JSON:-}"
if [ -n "$TIMING_JSON" ] && [ -f "$TIMING_JSON" ]; then
    echo "--- Build Timing Report ---"
    if run_py build_timing_report.py "$TIMING_JSON" "$TRACKING_DIR/lake_timing.md" 2>&1; then
        echo "[PASS] Build timing: generated ($TRACKING_DIR/lake_timing.md)"
    else
        echo "[WARN] Build timing: report generation failed"
        EXIT_CODE=1
    fi
else
    echo "[INFO] Build timing: no LAKE_TIMING_JSON provided -- skipping."
fi
echo ""

echo "=========================================="
echo "              SUMMARY                     "
echo "=========================================="
echo ""
echo "Reports generated:"
ls -la "$TRACKING_DIR"/*.md 2>/dev/null | awk '{print "  " $NF}'
echo ""

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "[PASS] ALL CHECKS PASSED"
else
    echo "[WARN] SOME CHECKS REPORTED ISSUES"
    if [ "$STRICT" = "--strict" ]; then
        echo "  (strict mode: exiting with error)"
        exit 1
    fi
fi

exit $EXIT_CODE

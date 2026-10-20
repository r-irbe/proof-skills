#!/usr/bin/env bash
# Council Pre-Check Script
# Run before any council review session to verify project health.
#
# Usage:
#   ./council_precheck.sh [LEAN_DIR] [--strict]

set -euo pipefail

LEAN_DIR="${1:-EASCI}"
STRICT="${2:-}"
ERRORS=0
WARNINGS=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  Council Pre-Check"
echo "========================================="
echo ""

# 1. Build check
echo "--- Build Check ---"
if lake build 2>&1 | tail -5; then
    echo "[PASS] Build: PASS"
else
    echo "[FAIL] Build: FAIL"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Proof escape check
echo "--- Proof Escape Check ---"
ESCAPE_REPORT="$(mktemp)"
ESCAPE_COUNT=$(python3 - "$LEAN_DIR" "$ESCAPE_REPORT" "$SCRIPT_DIR" <<'PY'
from pathlib import Path
import re
import sys

lean_dir = Path(sys.argv[1])
report = Path(sys.argv[2])
script_dir = Path(sys.argv[3])
sys.path.insert(0, str(script_dir))

from axiom_audit import strip_comments_preserving_newlines

findings = []
for lean_file in sorted(lean_dir.rglob('*.lean')):
    source = strip_comments_preserving_newlines(
        lean_file.read_text(encoding='utf-8')
    )
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        if re.search(r'\bsorry\b|\badmit\b', raw_line):
            findings.append((lean_file, line_no, raw_line.strip()))

report.write_text(
    ''.join(f'{path}:{line_no}: {line}\n' for path, line_no, line in findings[:20]),
    encoding='utf-8',
)
print(len(findings))
PY
)
if [ "$ESCAPE_COUNT" -eq 0 ]; then
    echo "[PASS] Proof escapes: 0 real sorry/admit instances"
else
    echo "[WARN] Proof escapes: $ESCAPE_COUNT real sorry/admit instance(s)"
    cat "$ESCAPE_REPORT"
    WARNINGS=$((WARNINGS + 1))
fi
rm -f "$ESCAPE_REPORT"
echo ""

# 3. Convention check
echo "--- Convention Check ---"

AUTO_REPORT="$(mktemp)"
AUTO_MISSING=$(python3 - "$LEAN_DIR" "$AUTO_REPORT" <<'PY'
from pathlib import Path
import sys

lean_dir = Path(sys.argv[1])
report = Path(sys.argv[2])
missing = []
for lean_file in sorted(lean_dir.rglob('*.lean')):
    text = lean_file.read_text(encoding='utf-8')
    if 'set_option autoImplicit false' not in text:
        missing.append(lean_file)
report.write_text(''.join(f'    {path}\n' for path in missing), encoding='utf-8')
print(len(missing))
PY
)
if [ "$AUTO_MISSING" -eq 0 ]; then
    echo "[PASS] autoImplicit false: all modules"
else
    echo "[WARN] autoImplicit false: missing in $AUTO_MISSING module(s):"
    cat "$AUTO_REPORT"
    WARNINGS=$((WARNINGS + 1))
fi
rm -f "$AUTO_REPORT"

DOC_REPORT="$(mktemp)"
DOC_MISSING=$(python3 - "$LEAN_DIR" "$DOC_REPORT" <<'PY'
from pathlib import Path
import re
import sys

lean_dir = Path(sys.argv[1])
report = Path(sys.argv[2])
missing = []
for lean_file in sorted(lean_dir.rglob('*.lean')):
    text = lean_file.read_text(encoding='utf-8')
    if re.search(r'^/-!', text, flags=re.MULTILINE) is None:
        missing.append(lean_file)
report.write_text(''.join(f'    {path}\n' for path in missing), encoding='utf-8')
print(len(missing))
PY
)
if [ "$DOC_MISSING" -eq 0 ]; then
    echo "[PASS] Module docstrings: all modules"
else
    echo "[WARN] Module docstrings: missing in $DOC_MISSING module(s):"
    cat "$DOC_REPORT"
    WARNINGS=$((WARNINGS + 1))
fi
rm -f "$DOC_REPORT"
echo ""

# 4. Git status
echo "--- Git Status ---"
if git diff --quiet HEAD 2>/dev/null; then
    echo "[PASS] Git: clean working tree"
else
    CHANGED=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
    echo "[WARN] Git: $CHANGED file(s) with uncommitted changes"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 5. Quick metrics
echo "--- Project Metrics ---"
read -r MODULE_COUNT TOTAL_LINES TOTAL_THMS TOTAL_DEFS RAW_AXIOMS <<< "$(python3 - "$LEAN_DIR" "$SCRIPT_DIR" <<'PY'
from pathlib import Path
import re
import sys

lean_dir = Path(sys.argv[1])
script_dir = Path(sys.argv[2])
sys.path.insert(0, str(script_dir))

from axiom_audit import extract_theorems, scan_raw_axioms, strip_comments_preserving_newlines

files = sorted(lean_dir.rglob('*.lean'))
defs_re = re.compile(r'^(?:def|structure|inductive|class)\b')
defs = 0
for lean_file in files:
    source = strip_comments_preserving_newlines(
        lean_file.read_text(encoding='utf-8')
    )
    defs += sum(1 for line in source.splitlines() if defs_re.search(line))
lines = sum(len(path.read_text(encoding='utf-8').splitlines()) for path in files)
theorems = sum(len(names) for names in extract_theorems(lean_dir).values())
raw_axioms = sum(len(items) for items in scan_raw_axioms(lean_dir).values())
print(len(files), lines, theorems, defs, raw_axioms)
PY
)"

echo "  Lines:       $TOTAL_LINES"
echo "  Theorems:    $TOTAL_THMS"
echo "  Definitions: $TOTAL_DEFS"
echo "  Modules:     $MODULE_COUNT"
echo "  Escapes:     $ESCAPE_COUNT"
echo "  Raw axioms:  $RAW_AXIOMS"
echo ""

echo "========================================="
echo "  Summary: $ERRORS error(s), $WARNINGS warning(s)"
echo "========================================="

if [ "$ERRORS" -gt 0 ]; then
    echo "FAIL: Fix errors before starting council review"
    exit 1
elif [ "$WARNINGS" -gt 0 ] && [ "$STRICT" = "--strict" ]; then
    echo "FAIL (strict mode): Fix warnings before starting council review"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "PASS with warnings"
    exit 0
else
    echo "PASS: Ready for council review"
    exit 0
fi

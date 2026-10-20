#!/usr/bin/env bash
# lean_lint_harvest.sh -- harvest linter findings corpus-wide, read-only.
#
# Runs `lake env lean -D<flag>=true` per file (no lakefile change, no build
# artifact churn: safe on a shared tree while other sessions build), in
# parallel, and tabulates findings per linter per module.
#
# Usage:
#   scripts/lean_lint_harvest.sh <out.tsv> "<flag1> <flag2> ..." [<file>...]

set -euo pipefail
OUT="${1:?usage: lean_lint_harvest.sh <out.tsv> \"<flags>\" [files...]}"
FLAGS="${2:?usage: lean_lint_harvest.sh <out.tsv> \"<flags>\" [files...]}"
shift 2
JOBS="${HARVEST_JOBS:-8}"
TMO="${HARVEST_TIMEOUT:-300}"
LEAN_DIR="${LEAN_DIR:-EASCI}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
PKG_DIR="$(pwd)"
[ -f "$PKG_DIR/lakefile.toml" ] || [ -f "$PKG_DIR/lakefile.lean" ] || { echo "not in a lake package" >&2; exit 1; }

if [ "$#" -gt 0 ]; then FILES=("$@"); else
  mapfile -t FILES < <(git ls-files "$LEAN_DIR/**/*.lean" "$LEAN_DIR/*.lean")
fi

# Delegation: prefer the packaged TS port (row semantics locked by
# tests in lean-analysis / lean-lsp-mcp); the awk path below mirrors it for no-node hosts.
SCRIPT_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for HARVEST_CLI in \
  "$ROOT/packages/lean-analysis/bin/lean-harvest.js" \
  "$ROOT/docs/easci/lean/skills/tools/lean-lsp-mcp/bin/lean-harvest.js" \
  "$SCRIPT_HERE/../../tools/lean-lsp-mcp/bin/lean-harvest.js"; do
  if [ -f "$HARVEST_CLI" ] && command -v node >/dev/null 2>&1; then
    exec node "$HARVEST_CLI" "$OUT" "$FLAGS" "${FILES[@]}"
  fi
done

harvest_one() {
  f="$1"
  for fl in $HARVEST_FLAGS; do
    msg=$(cd "${HARVEST_PKG:-.}" && timeout "$HARVEST_TMO" lake env lean "-D$fl=true" "$f" 2>&1 || true)
    case "$fl" in
      linter.style.header) pat="header|doc-string" ;;
      linter.style.multiGoal) pat="multigoal|multiple goals" ;;
      linter.style.haveILetI) pat="haveilet|have" ;;
      *) pat="." ;;
    esac
    printf '%s\n' "$msg" | awk -v F="$f" -v L="$fl" -v P="$pat" '
      /^[^ ].*: (warning|error|information):/ {
        low = tolower($0)
        if (low ~ tolower(P)) {
          line="0"
          if (match($0, /:[0-9]+:/)) line = substr($0, RSTART+1, RLENGTH-2)
          msg=$0; sub(/^[^ ]*: /, "", msg)
          printf "%s\t%s\t%s\t%s\n", L, F, line, msg
        }
      }
      /invalid -D parameter/ {
        line="0"
        if (match($0, /:[0-9]+:/)) line = substr($0, RSTART+1, RLENGTH-2)
        printf "COVERAGE\t%s\t%s\t%s\n", F, line, $0
      }'
  done
}
export -f harvest_one
export HARVEST_PKG="$PKG_DIR" HARVEST_TMO="$TMO" HARVEST_FLAGS="$FLAGS"

: > "$OUT"
printf '%s\n' "${FILES[@]}" | xargs -P "$JOBS" -I{} bash -c 'harvest_one "$@"' _ {} >> "$OUT"

echo "== harvest: $FLAGS =="
echo "   files scanned : ${#FILES[@]}"
echo "   findings      : $(wc -l < "$OUT")"
awk -F'\t' '{c[$1]++} END {for (k in c) printf "   %-28s %d\n", k, c[k]}' "$OUT" | sort

#!/usr/bin/env bash
# profile_build.sh -- per-module compilation timing for a Lean 4 project.
# Auto-discovers modules from lean-project.toml, lakefile.lean, or .lake/build/lib/lean/.
# Strict 7-bit ASCII only (INV-001).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${LEAN_PROJECT_ROOT:-$(pwd)}"

eval "$(python3 - "$HERE" "$PROJECT_ROOT" <<'PYEOF'
import shlex, sys
sys.path.insert(0, sys.argv[1])
from project_config import load_project_config
cfg = load_project_config(sys.argv[2])
print(f"PROJECT_NAME={shlex.quote(cfg.name)}")
print(f"LEAN_DIR={shlex.quote(str(cfg.root))}")
print(f"CORPUS_SUBDIR={shlex.quote(cfg.lean_dir)}")
mods = " ".join(shlex.quote(m) for m in cfg.core_modules)
print(f"MODULES=({mods})")
PYEOF
)"

cd "$LEAN_DIR" || exit 1

if [ "$CORPUS_SUBDIR" != "." ] && [ -n "$CORPUS_SUBDIR" ]; then
  OLEAN_BASE="${LEAN_DIR}/.lake/build/lib/lean/${CORPUS_SUBDIR}"
  SRC_BASE="${LEAN_DIR}/${CORPUS_SUBDIR}"
  MOD_PREFIX="${CORPUS_SUBDIR}."
else
  OLEAN_BASE="${LEAN_DIR}/.lake/build/lib/lean"
  SRC_BASE="${LEAN_DIR}"
  MOD_PREFIX=""
fi

if [ "${1:-}" = "--list-modules" ]; then
  for MOD in "${MODULES[@]}"; do
    echo "${MOD_PREFIX}${MOD}"
  done
  exit 0
fi

echo "| Module | Lines | Build time (s) |"
echo "|---|---:|---:|"

for MOD in "${MODULES[@]}"; do
  SRC="${SRC_BASE}/${MOD}.lean"
  [ -f "$SRC" ] || continue
  LINES=$(wc -l < "$SRC" | tr -d ' ')

  rm -f "${OLEAN_BASE}/${MOD}.olean" "${OLEAN_BASE}/${MOD}.ilean" 2>/dev/null || true

  BUILD_OUT=$(timeout 300 lake build --verbose "${MOD_PREFIX}${MOD}" 2>&1 || true)
  TIME=$(echo "$BUILD_OUT" | grep -oE "Built ${MOD_PREFIX}${MOD} \([0-9.]+s\)" \
         | grep -oE '[0-9.]+s' | head -1 || true)
  TIME="${TIME:-cached/no-change}"

  echo "| ${MOD} | ${LINES} | ${TIME} |"
done

pkill -f "lake build" 2>/dev/null || true

#!/usr/bin/env bash
# census.sh -- Dynamic Lean 4 module & recursive corpus census.
# Auto-discovers modules from lean-project.toml, lakefile.lean, or .lake/build/lib/lean/.
# Strict 7-bit ASCII only (INV-001).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${LEAN_PROJECT_ROOT:-$(pwd)}"

eval "$(python3 - "$HERE" "$PROJECT_ROOT" <<'PYEOF'
import shlex, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from project_config import load_project_config
cfg = load_project_config(sys.argv[2])
print(f"PROJECT_NAME={shlex.quote(cfg.name)}")
print(f"PROJECT_ROOT={shlex.quote(str(cfg.root))}")
print(f"LEAN_DIR={shlex.quote(cfg.lean_dir)}")
mods = " ".join(shlex.quote(m) for m in cfg.core_modules)
print(f"CORE_MODULES=({mods})")
PYEOF
)"

CORPUS_DIR="$PROJECT_ROOT"
if [ "$LEAN_DIR" != "." ] && [ -n "$LEAN_DIR" ]; then
  CORPUS_DIR="$PROJECT_ROOT/$LEAN_DIR"
fi

cd "$CORPUS_DIR" || exit 1

echo "=== ${PROJECT_NAME} Lean 4 Module Census ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

total_lines=0
total_thms=0
total_simp=0

printf "%-25s %6s %6s %6s\n" "Module" "Lines" "Thms" "@[simp]"
printf "%-25s %6s %6s %6s\n" "-------------------------" "------" "------" "------"

for f in "${CORE_MODULES[@]}"; do
  [ -f "${f}.lean" ] || continue
  lines=$(wc -l < "${f}.lean" 2>/dev/null | tr -d ' ')
  thms=$(grep -c "^theorem\|^lemma" "${f}.lean" 2>/dev/null || true)
  simp=$( (grep -v "^\s*--" "${f}.lean" 2>/dev/null || true) | grep -c "@\[simp\]" || true)
  printf "%-25s %6s %6s %6s\n" "$f" "$lines" "$thms" "$simp"
  total_lines=$((total_lines + lines))
  total_thms=$((total_thms + thms))
  total_simp=$((total_simp + simp))
done

printf "%-25s %6s %6s %6s\n" "-------------------------" "------" "------" "------"
printf "%-25s %6s %6s %6s\n" "TOTAL (Core ${#CORE_MODULES[@]})" "$total_lines" "$total_thms" "$total_simp"
echo ""
echo "=== Full ${PROJECT_NAME} Recursive Corpus Census ==="
python3 -c '
import os, re

def strip_lean_comments(text):
    result = []
    i = 0
    n = len(text)
    depth = 0
    while i < n:
        if depth == 0 and text[i:i+2] == "--":
            i += 2
            while i < n and text[i] != "\n":
                i += 1
        elif text[i:i+2] == "/-":
            depth += 1
            i += 2
        elif depth > 0 and text[i:i+2] == "-/":
            depth -= 1
            i += 2
        elif depth > 0:
            if text[i] == "\n":
                result.append("\n")
            i += 1
        else:
            result.append(text[i])
            i += 1
    return "".join(result)

lean_files = []
for root, dirs, files in os.walk("."):
    if ".lake" in root.split(os.sep):
        continue
    for f in files:
        if f.endswith(".lean"):
            lean_files.append(os.path.join(root, f))
lean_files.sort()

thm_pattern = re.compile(r"^\s*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_\.]+)", re.MULTILINE)
def_pattern = re.compile(r"^\s*(?:protected\s+)?(?:def)\s+([A-Za-z0-9_\.]+)", re.MULTILINE)
sorry_pattern = re.compile(r"\bsorry\b")
admit_pattern = re.compile(r"\badmit\b")
axiom_pattern = re.compile(r"^\s*(?:protected\s+)?axiom\s+([A-Za-z0-9_\.]+)", re.MULTILINE)

total_thms = 0
total_defs = 0
total_sorry = 0
total_admit = 0
total_axioms = 0
total_lines = 0

for path in lean_files:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    total_lines += len(content.splitlines())
    code_only = strip_lean_comments(content)
    total_thms += len(thm_pattern.findall(code_only))
    total_defs += len(def_pattern.findall(code_only))
    total_sorry += len(sorry_pattern.findall(code_only))
    total_admit += len(admit_pattern.findall(code_only))
    total_axioms += len(axiom_pattern.findall(code_only))

print(f"Files:             {len(lean_files)}")
print(f"Total Lines:       {total_lines}")
print(f"Theorems + Lemmas: {total_thms}")
print(f"Definitions:       {total_defs}")
print(f"Total Decls:       {total_thms + total_defs}")
print(f"sorry count:       {total_sorry}")
print(f"admit count:       {total_admit}")
print(f"axiom count:       {total_axioms}")
'

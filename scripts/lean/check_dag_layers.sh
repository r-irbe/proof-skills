#!/usr/bin/env bash
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
# check_dag_layers.sh — verify Lean module DAG layer discipline.
#
# Usage:
#   check_dag_layers.sh LEAN_DIR LAYER_CONFIG
#
# LAYER_CONFIG is JSON of the form:
#   {"project": "MyProject", "layers": [["Mod1", "Mod2"], ["Mod3", "Mod4.Sub"]]}
#
# The first list is layer 0, the second is layer 1, and so on. A module at
# layer N must not import any configured module at layer N+1 or higher.
# Intra-layer imports are allowed. Imports involving modules absent from the
# config are skipped.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 LEAN_DIR LAYER_CONFIG" >&2
  exit 2
fi

LEAN_DIR="$1"
LAYER_CONFIG="$2"

if [[ ! -d "$LEAN_DIR" ]]; then
  echo "check_dag_layers: cannot find Lean directory: $LEAN_DIR" >&2
  exit 2
fi
if [[ ! -f "$LAYER_CONFIG" ]]; then
  echo "check_dag_layers: cannot find layer config: $LAYER_CONFIG" >&2
  exit 2
fi

LEAN_DIR="$(cd "$LEAN_DIR" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PROJECT="$(python3 - "$LAYER_CONFIG" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)
project = data.get('project', 'MyProject')
if not isinstance(project, str) or not project:
    raise SystemExit('invalid layer config: project must be a non-empty string')
print(project)
PY
)"

declare -A LAYERS
while IFS=$'\t' read -r module layer; do
  [[ -n "$module" ]] || continue
  LAYERS["$module"]="$layer"
done < <(python3 - "$LAYER_CONFIG" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)
layers = data.get('layers')
if not isinstance(layers, list):
    raise SystemExit('invalid layer config: layers must be a list')
for i, layer in enumerate(layers):
    if not isinstance(layer, list):
        raise SystemExit('invalid layer config: each layer must be a list')
    for module in layer:
        if not isinstance(module, str) or not module:
            raise SystemExit('invalid layer config: module names must be non-empty strings')
        print(f"{module}\t{i}")
PY
)

errors=0
total=0

while IFS= read -r -d '' file; do
  rel="${file#$LEAN_DIR/}"
  src_module="${rel%.lean}"
  src_module="${src_module//\//.}"

  while IFS= read -r line; do
    read -r first second _rest <<<"$line"
    if [[ "$first" != "import" || "$second" != "$PROJECT."* ]]; then
      continue
    fi
    dst_module="${second#"$PROJECT."}"

    src_layer="${LAYERS[$src_module]:-}"
    dst_layer="${LAYERS[$dst_module]:-}"

    # Skip if either module is not in the layer map (external or unconfigured).
    if [[ -z "$src_layer" || -z "$dst_layer" ]]; then
      continue
    fi

    total=$((total + 1))

    if (( dst_layer > src_layer )); then
      echo -e "${RED}VIOLATION${NC}: $src_module (L$src_layer) imports $dst_module (L$dst_layer)"
      errors=$((errors + 1))
    fi
  done < "$file"
done < <(find "$LEAN_DIR" -type f -name '*.lean' -print0)

echo ""
echo "DAG layer check: $total imports checked, $errors violations"

if (( errors > 0 )); then
  echo -e "${RED}FAIL${NC}: $errors layer violation(s) found"
  exit 1
else
  echo -e "${GREEN}PASS${NC}: all imports respect layer discipline"
  exit 0
fi

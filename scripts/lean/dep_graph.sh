#!/usr/bin/env bash
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
# dep_graph.sh — generate a Lean project module dependency graph in DOT format.
#
# Usage:
#   dep_graph.sh [--project NS] LEAN_DIR [LAYER_CONFIG]
#   dep_graph.sh [--project NS] LEAN_DIR [LAYER_CONFIG] | dot -Tpng -o deps.png
#
# LAYER_CONFIG, when supplied, is JSON of the form:
#   {"project": "MyProject", "layers": [["Mod1", "Mod2"], ["Mod3", "Mod4.Sub"]]}
#
# If no config is supplied, local imports are matched with --project (default:
# MyProject) and all nodes are emitted in a single cluster.

set -euo pipefail

PROJECT_OVERRIDE=""
if [[ $# -gt 0 && "$1" == "--project" ]]; then
  if [[ $# -lt 3 ]]; then
    echo "usage: $0 [--project NS] LEAN_DIR [LAYER_CONFIG]" >&2
    exit 2
  fi
  PROJECT_OVERRIDE="$2"
  shift 2
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 [--project NS] LEAN_DIR [LAYER_CONFIG]" >&2
  exit 2
fi

LEAN_DIR="$1"
LAYER_CONFIG="${2:-}"

if [[ ! -d "$LEAN_DIR" ]]; then
  echo "dep_graph: cannot find Lean directory: $LEAN_DIR" >&2
  exit 2
fi
if [[ -n "$LAYER_CONFIG" && ! -f "$LAYER_CONFIG" ]]; then
  echo "dep_graph: cannot find layer config: $LAYER_CONFIG" >&2
  exit 2
fi

LEAN_DIR="$(cd "$LEAN_DIR" && pwd)"

python3 - "$LEAN_DIR" "$LAYER_CONFIG" "$PROJECT_OVERRIDE" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

lean_dir = Path(sys.argv[1])
config_path = Path(sys.argv[2]) if sys.argv[2] else None
project_override = sys.argv[3] or None

config = None
if config_path is not None:
    with config_path.open(encoding='utf-8') as f:
        config = json.load(f)

project = project_override or (config or {}).get('project') or 'MyProject'
graph_name = re.sub(r'\W+', '_', ((config or {}).get('project') or project_override or 'Project'))
if not graph_name:
    graph_name = 'Project'

layer_for: dict[str, int] = {}
if config is not None:
    layers = config.get('layers')
    if not isinstance(layers, list):
        raise SystemExit('invalid layer config: layers must be a list')
    for idx, layer in enumerate(layers):
        if not isinstance(layer, list):
            raise SystemExit('invalid layer config: each layer must be a list')
        for module in layer:
            if not isinstance(module, str) or not module:
                raise SystemExit('invalid layer config: module names must be non-empty strings')
            layer_for[module] = idx
            layer_for[module.split('.', 1)[0]] = idx

import_re = re.compile(rf'^import\s+{re.escape(project)}\.(\S+)')
edges: set[tuple[str, str]] = set()
nodes: set[str] = set()

for path in sorted(lean_dir.rglob('*.lean')):
    rel = path.relative_to(lean_dir).with_suffix('').as_posix().replace('/', '.')
    src = rel.split('.', 1)[0]
    nodes.add(src)
    for line in path.read_text(encoding='utf-8').splitlines():
        match = import_re.match(line.strip())
        if not match:
            continue
        target = match.group(1)
        tgt = target.split('.', 1)[0]
        nodes.add(tgt)
        if src != tgt:
            edges.add((src, tgt))

palette = ['#e8f5e9', '#e3f2fd', '#fff3e0', '#fce4ec', '#f3e5f5', '#ede7f6', '#e0f7fa', '#f9fbe7']
print(f'digraph {graph_name} {{')
print('  rankdir=BT;')
print('  node [shape=box, style=filled, fontname="Helvetica", fontsize=10];')
print()

if config is None:
    print('  subgraph cluster_Project { label="Project modules"; style=dashed; color=gray;')
    for node in sorted(nodes):
        print(f'    "{node}" [fillcolor="#e8f5e9"];')
    print('  }')
else:
    by_layer: dict[int, list[str]] = {}
    other: list[str] = []
    for node in sorted(nodes):
        layer = layer_for.get(node)
        if layer is None:
            other.append(node)
        else:
            by_layer.setdefault(layer, []).append(node)
    for layer in sorted(by_layer):
        color = palette[layer % len(palette)]
        print(f'  subgraph cluster_L{layer} {{ label="Layer {layer}"; style=dashed; color=gray;')
        for node in by_layer[layer]:
            print(f'    "{node}" [fillcolor="{color}"];')
        print('  }')
    if other:
        print('  subgraph cluster_Other { label="Other modules"; style=dashed; color=gray;')
        for node in other:
            print(f'    "{node}" [fillcolor="#eeeeee"];')
        print('  }')

print()
for src, tgt in sorted(edges):
    print(f'  "{src}" -> "{tgt}";')
print('}')
PY

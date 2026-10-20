"""Cross-theorem have-clustering (S5 v1).

The corpus's shared lemmas (the refactor campaign's 16 extractions)
were human-found cross-proof patterns. This mines the same shape at
corpus scale: normalize every `have <name> : <type> :=` block's
TYPE (whitespace-collapsed, name-stripped), cluster by normalized
shape, and report clusters that recur across >= MIN_FILES distinct
files - candidate module lemmas.

Textual v1 (no trace needed): the cluster key is the type shape,
not the proof, so alpha-equivalent haves (different bound names,
same statement) already unify. Line noise is absorbed by the
whitespace collapse; structural noise (different argument orders)
is NOT unified (documented v1 limitation).
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# The type capture is bounded to the have's own indentation block:
# (?:(?!^\1[^\s]).)*? refuses to cross a line at the have's indent or
# less (a DOTALL `have` without `:=` would otherwise swallow the file).
HAVE_RE = re.compile(
    r"^([ \t]*)have\s+([A-Za-z_][\w']*)\s*:"
    r"((?:(?!^\1[^\s]).)*?)(?::=|:=)",
    re.MULTILINE | re.DOTALL,
)
MAX_TYPE_LEN = 200
MIN_FILES = 3


def _collapse(ws: str) -> str:
    # v1.1: a capture that ran into an adjacent have (the := boundary
    # fell on a later line) must not carry the "; have <name>" tail
    # into the cluster key.
    ws = ws.split("; have")[0]
    ws = ws.split("\n have")[0]
    return " ".join(ws.split())


def cluster_haves(
    sources: dict[str, str],
) -> dict[str, dict]:
    """sources: {relative_path: source_text}. Returns {key: cluster}."""
    clusters: dict[str, dict] = defaultdict(
        lambda: {"files": set(), "theorems": set(), "example": "", "count": 0}
    )
    for path, text in sources.items():
        for m in HAVE_RE.finditer(text):
            type_shape = _collapse(m.group(3)).strip()[:MAX_TYPE_LEN]
            if len(type_shape) < 12:  # trivial haves are idiomatic, not patterns
                continue
            key = type_shape
            c = clusters[key]
            c["files"].add(path)
            c["count"] += 1
            if not c["example"]:
                line = text[: m.start(3)].count("\n") + 1
                c["example"] = f"{path}:{line}"
    # report only cross-file clusters meeting the threshold
    out = {}
    for key, c in clusters.items():
        if len(c["files"]) >= MIN_FILES:
            out[key] = {
                "files": sorted(c["files"]),
                "n_files": len(c["files"]),
                "occurrences": c["count"],
                "example": c["example"],
            }
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["n_files"]))


def render_report(clusters: dict[str, dict]) -> str:
    lines = [
        "---",
        'garden_schema_version: "0.1"',
        'taxonomy_version: "0.1.0"',
        "doc_id: tacitdoc:altproof-have-clusters",
        'title: "Cross-theorem have-clustering (S5 v1)"',
        "document_role: research",
        "lifecycle_state: active",
        "disposition: adopt",
        "evidence_strength: direct",
        "confidence: high",
        'id: "REF-ALT-PROOF-HAVE-CLUSTERS"',
        'maturity: "seedling"',
        'verification: "unverified"',
        "sources:",
        '  - "docs/investigation-garden/altproof/COUNCIL_CHARTER.md"',
        "related:",
        '  - "MOC-ALT-PROOF-COUNCIL"',
        '  - "REF-ALT-PROOF-CLUSTER-REVIEW"',
        '  - "REF-ALT-PROOF-CORPUS-SCALE-SWEEP"',
        "indexed-by:",
        '  - "MOC-ALT-PROOF-COUNCIL"',
        "---",
        "",
        "# Cross-theorem have-clustering (S5 v1)",
        "",
        f"Clusters with >= {MIN_FILES} distinct files. Key = normalized have-type shape.",
        "",
        "| shape (first 90 chars) | files | occurrences | example |",
        "|---|---|---|---|",
    ]
    for key, c in clusters.items():
        k = key[:90].replace("|", "\\|")
        lines.append(f"| `{k}` | {c['n_files']} | {c['occurrences']} | {c['example']} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    root = Path(argv[1])
    sources = {
        str(p.relative_to(root)): p.read_text(encoding="utf-8")
        for p in sorted(root.rglob("*.lean"))
    }
    clusters = cluster_haves(sources)
    print(json.dumps({"files": len(sources), "clusters": len(clusters)}))
    if len(argv) > 2:
        Path(argv[2]).write_text(render_report(clusters), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

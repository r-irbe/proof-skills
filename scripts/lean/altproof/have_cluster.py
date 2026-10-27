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


# --------------------------------------------------------------------------
# Proposal 9A: Numina 6-Pattern Structural Logic Golfer (`golfer.md:31-200`)
# --------------------------------------------------------------------------

GOLF_PATTERNS: tuple[str, ...] = (
    "CIRCULAR_HAVE_DETOUR",
    "UNUSED_LOCAL_BINDING",
    "EQUALITY_INEQUALITY_DETOUR",
    "OVER_DECOMPOSED_OMEGA_CHAIN",
    "MULTILINE_PROJECTION_DESTRUCTURE",
    "SINGLE_USE_TRIVIAL_BINDING",
)


def detect_structural_golf_opportunities(proof_text: str) -> list[dict]:
    """Detect all 6 structural logic golfing patterns from `numina-lean-agent` (`golfer.md:31-200`):
      1. `CIRCULAR_HAVE_DETOUR`: proving `have h2 : T := ...` with the exact same normalized
         type `T` as an earlier `have h1 : T` (or concluding `exact h1` after re-deriving `h1`).
      2. `UNUSED_LOCAL_BINDING`: local `have h ... :=` or `let x :=` whose bound name is never
         referenced in subsequent proof lines.
      3. `EQUALITY_INEQUALITY_DETOUR`: `have h : a = b := ...` immediately feeding into a linear
         inequality step (`linarith`/`omega`) where `h` is used only once.
      4. `OVER_DECOMPOSED_OMEGA_CHAIN`: 2+ sequential `have` steps closed by `omega`/`linarith`/`grind`
         feeding into a final `omega`/`linarith`/`grind`.
      5. `MULTILINE_PROJECTION_DESTRUCTURE`: 2+ lines extracting `.1`/`.2`/`.fst`/`.snd`/`.left`/`.right`
         from the same hypothesis instead of `obtain ⟨a, b⟩ := h`.
      6. `SINGLE_USE_TRIVIAL_BINDING`: `have h := x.symm` / `have h := rfl` / `have h := by rfl`
         used at most once.
    """
    lines = (proof_text or "").splitlines()
    findings: list[dict] = []

    have_stmt_re = re.compile(
        r"^[ \t]*(have|let)\s+([A-Za-z_][A-Za-z0-9_']*)\s*(?:(?<!:):(?!\s*=)\s*(.+?))?\s*:=\s*(.*)$"
    )
    proj_re = re.compile(
        r"^[ \t]*(?:have|let)\s+([A-Za-z_][A-Za-z0-9_']*)\s*(?::[^:=]+)?\s*:=\s*([A-Za-z_][A-Za-z0-9_']*)\.(1|2|fst|snd|left|right)\b"
    )
    trivial_rhs_re = re.compile(
        r"^(?:by\s+)?(?:rfl|exact\s+rfl|[A-Za-z_][A-Za-z0-9_']*\.(?:symm|mp|mpr))\s*$"
    )
    omega_closer_re = re.compile(r"\b(?:omega|linarith|grind)\b")

    parsed_bindings: list[dict] = []
    proj_by_source: dict[str, list[tuple[int, str, str]]] = defaultdict(list)

    for idx, raw_ln in enumerate(lines, start=1):
        stripped = raw_ln.strip()
        if not stripped or stripped.startswith("--"):
            continue

        pm = proj_re.match(raw_ln)
        if pm:
            proj_by_source[pm.group(2)].append((idx, pm.group(1), pm.group(3)))

        hm = have_stmt_re.match(raw_ln)
        if hm:
            kw, bname, btype, brhs = (
                hm.group(1),
                hm.group(2),
                (hm.group(3) or "").strip(),
                hm.group(4).strip(),
            )
            parsed_bindings.append(
                {
                    "line": idx,
                    "kind": kw,
                    "name": bname,
                    "type": " ".join(btype.split()),
                    "rhs": brhs,
                }
            )

    # 1. CIRCULAR_HAVE_DETOUR: duplicate have type shapes or circular re-derivation
    seen_types: dict[str, tuple[int, str]] = {}
    for b in parsed_bindings:
        t_norm = b["type"]
        if t_norm and len(t_norm) >= 3:
            if t_norm in seen_types:
                prev_ln, prev_nm = seen_types[t_norm]
                findings.append(
                    {
                        "pattern": "CIRCULAR_HAVE_DETOUR",
                        "line": b["line"],
                        "name": b["name"],
                        "detail": (
                            f"`have {b['name']} : {t_norm}` duplicates earlier `have {prev_nm} : {t_norm}` "
                            f"(line {prev_ln}); reuse `{prev_nm}` directly"
                        ),
                    }
                )
            else:
                seen_types[t_norm] = (b["line"], b["name"])

    # 2. UNUSED_LOCAL_BINDING & 6. SINGLE_USE_TRIVIAL_BINDING & 3. EQUALITY_INEQUALITY_DETOUR
    for b in parsed_bindings:
        bname = b["name"]
        if bname.startswith("_"):
            continue
        after_text = "\n".join(lines[b["line"] :])
        word_rx = re.compile(rf"(?<![A-Za-z0-9_']){re.escape(bname)}(?![A-Za-z0-9_'])")
        uses = len(word_rx.findall(after_text))
        if uses == 0:
            findings.append(
                {
                    "pattern": "UNUSED_LOCAL_BINDING",
                    "line": b["line"],
                    "name": bname,
                    "detail": f"Local `{b['kind']} {bname}` is never referenced in subsequent proof steps",
                }
            )
            continue

        if uses <= 1 and trivial_rhs_re.match(b["rhs"]):
            findings.append(
                {
                    "pattern": "SINGLE_USE_TRIVIAL_BINDING",
                    "line": b["line"],
                    "name": bname,
                    "detail": (
                        f"Single-use trivial binding `{b['kind']} {bname} := {b['rhs']}`; "
                        f"inline `{b['rhs'].replace('by ', '')}` at the callsite"
                    ),
                }
            )

        if (
            uses == 1
            and "=" in b["type"]
            and not any(op in b["type"] for op in ("<=", ">=", "<", ">", "\u2264", "\u2265"))
            and omega_closer_re.search(after_text)
        ):
            findings.append(
                {
                    "pattern": "EQUALITY_INEQUALITY_DETOUR",
                    "line": b["line"],
                    "name": bname,
                    "detail": (
                        f"Single-use equality `have {bname} : {b['type']}` feeds into a linear solver; "
                        f"fold directly into `omega`/`linarith`"
                    ),
                }
            )

    # 4. OVER_DECOMPOSED_OMEGA_CHAIN: 2+ omega/linarith/grind haves feeding a final omega/linarith/grind
    omega_haves = [
        b for b in parsed_bindings if omega_closer_re.search(b["rhs"])
    ]
    non_empty_lines = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("--")]
    final_is_omega = bool(non_empty_lines and omega_closer_re.search(non_empty_lines[-1]))
    if len(omega_haves) >= 2 and final_is_omega:
        findings.append(
            {
                "pattern": "OVER_DECOMPOSED_OMEGA_CHAIN",
                "line": omega_haves[0]["line"],
                "name": omega_haves[0]["name"],
                "detail": (
                    f"{len(omega_haves)} intermediate `have` steps closed by `omega`/`linarith`/`grind` "
                    f"precede a final linear closer; collapse into a single `omega`/`linarith` call"
                ),
            }
        )

    # 5. MULTILINE_PROJECTION_DESTRUCTURE: 2+ projections from the same pair/conjunction hypothesis
    for src_hyp, projs in sorted(proj_by_source.items()):
        if len(projs) >= 2:
            first_ln = projs[0][0]
            bound_names = ", ".join(nm for _, nm, _ in projs)
            findings.append(
                {
                    "pattern": "MULTILINE_PROJECTION_DESTRUCTURE",
                    "line": first_ln,
                    "name": src_hyp,
                    "detail": (
                        f"Multiple projection bindings ({bound_names}) from `{src_hyp}`; "
                        f"replace with `obtain <{bound_names}> := {src_hyp}`"
                    ),
                }
            )

    return findings


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

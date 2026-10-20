"""Corpus report driver - renders the whole-corpus elegance suite.

v3: candidates pass detect_v3 (v2 noise gate + named-term demotion)
with per-file module symbols - the suite carries the v3 candidate set.

Walks every traced ast.json under the LeanDojo sandbox build dir,
groups tactics into proof blocks (position-gap attribution, v1),
runs the extraction detector, and renders one Markdown report per
source file plus an INDEX.md sorted by candidate count.

Per-file reports are capped at MAX_BLOCKS_PER_FILE blocks (ranked
by total estimated saving) so the suite stays reviewable; the cap
and the omitted-block count are recorded in each report's header.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path
if str(_Path(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extraction_detector import detect_v3, module_symbols
from report_renderer import BlockReport, render_file

DECL_START_RE = re.compile(
    r"^(?:@[^\n]*\n)*\s*(?:theorem|lemma|def|instance|abbrev)\s+([A-Za-z_][\w']*)",
    re.MULTILINE,
)

MAX_BLOCKS_PER_FILE = 50


def bytepos(p) -> int:
    return int(p["byteIdx"]) if isinstance(p, dict) else int(p)


def blocks_for_file(ast: dict, source: str) -> list[tuple[list, str]]:
    """Group tactic traces into (block, proof_text) pairs."""
    blocks, cur = [], []
    for tc in ast.get("tactics", []):
        pos, end = bytepos(tc["pos"]), bytepos(tc["endPos"])
        if cur and pos != cur[-1][1]:
            blocks.append(cur)
            cur = []
        cur.append((pos, end))
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        out.append((b, "\n".join(source[p:e] for p, e in b)))
    return out


def decl_spans(source: str) -> list[tuple[str, int, int]]:
    """Top-level declaration spans (name, start, end) from source text;
    end is the next declaration's start or EOF. v1 textual attribution
    (position only, not semantics)."""
    matches = list(DECL_START_RE.finditer(source))
    spans = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(source)
        spans.append((m.group(1), m.start(), end))
    return spans


def attribute_theorem(pos: int, spans: list) -> str:
    name = "(outside declarations)"
    for n, s0, s1 in spans:
        if s0 <= pos < s1:
            name = n
    return name


def report_one(ast_path: Path, sandbox: Path) -> tuple[str, int, int, str] | None:
    """Render one file's report. Returns (rel_source, n_blocks_with_cands,
    total_candidates, markdown) or None."""
    rel = ast_path.relative_to(sandbox / ".lake/build/ir")
    src = sandbox / (str(rel)[: -len(".ast.json")] + ".lean")
    if not src.exists():
        return None
    try:
        ast = json.loads(ast_path.read_text())
        source = src.read_text()
    except Exception:
        return None
    file_syms = module_symbols(source)
    spans = decl_spans(source)
    entries = []
    total = 0
    for b, proof_text in blocks_for_file(ast, source):
        cands = detect_v3(proof_text, file_symbols=file_syms)
        if not cands:
            continue
        total += len(cands)
        thm = attribute_theorem(b[0][0], spans)
        ls = source[: b[0][0]].count("\n") + 1
        le = source[: b[-1][1]].count("\n") + 1
        saving = sum(c.estimated_lines_saved for c in cands)
        entries.append(
            (
                saving,
                BlockReport(
                    ls,
                    le,
                    proof_text.strip(),
                    cands[:3],
                ),
            )
        )
        entries[-1][1].theorem = thm
    if not entries:
        return None
    entries.sort(key=lambda e: -e[0])
    omitted = max(0, len(entries) - MAX_BLOCKS_PER_FILE)
    kept = [e[1] for e in entries[:MAX_BLOCKS_PER_FILE]]
    md = render_file(str(rel)[: -len(".ast.json")] + ".lean", kept)
    # theorem-attributed section titles (S2): rewrite the per-block
    # "#### proof at lines A-B" headers to name the enclosing theorem.
    import re as _re

    by_line = {}
    for saving, br in entries:
        by_line[br.line_start] = getattr(br, "theorem", "?")

    def _sub(m):
        thm = by_line.get(int(m.group(1)), "?")
        return f"#### `{thm}` (lines {m.group(1)}-{m.group(2)})"

    md = _re.sub(r"#### proof at lines (\d+)-(\d+)", _sub, md)
    if omitted:
        md += (
            f"\n> {omitted} further block(s) with candidates omitted "
            f"(cap {MAX_BLOCKS_PER_FILE}/file, ranked by estimated saving).\n"
        )
    return str(rel)[: -len(".ast.json")] + ".lean", len(entries), total, md


def main() -> int:
    sandbox = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    n_files = n_blocks = n_cands = 0
    for ast_path in sorted((sandbox / ".lake/build/ir").rglob("*.ast.json")):
        r = report_one(ast_path, sandbox)
        if r is None:
            continue
        rel, nb, nc, md = r
        n_files += 1
        n_blocks += nb
        n_cands += nc
        target = out_dir / (rel + ".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(md)
        index.append((nc, nb, rel))
    index.sort(reverse=True)
    lines = [
        "# Elegance report suite - index",
        "",
        (f"{n_files} files with candidates; {n_blocks} proof blocks; {n_cands} candidates."),
        "",
        "| candidates | blocks | file |",
        "|---|---|---|",
    ]
    for nc, nb, rel in index:
        lines.append(f"| {nc} | {nb} | [{rel}](../../../easci/lean/{rel}) |")
    (out_dir / "INDEX.md").write_text("\n".join(lines) + "\n")
    print(f"SUITE: {n_files} files, {n_blocks} blocks, {n_cands} candidates -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

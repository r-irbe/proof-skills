#!/usr/bin/env python3
"""Offline `.ilean` + `.ast.json` symbol and declaration-span index (Proposal 9A, S2 & S3).

Supports two offline trace backends without requiring `lake serve` or LeanDojo XML:
  1. Native Lean 4 `.ilean` index (`ILeanIndex`): reads `.lake/build/lib/**/*.ilean`
     JSON files (561 modules indexed in <0.4s), extracting:
       - `decls`: `{decl_name: [s_line, s_col, e_line, e_col, d_line, d_col, de_line, de_col]}`
         for S2 exact theorem-span attribution.
       - `references`: `{symbol_name: {"definition": [...], "usages": [[l0, c0, l1, c1], ...]}}`
         for S3 cross-module symbol demotion.
  2. Legacy `.ast.json` trace index (`TraceIndex`): reads `<Module>.ast.json` with
     `{"module": "...", "symbols": [...]}` for backward compatibility with existing tests.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TheoremSpan:
    """Exact 1-based declaration span for S2 theorem attribution."""

    name: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    source: str = "ilean"  # "ilean" | "source-regex"


class TraceIndex:
    """Unified `.ilean` + `.ast.json` symbol and theorem-span index."""

    def __init__(self, trace_root: Path | str | None = None) -> None:
        self._by_rel: dict[str, set[str]] = {}
        self._spans_by_rel: dict[str, list[TheoremSpan]] = {}
        self._all_defined_symbols: set[str] = set()
        if trace_root is None:
            return
        root = Path(trace_root)
        if not root.exists():
            return

        lake_lib = root / ".lake" / "build" / "lib"
        if lake_lib.exists():
            # Fast path: scan only `.lake/build/lib/**/*.ilean` without walking `.lake/packages/`
            for p in lake_lib.rglob("*.ilean"):
                self._load_ilean_file(p, lake_lib)
            return

        # Fallback: scan `.ast.json` and `.ilean` files outside `.lake/packages/`
        for p in root.rglob("*.ast.json"):
            if "packages" in p.parts and ".lake" in p.parts:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            rel = str(p.relative_to(root))[: -len(".ast.json")] + ".lean"
            syms = set(data.get("symbols", []))
            self._by_rel.setdefault(rel, set()).update(syms)
            self._all_defined_symbols.update(syms)

        for p in root.rglob("*.ilean"):
            if "packages" in p.parts and ".lake" in p.parts:
                continue
            self._load_ilean_file(p, root)

    def _load_ilean_file(self, ilean_path: Path, base_dir: Path) -> None:
        try:
            data = json.loads(ilean_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return

        mod_name = str(data.get("module", ""))
        if mod_name:
            rel = mod_name.replace(".", "/") + ".lean"
        else:
            rel_p = str(ilean_path.relative_to(base_dir))
            if rel_p.startswith("lean/"):
                rel_p = rel_p[len("lean/") :]
            rel = rel_p[: -len(".ilean")] + ".lean"

        syms: set[str] = self._by_rel.setdefault(rel, set())
        spans: list[TheoremSpan] = self._spans_by_rel.setdefault(rel, [])

        decls = data.get("decls") or {}
        if isinstance(decls, dict):
            for dname, coords in decls.items():
                short = dname.split(".")[-1]
                syms.add(dname)
                syms.add(short)
                self._all_defined_symbols.add(dname)
                self._all_defined_symbols.add(short)
                if isinstance(coords, list) and len(coords) >= 4:
                    spans.append(
                        TheoremSpan(
                            name=short,
                            start_line=int(coords[0]),
                            start_col=int(coords[1]),
                            end_line=int(coords[2]),
                            end_col=int(coords[3]),
                            source="ilean",
                        )
                    )

        refs = data.get("references") or {}
        if isinstance(refs, dict):
            for rname, rinfo in refs.items():
                if rname.startswith("_private."):
                    parts = rname.split(".")
                    short = parts[-1]
                else:
                    short = rname.split(".")[-1]
                syms.add(rname)
                syms.add(short)
                if isinstance(rinfo, dict) and rinfo.get("definition"):
                    self._all_defined_symbols.add(rname)
                    self._all_defined_symbols.add(short)

        spans.sort(key=lambda s: (s.start_line, s.start_col))

    def symbols_for(self, source_rel: str) -> set[str]:
        """Return known symbols for `source_rel` (matching either exact relative path or suffix)."""
        if source_rel in self._by_rel:
            return set(self._by_rel[source_rel])
        norm = source_rel.lstrip("./")
        for k, v in self._by_rel.items():
            if k.endswith(norm) or norm.endswith(k):
                return set(v)
        return set()

    def theorem_spans_for(self, source_rel: str) -> list[TheoremSpan]:
        """Return sorted `TheoremSpan` list for `source_rel` from `.ilean` metadata."""
        if source_rel in self._spans_by_rel:
            return list(self._spans_by_rel[source_rel])
        norm = source_rel.lstrip("./")
        for k, v in self._spans_by_rel.items():
            if k.endswith(norm) or norm.endswith(k):
                return list(v)
        return []

    @property
    def all_defined_symbols(self) -> set[str]:
        return set(self._all_defined_symbols)


def attribute_theorem_spans(
    source_text: str,
    index: TraceIndex | None = None,
    source_rel: str = "",
) -> list[TheoremSpan]:
    """S2 theorem-span attribution: returns exact declaration spans `[start_line..end_line]`
    from `.ilean` when available, falling back to lexer-safe regex declaration scanning."""
    if index is not None and source_rel:
        ilean_spans = index.theorem_spans_for(source_rel)
        if ilean_spans:
            return ilean_spans

    lines = source_text.splitlines()
    decl_re = re.compile(
        r"^[ \t]*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|def|abbrev|example)\s+([A-Za-z_][A-Za-z0-9_']*)?"
    )
    top_re = re.compile(
        r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|def|abbrev|example|structure|inductive|class|instance|namespace|end|section)\b"
    )
    spans: list[TheoremSpan] = []
    n = len(lines)
    i = 0
    while i < n:
        m = decl_re.match(lines[i])
        if not m:
            i += 1
            continue
        name = (m.group(1) or "(example)").strip()
        start_ln = i + 1
        j = i + 1
        end_ln = start_ln
        while j < n:
            ln = lines[j]
            if ln and ln[0] not in (" ", "\t") and top_re.match(ln):
                break
            if ln.strip() and not ln.strip().startswith("--"):
                end_ln = j + 1
            j += 1
        spans.append(
            TheoremSpan(
                name=name,
                start_line=start_ln,
                start_col=0,
                end_line=end_ln,
                end_col=len(lines[end_ln - 1]) if end_ln <= n else 0,
                source="source-regex",
            )
        )
        i = j
    return spans


def find_enclosing_theorem(
    line_1based: int,
    spans: list[TheoremSpan],
) -> str | None:
    """Return the theorem name whose span `[start_line, end_line]` encloses `line_1based`."""
    for sp in spans:
        if sp.start_line <= line_1based <= sp.end_line:
            return sp.name
    return None

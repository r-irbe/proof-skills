#!/usr/bin/env python3
"""U0 mechanical audit: docstring/naming census over the Lean corpus.

Walks docs/easci/lean/EASCI (source + tests) and packages/ (standalone
extractions), counting per module: declarations by kind, /-- docstrings,
/-! module docstrings, naming-conformance flags (theorem/lemma/def names
that begin uppercase, which mathlib reserves for structures/classes),
`example` uses (anonymous worked examples, concentrated in tests), and
sorry occurrences (must stay zero).

Output: markdown with a per-file table + summary, on stdout.
  python3 census_docstrings.py > docstring-census-<date>.md
"""

import os
import re
import sys

ROOT = (
    sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
)  # -> docs/easci/lean
assert os.path.isdir(os.path.join(ROOT, "EASCI")), f"EASCI not under {ROOT}"

DECL = re.compile(
    r"^(theorem|lemma|def|instance|abbrev|structure|class)\s+([A-Za-z_][A-Za-z0-9_']*)"
)
KIND_UPPER = {"theorem", "lemma", "def", "instance", "abbrev"}  # these must be lowercase-first


def scan(path):
    decls = docstrings = moduledoc = examples = sorry = 0
    by_kind = {}
    upper_flags = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            in_block = None  # '/--' or '/-!' while inside a doc block
            for ln, line in enumerate(fh, 1):
                if in_block:
                    if "-/" in line:
                        in_block = None
                    continue
                if line.startswith("/--"):
                    docstrings += 1
                    if "-/" not in line[3:]:
                        in_block = "/--"
                    continue
                if line.startswith("/-!"):
                    moduledoc += 1
                    if "-/" not in line[3:]:
                        in_block = "/-!"
                    continue
                m = DECL.match(line)
                if m:
                    kind, name = m.group(1), m.group(2)
                    decls += 1
                    by_kind[kind] = by_kind.get(kind, 0) + 1
                    if kind in KIND_UPPER and name[0].isupper():
                        upper_flags.append(f"L{ln}: {kind} {name}")
                if re.match(r"^example\b", line) or (
                    re.search(r"\bexample\b\s*:?", line) and "example" in line.split("--")[0]
                ):
                    pass  # counted below, cheap and exact enough
                if re.match(r"^example\b", line):
                    examples += 1
                if re.match(r"^\s*sorry\s*$", line):
                    sorry += 1
    except OSError as exc:
        print(f"unreadable: {path}: {exc}", file=sys.stderr)
    return dict(
        decls=decls,
        docstrings=docstrings,
        moduledoc=moduledoc,
        examples=examples,
        sorry=sorry,
        upper=upper_flags,
        by_kind=by_kind,
    )


def collect(base, tag):
    rows = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in sorted(filenames):
            if not fn.endswith(".lean"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base)
            is_test = (
                "/Test" in "/" + rel.replace(os.sep, "/")
                or "/Tests" in "/" + rel.replace(os.sep, "/")
                or rel.startswith("Tests")
                or ("/test" in ("/" + rel).lower() and "Test" in rel)
            )
            r = scan(full)
            r["path"] = rel
            r["tag"] = tag + (":tests" if is_test else "")
            if r["decls"] or r["examples"] or r["moduledoc"]:
                rows.append(r)
    return rows


rows_easci = collect(os.path.join(ROOT, "EASCI"), "EASCI")
rows_pkg = []
pkg_root = os.path.join(ROOT, "..", "..", "..", "packages")  # -> repo packages/
if os.path.isdir(pkg_root):
    for pkg in sorted(os.listdir(pkg_root)):
        pdir = os.path.join(pkg_root, pkg)
        if (
            os.path.isdir(os.path.join(pdir, "ReinforcementLearning"))
            or os.path.isdir(os.path.join(pdir, "StochasticCCV"))
            or os.path.isdir(os.path.join(pdir, "AgenticSafety"))
            or os.path.isdir(os.path.join(pdir, "ProvenanceChain"))
            or os.path.isdir(os.path.join(pdir, "CuspCatastrophe"))
            or os.path.isdir(os.path.join(pdir, "PhasePortrait"))
            or os.path.isdir(os.path.join(pdir, "Tacit"))
        ):
            for r in collect(os.path.join(pdir), f"packages/{pkg}"):
                rows_pkg.append(r)

out = []
out.append("# U0 docstring/naming census (generated)")
out.append("")
out.append(
    "Generator: `docs/easci/lean/scripts/census_docstrings.py`. "
    "Counts are line-based (a `/--` opener per docstring; decls by "
    "leading keyword). Naming flags: theorem/lemma/def/instance "
    "names beginning uppercase (mathlib reserves uppercase-first "
    "for structures/classes). `example` = anonymous worked examples."
)
out.append("")
tot = dict(decls=0, docstrings=0, moduledoc=0, examples=0, sorry=0)
out.append("## EASCI tree")
out.append("")
out.append("| module | decls | /-- | /-! | examples | naming flags |")
out.append("| --- | ---: | ---: | ---: | ---: | ---: |")
for r in sorted(rows_easci, key=lambda r: r["path"]):
    tot["decls"] += r["decls"]
    tot["docstrings"] += r["docstrings"]
    tot["moduledoc"] += 1 if r["moduledoc"] else 0
    tot["examples"] += r["examples"]
    tot["sorry"] += r["sorry"]
    flag = f"{len(r['upper'])}" if r["upper"] else ""
    out.append(
        f"| `{r['path']}` ({r['tag']}) | {r['decls']} | {r['docstrings']} | "
        f"{1 if r['moduledoc'] else 0} | {r['examples']} | {flag} |"
    )
out.append("")
ptot = dict(decls=0, docstrings=0, moduledoc=0, examples=0, sorry=0)
out.append("## packages/ extractions")
out.append("")
out.append("| package | files | decls | /-- | /-! | examples | naming flags |")
out.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
bypkg = {}
for r in rows_pkg:
    pkg = r["tag"].split("/")[1]
    d = bypkg.setdefault(
        pkg, dict(files=0, decls=0, docstrings=0, moduledoc=0, examples=0, upper=0, sorry=0)
    )
    d["files"] += 1
    d["decls"] += r["decls"]
    d["docstrings"] += r["docstrings"]
    d["moduledoc"] += 1 if r["moduledoc"] else 0
    d["examples"] += r["examples"]
    d["upper"] += len(r["upper"])
    d["sorry"] += r["sorry"]
    ptot["decls"] += r["decls"]
    ptot["docstrings"] += r["docstrings"]
    ptot["moduledoc"] += 1 if r["moduledoc"] else 0
    ptot["examples"] += r["examples"]
    ptot["sorry"] += r["sorry"]
for pkg, d in sorted(bypkg.items()):
    out.append(
        f"| {pkg} | {d['files']} | {d['decls']} | {d['docstrings']} | "
        f"{d['moduledoc']} | {d['examples']} | {d['upper']} |"
    )
out.append("")
out.append("## Summary")
out.append("")
out.append(
    f"- EASCI tree: {len(rows_easci)} files, {tot['decls']} declarations, "
    f"{tot['docstrings']} `/--` docstrings, {tot['moduledoc']} modules with "
    f"`/-!` module docs, {tot['examples']} anonymous examples, "
    f"{tot['sorry']} sorry lines."
)
out.append(
    f"- packages/: {len(rows_pkg)} files, {ptot['decls']} declarations, "
    f"{ptot['docstrings']} `/--` docstrings, {ptot['moduledoc']} modules with "
    f"`/-!`, {ptot['examples']} examples, {ptot['sorry']} sorry lines."
)
nc = sum(len(r["upper"]) for r in rows_easci + rows_pkg)
out.append(f"- Naming flags (uppercase-first non-structure names): {nc}.")
out.append("- `sorry` must stay 0; any nonzero line above is a finding.")
out.append("")
sys.stdout.write("\n".join(out))

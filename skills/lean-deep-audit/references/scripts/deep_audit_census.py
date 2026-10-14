#!/usr/bin/env python3
#  Generic copy shipped with the lean-deep-audit skill (proof-skills).
#  Upstream-use: python3 deep_audit_census.py --corpus <path/to/lib/sources> [--out report.md]
#  The PROJECT-side instance of this script lives in the consuming repo's scripts/.
"""Deep-audit censuses P4 (inhabitation) and P5 (type continuity).

P4: for every structure/class/inductive, does an inhabitation witness
exist (an Inhabited/Nonempty instance, a deriving clause, or an explicit
term witness)?  Unexplained types = vacuous-implication candidates.

P5: foundational-type duplication - the same type basename declared in
more than one module (different namespaces can legally host identical
basenames; each collision is a shared-vs-duplicated question), plus the
shared-foundation ranking (types whose basenames are referenced by the
most modules).

Deterministic; corpus-order sorted output. Reports go to stdout or
--out (markdown).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

DECL_RE = re.compile(
    r"^(abstract\s+)?(private\s+|protected\s+)?(structure|class|inductive)\s+([A-Za-z_][A-Za-z0-9_']*)"
)
ABBREV_RE = re.compile(r"^abbrev\s+([A-Za-z_][A-Za-z0-9_']*)")
INSTANCE_RE = re.compile(
    r"^instance\s+[A-Za-z_^{s]*[A-Za-z0-9_']*\s*[^:]*:\s*(Inhabited|Nonempty|LawfulInhabited)\s+([A-Za-z_][A-Za-z0-9_.']*)"
)
DERIVING_RE = re.compile(r"\bderiving\b[^\n]*\b(Inhabited|Nonempty)\b")
TERM_WITNESS_RE = re.compile(
    r"^(noncomputable\s+)?(def|example)\s+[A-Za-z_][A-Za-z0-9_']*\s*:[^:=]*\b([A-Z][A-Za-z0-9_']*)\b[^=]*:="
)
NAMESPACE_RE = re.compile(r"^namespace\s+(\S+)")
END_RE = re.compile(r"^end\b")


def parse_corpus(corpus: Path) -> dict:
    types: dict[str, list] = defaultdict(list)  # basename -> [{module, ns, file, kind}]
    insts: dict[str, set] = defaultdict(set)  # type basename -> {class}
    deriving_hits: dict[str, set] = defaultdict(set)
    term_wits: dict[str, set] = defaultdict(set)
    refs: dict[str, set] = defaultdict(set)  # basename referenced in module -> modules

    files = sorted(corpus.rglob("*.lean"))
    file_lines = {f: f.read_text(encoding="utf-8").splitlines() for f in files}

    # Pass 1: declarations, instances, derivings, term witnesses.
    for f in files:
        module = f.relative_to(corpus.parent).with_suffix("").as_posix().replace("/", ".")
        ns_stack: list[str] = []
        pending_derive = 0
        for raw in file_lines[f]:
            line = raw.strip()
            if nm := NAMESPACE_RE.match(raw):
                ns_stack.append(nm.group(1))
                pending_derive = 0
                continue
            if END_RE.match(raw):
                if ns_stack:
                    ns_stack.pop()
                pending_derive = 0
                continue

            m = DECL_RE.match(raw)
            if m:
                kind, base = m.group(3), m.group(4)
                ns = ".".join(ns_stack)
                types[base].append({"module": module, "ns": ns, "file": str(f), "kind": kind})
                pending_derive = 4  # look a few lines ahead for deriving
                continue

            if am := ABBREV_RE.match(raw):
                base = am.group(1)
                types.setdefault(base, []).append(
                    {"module": module, "ns": ".".join(ns_stack), "file": str(f), "kind": "abbrev"}
                )
                pending_derive = 4
                continue

            im = INSTANCE_RE.match(raw)
            if im:
                insts[im.group(2).split(".")[-1]].add(im.group(1))
                pending_derive = 0
                continue

            if pending_derive > 0:
                dm = DERIVING_RE.search(raw)
                # attaches to the most recently declared type
                if dm and types:
                    last_base = next(reversed(types))  # insertion-ordered dict
                    deriving_hits[last_base].add(dm.group(1))
                pending_derive -= 1
                continue

            tm = TERM_WITNESS_RE.match(raw)
            if tm:
                term_wits[tm.group(3)].add(module)
                continue

    # Pass 2: reference counting via one precompiled alternation.
    if types:
        alt = re.compile(r"\b(" + "|".join(sorted(re.escape(b) for b in types)) + r")\b")
        for f in files:
            module = f.relative_to(corpus.parent).with_suffix("").as_posix().replace("/", ".")
            for raw in file_lines[f]:
                for mm in alt.finditer(raw):
                    refs[mm.group(1)].add(module)

    return {
        "types": types,
        "instances": insts,
        "derivings": deriving_hits,
        "term_witnesses": term_wits,
        "refs": refs,
    }


def report(data: dict, corpus_name: str) -> str:
    types = data["types"]
    insts = data["instances"]
    derivs = data["derivings"]
    wits = data["term_witnesses"]
    out: list[str] = []
    out.append("# Deep-audit censuses P4 + P5")
    out.append("")
    out.append(f"Corpus: `{corpus_name}`. Generated by `scripts/deep_audit_census.py`.")
    out.append("")

    # ---- P4 ----
    out.append("## P4 - Inhabitation coverage")
    out.append("")
    total = len(types)
    witnessed = t = 0
    unexplained: list[tuple[str, list]] = []
    for base in sorted(types):
        has_inst = base in insts or base in derivs
        has_term = base in wits
        if has_inst:
            witnessed += 1
        elif has_term:
            t += 1
        else:
            unexplained.append((base, types[base]))
    out.append(
        f"| class | count |\n| --- | --- |\n"
        f"| type declarations (structure/class/inductive/abbrev) | {total} |\n"
        f"| Inhabited/Nonempty instance or deriving | {witnessed} |\n"
        f"| term-witness only (a def returns the type) | {t} |\n"
        f"| unexplained (no witness found) | {len(unexplained)} |"
    )
    out.append("")
    out.append("### Unexplained types (the review list)")
    out.append("")
    out.append("| type | kind | module(s) |")
    out.append("| --- | --- | --- |")
    for base, decls in unexplained:
        mods = ", ".join(sorted({d["module"] for d in decls}))
        kinds = "/".join(sorted({d["kind"] for d in decls}))
        out.append(f"| `{base}` | {kinds} | {mods} |")
    out.append("")

    # ---- P5 ----
    out.append("## P5 - Type continuity (duplication candidates)")
    out.append("")
    out.append(
        f"- distinct type basenames: {total}; declared in more than one module: "
        f"{sum(1 for d in types.values() if len({x['module'] for x in d}) > 1)}"
    )
    out.append("")
    out.append("| basename | declarations (module.kind) |")
    out.append("| --- | --- |")
    for base in sorted(types):
        decls = types[base]
        mods = {x["module"] for x in decls}
        if len(mods) > 1:
            forms = "; ".join(
                sorted({f"{x['module']}.{x['kind']}[{x['ns'] or 'root'}]" for x in decls})
            )
            out.append(f"| `{base}` | {forms} |")
    out.append("")
    out.append("### Shared-foundation ranking (basenames referenced by the most modules)")
    out.append("")
    top = sorted(data["refs"].items(), key=lambda kv: (-len(kv[1]), kv[0]))[:25]
    out.append("| basename | modules referencing |")
    out.append("| --- | --- |")
    for base, mods in top:
        out.append(f"| `{base}` | {len(mods)} |")
    out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, required=True, help="path to the PROJECT/ directory")
    ap.add_argument("--out", type=Path, default=None, help="write the markdown report here")
    args = ap.parse_args()

    data = parse_corpus(args.corpus)
    text = report(data, args.corpus.name)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)

    types = data["types"]
    unex = sum(
        1
        for b, d in types.items()
        if b not in data["instances"]
        and b not in data["derivings"]
        and b not in data["term_witnesses"]
    )
    print(
        f"P4: {len(types)} types, {unex} unexplained; "
        f"P5: {sum(1 for d in types.values() if len({x['module'] for x in d}) > 1)} multi-module basenames",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

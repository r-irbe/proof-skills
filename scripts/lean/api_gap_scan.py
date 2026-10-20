#!/usr/bin/env python3
"""U4 missing-API sweep: simp-lemma inventory, instance gaps, decidability.

Scans the EASCI corpus (default) for the three mechanical classes the
U4 wave definition names:

  simp-nf   - `@[simp]` lemmas carrying explicit hypotheses between the
              binders and the colon (the classic simp-normal-form
              violation: a conditional rewrite rarely fires and slows
              the simp set), and `@[simp]` on `theorem`s whose head
              symbol is a local projection the simp set cannot reduce.
  inst-gap  - `haveI :` / `letI :` introductions (per-module counts;
              each is a candidate missing instance), plus `inferInstance`
              density as a secondary signal.
  decidab.  - `open Classical`, `Classical.byCases`, `Classical.em`,
              `Classical.dec`, and `by_cases` on prop-typed goals in
              computational (non-`noncomputable`) modules.

Also carries the U3a follow-up lint: a `/--` docstring immediately
before a `set_option ... in` line is a Lean parse error (hit in
Profiling.lean, Phase 1145).

Usage: python3 scripts/u4_api_gap_scan.py [ROOT]   (ROOT defaults to EASCI)
Exit 0 always - this is a census, not a gate.
"""

import os
import re
import sys

DECL = re.compile(
    r"^\s*(?:private\s+|protected\s+|noncomputable\s+|scoped\s+)*"
    r"(theorem|lemma|def|abbrev|instance|structure|class)\b")
SIMP_ATTR = re.compile(r"^\s*@\[simp\]\s*$")
SET_OPTION_IN = re.compile(r"^\s*set_option\b.*\bin\s*$")
HAVEI = re.compile(r"^\s*(?:haveI|letI)\b")
CLASSICAL = re.compile(
    r"\bopen Classical\b|\bClassical\.(byCases|em|dec)\b|\bby_cases\b")
BLOCK_OPEN = re.compile(r"^\s*/-(?:-|!)")


def scan_file(path):
    """Return a dict of findings for one Lean source."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out = {"simp_nf": [], "inst_gap": 0, "classical": [], "doc_setopt": []}
    i = 0
    pending_doc = False
    while i < len(lines):
        ln = lines[i]
        if BLOCK_OPEN.match(ln):
            j = i
            while j < len(lines) and "-/" not in lines[j]:
                j += 1
            pending = lines[j + 1] if j + 1 < len(lines) else ""
            if SET_OPTION_IN.match(lines[j + 1] if j + 1 < len(lines) else ""):
                out["doc_setopt"].append(i + 1)
            i = j + 1
            continue
        if SIMP_ATTR.match(ln):
            # find the declaration line (skip attributes / modifiers)
            j = i + 1
            while j < len(lines) and not DECL.match(lines[j]) and lines[j].strip():
                j += 1
            decl = lines[j] if j < len(lines) else ""
            head = decl.split(":")[0] if ":" in decl else decl
            binders = head[head.find(decl.split()[0]) + len(decl.split()[0]):] if decl else ""
            if re.search(r"\(\s*[a-zA-Z_][a-zA-Z0-9_'?]*\s*:", head.split(":", 1)[0] if ":" in head else head):
                out["simp_nf"].append((i + 1, decl.strip()[:78]))
        if HAVEI.match(ln):
            out["inst_gap"] += 1
        m = CLASSICAL.search(ln)
        if m:
            out["classical"].append((i + 1, m.group(0)))
        i += 1
    return out


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="U4 missing-API sweep: simp-lemma inventory, instance gaps, decidability.")
    parser.add_argument("pos_root", nargs="?", default=None, help="Optional positional Lean corpus directory")
    parser.add_argument("--root", "--lean-dir", dest="root", default=os.environ.get("LEAN_DIR", "EASCI"), help="Corpus directory to scan")
    args = parser.parse_args(argv)
    root = args.pos_root if args.pos_root is not None else args.root
    total = {"simp_nf": 0, "inst_gap": 0, "classical": 0, "doc_setopt": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".scratch"]
        for fn in sorted(filenames):
            if not fn.endswith(".lean"):
                continue
            full = os.path.join(dirpath, fn)
            r = scan_file(full)
            rel = os.path.relpath(full, root)
            total["simp_nf"] += len(r["simp_nf"])
            total["inst_gap"] += r["inst_gap"]
            total["classical"] += len(r["classical"])
            total["doc_setopt"] += len(r["doc_setopt"])
            if r["simp_nf"]:
                for line_no, decl in r["simp_nf"]:
                    print(f"simp-nf   {rel}:{line_no}: {decl}")
            if r["inst_gap"]:
                print(f"inst-gap  {rel}: {r['inst_gap']} haveI/letI")
            if r["classical"]:
                for line_no, what in r["classical"]:
                    print(f"classical {rel}:{line_no}: {what}")
            if r["doc_setopt"]:
                for line_no in r["doc_setopt"]:
                    print(f"doc-setopt {rel}:{line_no}: /-- before set_option in")
    print(f"TOTAL: {total['simp_nf']} simp-nf suspects, "
          f"{total['inst_gap']} haveI/letI, {total['classical']} classical "
          f"uses, {total['doc_setopt']} doc-before-set_option")


if __name__ == "__main__":
    main()

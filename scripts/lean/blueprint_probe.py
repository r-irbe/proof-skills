#!/usr/bin/env python3
r"""Blueprint probe - the \leanok fifth-gate machinery (BLOCK mode).

Checks, for every \lean{foo} in blueprint/src/content.tex:
  1. RESOLVES: the fully-qualified declaration name exists in the corpus
     source (<lean-dir>/**/*.lean);
  2. ANNOTATED: the containing LaTeX node carries \leanok;
  3. COVERAGE: annotated-node count vs corpus declaration total (the
     ratchet baseline).

Usage:
  python3 blueprint_probe.py [--root PATH] [--lean-dir DIR] [--blueprint-src DIR] [--checkdecls] [--checkdecls-errors]
"""

import argparse
import glob
import re
import sys
from pathlib import Path

_word_re = re.compile(r"\w")


def _appears_as_word(name: str, haystack: str) -> bool:
    r"""True iff `name` occurs in `haystack` not adjacent to word chars."""
    if not name:
        return bool(re.search(r"(?<!\w)(?!\w)", haystack))
    start = 0
    while True:
        i = haystack.find(name, start)
        if i < 0:
            return False
        j = i + len(name)
        before_ok = i == 0 or not _word_re.match(haystack[i - 1])
        after_ok = j == len(haystack) or not _word_re.match(haystack[j])
        if before_ok and after_ok:
            return True
        start = i + 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."), help="Lean project root")
    ap.add_argument("--lean-dir", type=str, default="EASCI", help="Lean corpus subdirectory under --root")
    ap.add_argument("--blueprint-src", type=Path, default=None, help="Blueprint src dir (default: <root>/blueprint/src)")
    ap.add_argument("--checkdecls", action="store_true", help="Advisory reverse check for unreferenced declarations")
    ap.add_argument("--checkdecls-errors", action="store_true", help="Exit 1 if reverse check finds unreferenced declarations")
    args = ap.parse_args(argv)

    root = args.root.resolve()
    bp_src = (args.blueprint_src or (root / "blueprint" / "src")).resolve()
    src_tex = bp_src / "content.tex"
    sections = sorted((bp_src / "sections").glob("*.tex"))
    checkdecls_errors = args.checkdecls_errors
    checkdecls = checkdecls_errors or args.checkdecls

    tex = (
        src_tex.read_text(encoding="utf-8")
        + "\n"
        + "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sections)
    )
    blocks = re.findall(
        r"\\begin\{(theorem|lemma|definition|proposition|corollary)\}(.*?)\\end\{\1\}", tex, re.S
    )
    lean_glob = str(root / args.lean_dir / "**" / "*.lean")
    sources = "\n".join(
        Path(f).read_text(encoding="utf-8", errors="replace")
        for f in glob.glob(lean_glob, recursive=True)
    )
    decls_total = len(
        re.findall(
            r"^(?:noncomputable )?(?:theorem|lemma|def|abbrev|instance|structure)\b", sources, re.M
        )
    )

    resolved = missing = ok = no_ok = 0
    found_cache: dict[str, bool] = {}
    for _env, body in blocks:
        lab = re.search(r"\\label\{([^}]+)\}", body)
        lean = re.search(r"\\lean\{([^}]+)\}", body)
        has_ok = "\\leanok" in body
        name = lab.group(1) if lab else "?"
        if not lean:
            print(f"WARN node {name}: no \\lean target")
            continue
        target = lean.group(1).strip()
        last = target.split(".")[-1]
        if last not in found_cache:
            found_cache[last] = _appears_as_word(last, sources)
        if found_cache[last]:
            resolved += 1
        else:
            missing += 1
            print(f"WARN node {name}: \\lean{{{target}}} NOT FOUND in corpus source")
        if has_ok:
            ok += 1
        else:
            no_ok += 1
            print(f"WARN node {name}: missing \\leanok")

    nodes = len(blocks)
    cov = (ok / nodes * 100) if nodes else 0.0
    pct_corpus = (ok / decls_total * 100) if decls_total else 0.0
    print(
        f"nodes: {nodes} | resolved: {resolved}/{nodes} | leanok: {ok}/{nodes}"
        f" ({cov:.0f}% of blueprint) | corpus coverage: {ok}/{decls_total}"
        f" ({pct_corpus:.2f}%) | ratchet: BLOCK (coverage {pct_corpus:.2f}% >= 50%)"
    )

    unreferenced_count = 0
    if checkdecls:
        referenced = set()
        for _env, body in blocks:
            lean = re.search(r"\\lean\{([^}]+)\}", body)
            if lean:
                for part in lean.group(1).split(","):
                    part = part.strip()
                    if part:
                        referenced.add(part.split(".")[-1])
        decl_head_re = re.compile(
            r"^(?:noncomputable )?(theorem|lemma|def|abbrev|instance|structure)\b"
        )
        decl_name_re = re.compile(r"[A-Za-z_][\w'!]*")
        by_module = {}
        named_total = 0
        anonymous = 0
        for path in sorted(glob.glob(lean_glob, recursive=True)):
            module = str(Path(path).relative_to(root / args.lean_dir))
            hits = []
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    head = decl_head_re.match(line)
                    if not head:
                        continue
                    i = head.end()
                    n = len(line)
                    while i < n:
                        c = line[i]
                        if c.isspace():
                            i += 1
                        elif c in "([{":
                            depth = 1
                            i += 1
                            while i < n and depth:
                                d = line[i]
                                if d in "([{":
                                    depth += 1
                                elif d in ")]}":
                                    depth -= 1
                                i += 1
                        else:
                            break
                    name_m = decl_name_re.match(line, i)
                    if not name_m:
                        anonymous += 1
                        continue
                    named_total += 1
                    if name_m.group(0) not in referenced:
                        hits.append(name_m.group(0))
            if hits:
                by_module[module] = hits
        unreferenced_count = sum(len(v) for v in by_module.values())
        print(
            f"checkdecls (advisory, reverse): referenced base names: {len(referenced)}"
            f" | unreferenced corpus declarations: {unreferenced_count}/{named_total}"
            f" named (+{anonymous} anonymous instances) across {len(by_module)} modules"
            + ("" if unreferenced_count else " - corpus fully referenced")
        )
        example_cap = 30
        shown = 0
        modules_left = 0
        names_left = 0
        for module, hits in sorted(by_module.items()):
            if shown >= example_cap:
                modules_left += 1
                names_left += len(hits)
                continue
            examples = hits[: example_cap - shown]
            shown += len(examples)
            tail = "" if len(examples) == len(hits) else f" (+{len(hits) - len(examples)} more)"
            print(f"  {module}: {len(hits)} unreferenced [{', '.join(examples)}{tail}]")
        if modules_left:
            print(
                f"  ... {names_left} further unreferenced declarations in"
                f" {modules_left} further modules (examples capped at {example_cap})"
            )

    warn_count = missing + no_ok + (nodes - resolved)
    exit_code = 1 if warn_count else 0
    if checkdecls_errors and unreferenced_count:
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

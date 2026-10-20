#!/usr/bin/env python3
"""Per-example documentation coverage for the EASCI corpus.

Companion to census_docstrings.py for the U1b wave (example docstrings).
The census counts `/-!` and `/--` openers line-wise but cannot say
WHETHER an `example` is documented. This tool attributes documentation
to each example with the group-block semantics ruled in 2026-10-10:

  An `example` is documented when the nearest preceding significant
  line closes a `/--` or `/-!` block, with no intervening declaration,
  section boundary, or namespace change. A single group block therefore
  covers a homogeneous run of examples beneath it; an own `/--` is just
  the width-1 case. Coverage is cleared by a non-example declaration
  (theorem/def/...), `section`/`namespace`/`end`, or a new block.

The tool also flags doubled docstrings - a docstring block whose next
significant line is another docstring block - which is a Lean parse
error ("unexpected token '/--'; expected ..."), the failure mode hit
while documenting Tests/CCVGating.lean.

Usage:
  python3 scripts/example_doc_coverage.py [ROOT]      # gap map over ROOT
  python3 scripts/example_doc_coverage.py --self-test # semantics check
"""

import os
import re
import sys

DECL = re.compile(
    r"^\s*(?:private\s+|protected\s+|noncomputable\s+|scoped\s+|partial\s+)*"
    r"(theorem|lemma|def|abbrev|instance|structure|class|inductive|axiom|"
    r"macro|syntax|elab|example)\b"
)
EXAMPLE = re.compile(r"^\s*(?:noncomputable\s+|private\s+|protected\s+)*example\b")
BOUNDARY = re.compile(r"^\s*(?:section|namespace|end)\b")
BLOCK_OPEN = re.compile(r"^\s*/-(?:-|!)")
LINE_COMMENT = re.compile(r"^\s*--")


def scan_text(text):
    """Return (documented, undocumented, doubled) for one Lean source."""
    lines = text.split("\n")
    documented = undocumented = doubled = 0
    pending = False          # a docstring block is covering the next decls
    i = 0
    while i < len(lines):
        line = lines[i]
        if BLOCK_OPEN.match(line):
            # consume the whole block comment; remember the kind: a /--
            # docstring attaches to the next declaration, a /-! module
            # doc is unattached (so /-! -> /-- adjacencies are legal and
            # only a /-- immediately followed by another /-- is the
            # parse-error class hit in Tests/CCVGating.lean).
            kind = "module" if line.lstrip().startswith("/-!") else "decl"
            j = i
            while j < len(lines) and "-/" not in lines[j]:
                j += 1
            # doubled? a /-- docstring whose next significant line opens
            # another /-- docstring
            k = j + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            if (kind == "decl" and k < len(lines)
                    and lines[k].lstrip().startswith("/--")):
                doubled += 1
            pending = True
            i = j + 1
            continue
        if LINE_COMMENT.match(line):
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        if EXAMPLE.match(line):
            if pending:
                documented += 1
            else:
                undocumented += 1
            i += 1
            continue          # group coverage persists across the run
        if DECL.match(line) or BOUNDARY.match(line):
            pending = False
            i += 1
            continue
        i += 1
    return documented, undocumented, doubled


SELF_TEST = """\
/-! module doc -/
import EASCI.Foo

/-!
# Group
-/

/-- own doc -/
example : True := by decide

example : 1 + 1 = 2 := by decide

example : 2 + 2 = 4 := by decide

theorem unrelated : True := trivial

example : 3 + 3 = 6 := by decide

namespace Inner

/-- fine doc -/
example : True := by decide

end Inner

/-- doubled one -/
/-- doubled two -/
example : True := by decide

/-!
Run group
-/

example : 4 + 4 = 8 := by decide

example : 5 + 5 = 10 := by decide
"""


def self_test():
    d, u, dbl = scan_text(SELF_TEST)
    ok = True
    # 8 examples: 3 under the /-- group, 1 own before the theorem, 1 after
    # the theorem (undocumented), 1 in Inner (own), 2 under the /-! group.
    # Doubled: only the /-- -> /-- pair; the /-! group -> own-doc adjacency
    # is legal (module docs are unattached).
    if (d, u, dbl) != (7, 1, 1):
        print(f"self-test FAIL: documented={d} undocumented={u} doubled={dbl}"
              " (expected 7, 1, 1)")
        ok = False
    else:
        print("self-test ok: 7 documented, 1 undocumented, 1 doubled")
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    root = sys.argv[1] if len(sys.argv) > 1 else "EASCI"
    total_u = total_d = total_dbl = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".scratch"]
        for fn in sorted(filenames):
            if not fn.endswith(".lean"):
                continue
            full = os.path.join(dirpath, fn)
            d, u, dbl = scan_text(open(full, encoding="utf-8").read())
            path = os.path.relpath(full, root)
            total_d += d
            total_u += u
            total_dbl += dbl
            if u or dbl:
                marks = []
                if u:
                    marks.append(f"{u} undocumented")
                if dbl:
                    marks.append(f"{dbl} doubled-docstring pairs")
                print(f"{path}: {', '.join(marks)} ({d} documented)")
    print(f"TOTAL: {total_d} documented, {total_u} undocumented, "
          f"{total_dbl} doubled pairs")
    sys.exit(1 if (total_u or total_dbl) else 0)


if __name__ == "__main__":
    main()

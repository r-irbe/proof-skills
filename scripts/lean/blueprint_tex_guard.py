#!/usr/bin/env python3
"""Pre-render guard for the blueprint TeX sources.

Catches, in seconds, the generator-defect classes that have each cost a
full act-render cycle (2026-10-14..16):

  1. Leaked HTML entities (&nbsp; &amp; &lt; &gt; &le; &ge; &times;
     &rarr; &larr; &minus; &#NN;) -- the &nbsp; at
     epistemics-opinion.tex l.380 was read by LaTeX as an alignment tab
     and hard-stopped the render.                            ERROR
  2. Doubled-backslash corruption: two backslashes immediately followed
     by an ASCII letter (the wave generator's mangled commands; legitimate
     row separators are followed by newline, space, comma or &).
     tensornetwork-quantumbondcompression.tex carried 81 of these.  ERROR
  3. Math-bearing section titles whose math carries control sequences
     and lacks \\texorpdfstring (\\\\times and \\\\nabla hard-error
     hyperref's pdfstringdef; most other symbols only warn).   WARN

Errors block (exit 1); warnings are listed but do not block.  The
generator-side fix is the emitting lane's debt; this guard keeps the
pipeline honest until it lands.

Usage:
  python3 tools/blueprint_tex_guard.py [--root PATH] [--self-test]
Exit: 0 clean (warnings allowed) / 1 findings / 2 usage error.
"""

import argparse
import re
import sys
from pathlib import Path

BS = chr(92)

ENTITY_RE = re.compile(r"&[a-zA-Z]{2,10};|&#\d+;")
DOUBLED_RE = re.compile(re.escape(BS + BS) + r"(?=[A-Za-z])")
HASH_RE = re.compile(r"(?<!" + re.escape(BS) + r")#")
MACRO_RE = re.compile(re.escape(BS) + r"(?:newcommand|renewcommand|def|newenvironment|newtheorem)\b")
N_WORDS = set("""nabla nu ne neq ni nleq ngeq nless ngtr nsim nmid notin
nsucceq npreceq nsubset nsupset nsubseteq nsupseteq nprec nsucc
ncong nvdash nvDash nparallel neg nexists nwarrow nearrow
nrightarrow nleftarrow nRightarrow nLeftarrow nLeftrightarrow nleftrightarrow
nonumber notag noindent nolimits norm natural null not
newcommand renewcommand newenvironment newtheorem newpage newline
newtoks newsavebox newcounter newlength nobreak nobreakspace
nolinebreak nopagebreak nth nto""".split())
CTRL_WORD_RE = re.compile(re.escape(BS) + r"([a-zA-Z]*)")
TITLE_RE = re.compile(r"^" + re.escape(BS) + r"(?:sub)*section\*?\{")
TITLE_MATH_CS_RE = re.compile(r"\$[^$]*" + re.escape(BS) + r"[A-Za-z]+[^$]*\$")


def scan_text(name, text):
    """Return (errors, warnings) as lists of 'file:line: class message'."""
    errors, warnings = [], []
    for i, line in enumerate(text.split("\n"), 1):
        if ENTITY_RE.search(line):
            errors.append(f"{name}:{i}: HTML entity leaked into LaTeX: "
                          f"{ENTITY_RE.search(line).group(0)!r}")
        if DOUBLED_RE.search(line):
            errors.append(f"{name}:{i}: doubled backslash before a letter "
                          f"(corrupted command)")
        if (TITLE_RE.match(line) and "texorpdfstring" not in line
                and TITLE_MATH_CS_RE.search(line)):
            warnings.append(f"{name}:{i}: math-bearing section title with "
                            f"control-sequence math and no texorpdfstring")
        stripped = line.lstrip()
        if (not stripped.startswith("%") and HASH_RE.search(line)
                and not MACRO_RE.search(line)):
            errors.append(f"{name}:{i}: raw # in text (macro parameter "
                          f"character; escape as " + BS + "#)")
        for m in CTRL_WORD_RE.finditer(line):
            word = m.group(1)
            if word.startswith("n") and word not in N_WORDS:
                errors.append(f"{name}:{i}: literal-n escape or unknown "
                              f"n-word " + BS + word + " (generator leak)")
    return errors, warnings


def run_scan(sections):
    errors, warnings = [], []
    files = sorted(sections.glob("*.tex"))
    for p in files:
        e, w = scan_text(p.name, p.read_text(errors="replace"))
        errors.extend(e)
        warnings.extend(w)
    return len(files), errors, warnings


def self_test():
    cases = [
        ("entity nbsp", "x &nbsp; y", 1, 0),
        ("entity numeric (two defects: & and #)", "x &#8212; y", 2, 0),
        ("legit table amp", "a & b", 0, 0),
        ("legit escaped amp", "a " + BS + "& b;", 0, 0),
        ("raw hash", "finding #20", 1, 0),
        ("escaped hash", "finding " + BS + "#20", 0, 0),
        ("hash in comment", "% W13 #eval", 0, 0),
        ("hash in macro", BS + "newcommand{" + BS + "x}[1]{#1}", 0, 0),
        ("literal n escape", "for $x$," + BS + "nincreasing y", 1, 0),
        ("bare n symbol", "a " + BS + "n b", 1, 0),
        ("nabla ok", "$" + BS + "nabla P$", 0, 0),
        ("newcommand ok", BS + "newcommand{" + BS + "x}{y}", 0, 0),
        ("doubled command", "a " + BS + BS + "times b", 1, 0),
        ("legit row sep", "p_i & j = i + 1," + BS + BS, 0, 0),
        ("legit sep then space", BS + BS + " 1 & t_1", 0, 0),
        ("title with math", BS + "section{T $" + BS + "nabla$}", 0, 1),
        ("title guarded", BS + "section{T " + BS + "texorpdfstring{$"
         + BS + "nabla$}{x}}", 0, 0),
        ("clean line", "plain text with no defects", 0, 0),
    ]
    passed = 0
    for label, text, want_e, want_w in cases:
        e, w = scan_text("t", text)
        ok = len(e) == want_e and len(w) == want_w
        print(f"  [{'PASS' if ok else 'FAIL'}] {label} "
              f"(errors={len(e)} warnings={len(w)})")
        passed += ok
    print(f"blueprint_tex_guard self-test: "
          f"{'PASSED' if passed == len(cases) else 'FAILED'} "
          f"({passed}/{len(cases)} checks)")
    return passed == len(cases)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    default_root = Path("blueprint/src/sections")
    ap.add_argument("--root", default=str(default_root),
                    help="sections directory to scan")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(0 if self_test() else 1)

    sections = Path(args.root)
    if not sections.is_dir():
        print(f"scan root not found: {sections}", file=sys.stderr)
        sys.exit(2)

    nfiles, errors, warnings = run_scan(sections)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"blueprint_tex_guard: {nfiles} files scanned, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

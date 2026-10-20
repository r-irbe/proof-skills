#!/usr/bin/env python3
"""U2a naming triage + tests/example inventory over the Lean corpus.

Classifies every uppercase-first theorem/lemma/def/instance name into:
  is-prefix      - `IsXxx` predicates (mathlib-accepted convention)
  acronym-lead   - begins with a known acronym (CCV, LTS, BFT, RS, IFS, ...)
  camel-struct   - multi-word CamelCase that reads like a structure name
  other          - genuine nonconformance candidates
Also inventories the test files: decls, anonymous `example`s, and named
`example`-style worked cases available for folding into docstrings.

Output: markdown on stdout.
  python3 census_naming.py > u2-naming-audit.md
"""

import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
PKG = os.path.join(ROOT, "..", "..", "..", "packages")
assert os.path.isdir(os.path.join(ROOT, "EASCI")), f"EASCI not under {ROOT}"

DECL = re.compile(r"^(theorem|lemma|def|instance|abbrev)\s+([A-Za-z_][A-Za-z0-9_']*)")
ACRONYMS = (
    "CCV",
    "LTS",
    "BFT",
    "RS",
    "IFS",
    "EASCI",
    "OT",
    "KL",
    "Fisher",
    "OTF",
    "GS",
    "IVT",
    "FAFG",
    "FEG",
    "KL",
)
TEST_MARKERS = ("Test", "Tests")

DOMAIN = re.compile(r"^(G[1-5T]|F[0-9]{1,2}|P[0-9]|S[1-9])$")


def classify(name):
    if DOMAIN.fullmatch(name):
        return "domain-name"
    if name.startswith("Is"):
        return "is-prefix"
    for a in ACRONYMS:
        if name.startswith(a):
            return "acronym-lead"
    if re.fullmatch(r"[A-Z][a-z]+[A-Z].*", name):
        return "camel-struct"
    return "other"


def files_under(base):
    for dirpath, _d, fns in os.walk(base):
        if ".lake" in dirpath.split(os.sep):
            continue
        for fn in sorted(fns):
            if fn.endswith(".lean"):
                yield os.path.join(dirpath, fn)


def scan(path):
    decls = examples = 0
    upper = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        in_block = None
        for ln, line in enumerate(fh, 1):
            if in_block:
                if "-/" in line:
                    in_block = None
                continue
            if line.startswith("/--"):
                in_block = "/--"
                continue
            if line.startswith("/-!"):
                in_block = "/-!"
                continue
            m = DECL.match(line)
            if m:
                decls += 1
                name = m.group(2)
                if name[0].isupper():
                    upper.append((ln, m.group(1), name, classify(name)))
            if re.match(r"^example\b", line):
                examples += 1
    return decls, examples, upper


out = []
cat_tot = {"domain-name": 0, "is-prefix": 0, "acronym-lead": 0, "camel-struct": 0, "other": 0}
per_mod_other = []
for base, tag in [(os.path.join(ROOT, "EASCI"), "EASCI")] + [
    (os.path.join(PKG, p), f"packages/{p}")
    for p in sorted(os.listdir(PKG))
    if os.path.isdir(os.path.join(PKG, p))
]:
    for f in files_under(base):
        rel = os.path.relpath(f, base)
        is_test = any(m in rel for m in TEST_MARKERS)
        decls, examples, upper = scan(f)
        for _ln, _kind, _name, cat in upper:
            cat_tot[cat] += 1
        others = [(ln, kind, name) for ln, kind, name, c in upper if c == "other"]
        if others:
            per_mod_other.append((rel, tag, len(others), others[:3]))
        if is_test and (decls or examples):
            out.append(f"- TEST `{tag}/{rel}`: {decls} decls, {examples} anonymous examples")

out.insert(0, "")
tot_upper = sum(cat_tot.values())
summary = [
    "# U2a naming audit + tests/example inventory (2026-10-02)",
    "",
    "Generator: `docs/easci/lean/scripts/census_naming.py`. Triage of the",
    "uppercase-first flags from the U0 census, plus the test-file inventory",
    'for the sign-off requirement "fold in the tests and their examples".',
    "",
    "## Naming triage (uppercase-first declarations, corpus-wide)",
    "",
    f"- total uppercase-first: {tot_upper}",
    f"- domain-name codes (G1-G5/F-codes/P-codes; intentional EASCI naming): {cat_tot['domain-name']}",
    f"- `Is`-prefixed predicates (mathlib-accepted): {cat_tot['is-prefix']}",
    f"- acronym-leading (CCV/LTS/BFT/RS/IFS/...): {cat_tot['acronym-lead']}",
    f"- camel-structure-like: {cat_tot['camel-struct']}",
    f"- **other (genuine nonconformance candidates): {cat_tot['other']}**",
    "",
    "Modules carrying `other` findings (top by count):",
    "",
]
per_mod_other.sort(key=lambda r: -r[2])
for rel, tag, n, sample in per_mod_other[:20]:
    smp = "; ".join(f"{k} {nm}" for _l, k, nm in sample)
    summary.append(f"- `{tag}/{rel}`: {n} ({smp})")
summary.append("")
summary.append("## Test files with foldable content")
summary.append("")
out.extend(summary)
sys.stdout.write("\n".join(out))

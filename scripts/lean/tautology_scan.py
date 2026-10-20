#!/usr/bin/env python3
#  Generic copy shipped with the lean-deep-audit skill (proof-skills).
#  Upstream-use: python3 deep_audit_census.py --corpus <path/to/lib/sources> [--out report.md]
#  The PROJECT-side instance of this script lives in the consuming repo's scripts/.
"""Deep-audit P3: tautology / spec-baking candidate scan.

Finds theorem/lemma declarations whose ENTIRE proof body is one of the
suspicious trivial forms:

  rfl, by rfl, trivial, by trivial, assumption, by assumption,
  by simp / by simp_all / by simp_all_full (bare, no args),
  by decide, by omega (bare),
  exact <hypothesis>, := <hypothesis>, := h.<field> (a bare projection)

Each candidate is a TRIAGE INPUT, not a verdict: a `rfl` on a genuine
definitional lemma is fine; the question the reviewer answers per
candidate is whether the STATEMENT carries mathematical content or
bakes its conclusion into a hypothesis / structure field.

Deterministic; candidates sorted by (module, line).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

THM_RE = re.compile(
    r"^(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?(?:private\s+|protected\s+)?"
    r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)"
)
NEXT_DECL_RE = re.compile(
    r"^(?:@\[|noncomputable\s|private\s|protected\s|theorem\s|lemma\s|def\s|"
    r"instance\s|abbrev\s|structure\s|class\s|inductive\s|example\s|opaque\s|"
    r"namespace\s|end\b|section\b|#[-a-z])"
)

TRIVIAL_BODIES = {
    "rfl",
    "by rfl",
    "trivial",
    "by trivial",
    "assumption",
    "by assumption",
    "by simp",
    "by simp_all",
    "by simp_all_full",
    "by decide",
    "by omega",
    "by norm_num",
    "by simp_all <",
    "by tauto",
    "by itauto",
    "by simp [*]",
    "by exact trivial",
    "by exact rfl",
    "by rfl <",
    "by constructor",
}

# `:= h`, `:= hfoo`, `exact h`, `exact hfoo`, `:= h.bar`, `exact h.bar`
BARE_HYP_RE = re.compile(
    r"^(?:by\s+)?(?:exact\s+)?([A-Za-z_][A-Za-z0-9_']*)(\.[A-Za-z0-9_']+)?\s*$"
)


def parse_file(path: Path, root_ns_hint: str) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    module = path.relative_to(path.parent.parent).with_suffix("").as_posix().replace("/", ".")
    candidates: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        m = THM_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(2)
        start = i
        # find the proof body: the first ':=' at top level after the decl,
        # then collect until the next top-level declaration.
        j = i + 1
        stmt_text = lines[i].rstrip()
        body_start = None
        while j < n and j - i < 60:
            if ":=" in lines[j] and not lines[j].lstrip().startswith("--"):
                body_start = j
                break
            stmt_text += " " + lines[j].strip()
            j += 1
        if body_start is None:
            i += 1
            continue
        # proof body lines: from body_start (text after ':=') to next decl
        body_parts: list[str] = []
        after = lines[body_start].split(":=", 1)[1].strip()
        if after:
            body_parts.append(after)
        k = body_start + 1
        while k < n and not NEXT_DECL_RE.match(lines[k]):
            ln = lines[k]
            if ln.strip() and not ln.strip().startswith("--"):
                body_parts.append(ln.strip())
            k += 1
        body = " ".join(body_parts).strip()
        # the body must end before the next declaration starts (heuristic:
        # the next decl's own ':=' would have been swallowed; that is fine,
        # candidates are decided on the FIRST tokens).
        first = body.split(". ")[0].strip().rstrip(",").strip()
        norm = " ".join(first.split())
        is_candidate = False
        why = ""
        if norm in TRIVIAL_BODIES:
            is_candidate, why = True, "trivial body"
        else:
            bm = BARE_HYP_RE.match(norm)
            if (
                bm
                and bm.group(1)[0].islower()
                and bm.group(1)
                not in {
                    "it",
                    "this",
                    "h",
                    "he",
                    "hf",  # single-letter h still flagged below
                }
            ) or (bm and bm.group(1) in {"h", "h1", "h2", "h'", "hh"}):
                is_candidate, why = True, "bare hypothesis/projection"
        if is_candidate:
            candidates.append(
                {
                    "module": module,
                    "line": start + 1,
                    "name": name,
                    "why": why,
                    "body": norm[:80],
                    "stmt": stmt_text.strip()[:160],
                }
            )
        i = body_start + 1 if k > body_start else i + 1
    return candidates


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--namespace", type=str, default=None, help="Root namespace hint (defaults to corpus basename)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    all_c: list[dict] = []
    for f in sorted(args.corpus.rglob("*.lean")):
        ns = args.namespace or args.corpus.resolve().name
        all_c.extend(parse_file(f, ns))
    all_c.sort(key=lambda c: (c["module"], c["line"]))

    lines_out = [
        "# Deep-audit P3 - tautology / spec-baking candidates",
        "",
        f"Corpus: `{args.corpus.name}`. Generated by `scripts/tautology_scan.py`.",
        "Candidates, not verdicts: each needs a triage disposition",
        "(definitional-ok / rewrite-the-statement / already-fixed).",
        "",
        f"{len(all_c)} candidates.",
        "",
        "| module:line | name | why | proof body | statement (head) |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in all_c:
        lines_out.append(
            f"| {c['module']}:{c['line']} | `{c['name']}` | {c['why']} "
            f"| `{c['body']}` | {c['stmt']} |"
        )
    text = "\n".join(lines_out) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(all_c)} candidates)", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

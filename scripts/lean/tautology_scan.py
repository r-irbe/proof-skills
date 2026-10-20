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
SIMP_ATTR_RE = re.compile(r"@\[[^\]]*\bsimp\b[^\]]*\]")
EQUATIONAL_SUFFIXES = (
    "_def",
    "_apply",
    "_zero",
    "_succ",
    "_one",
    "_two",
    "_nil",
    "_cons",
    "_r",
    "_s",
    "_k",
    "_e",
    "_top",
    "_bot",
    "_atom",
    "_not",
    "_and",
    "_or",
    "_imp",
    "_box",
    "_diamond",
    "_tau",
    "_par",
    "_bang",
    "_stable",
    "_transition",
    "_collapse",
    "_chaos",
)


def _strip_outer_parens(expr: str) -> str:
    s = expr.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        in_string = False
        balanced = True
        for idx, c in enumerate(s):
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0 and idx < len(s) - 1:
                    balanced = False
                    break
        if balanced and depth == 0:
            s = s[1:-1].strip()
        else:
            break
    return s


def _extract_conclusion(signature: str) -> str:
    sig = re.sub(r"^(?:@\[[^\]]*\]\s*)*", "", signature.strip())
    m = re.match(
        r"^(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|example)\b(?:\s+\S+)?",
        sig,
    )
    if m:
        sig = sig[m.end() :]
    depth = 0
    in_string = False
    i = 0
    colon_pos = -1
    while i < len(sig):
        c = sig[i]
        if c == '"':
            in_string = not in_string
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c in "([{⟨":
            depth += 1
        elif c in ")]}⟩":
            depth -= 1
        elif c == ":" and depth == 0:
            if i + 1 < len(sig) and sig[i + 1] == "=":
                break
            colon_pos = i
            break
        i += 1
    if colon_pos < 0:
        return ""
    conclusion = sig[colon_pos + 1 :]
    conclusion = re.sub(r":=.*$", "", conclusion, flags=re.DOTALL)
    return conclusion.strip()


def _find_top_level_eq(text: str) -> tuple[int, str] | None:
    depth = 0
    in_string = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            in_string = not in_string
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c in "([{⟨":
            depth += 1
            i += 1
            continue
        if c in ")]}⟩":
            depth -= 1
            i += 1
            continue
        if depth != 0:
            i += 1
            continue
        if text[i : i + 1] == "↔":
            return (i, "↔")
        if c == "=":
            prev = text[i - 1] if i > 0 else ""
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if prev in ":=<>!≤≥≠≡↔":
                i += 1
                continue
            if nxt == "=":
                i += 2
                continue
            return (i, "=")
        i += 1
    return None


def _is_definitional_unfolding(stmt_clean: str, norm: str, has_simp: bool) -> bool:
    """Return True if a trivial `rfl` proof is a genuine non-reflexive
    definitional unfolding or projection rewrite (`f x = rhs` with `lhs != rhs`)
    tagged `@[simp]` or named with an equational/projection suffix.
    """
    if norm not in {"rfl", "by rfl", "by exact rfl", "Iff.rfl", "by exact Iff.rfl"}:
        return False
    conc = _extract_conclusion(stmt_clean)
    eq = _find_top_level_eq(conc)
    if not eq:
        return False
    idx, op = eq
    lhs = " ".join(_strip_outer_parens(conc[:idx]).split())
    rhs = " ".join(_strip_outer_parens(conc[idx + len(op) :]).split())
    if not lhs or not rhs or lhs == rhs:
        return False
    if has_simp:
        return True
    m = THM_RE.match(stmt_clean)
    if not m:
        return False
    name = m.group(2)
    return name.endswith(EQUATIONAL_SUFFIXES) or "_eq_" in name


def parse_file(
    path: Path, root_ns_hint: str, *, include_definitional: bool = False
) -> list[dict]:
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
        has_simp = bool(SIMP_ATTR_RE.search(lines[i])) or (
            i > 0 and bool(SIMP_ATTR_RE.search(lines[i - 1]))
        )
        # find the proof body: the first ':=' at top level on or after the decl,
        # then collect until the next top-level declaration.
        stmt_text = lines[i].rstrip()
        if ":=" in lines[i] and not lines[i].lstrip().startswith("--"):
            body_start = i
        else:
            j = i + 1
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
        stmt_clean = (
            lines[i].split(":=", 1)[0].strip()
            if ":=" in lines[i]
            else (stmt_text + " " + lines[body_start].split(":=", 1)[0].strip())
        )
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
        if is_candidate and (
            include_definitional
            or not _is_definitional_unfolding(stmt_clean, norm, has_simp)
        ):
            stmt_display = (
                lines[i].strip() if ":=" in lines[i] else stmt_clean.strip()
            )
            candidates.append(
                {
                    "module": module,
                    "line": start + 1,
                    "name": name,
                    "why": why,
                    "body": norm[:80],
                    "stmt": stmt_display[:160],
                }
            )
        i = body_start + 1 if k > body_start else i + 1
    return candidates


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--namespace", type=str, default=None, help="Root namespace hint (defaults to corpus basename)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--include-definitional",
        action="store_true",
        help="Include @[simp] and equational definitional unfolding/projection rfl lemmas",
    )
    args = ap.parse_args()

    all_c: list[dict] = []
    for f in sorted(args.corpus.rglob("*.lean")):
        ns = args.namespace or args.corpus.resolve().name
        all_c.extend(
            parse_file(f, ns, include_definitional=args.include_definitional)
        )
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

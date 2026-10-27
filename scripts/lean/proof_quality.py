#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Proof Quality Analyzer for Lean 4 projects.

Static analysis of Lean 4 proof quality (both tactic-mode `:= by …` and
term-mode `:= <term>` proofs; recognises `example` and the
`private`/`protected`/`public`/`scoped`/`noncomputable` modifiers):
  - Detect potential vacuous truths (empty hypotheses → trivial conclusions)
  - Detect `: True` placeholders, term-mode truth witnesses, and likely
    tautology/smoke-test closures
  - Find overly long proofs (candidate for decomposition), refined by a
    structural branch-point signal
  - Detect redundant hypotheses (hypothesis never used in proof term)
  - Find tactic diversity (over-reliance on omega/simp)
  - Detect potential duplication (similarly-structured theorems)

Usage:
    python3 scripts/lean/proof_quality.py [--lean-dir MyProject] [--output proof_quality.md]
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def analyze_module(filepath: Path) -> dict:
    """Analyze proof quality for one module."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()
    module = filepath.stem

    findings = []
    stats = {
        "module": module,
        "tactic_usage": Counter(),
        "proof_lengths": [],
        "theorem_count": 0,
    }

    # Parse theorem blocks from the comment-stripped source so that
    # interspersed `/- Remark: ... -/` blocks between theorems do not
    # leak into the previous theorem's body line-count.  Stripping
    # preserves line numbers (each comment char becomes a space) so
    # `thm['line']` and the rest of the analysis remain accurate.
    # (W12 r03, replaces an earlier column-0 `/-` halt-condition
    # heuristic that was unsafe inside `by`-blocks.)
    stripped_text = "\n".join(_strip_lean_comments(lines))
    theorem_blocks = extract_theorem_blocks(stripped_text)
    for thm in theorem_blocks:
        thm["docstring"] = _extract_preceding_docstring(lines, thm["line"])

    for thm in theorem_blocks:
        stats["theorem_count"] += 1

        # Count tactics used
        tactics_used = extract_tactics(thm["body"])
        for tactic in tactics_used:
            stats["tactic_usage"][tactic] += 1

        # Proof length (count non-blank, non-comment lines only)
        proof_lines = [
            ln
            for ln in thm["body"].splitlines()
            if ln.strip() and not ln.strip().startswith("--")
        ]
        body_lines = len(proof_lines)
        stats["proof_lengths"].append((thm["name"], body_lines))

        # Long-proof bands (W12 r04, after rubber-duck critique):
        # Mathlib4 routinely contains substantive proofs of 50–100
        # lines without enforcing a hard limit.  Splitting the
        # severity reflects this: 31–59 is advisory (P3), 60–99 is
        # improvement (P2), and ≥100 is a strong-signal P1 outlier.
        # Bands preserve visibility while reserving the loud signal
        # for genuine outliers.
        #
        # Structural signal (Wave-05): raw line count alone cannot tell a
        # flat 40-line `calc` (hard to split) from a 40-line proof with
        # many independent case branches (a natural decomposition
        # candidate).  `branch_points` counts focus dots / case splits /
        # combinators; a 31–59 line proof that is *also* structurally
        # branchy is escalated P3 → P2.
        branch_points = _structural_branch_points(thm["body"])
        if body_lines >= 100:
            findings.append(
                {
                    "type": "long-proof",
                    "severity": "P1",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": (
                        f"Proof is {body_lines} lines ({branch_points} branch "
                        f"points) — strongly consider decomposition or "
                        f"extraction of reusable lemmas"
                    ),
                }
            )
        elif body_lines >= 60:
            findings.append(
                {
                    "type": "long-proof",
                    "severity": "P2",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": (
                        f"Proof is {body_lines} lines ({branch_points} branch "
                        f"points) — consider decomposition"
                    ),
                }
            )
        elif body_lines > 30:
            branchy = branch_points >= 12
            findings.append(
                {
                    "type": "long-proof",
                    "severity": "P2" if branchy else "P3",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": (
                        f"Proof is {body_lines} lines with {branch_points} "
                        f"branch points — multiple independent branches suggest "
                        f"natural helper-lemma extraction"
                        if branchy
                        else f"Proof is {body_lines} lines ({branch_points} branch "
                        f"points) — review for natural helper-lemma extraction "
                        f"(advisory)"
                    ),
                }
            )

        # Check for potential vacuous truth
        if is_vacuous_candidate(thm["signature"], thm["body"]):
            findings.append(
                {
                    "type": "vacuous-candidate",
                    "severity": "P1",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": "May be vacuously true — proof uses False.elim or absurd with impossible hypothesis",
                }
            )

        findings.extend(find_tautology_candidates(thm))

        # Check hypothesis and value/underscore binder usage
        unused = find_unused_hypotheses(thm["signature"], thm["body"])
        binder_types = {
            name: b["type"]
            for b in _extract_binders_list(thm["signature"])
            for name in b["names"]
        }
        for hyp in unused:
            is_val_or_under = hyp.startswith("_") or _is_value_type(
                binder_types.get(hyp, "")
            )
            findings.append(
                {
                    "type": "UNUSED_VALUE_OR_UNDERSCORE_BINDER"
                    if is_val_or_under
                    else "unused-hypothesis",
                    "severity": "P2",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": f"Binder `{hyp}` is unused in conclusion, other hypotheses, and proof body",
                }
            )

    # @[simp] loop-risk scan (W9 HITL B-1): for each `@[simp]` rewrite rule,
    # if the head symbol of the LHS occurs as a function application in the
    # RHS, flag it as a potential rewrite loop. False positives are possible
    # for terminating simp lemmas that recurse on a strictly smaller
    # argument; manual review of any flagged rule is required.
    findings.extend(find_simp_loops(text, theorem_blocks))
    findings.extend(find_one_way_bool_checkers(text, theorem_blocks))

    # Heartbeat-budget scan (W10 r27): file-level `set_option maxHeartbeats N`
    # values that exceed sane review thresholds are flagged. The rule is:
    #   * N ≤ 200_000 — clean (default Lean budget is 200_000)
    #   * 200_000 < N ≤ 1_000_000 — P2 warning (consider proof split / hint)
    #   * N > 1_000_000 — P1 (almost always indicates an unfinished refactor
    #     or a perf regression that should be tracked).
    # `set_option maxHeartbeats 0` disables the budget entirely and is also
    # flagged as P1 (defeats the elaborator's safety net).
    findings.extend(find_heartbeat_overrides(text, filepath))

    # Tactic diversity check
    total_tactics = sum(stats["tactic_usage"].values())
    if total_tactics > 0:
        top_tactic, top_count = stats["tactic_usage"].most_common(1)[0]
        if top_count / total_tactics > 0.5 and total_tactics > 10:
            findings.append(
                {
                    "type": "low-tactic-diversity",
                    "severity": "P3",
                    "theorem": "(module-level)",
                    "line": 0,
                    "detail": f"{top_tactic} used {top_count}/{total_tactics} times ({top_count / total_tactics:.0%})",
                }
            )

    return {"findings": findings, "stats": stats}


def extract_theorem_blocks(text: str) -> list[dict]:
    """Extract theorem name, signature, body, and line number.

    Handles both proof styles:
      * tactic-mode  — `... := by <tactics>`
      * term-mode    — `... := <term>` (e.g. `:= rfl`, `:= ⟨h₁, h₂⟩`)

    The separator between signature and proof is the first *depth-0*
    `:=` (so binder defaults like `(n := 0)` inside parens are not
    mistaken for the proof assignment).  The proof body then runs until
    the next top-level declaration at column 0.

    Modifier/keyword coverage (FQ-1/FQ-2, Wave-05 calibration): the
    declaration and terminator regexes recognise `example` and the
    `private`/`protected`/`public`/`scoped`/`noncomputable` modifiers.
    Earlier revisions only matched `theorem|lemma|private …` and only
    `:= by`, which (a) dropped every term-mode proof and (b) let a
    term-mode signature keep scanning forward, swallowing the following
    declarations — together missing ~22% of declarations on large corpora.
    """
    blocks = []
    lines = text.splitlines()
    i = 0
    # Optional leading attributes, then optional declaration modifiers.
    _ATTR = r"(?:@\[[^\]]*\]\s*)*"
    _MODS = r"(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
    # Top-level declaration starters — used to know when to stop
    # collecting proof-body lines.
    TOP_LEVEL = re.compile(
        _ATTR + _MODS + r"(?:theorem|lemma|example|"
        r"def|abbrev|instance|structure|inductive|class|"
        r"end|namespace|section|"
        r"open|set_option|attribute|#|/--|--\s*[§=])"
    )
    # Declarations we actually analyze (carry a proof we can inspect).
    DECL_RE = re.compile(_ATTR + _MODS + r"(theorem|lemma|example)\b(?:\s+(\S+))?")
    while i < len(lines):
        m = DECL_RE.match(lines[i])
        if not m:
            i += 1
            continue
        kind = m.group(1)
        if kind == "example":
            raw_name = "(example)"
        else:
            name_tok = m.group(2) or ""
            raw_name = name_tok.split("(")[0].split(":")[0].strip() or "(anonymous)"
        start_line = i + 1  # 1-based

        # Scan forward to the first depth-0 `:=` separating signature
        # from proof, tracking bracket depth across continuation lines.
        depth = 0
        in_string = False
        found_assign = False
        assign_line = -1
        assign_col = -1
        sig_lines = []
        j = i
        while j < len(lines):
            line = lines[j]
            # A new top-level declaration at column 0 before any `:=`
            # means this declaration has no inspectable proof body
            # (forward declaration, `where`-less ref, etc.); bail out.
            if j > i and line and line[0] not in (" ", "\t") and TOP_LEVEL.match(line):
                break
            k = 0
            n = len(line)
            while k < n:
                c = line[k]
                if c == '"':
                    in_string = not in_string
                    k += 1
                    continue
                if in_string:
                    k += 1
                    continue
                if c in "([{⟨":
                    depth += 1
                elif c in ")]}⟩":
                    depth -= 1
                elif c == ":" and depth == 0 and k + 1 < n and line[k + 1] == "=":
                    found_assign = True
                    assign_line = j
                    assign_col = k
                    break
                k += 1
            if found_assign:
                break
            sig_lines.append(line)
            j += 1
        if not found_assign:
            i += 1
            continue

        # Signature is everything up to (not including) the `:=`.
        sig_lines.append(lines[assign_line][:assign_col])
        signature = "\n".join(sig_lines)

        # Seed the body from the remainder of the `:=` line, deciding
        # between tactic-mode (`by …`) and term-mode.
        body_lines = []
        remainder = lines[assign_line][assign_col + 2 :]
        rstrip = remainder.strip()
        j = assign_line + 1
        if re.match(r"by\b", rstrip):
            after = remainder[remainder.index("by") + 2 :]
            if after.strip():
                body_lines.append(after)
        elif rstrip == "":
            # Proof starts on a following line: a leading `by` token
            # means tactic-mode, otherwise it is a term-mode body.
            if j < len(lines) and re.match(r"by\b", lines[j].strip()):
                bl = lines[j]
                after = bl[bl.index("by") + 2 :]
                if after.strip():
                    body_lines.append(after)
                j += 1
        else:
            # Term-mode: the remainder is the start of the proof term.
            body_lines.append(remainder)

        # Collect the rest of the body until the next top-level decl.
        while j < len(lines):
            line = lines[j]
            if line == "" or line[0:1] in (" ", "\t"):
                body_lines.append(line)
                j += 1
                continue
            if TOP_LEVEL.match(line):
                break
            # Non-indented continuation (e.g. `| pattern => …`).
            body_lines.append(line)
            j += 1

        body = "\n".join(body_lines)
        blocks.append(
            {
                "kind": kind,
                "name": raw_name,
                "signature": signature,
                "body": body,
                "line": start_line,
            }
        )
        i = j  # advance past body
    return blocks


def extract_tactics(body: str) -> list[str]:
    """Extract tactic names from a proof body."""
    # Common Lean 4 tactics
    known_tactics = [
        "simp",
        "omega",
        "linarith",
        "nlinarith",
        "norm_num",
        "ring",
        "ring_nf",
        "exact",
        "apply",
        "intro",
        "intros",
        "constructor",
        "cases",
        "induction",
        "rfl",
        "ext",
        "funext",
        "congr",
        "rw",
        "rewrite",
        "subst",
        "have",
        "let",
        "obtain",
        "rcases",
        "rintro",
        "contradiction",
        "absurd",
        "exfalso",
        "aesop",
        "decide",
        "trivial",
        "assumption",
        "calc",
        "conv",
        "show",
        "suffices",
        "refine",
        "use",
        "existsi",
        "push_neg",
        "by_contra",
        "by_cases",
        "gcongr",
        "positivity",
        "bound_tac",
        "auto",
        "duper",
    ]

    found = []
    for tactic in known_tactics:
        pattern = re.compile(rf"\b{re.escape(tactic)}\b")
        count = len(pattern.findall(body))
        found.extend([tactic] * count)

    return found




FIDELITY_ECHO_BODIES = {
    "assumption",
    "by assumption",
    "trivial",
    "by trivial",
}

DOCSTRING_OVERCLAIM_KEYWORDS = (
    "kuratowski",
    "bipartite",
    "quorum",
    "byzantine",
    "non-empty",
    "8 nibbles",
    "bijection",
)


def _extract_binders_list(signature: str) -> list[dict]:
    """Extract top-level binders (names, type, raw) before the conclusion colon."""
    sig = signature
    m = re.match(
        r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
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

    header = sig[:colon_pos] if colon_pos >= 0 else sig
    binders: list[dict] = []
    j = 0
    while j < len(header):
        if header[j] in "({[⦃":
            open_ch = header[j]
            close_ch = {"(": ")", "{": "}", "[": "]", "⦃": "⦄"}[open_ch]
            d = 1
            k = j + 1
            in_s = False
            top_colon = -1
            while k < len(header) and d > 0:
                ch = header[k]
                if ch == '"':
                    in_s = not in_s
                elif not in_s:
                    if ch == open_ch:
                        d += 1
                    elif ch == close_ch:
                        d -= 1
                        if d == 0:
                            break
                    elif ch == ":" and d == 1 and top_colon < 0:
                        if k + 1 < len(header) and header[k + 1] == "=":
                            k += 1
                        else:
                            top_colon = k
                k += 1
            if d == 0 and top_colon > j:
                names_str = header[j + 1 : top_colon].strip()
                type_str = header[top_colon + 1 : k].strip()
                names = [
                    tok
                    for tok in names_str.split()
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok)
                ]
                binders.append(
                    {
                        "names": names,
                        "type": _normalize_ws(type_str),
                        "bracket": open_ch,
                        "raw": header[j : k + 1],
                    }
                )
            j = k + 1
        else:
            j += 1
    return binders


def _strip_outer_parens_balanced(s: str) -> str:
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        d = 0
        ok = True
        for idx, ch in enumerate(s):
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
                if d == 0 and idx < len(s) - 1:
                    ok = False
                    break
        if ok and d == 0:
            s = s[1:-1].strip()
        else:
            break
    return s


def _norm_prop_expr(s: str) -> str:
    return _normalize_ws(_strip_outer_parens_balanced(s))


def _swap_eq_sides(s: str) -> str | None:
    s_clean = _norm_prop_expr(s)
    eq = _find_top_level_eq(s_clean)
    if eq is None:
        return None
    idx, op = eq
    lhs = _norm_prop_expr(s_clean[:idx])
    rhs = _norm_prop_expr(s_clean[idx + len(op) :])
    if lhs and rhs:
        return f"{rhs} {op} {lhs}"
    return None


def _is_value_type(type_str: str) -> bool:
    t = _norm_prop_expr(type_str)
    if re.search(
        r"(?:=|≠|!=|<=|>=|<|>|≤|≥|↔|∧|∨|/\\|\\/|→|->|\bTrue\b|\bFalse\b|\bAnd\b|\bOr\b|\bNot\b|\bProp\b|¬)",
        t,
    ):
        return False
    value_heads = {
        "Nat",
        "ℕ",
        "Int",
        "ℤ",
        "Rat",
        "ℚ",
        "Real",
        "ℝ",
        "Bool",
        "String",
        "Char",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "USize",
        "Float",
        "BitVec",
        "Fin",
        "List",
        "Array",
        "Vector",
        "Option",
        "Finset",
    }
    head = t.split()[0] if t.split() else ""
    if head in value_heads:
        return True
    if re.match(r"^[A-Z][A-Za-z0-9_.]*$", head) and not head.startswith(
        ("Is", "Has", "WellFormed", "Valid", "Type", "Sort")
    ):
        return True
    return False


def _extract_preceding_docstring(raw_lines: list[str], decl_line_1based: int) -> str:
    """Extract `/-- ... -/` docstring immediately preceding `decl_line_1based`."""
    idx = decl_line_1based - 2
    while idx >= 0 and (
        not raw_lines[idx].strip() or raw_lines[idx].strip().startswith("@[")
    ):
        idx -= 1
    if idx < 0 or "-/" not in raw_lines[idx]:
        return ""
    end_idx = idx
    start_idx = end_idx
    while start_idx >= 0:
        if "/--" in raw_lines[start_idx]:
            return "\n".join(raw_lines[start_idx : end_idx + 1])
        if (
            start_idx < end_idx
            and raw_lines[start_idx].strip()
            and not raw_lines[start_idx].startswith((" ", "\t", "*", "|"))
        ):
            if any(
                raw_lines[start_idx].lstrip().startswith(k)
                for k in ("theorem ", "lemma ", "def ", "structure ", "inductive ")
            ):
                break
        start_idx -= 1
    return ""


def detect_hypothesis_echo(signature: str, body: str) -> str | None:
    """Detect HYPOTHESIS_ECHO: conclusion is syntactically identical (or direct And/symm wrapper)
    to a hypothesis binder type and closed by exact h, assumption, ⟨h1, h2⟩, And.intro, or h.symm."""
    conclusion = _norm_prop_expr(_extract_conclusion(signature))
    if not conclusion:
        return None
    binders = _extract_binders_list(signature)
    hyp_types = [_norm_prop_expr(b["type"]) for b in binders if b["type"]]
    if not hyp_types:
        return None
    body_lines = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    body_norm = _normalize_ws(" ".join(body_lines))
    if body_norm.startswith("by "):
        body_norm = body_norm[3:].strip()

    echo_closer = bool(
        body_norm in FIDELITY_ECHO_BODIES
        or re.match(
            r"^(?:exact\s+)?(?:[A-Za-z_][A-Za-z0-9_']*(?:\.(?:symm|mp|mpr|left|right|1|2))?|"
            r"⟨\s*[A-Za-z0-9_'.\s,]+\s*⟩|"
            r"And\.intro\s+[A-Za-z0-9_'.]+\s+[A-Za-z0-9_'.]+|"
            r"Iff\.intro\s+.*|"
            r"Eq\.symm\s+[A-Za-z0-9_'.]+)$",
            body_norm,
        )
    )
    if not echo_closer:
        return None

    for ht in hyp_types:
        if conclusion == ht:
            return f"Conclusion `{conclusion}` echoes hypothesis `{ht}` and is closed by `{body_norm}`"
        swapped = _swap_eq_sides(ht)
        if swapped and conclusion == swapped:
            return f"Conclusion `{conclusion}` is the symmetric echo of hypothesis `{ht}` closed by `{body_norm}`"
        for sep in ("∧", "/\\", "And"):
            if sep in ht:
                parts = [_norm_prop_expr(p) for p in ht.split(sep)]
                if conclusion in parts:
                    return f"Conclusion `{conclusion}` projects conjunct from hypothesis `{ht}` via `{body_norm}`"

    for sep in ("∧", "/\\"):
        if sep in conclusion:
            c_parts = [_norm_prop_expr(p) for p in conclusion.split(sep) if _norm_prop_expr(p)]
            if c_parts and all(cp in hyp_types for cp in c_parts):
                return f"Conjunction conclusion `{conclusion}` directly echoes hypotheses via `{body_norm}`"
    return None


def detect_reflexive_tautology(signature: str, body: str) -> str | None:
    """Detect REFLEXIVE_TAUTOLOGY: conclusion is `lhs = rhs` (or `(lhs == rhs) = (lhs' == rhs')`)
    with `lhs == rhs` closed by `rfl`."""
    conclusion = _norm_prop_expr(_extract_conclusion(signature))
    if not conclusion:
        return None
    body_lines = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    body_norm = _normalize_ws(" ".join(body_lines))
    if body_norm not in {
        "rfl",
        "by rfl",
        "exact rfl",
        "by exact rfl",
        "Eq.refl",
        "Iff.rfl",
        "by exact Iff.rfl",
    }:
        return None
    refl = _reflexive_conclusion(conclusion)
    if refl:
        return f"Conclusion `{refl}` has identical LHS and RHS and is closed by `{body_norm}`"
    m_beq = re.match(
        r"^\(?(.+?)\s*==\s*(.+?)\)?\s*=\s*\(?(.+?)\s*==\s*(.+?)\)?$", conclusion
    )
    if m_beq:
        l1, r1, l2, r2 = (
            _norm_prop_expr(m_beq.group(1)),
            _norm_prop_expr(m_beq.group(2)),
            _norm_prop_expr(m_beq.group(3)),
            _norm_prop_expr(m_beq.group(4)),
        )
        if l1 == l2 and r1 == r2:
            return f"Boolean equality conclusion `{conclusion}` is syntactically reflexive (`{body_norm}`)"
    return None


def detect_nat_nonneg_triviality(signature: str, body: str = "") -> str | None:
    """Detect NAT_NONNEG_TRIVIALITY: conclusion is `e >= 0`, `e ≥ 0`, `0 <= e`, or `0 ≤ e` over Nat binders."""
    conclusion = _norm_prop_expr(_extract_conclusion(signature))
    if not conclusion:
        return None
    binders = _extract_binders_list(signature)
    nat_vars: set[str] = set()
    for b in binders:
        if b["type"] in {"Nat", "ℕ"}:
            nat_vars.update(b["names"])
    if not nat_vars and not re.search(r"\b(?:Nat|ℕ)\b", signature):
        return None

    m_ge = re.match(r"^(.+?)\s*(?:>=|≥)\s*0$", conclusion)
    m_le = re.match(r"^0\s*(?:<=|≤)\s*(.+)$", conclusion)
    expr = _norm_prop_expr(
        m_ge.group(1) if m_ge else (m_le.group(1) if m_le else "")
    )
    if not expr:
        return None
    if (
        "Finset.sum" in expr
        or "∑" in expr
        or re.search(r"\b(?:Real|ℝ|Int|ℤ|Rat|ℚ)\b", signature)
    ):
        return None
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_']*\b", expr))
    if tokens & nat_vars or re.search(r"\bNat\.", expr):
        return f"Conclusion `{conclusion}` is a trivial Nat non-negativity bound (`0 <= e` holds for all `Nat`)"
    return None


_LEAN_PRECEDING_KW = {"then", "else", "in", "fun", "let", "have", "return", "by"}
_LEAN_FOLLOWING_KW = {"then", "else", "with", "by"}


def _is_standalone_nat_sub_match(
    clause: str, m: re.Match, nat_vars: set[str]
) -> bool:
    lhs, rhs = m.group(1), m.group(2)
    if lhs not in nat_vars or rhs == "0" or lhs == rhs:
        return False
    before = clause[: m.start(1)].rstrip()
    if before:
        if before[-1] in (")", "]"):
            return False
        pm = re.search(r"([A-Za-z0-9_'.]+)$", before)
        if pm and pm.group(1) not in _LEAN_PRECEDING_KW:
            return False
    if not rhs.isdigit():
        if rhs not in nat_vars:
            return False
        after = clause[m.end(2) :]
        if after.startswith("."):
            return False
        fm = re.match(r"^\s+([A-Za-z0-9_'(]+)", after)
        if fm:
            tok = fm.group(1).split("(")[0]
            if tok not in _LEAN_FOLLOWING_KW:
                return False
    return True


def _is_nat_sub_guarded(lhs: str, rhs: str, other_hyps: str) -> bool:
    L = re.escape(lhs)
    R = re.escape(rhs)
    guard_patterns = [
        rf"\b{R}\b[^;]*(?:<=|≤|<)\s*[^;]*\b{L}\b",
        rf"\b{L}\b[^;]*(?:>=|≥|>)\s*[^;]*\b{R}\b",
        rf"\b{L}\b\s*=\s*\b{R}\b",
        rf"\b{R}\b\s*=\s*\b{L}\b",
        rf"\b{L}\b\s*=\s*[^;]*\b{R}\b\s*\+",
        rf"\b{L}\b\s*=\s*[^;]*\+\s*[^;]*\b{R}\b",
        rf"\b{R}\b\s*\+[^;=]*=\s*\b{L}\b",
        rf"\+\s*[^;=]*\b{R}\b[^;=]*=\s*\b{L}\b",
        rf"\b{R}\b\s*=\s*\b{L}\b\s*-",
        rf"\b{L}\b\s*=\s*\(?([A-Za-z0-9_']+\s*\+\s*[A-Za-z0-9_']+)\)?.*?\b{R}\b\s*=\s*\(?\1\)?\s*-",
    ]
    if rhs.isdigit():
        guard_patterns.extend(
            [
                rf"\b{L}\b[^;]*(?:>=|≥|>)\s*\d+",
                rf"\d+\s*(?:<=|≤|<)\s*[^;]*\b{L}\b",
                rf"\b{L}\s*!=\s*0",
                rf"\b{L}\s*≠\s*0",
                rf"0\s*<\s*[^;]*\b{L}\b",
                rf"\b{L}\b\s*>\s*0",
            ]
        )
        if rhs == "1":
            guard_patterns.extend(
                [
                    rf"\b[A-Za-z0-9_']+\s*<\s*\b{L}\b",
                    rf"\b{L}\b\s*>\s*\b[A-Za-z0-9_']+",
                    rf"\b{L}\b\s*(?:>=|≥)\s*[A-Za-z0-9_']+\s*\+\s*[A-Za-z0-9_']+",
                    rf"[A-Za-z0-9_']+\s*\+\s*[A-Za-z0-9_']+\s*(?:<=|≤)\s*\b{L}\b",
                ]
            )
    return any(re.search(gp, other_hyps) for gp in guard_patterns)


def detect_nat_sub_unguarded(signature: str) -> str | None:
    """Detect NAT_SUB_UNGUARDED: theorem signature contains `a - b` over Nat binders without
    any ordering or additive/equality guard in hypotheses."""
    binders = _extract_binders_list(signature)
    nat_vars: set[str] = set()
    prop_clauses: list[str] = []
    for b in binders:
        if b["type"] in {"Nat", "ℕ"}:
            nat_vars.update(b["names"])
        elif not _is_value_type(b["type"]):
            prop_clauses.append(b["type"])
    if not nat_vars:
        return None

    conclusion = _norm_prop_expr(_extract_conclusion(signature))
    arrow_parts = re.split(r"→|->", conclusion)
    for part in arrow_parts:
        if part.strip():
            prop_clauses.append(part.strip())

    for idx, clause in enumerate(prop_clauses):
        other_hyps = " ; ".join(prop_clauses[:idx] + prop_clauses[idx + 1 :])
        for m in re.finditer(
            r"\b([A-Za-z_][A-Za-z0-9_']*)\s*-\s*([A-Za-z_][A-Za-z0-9_']*|\d+)\b",
            clause,
        ):
            if not _is_standalone_nat_sub_match(clause, m, nat_vars):
                continue
            lhs, rhs = m.group(1), m.group(2)
            if not _is_nat_sub_guarded(lhs, rhs, other_hyps):
                return f"Nat subtraction `{lhs} - {rhs}` in `{clause}` has no ordering guard (`{rhs} <= {lhs}`) in hypotheses"
    return None

def detect_misaligned_docstring(
    docstring: str, signature: str, body: str
) -> str | None:
    """Detect MISALIGNED_DOCSTRING: docstring claims complex domain properties while the
    theorem statement is a 1-operator inequality/equality proved in 1 line by rfl or omega."""
    if not docstring:
        return None
    doc_lower = docstring.lower()
    matched_kw = [kw for kw in DOCSTRING_OVERCLAIM_KEYWORDS if kw in doc_lower]
    if not matched_kw:
        return None

    body_lines = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    if len(body_lines) != 1:
        return None
    body_norm = _normalize_ws(body_lines[0])
    if body_norm not in {
        "rfl",
        "by rfl",
        "omega",
        "by omega",
        "decide",
        "by decide",
        "trivial",
        "by trivial",
    }:
        return None

    conclusion = _norm_prop_expr(_extract_conclusion(signature))
    if any(
        q in conclusion
        for q in ("∀", "∃", "↔", "∧", "∨", "Finset", "Set", "Graph", "Bijective")
    ):
        return None
    return (
        f"Docstring claims domain property ({', '.join(matched_kw)}) but theorem `{conclusion}` "
        f"is a 1-line `{body_norm}` arithmetic/reflexive check"
    )


def find_one_way_bool_checkers(text: str, theorem_blocks: list[dict]) -> list[dict]:
    """Detect ONE_WAY_BOOL_CHECKER: executable `Bool`-returning function `def f ... : Bool`
    that only has a one-way `f ... = true -> ...` theorem in the module without a companion
    `↔` (`iff`) or completeness (`... -> f ... = true` / `f ... = false`) theorem."""
    stripped = "\n".join(_strip_lean_comments(text.splitlines()))
    def_re = re.compile(
        r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*def\s+([A-Za-z_][A-Za-z0-9_']*)\b[\s\S]*?:\s*Bool\s*:=",
        re.MULTILINE,
    )
    bool_defs: dict[str, int] = {}
    for m in def_re.finditer(stripped):
        # Ensure we didn't cross another top-level declaration between `def` and `: Bool :=`
        span_text = m.group(0)
        if len(re.findall(r"(?m)^\s*(?:def|theorem|lemma|structure|inductive)\b", span_text)) > 1:
            continue
        fn_name = m.group(1)
        line_no = stripped[: m.start()].count("\n") + 1
        bool_defs[fn_name] = line_no

    if not bool_defs:
        return []

    findings: list[dict] = []
    for fn_name, def_line in bool_defs.items():
        one_way_soundness: list[dict] = []
        has_iff_or_complete = False
        fn_pat = re.compile(rf"\b{re.escape(fn_name)}\b")
        for thm in theorem_blocks:
            sig = thm["signature"]
            if not fn_pat.search(sig):
                continue
            conc = _norm_prop_expr(_extract_conclusion(sig))
            if (
                "↔" in sig
                or "<->" in sig
                or re.search(r"\bIff\b", sig)
                or thm["name"].endswith("_iff")
            ):
                has_iff_or_complete = True
                break
            for arrow in ("→", "->"):
                if arrow in conc:
                    parts = [p.strip() for p in conc.split(arrow)]
                    lhs_parts = " -> ".join(parts[:-1])
                    rhs = parts[-1]
                    if fn_pat.search(rhs) and not fn_pat.search(lhs_parts) and not any(
                        fn_pat.search(b["type"]) for b in _extract_binders_list(sig)
                    ):
                        has_iff_or_complete = True
                        break
            if has_iff_or_complete:
                break
            if re.search(
                rf"\b{re.escape(fn_name)}\b[\s\S]*?=\s*false", sig
            ) and _bound_variable_names(sig):
                has_iff_or_complete = True
                break
            if re.search(rf"\b{re.escape(fn_name)}\b[\s\S]*?=\s*true", sig):
                one_way_soundness.append(thm)

        if one_way_soundness and not has_iff_or_complete:
            first_thm = one_way_soundness[0]
            findings.append(
                {
                    "type": "ONE_WAY_BOOL_CHECKER",
                    "severity": "P2",
                    "theorem": first_thm["name"],
                    "line": first_thm["line"],
                    "detail": (
                        f"Executable Bool checker `{fn_name}` (line {def_line}) only has one-way "
                        f"soundness (`{first_thm['name']}`) without a companion `↔` (`iff`) or completeness theorem"
                    ),
                }
            )
    return findings


def is_vacuous_candidate(signature: str, body: str) -> bool:
    """Heuristic: check if proof might be vacuously true or a specification echo/tautology.

    Flags proofs where:
    1. The conclusion is `False` (disjointness/impossibility) with structurally impossible
       hypotheses (`False`, `0 > 1`, `¬ True`), OR
    2. The theorem exhibits `HYPOTHESIS_ECHO`, `REFLEXIVE_TAUTOLOGY`, or `NAT_NONNEG_TRIVIALITY`.
    """
    if "False.elim" in body or "absurd" in body or "exfalso" in body:
        if re.search(r"rw\s*\[.*_iff", body):
            return False
        if "False" in signature or "0 > 1" in signature or "¬ True" in signature:
            return True
    if detect_hypothesis_echo(signature, body):
        return True
    if detect_reflexive_tautology(signature, body):
        return True
    if detect_nat_nonneg_triviality(signature, body):
        return True
    return False


def find_tautology_candidates(thm: dict) -> list[dict]:
    """Precision-oriented tautology/smoke-test candidates.

    These are intentionally triage findings.  Short proofs are often good Lean;
    the detector only flags shapes that repeatedly hide placeholder statements:
    `: True`, a term-mode truth witness (`trivial`/`True.intro`/`⟨⟩`), a single
    bare `decide`, or a single bare `rfl` over a reflexive equality/iff.

    Severity calibration (Wave-05):
      * `truth-stub` (`: True` conclusion) — P1; almost always a placeholder.
      * `truth-stub-term` (term-mode `trivial`/`True.intro`/`⟨⟩` proving a
        non-`True` goal) — P2; a nullary witness that usually marks a
        smoke/stub statement (FQ-3).
      * `decide-closed-candidate` — bare `decide`.  Concrete, closed targets
        (no binders/quantifiers) are the *intended* use of `decide`, so they
        are advisory P3; targets carrying variables/quantifiers stay P2
        because they are the shapes that hide non-substantive smoke (FQ-4).
    """
    signature = thm["signature"]
    body = thm["body"]
    conclusion = _normalize_ws(_extract_conclusion(signature))
    body_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("--")
    ]
    body_norm = _normalize_ws(" ".join(body_lines))
    findings: list[dict] = []

    if conclusion == "True":
        findings.append(
            {
                "type": "truth-stub",
                "severity": "P1",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": "Statement conclusion is exactly `True`; treat as placeholder/smoke unless explicitly documented",
            }
        )
        return findings

    # Term-mode truth witnesses (FQ-3): a nullary proof term such as
    # `trivial`, `True.intro`, or the empty anonymous constructor `⟨⟩`
    # only closes goals that are definitionally `True`/a nullary
    # structure.  When the *stated* conclusion is not literally `True`
    # this shape usually marks a smoke/stub statement worth review.
    if body_norm in {"trivial", "True.intro", "⟨⟩", "⟨ ⟩"}:
        findings.append(
            {
                "type": "truth-stub-term",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": (
                    f"Proof is a nullary truth witness (`{body_norm}`); the goal "
                    f"is provable by a trivial term — confirm it is a substantive "
                    f"statement, not a placeholder/smoke"
                ),
            }
        )

    if body_norm in {"decide", "exact decide"}:
        concrete = _is_concrete_decide_target(signature)
        findings.append(
            {
                "type": "decide-closed-candidate",
                "severity": "P3" if concrete else "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": (
                    "Proof is a single bare `decide` over a concrete closed "
                    "proposition (decide is the intended tool here; advisory)"
                    if concrete
                    else "Proof is a single bare `decide` and the statement carries "
                    "variables/quantifiers; review whether it is finite "
                    "smoke-test code or a substantive theorem"
                ),
            }
        )

    if body_norm == "rfl":
        reflexive = _reflexive_conclusion(conclusion)
        if reflexive:
            findings.append(
                {
                    "type": "rfl-reflexive-candidate",
                    "severity": "P2",
                    "theorem": thm["name"],
                    "line": thm["line"],
                    "detail": f"Proof is `rfl` and conclusion is definitionally reflexive (`{reflexive}`); review name/docstring for overclaim",
                }
            )

    refl_taut = detect_reflexive_tautology(signature, body)
    if refl_taut:
        findings.append(
            {
                "type": "REFLEXIVE_TAUTOLOGY",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": refl_taut,
            }
        )

    hyp_echo = detect_hypothesis_echo(signature, body)
    if hyp_echo:
        findings.append(
            {
                "type": "HYPOTHESIS_ECHO",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": hyp_echo,
            }
        )

    nat_nonneg = detect_nat_nonneg_triviality(signature, body)
    if nat_nonneg:
        findings.append(
            {
                "type": "NAT_NONNEG_TRIVIALITY",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": nat_nonneg,
            }
        )

    nat_sub = detect_nat_sub_unguarded(signature)
    if nat_sub:
        findings.append(
            {
                "type": "NAT_SUB_UNGUARDED",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": nat_sub,
            }
        )

    doc_misaligned = detect_misaligned_docstring(
        thm.get("docstring", ""), signature, body
    )
    if doc_misaligned:
        findings.append(
            {
                "type": "MISALIGNED_DOCSTRING",
                "severity": "P2",
                "theorem": thm["name"],
                "line": thm["line"],
                "detail": doc_misaligned,
            }
        )

    return findings


def _is_concrete_decide_target(signature: str) -> bool:
    """True if a `decide` target is a concrete, closed proposition.

    Concrete == no binders introduced in the signature and no `∀`/`∃`
    quantifier anywhere.  For such statements `decide` is the intended
    discharge tactic, so the finding is downgraded to advisory (FQ-4).
    """
    if _bound_variable_names(signature):
        return False
    return not ("∀" in signature or "∃" in signature)


def find_unused_hypotheses(signature: str, body: str) -> list[str]:
    """Find named hypotheses or value binders that don't appear in the proof body or statement.

    Accounting rules:
    - Value binders `(x : T)` (e.g. `Nat`, `Int`, `Bool`, domain structures) that do not appear
      anywhere in the conclusion, in any other binder's type, or in the proof body are ALWAYS
      flagged even when whole-context automation (`omega`, `simp`, `decide`, `grind`) is used,
      because an unreferenced value parameter cannot constrain a closed arithmetic goal.
    - Explicit underscore-prefixed hypothesis/value binders `(_h : P)` that are never referenced
      in the conclusion, other binder types, or the proof body are ALWAYS flagged as
      `UNUSED_VALUE_OR_UNDERSCORE_BINDER` candidates.
    - For non-underscore proposition hypotheses `(h : P)`, whole-context automation tactics
      (`omega`, `simp`, `decide`, `grind`, etc.) may consume `h` from the local context without
      naming it, so only non-automated bodies flag those.
    """
    AUTOMATION_TACTICS = [
        "omega",
        "simp",
        "simpa",
        "nlinarith",
        "linarith",
        "ring",
        "decide",
        "bv_decide",
        "positivity",
        "norm_num",
        "auto",
        "duper",
        "aesop",
        "tauto",
        "trivial",
        "assumption",
        "exact_mod_cast",
        "simp_all",
        "grind",
    ]
    has_automation = any(
        re.search(rf"\b{re.escape(tactic)}\b", body) for tactic in AUTOMATION_TACTICS
    ) or ("unfold" in body)

    conclusion = _extract_conclusion(signature)
    binders = _extract_binders_list(signature)
    unused: list[str] = []

    for idx, b in enumerate(binders):
        b_type = b["type"]
        is_val = _is_value_type(b_type)
        for name in b["names"]:
            if name == "_":
                continue
            is_underscore = name.startswith("_")
            if b["bracket"] != "(" and not is_underscore:
                continue
            if len(name) == 1 and not is_val and not is_underscore:
                continue
            word_re = re.compile(rf"(?<![A-Za-z0-9_']){re.escape(name)}(?![A-Za-z0-9_'])")
            if word_re.search(conclusion):
                continue
            used_in_other = False
            for other_idx, other_b in enumerate(binders):
                if other_idx == idx:
                    continue
                if word_re.search(other_b["type"]):
                    used_in_other = True
                    break
            if used_in_other:
                continue
            if word_re.search(body):
                continue
            if is_underscore or is_val or not has_automation:
                unused.append(name)

    return unused


def _strip_lean_comments(lines: list[str]) -> list[str]:
    """Replace text inside Lean comments with spaces (preserving line
    numbers and column positions). Handles single-line `--` comments,
    block comments `/- ... -/`, and docstring blocks `/-- ... -/`.

    The Lean spec allows `/-` blocks to nest, but for the purposes of
    avoiding `@[simp]` false positives a single-level scanner is
    sufficient since the corpus does not nest comments inside docstrings.
    """
    out: list[str] = []
    in_block = False
    for raw in lines:
        chars = list(raw)
        i = 0
        n = len(chars)
        while i < n:
            if in_block:
                if i + 1 < n and chars[i] == "-" and chars[i + 1] == "/":
                    chars[i] = " "
                    chars[i + 1] = " "
                    in_block = False
                    i += 2
                    continue
                chars[i] = " "
                i += 1
                continue
            # Single-line comment: rest of line becomes whitespace
            if i + 1 < n and chars[i] == "-" and chars[i + 1] == "-":
                for j in range(i, n):
                    chars[j] = " "
                break
            # Start of block / docstring
            if i + 1 < n and chars[i] == "/" and chars[i + 1] == "-":
                in_block = True
                chars[i] = " "
                chars[i + 1] = " "
                i += 2
                continue
            i += 1
        out.append("".join(chars))
    return out


def find_simp_loops(text: str, theorem_blocks: list[dict]) -> list[dict]:
    """Detect `@[simp]` rewrite rules whose LHS head symbol re-appears in
    the RHS — a classic source of simp-set non-termination (W9 HITL B-1).

    Heuristic:
    1. Scan source for any `@[...simp...]` attribute marker (handles
       priorities, bundled attributes, pre/post arrows, and `@[simp ←]`).
    2. Pair each marker with the next theorem/lemma block on the same or
       a nearby (≤ 5 lines away) following line.
    3. Extract the conclusion of that block, split on the first top-level
       `=` or `↔`, identify the LHS head symbol, then check whether the
       same head symbol appears as a whole word in the RHS.

    The check is intentionally conservative — it only flags when the LHS
    head IS a real Lean identifier (alphabetic/underscore initial) and is
    distinct from the theorem name itself. Manual review is required for
    any hit.
    """
    findings: list[dict] = []
    lines = text.splitlines()

    # Strip Lean comments before scanning so docstrings that mention
    # `@[simp]` literally (e.g., in a "this is NOT @[simp]" note) don't
    # trigger false positives. We replace docstring/comment characters
    # with spaces (preserving line numbers and column positions).
    stripped_lines = _strip_lean_comments(lines)

    # Step 1: collect every `@[simp]`-bearing attribute line
    simp_marker_re = re.compile(r"@\[\s*([^\]]*)\]")
    simp_lines: list[tuple[int, str, str]] = []  # (1-based line, attr text, raw line)
    for idx, line in enumerate(stripped_lines, start=1):
        for m in simp_marker_re.finditer(line):
            attr = m.group(1)
            tokens = [t.strip() for t in attr.split(",") if t.strip()]
            head_tokens = [t.split()[0] if t.split() else "" for t in tokens]
            if "simp" in head_tokens:
                simp_lines.append((idx, attr, line))
                break  # one simp annotation per line is enough

    # Step 2: pair each simp marker with a theorem/lemma block
    by_start_line = {thm["line"]: thm for thm in theorem_blocks}
    for attr_line, _attr_text, attr_raw in simp_lines:
        target_thm = None

        # Same-line attribute: `@[simp] theorem foo : ...`
        # If a theorem keyword is already on this line, we ONLY accept the
        # match coming from `by_start_line[attr_line]`. Falling through to
        # the look-ahead would incorrectly bind this attribute to the next
        # theorem. (Bug fix surfaced by W9 HITL B-1 false positives.)
        same_line_thm = bool(re.search(r"(?:theorem|lemma)\s+\S+", attr_raw))
        if same_line_thm:
            target_thm = by_start_line.get(attr_line)
            if target_thm is None:
                continue  # parser missed this theorem; skip rather than misattribute

        # Otherwise look ahead a few lines for the next theorem block
        if target_thm is None:
            candidates = [t for t in theorem_blocks if t["line"] > attr_line]
            if candidates:
                nearest = min(candidates, key=lambda t: t["line"])
                if nearest["line"] - attr_line <= 5:
                    target_thm = nearest

        if target_thm is None:
            continue

        loop_detail = check_simp_lhs_in_rhs(target_thm["signature"], target_thm["name"])
        if loop_detail:
            findings.append(
                {
                    "type": "simp-loop-risk",
                    "severity": "P1",
                    "theorem": target_thm["name"],
                    "line": target_thm["line"],
                    "detail": loop_detail,
                }
            )

    return findings


def find_heartbeat_overrides(text: str, filepath: Path) -> list[dict]:
    """Detect `set_option maxHeartbeats N` (or `synthInstance.maxHeartbeats`)
    overrides that exceed sane review thresholds.

    Returns one finding per offending occurrence. The line number is the
    1-based line of the override in the file.

    Severity rules (W10 r27):
      * `maxHeartbeats N`, N > 1_000_000  → P1 (heartbeat-budget-excessive)
      * `maxHeartbeats 0`                  → P1 (heartbeat-budget-disabled)
      * `maxHeartbeats N`, 200_000 < N ≤ 1_000_000 → P2 (heartbeat-budget-elevated)

    `set_option maxHeartbeats N` *inside* a `set_option ... in` clause is
    detected the same way (the regex matches the option name and number).
    """
    findings = []
    pattern = re.compile(
        r"^\s*set_option\s+"
        r"(?P<opt>(?:synthInstance\.)?maxHeartbeats)\s+"
        r"(?P<n>\d+)\b"
    )
    for idx, line in enumerate(text.splitlines(), start=1):
        m = pattern.match(line)
        if not m:
            continue
        n = int(m.group("n"))
        opt = m.group("opt")
        if n == 0:
            findings.append(
                {
                    "type": "heartbeat-budget-disabled",
                    "severity": "P1",
                    "theorem": "(file-level)",
                    "line": idx,
                    "detail": (
                        f"`set_option {opt} 0` disables the elaborator safety net "
                        f"in {filepath.name}; never ship 0"
                    ),
                }
            )
        elif n > 1_000_000:
            findings.append(
                {
                    "type": "heartbeat-budget-excessive",
                    "severity": "P1",
                    "theorem": "(file-level)",
                    "line": idx,
                    "detail": (
                        f"`set_option {opt} {n}` exceeds 1_000_000 in "
                        f"{filepath.name}; almost always indicates a perf "
                        f"regression that should be tracked"
                    ),
                }
            )
        elif n > 200_000:
            findings.append(
                {
                    "type": "heartbeat-budget-elevated",
                    "severity": "P2",
                    "theorem": "(file-level)",
                    "line": idx,
                    "detail": (
                        f"`set_option {opt} {n}` is above the 200_000 default in "
                        f"{filepath.name}; consider proof split or term-mode hint"
                    ),
                }
            )
    return findings


def check_simp_lhs_in_rhs(signature: str, theorem_name: str) -> str | None:
    """Return a description if the LHS head symbol of the conclusion
    appears in the RHS, signalling a possible simp loop. Otherwise None.
    """
    conclusion = _extract_conclusion(signature)
    if not conclusion:
        return None

    eq = _find_top_level_eq(conclusion)
    if eq is None:
        return None
    idx, op = eq
    lhs = conclusion[:idx].strip()
    rhs = conclusion[idx + len(op) :].strip()
    if not lhs or not rhs:
        return None

    head = _extract_head_symbol(lhs)
    if not head:
        return None
    # Skip if head is the theorem name itself — circular by construction
    if head == theorem_name:
        return None
    # Skip operator-shaped heads (e.g. `=`, `+`, `≤`)
    if not re.match(r"^[A-Za-z_]", head):
        return None
    # Skip common Lean keywords that may appear at LHS head accidentally
    KEYWORDS = {"fun", "if", "then", "else", "let", "match", "with", "do"}
    if head in KEYWORDS:
        return None
    # Skip if head is a bound variable from the theorem signature.
    # Bound variables are introduced by `(name : ...)`, `{name : ...}`,
    # `[name : ...]` or `⦃name : ...⦄` binders; using one of them as
    # head is not a function-symbol rewrite, so simp cannot loop.
    if head in _bound_variable_names(signature):
        return None

    if re.search(r"(?<![A-Za-z0-9_])" + re.escape(head) + r"(?![A-Za-z0-9_])", rhs):
        # Skip structural recursion / homomorphism unfoldings where the LHS
        # has a compound argument `(a op b)` or `(ctor ...)` that strictly
        # decreases in every recursive call on the RHS.
        lhs_after_head = lhs[lhs.find(head) + len(head) :].strip()
        if "(" in lhs_after_head:
            return None
        return f"@[simp] LHS head `{head}` appears in RHS - potential rewrite loop"
    return None


def _bound_variable_names(signature: str) -> set[str]:
    """Collect identifier names introduced by binders in the signature.
    Handles `(x y z : T)`, `{x : T}`, `[inst : T]`, and `⦃a : T⦄` forms.
    """
    names: set[str] = set()
    # Match each binder group; capture the variable list before the colon.
    binder_re = re.compile(r"[\(\{\[⦃]\s*([^\):\}\]⦄]+?)\s*:\s*[^\)\}\]⦄]+[\)\}\]⦄]")
    for m in binder_re.finditer(signature):
        for tok in m.group(1).split():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
                names.add(tok)
    return names


def _extract_conclusion(signature: str) -> str:
    """Strip the leading `theorem foo` / `lemma foo` and binders, returning
    the conclusion type (the text after the first depth-0 `:` that isn't
    `:=`).
    """
    sig = signature
    m = re.match(
        r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
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
                break  # `:=` ends the signature without a colon-typed conclusion
            colon_pos = i
            break
        i += 1

    if colon_pos < 0:
        return ""
    conclusion = sig[colon_pos + 1 :]
    # Strip trailing `:= ...` or `:= by ...` if signature included it
    conclusion = re.sub(r":=.*$", "", conclusion, flags=re.DOTALL)
    return conclusion.strip()


def _find_top_level_eq(text: str) -> tuple[int, str] | None:
    """Locate the leftmost depth-0 `=` (not part of `:=`, `==`, `≤`, `≥`,
    `≠`, etc.) or `↔` in the text. Returns (index, operator) or None.
    """
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
        if text[i : i + 3] == "<->":
            return (i, "<->")
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


def _extract_head_symbol(lhs: str) -> str | None:
    """Pull the leftmost non-paren identifier from a LHS expression."""
    s = lhs.strip()
    # Strip outer parens that wrap the whole expression
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        balanced = True
        for j, c in enumerate(s):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0 and j < len(s) - 1:
                    balanced = False
                    break
        if balanced:
            s = s[1:-1].strip()
        else:
            break

    # First token (split on whitespace or dot, keeping namespaced heads)
    tok = re.split(r"[\s(){}\[\],]", s, maxsplit=1)[0]
    # Drop a `.` suffix used by dot notation like `Foo.bar baz`
    if "." in tok:
        tok = tok.split(".")[-1]
    if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
        return tok
    return None


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _structural_branch_points(body: str) -> int:
    """Count case-split / focusing structure in a tactic proof body.

    A heuristic proxy for "how decomposable" a long proof is.  Counts
    focus dots (`·`/`. `), `case`/`next` headers, pattern bullets (`| `),
    the `<;>` combinator, and the branch-introducing tactics
    `rcases`/`obtain`/`cases`/`induction`/`by_cases`/`match`.  Higher
    counts indicate many independent sub-goals — a natural extraction
    signal — whereas a flat `calc`/`simp` block scores near zero.
    """
    count = 0
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(("·", ". ")):
            count += 1
        if re.match(r"(case|next)\b", stripped):
            count += 1
        if stripped.startswith("| "):
            count += 1
    count += len(re.findall(r"<;>", body))
    count += len(
        re.findall(r"\b(?:rcases|obtain|cases|induction|by_cases|match)\b", body)
    )
    return count


def _reflexive_conclusion(conclusion: str) -> str | None:
    eq = _find_top_level_eq(conclusion)
    if eq is None:
        return None
    idx, op = eq
    lhs = _normalize_ws(conclusion[:idx])
    rhs = _normalize_ws(conclusion[idx + len(op) :])
    if lhs and lhs == rhs:
        return f"{lhs} {op} {rhs}"
    return None


def generate_report(
    results: list[dict], output: Path, excluded_dirs: list[str] | None = None
) -> None:
    """Generate Markdown quality report."""
    all_findings = []
    all_stats = []
    for r in results:
        all_findings.extend(r["findings"])
        all_stats.append(r["stats"])
    excluded_dirs = excluded_dirs or []

    total_thms = sum(s["theorem_count"] for s in all_stats)
    global_tactics = Counter()
    for s in all_stats:
        global_tactics += s["tactic_usage"]

    lines = [
        "# Proof Quality Analysis",
        "",
        "## Summary",
        f"- **Modules analyzed:** {len(all_stats)}",
        f"- **Theorems analyzed:** {total_thms}",
        f"- **Total findings:** {len(all_findings)}",
        f"- **P1 (important):** {sum(1 for f in all_findings if f['severity'] == 'P1')}",
        f"- **P2 (improvement):** {sum(1 for f in all_findings if f['severity'] == 'P2')}",
        f"- **P3 (style):** {sum(1 for f in all_findings if f['severity'] == 'P3')}",
        *(
            [
                f"- **Excluded dirs (vendored, style-gate exempt):** {', '.join(excluded_dirs)}"
            ]
            if excluded_dirs
            else []
        ),
        "",
        "## Tactic Usage (Global)",
        "",
        "| Tactic | Count | % |",
        "|---|---|---|",
    ]

    total_tactic_count = sum(global_tactics.values())
    for tactic, count in global_tactics.most_common(15):
        pct = count / total_tactic_count * 100 if total_tactic_count > 0 else 0
        lines.append(f"| {tactic} | {count} | {pct:.1f}% |")

    if all_findings:
        lines.extend(
            [
                "",
                "## Findings",
                "",
                "| Severity | Module | Theorem | Type | Detail |",
                "|---|---|---|---|---|",
            ]
        )
        for f in sorted(all_findings, key=lambda x: (x["severity"], x["theorem"])):
            lines.append(
                f"| {f['severity']} | — | {f['theorem']} | {f['type']} | {f['detail']} |"
            )

    lines.extend(
        [
            "",
            "---",
            "*Generated by proof_quality.py*",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Proof quality analysis")
    parser.add_argument(
        "--lean-dir",
        type=Path,
        default=Path("MyProject"),
        help="Directory containing .lean files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("proof_quality.md"),
        help="Output report path",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="DIR",
        help="Skip files under a directory with this name (relative to "
        "--lean-dir); repeatable. Intended for vendored code whose "
        "style quality is governed upstream — correctness gates "
        "(sorry/axiom audits) still cover it.",
    )
    args = parser.parse_args()

    results = []
    for f in sorted(args.lean_dir.rglob("*.lean")):
        rel = f.relative_to(args.lean_dir)
        if any(part in args.exclude_dir for part in rel.parts[:-1]):
            print(f"Skipping {rel} (excluded dir)")
            continue
        print(f"Analyzing {rel}...")
        result = analyze_module(f)
        results.append(result)
        findings = result["findings"]
        if findings:
            print(f"  {len(findings)} finding(s)")

    generate_report(results, args.output, args.exclude_dir)
    total = sum(len(r["findings"]) for r in results)
    print(f"\nTotal findings: {total}")
    print(f"Report: {args.output}")

    # Exit with error if P1 issues found
    p1_count = sum(1 for r in results for f in r["findings"] if f["severity"] == "P1")
    if p1_count > 0:
        print(f"\n{p1_count} P1 issue(s) found")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

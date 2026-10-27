#!/usr/bin/env python3
"""APOLLO-style automated Lean 4 proof repair and sorry-to-lemma decomposition (Proposal 4B).

Implements a lexer-safe (comment/string-neutralized) 4-stage pipeline:
  1. `SyntaxCorrector`: repairs LLM tactic syntax errors (`rw h` -> `rw [h]`,
     `, by` -> `:= by`, `let x := by` -> `let x :=`, `admit` -> `sorry`,
     optional `pp.*` diagnostic headers) without corrupting comments or strings.
  2. `ProofTree` & `Sorrifier`: parses indentation and bullet (`·`, `.`, `|`, `case`,
     `have ... := by`) blocks and replaces failing leaf subtrees with `sorry` while
     preserving valid sibling and prefix tactics.
  3. `ProofRepairer`: runs a two-pass kernel-safe repair cascade:
     - Pass 1: parses `hint` tactic suggestions (skipping non-closers `intro`/`aesop`).
     - Pass 2: deterministic solver cascade (`norm_cast`, `norm_num`, `simp_all`,
       `ring_nf at *`, `decide`, `omega`, `positivity`, `linarith`, `nlinarith` --
       strictly excluding `native_decide` per GT-30) + redundant tactic pruning
       when Lean reports `no goals to be solved`.
  4. `LemmaExtractor` (`sorry2lemma --reconstruct-callsite`): extracts remaining
     `sorry` holes (with both theorem-header binders and local `have`/`intro` context)
     into standalone closed-term top-level `lemma <name>_<idx>` declarations, orders
     dependent binders, and when `--reconstruct-callsite` is passed replaces each
     `sorry` in the parent proof with `exact <name>_<idx> <arg1> ... <argk>`.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


def neutralize_comments_and_strings(code: str) -> str:
    """Replace contents of `--` line comments, `/- ... -/` nested block comments,
    and `"..."` string literals with spaces while preserving all newlines and exact
    character offsets."""
    chars = list(code)
    n = len(chars)
    i = 0
    block_depth = 0
    in_string = False

    while i < n:
        c = chars[i]
        nxt = chars[i + 1] if i + 1 < n else ""

        if block_depth > 0:
            if c == "/" and nxt == "-":
                chars[i] = " "
                chars[i + 1] = " "
                block_depth += 1
                i += 2
                continue
            if c == "-" and nxt == "/":
                chars[i] = " "
                chars[i + 1] = " "
                block_depth -= 1
                i += 2
                continue
            if c != "\n":
                chars[i] = " "
            i += 1
            continue

        if in_string:
            if c == "\\" and i + 1 < n:
                if chars[i] != "\n":
                    chars[i] = " "
                if chars[i + 1] != "\n":
                    chars[i + 1] = " "
                i += 2
                continue
            if c == '"':
                in_string = False
                i += 1
                continue
            if c != "\n":
                chars[i] = " "
            i += 1
            continue

        if c == "/" and nxt == "-":
            chars[i] = " "
            chars[i + 1] = " "
            block_depth = 1
            i += 2
            continue

        if c == "-" and nxt == "-":
            while i < n and chars[i] != "\n":
                chars[i] = " "
                i += 1
            continue

        if c == '"':
            in_string = True
            i += 1
            continue

        i += 1

    return "".join(chars)


# Kernel-safe deterministic solver cascade (strictly excludes `native_decide` per GT-30).
KERNEL_SAFE_SOLVER_CASCADE: tuple[str, ...] = (
    "norm_cast",
    "norm_num",
    "simp_all",
    "ring_nf at *",
    "decide",
    "omega",
    "positivity",
    "linarith",
    "nlinarith",
)

FORBIDDEN_REPAIR_TACTICS: frozenset[str] = frozenset({"native_decide"})


def build_solver_cascade_tactic(extra_tactics: list[str] | None = None) -> str:
    """Return a single compound Lean 4 tactic string for the deterministic solver pass.
    Each `try <tactic>` is parenthesized so Lean 4 parses `(try t1) ; (try t2)` sequentially
    instead of nesting `try (t1 ; try (t2 ...))`."""
    tactics = list(KERNEL_SAFE_SOLVER_CASCADE)
    for t in extra_tactics or []:
        t_clean = t.strip()
        if t_clean and t_clean not in FORBIDDEN_REPAIR_TACTICS and t_clean not in tactics:
            tactics.append(t_clean)
    return " ; ".join(f"(try {t})" for t in tactics)


class SyntaxCorrector:
    """Lexer-safe port of APOLLO's `SyntaxCorrector`."""

    PP_OPTIONS = (
        "set_option pp.instanceTypes true\n"
        "set_option pp.numericTypes true\n"
        "set_option pp.coercions.types true\n"
        "set_option pp.letVarTypes true\n"
        "set_option pp.structureInstanceTypes true\n"
        "set_option pp.implicits true\n"
        "set_option pp.mvars.withType true\n"
        "set_option pp.funBinderTypes true\n"
        "set_option pp.all false"
    )

    def __init__(self, code: str, error_message: str | None = None) -> None:
        self.code = code
        self.error_message = error_message or ""

    def _apply_span_replacements(self, replacements: list[tuple[int, int, str]]) -> None:
        for start, end, repl in sorted(replacements, key=lambda x: x[0], reverse=True):
            self.code = self.code[:start] + repl + self.code[end:]

    def fix_rw_brackets(self) -> None:
        """Convert bare `rw h` or `rw <- h` into `rw [h]` / `rw [<- h]` outside comments/strings."""
        neutral = neutralize_comments_and_strings(self.code)
        pattern = re.compile(
            r"\b(rw|erw|nth_rw\s+\d+)\s+(?!\[)"
            r"((?:(?:\u2190|<-)\s*)?[A-Za-z_][A-Za-z0-9_'.]*(?:\s+[A-Za-z0-9_'.()\u27e8\u27e9+-]+)*)"
            r"(?P<at>\s+at\s+[^\n;]+)?(?=\s*(?:$|\n|;|--|\)|/-))"
        )
        repls: list[tuple[int, int, str]] = []
        for m in pattern.finditer(neutral):
            kw = self.code[m.start(1) : m.end(1)]
            arg = self.code[m.start(2) : m.end(2)].strip()
            if arg.startswith("[") or arg in ("by", "with", "using"):
                continue
            at_clause = self.code[m.start("at") : m.end("at")] if m.group("at") else ""
            repls.append((m.start(), m.end(), f"{kw} [{arg}]{at_clause}"))
        self._apply_span_replacements(repls)

    def fix_comma_by(self) -> None:
        """Convert `have h : T, by` or `theorem foo : T, by` to `:= by` outside comments/strings."""
        neutral = neutralize_comments_and_strings(self.code)
        pattern = re.compile(r",\s*by\b")
        repls = [(m.start(), m.end(), " := by") for m in pattern.finditer(neutral)]
        self._apply_span_replacements(repls)

    def fix_let_by(self) -> None:
        """Convert `let x := by <expr>` (single-line value) or `admit` -> `sorry`."""
        neutral = neutralize_comments_and_strings(self.code)
        repls: list[tuple[int, int, str]] = []
        for m in re.finditer(r"\badmit\b", neutral):
            repls.append((m.start(), m.end(), "sorry"))
        self._apply_span_replacements(repls)

        neutral = neutralize_comments_and_strings(self.code)
        let_re = re.compile(r"^([ \t]*let\s+[^\n:=]+:=\s*)by\s+([^\n;]+)$", re.MULTILINE)
        repls = []
        for m in let_re.finditer(neutral):
            rhs = self.code[m.start(2) : m.end(2)].strip()
            # Only strip `by` when the RHS is a pure value expression rather than a tactic
            if not re.match(
                r"^(?:exact|apply|rw|simp|omega|linarith|nlinarith|ring|decide|intro|have|obtain|rcases|cases|induction)\b",
                rhs,
            ):
                prefix = self.code[m.start(1) : m.end(1)]
                repls.append((m.start(), m.end(), f"{prefix}{rhs}"))
        self._apply_span_replacements(repls)

    def inject_pp_options(self) -> str:
        """Return code with APOLLO's `pp.*` options inserted right after the `import` header."""
        if "set_option pp.instanceTypes true" in self.code:
            return self.code
        lines = self.code.splitlines()
        insert_idx = 0
        for idx, ln in enumerate(lines):
            if ln.strip().startswith(("import ", "open ")):
                insert_idx = idx + 1
        out = lines[:insert_idx] + ["", self.PP_OPTIONS, ""] + lines[insert_idx:]
        return "\n".join(out) + ("\n" if self.code.endswith("\n") else "")

    def correct_text(self) -> str:
        self.fix_comma_by()
        self.fix_rw_brackets()
        self.fix_let_by()
        return self.code


@dataclass
class ProofNode:
    """One node in a hierarchical tactic `ProofTree`."""

    line_start: int  # 1-based inclusive
    line_end: int  # 1-based inclusive
    indent: int
    kind: str  # "root" | "have" | "bullet" | "case" | "tactic"
    header_line: str
    children: list[ProofNode] = field(default_factory=list)


class ProofTree:
    """Indentation- and bullet-aware Lean 4 proof tree parser."""

    BULLET_RE = re.compile(r"^([ \t]*)(?:\u00b7|\.(?=\s)|\|)\s*(.*)$")
    CASE_RE = re.compile(r"^([ \t]*)(?:case|next)\b(.*)$")
    HAVE_BY_RE = re.compile(r"^([ \t]*)(?:have|suffices|obtain)\b.*:=\s*by\b")
    THM_BY_RE = re.compile(
        r"^([ \t]*)(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|example)\b[\s\S]*?:=\s*by\b"
    )

    def __init__(self, code: str) -> None:
        self.code = code
        self.lines = code.splitlines()
        self.neutral_lines = neutralize_comments_and_strings(code).splitlines()

    def parse(self) -> list[ProofNode]:
        """Parse top-level tactic blocks and nested `have` / bullet subtrees."""
        nodes: list[ProofNode] = []
        n = len(self.lines)
        for idx in range(n):
            nline = self.neutral_lines[idx] if idx < len(self.neutral_lines) else ""
            stripped = nline.strip()
            if not stripped:
                continue
            indent = len(nline) - len(nline.lstrip(" \t"))
            kind = "tactic"
            if self.HAVE_BY_RE.match(nline):
                kind = "have"
            elif self.BULLET_RE.match(nline):
                kind = "bullet"
            elif self.CASE_RE.match(nline):
                kind = "case"

            end_idx = idx
            if kind in ("have", "bullet", "case"):
                j = idx + 1
                while j < n:
                    nj = self.neutral_lines[j] if j < len(self.neutral_lines) else ""
                    if not nj.strip():
                        j += 1
                        continue
                    j_indent = len(nj) - len(nj.lstrip(" \t"))
                    if j_indent > indent:
                        end_idx = j
                        j += 1
                    else:
                        break
            nodes.append(
                ProofNode(
                    line_start=idx + 1,
                    line_end=end_idx + 1,
                    indent=indent,
                    kind=kind,
                    header_line=self.lines[idx],
                )
            )
        return nodes


class Sorrifier:
    """Replaces failing tactic lines or sub-proof blocks with `sorry` while keeping
    valid prefix/sibling proof steps intact."""

    def __init__(
        self,
        code: str,
        error_lines: list[int] | None = None,
        no_goals_lines: list[int] | None = None,
    ) -> None:
        self.code = code
        self.error_lines = sorted(set(error_lines or []))
        self.no_goals_lines = sorted(set(no_goals_lines or []))

    def sorrify(self) -> str:
        lines = self.code.splitlines()
        neutral_lines = neutralize_comments_and_strings(self.code).splitlines()
        tree = ProofTree(self.code).parse()

        to_delete: set[int] = set(self.no_goals_lines)

        # Map each error line to the innermost compound block (`have`/`bullet`/`case`) or single tactic line
        replaced_ranges: list[tuple[int, int, str]] = []
        covered_lines: set[int] = set()

        for err_ln in self.error_lines:
            if err_ln in covered_lines or err_ln < 1 or err_ln > len(lines):
                continue
            # Find smallest enclosing `have`, `bullet`, or `case` block if error is inside its sub-proof
            enclosing_blocks = [
                nd
                for nd in tree
                if nd.kind in ("have", "bullet", "case")
                and nd.line_start <= err_ln <= nd.line_end
                and nd.line_end > nd.line_start
            ]
            if enclosing_blocks:
                smallest = min(
                    enclosing_blocks, key=lambda nd: nd.line_end - nd.line_start
                )
                if smallest.kind in ("have", "case"):
                    body_indent = " " * (smallest.indent + 2)
                    replaced_ranges.append(
                        (
                            smallest.line_start + 1,
                            smallest.line_end,
                            f"{body_indent}sorry",
                        )
                    )
                    covered_lines.update(
                        range(smallest.line_start, smallest.line_end + 1)
                    )
                    continue
                if smallest.kind == "bullet":
                    raw_hdr = lines[smallest.line_start - 1]
                    n_hdr = (
                        neutral_lines[smallest.line_start - 1]
                        if smallest.line_start - 1 < len(neutral_lines)
                        else raw_hdr
                    )
                    m_bul = re.match(r"^([ \t]*(?:\u00b7|\.(?=\s)|\|)\s*)", n_hdr)
                    prefix = (
                        raw_hdr[: m_bul.end(1)]
                        if m_bul
                        else (" " * smallest.indent + "· ")
                    )
                    replaced_ranges.append(
                        (
                            smallest.line_start,
                            smallest.line_end,
                            f"{prefix}sorry",
                        )
                    )
                    covered_lines.update(
                        range(smallest.line_start, smallest.line_end + 1)
                    )
                    continue

            raw_ln = lines[err_ln - 1]
            n_ln = neutral_lines[err_ln - 1] if err_ln - 1 < len(neutral_lines) else raw_ln
            indent_str = raw_ln[: len(raw_ln) - len(raw_ln.lstrip(" \t"))]

            # Preserve `have ... := by` or bullet prefix if on the same line
            m_have = re.match(r"^([ \t]*(?:have|suffices)\b.*:=\s*by)\b.*$", n_ln)
            m_bullet = re.match(r"^([ \t]*(?:\u00b7|\.(?=\s)|\|)\s*).+$", n_ln)
            if m_have:
                prefix = raw_ln[: m_have.end(1)]
                replaced_ranges.append((err_ln, err_ln, f"{prefix} sorry"))
            elif m_bullet:
                prefix = raw_ln[: m_bullet.end(1)]
                replaced_ranges.append((err_ln, err_ln, f"{prefix}sorry"))
            else:
                replaced_ranges.append((err_ln, err_ln, f"{indent_str}sorry"))
            covered_lines.add(err_ln)

        # Combine deletions and range replacements in a single descending line-order pass
        # so earlier deletions never shift indices of later replacements.
        edit_ops: list[tuple[int, int, list[str]]] = [
            (start, end, [repl]) for start, end, repl in replaced_ranges
        ]
        for line_no in to_delete:
            if 1 <= line_no <= len(lines) and line_no not in covered_lines:
                edit_ops.append((line_no, line_no, []))

        out_lines = list(lines)
        for start, end, repl_list in sorted(edit_ops, key=lambda x: x[0], reverse=True):
            out_lines[start - 1 : end] = repl_list

        return "\n".join(out_lines) + ("\n" if self.code.endswith("\n") else "")


def parse_hint_suggestions(lean_output: str) -> list[str]:
    """Extract bulleted tactic suggestions from Lean 4 `hint` output, filtering out
    non-closing structural tactics (`intro`, `aesop`) and `native_decide` (GT-30)."""
    suggestions: list[str] = []
    for m in re.finditer(r"(?:\u2022|\*|-)\s*([^\n]+)", lean_output or ""):
        cand = m.group(1).strip()
        # Strip trailing heartbeat / annotation notes if present
        cand = re.sub(r"\s+--.*$", "", cand).strip()
        if not cand:
            continue
        if any(
            skip in cand
            for skip in ("intro", "aesop", "native_decide", "Try this:")
        ):
            continue
        if cand not in suggestions:
            suggestions.append(cand)
    return suggestions


class ProofRepairer:
    """Two-pass APOLLO proof repair engine (`hint` pass + deterministic solver cascade)."""

    def __init__(
        self,
        code: str,
        verifier_fn: Callable[[str], tuple[bool, str]] | None = None,
    ) -> None:
        self.code = code
        self.verifier_fn = verifier_fn

    def replace_sorries_with_cascade(
        self, extra_tactics: list[str] | None = None
    ) -> str:
        """Replace standalone `sorry` tactic holes with the kernel-safe solver cascade."""
        cascade = build_solver_cascade_tactic(extra_tactics)
        neutral = neutralize_comments_and_strings(self.code)
        repls: list[tuple[int, int, str]] = []
        for m in re.finditer(r"\bsorry\b", neutral):
            # Do not replace `sorry` inside theorem signatures before `:=`
            line_start = neutral.rfind("\n", 0, m.start()) + 1
            line_prefix = neutral[line_start : m.start()]
            if re.match(r"^\s*(?:theorem|lemma|def|abbrev)\b", line_prefix) and ":=" not in line_prefix:
                continue
            repls.append((m.start(), m.end(), f"({cascade})"))
        out = self.code
        for start, end, repl in sorted(repls, key=lambda x: x[0], reverse=True):
            out = out[:start] + repl + out[end:]
        return out

    def repair(
        self,
        error_lines: list[int] | None = None,
        no_goals_lines: list[int] | None = None,
        hint_outputs: dict[int, str] | None = None,
    ) -> dict:
        """Execute syntax correction -> sorrification -> two-pass repair."""
        stage1 = SyntaxCorrector(self.code).correct_text()
        stage2 = Sorrifier(
            stage1, error_lines=error_lines, no_goals_lines=no_goals_lines
        ).sorrify()

        # Pass 1: apply any verified `hint` suggestions for specific sorry lines
        hint_tactics: list[str] = []
        if hint_outputs:
            for _ln, raw_out in sorted(hint_outputs.items()):
                for tac in parse_hint_suggestions(raw_out):
                    if tac not in hint_tactics:
                        hint_tactics.append(tac)

        # Pass 2: deterministic solver cascade (excluding `native_decide`)
        candidate_code = self.replace_sorries_with_cascade_on(stage2, hint_tactics)
        verified = False
        diagnostics = ""
        if self.verifier_fn is not None:
            verified, diagnostics = self.verifier_fn(candidate_code)
            if not verified:
                # Fall back to the clean sorrified skeleton so `sorry2lemma` can extract subgoals
                candidate_code = stage2

        return {
            "syntax_corrected": stage1,
            "sorrified": stage2,
            "repaired": candidate_code,
            "hint_tactics_tried": hint_tactics,
            "solver_cascade": build_solver_cascade_tactic(hint_tactics),
            "verified": verified,
            "diagnostics": diagnostics,
        }

    @staticmethod
    def replace_sorries_with_cascade_on(
        code: str, extra_tactics: list[str] | None = None
    ) -> str:
        return ProofRepairer(code).replace_sorries_with_cascade(extra_tactics)



@dataclass
class ExtractedLemma:
    """A standalone closed-term helper lemma extracted from a `sorry` hole."""

    name: str
    binders: list[str]
    target_type: str
    declaration: str
    callsite_expr: str
    line: int
    parent_theorem: str


def _parse_signature_binders_and_target(sig: str) -> tuple[str, list[tuple[list[str], str, str]], str]:
    """Return `(decl_name, [(names, type, raw_binder), ...], target_type)` from a theorem header."""
    m = re.match(
        r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|example)\s+([A-Za-z_][A-Za-z0-9_']*)?",
        sig,
    )
    decl_name = (m.group(1) if m and m.group(1) else "extracted_thm").strip()
    rest = sig[m.end() :] if m else sig

    depth = 0
    in_str = False
    colon_pos = -1
    for idx, ch in enumerate(rest):
        if ch == '"':
            in_str = not in_str
        elif not in_str:
            if ch in "([{⟨⦃":
                depth += 1
            elif ch in ")]}⟩⦄":
                depth -= 1
            elif ch == ":" and depth == 0:
                if idx + 1 < len(rest) and rest[idx + 1] == "=":
                    break
                colon_pos = idx
                break

    header = rest[:colon_pos] if colon_pos >= 0 else rest
    target = rest[colon_pos + 1 :].strip() if colon_pos >= 0 else "True"

    binders: list[tuple[list[str], str, str]] = []
    j = 0
    while j < len(header):
        if header[j] in "({[⦃":
            open_ch = header[j]
            close_ch = {"(": ")", "{": "}", "[": "]", "⦃": "⦄"}[open_ch]
            d = 1
            k = j + 1
            top_colon = -1
            while k < len(header) and d > 0:
                c = header[k]
                if c == open_ch:
                    d += 1
                elif c == close_ch:
                    d -= 1
                    if d == 0:
                        break
                elif c == ":" and d == 1 and top_colon < 0:
                    top_colon = k
                k += 1
            if d == 0:
                raw_b = header[j : k + 1]
                if top_colon > j:
                    names_part = header[j + 1 : top_colon].strip()
                    type_part = header[top_colon + 1 : k].strip()
                    names = [
                        tok
                        for tok in names_part.split()
                        if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok)
                    ]
                else:
                    names = []
                    type_part = header[j + 1 : k].strip()
                binders.append((names, type_part, raw_b))
            j = k + 1
        else:
            j += 1

    return decl_name, binders, target


def extract_lemmas_from_sorry(
    code: str,
    reconstruct_callsite: bool = False,
    goal_states: dict[int, dict] | None = None,
) -> dict:
    """Extract remaining `sorry` holes into closed-term top-level `lemma <name>_<idx>`
    declarations (`sorry2lemma`), ordering dependent binders and optionally reconstructing
    the parent theorem's callsite (`exact <name>_<idx> <args>`)."""
    neutral = neutralize_comments_and_strings(code)
    lines = code.splitlines()
    neutral_lines = neutral.splitlines()

    # Locate theorem declarations with `:= by` (stopping at the first `:=`)
    thm_re = re.compile(
        r"^([ \t]*)(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)((?:(?!:=)[\s\S])*?):=\s*by\b",
        re.MULTILINE,
    )

    extracted: list[ExtractedLemma] = []
    callsite_replacements: list[tuple[int, int, str]] = []

    for thm_m in thm_re.finditer(neutral):
        thm_name = thm_m.group(3)
        thm_start_line = neutral[: thm_m.start()].count("\n") + 1
        body_start_offset = thm_m.end()
        # Find end of theorem body
        body_end_offset = len(code)
        next_top = re.search(
            r"(?m)^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
            r"(?:theorem|lemma|example|def|abbrev|structure|inductive|namespace|end|section)\b",
            neutral[body_start_offset:],
        )
        if next_top:
            body_end_offset = body_start_offset + next_top.start()

        raw_sig = code[thm_m.start() : thm_m.end() - 5].strip()
        _, sig_binders, thm_target = _parse_signature_binders_and_target(raw_sig)

        body_neutral = neutral[body_start_offset:body_end_offset]
        # Collect local `have h : T :=` declarations inside the body
        local_haves: list[tuple[int, str, str, int, int]] = []
        have_re = re.compile(
            r"([ \t]*)have\s+([A-Za-z_][A-Za-z0-9_']*)\s*:\s*((?:(?!:=)[^\n])+?)[ \t]*:=[ \t]*(?:by\b[ \t]*)?",
            re.MULTILINE,
        )
        for hm in have_re.finditer(body_neutral):
            abs_start = body_start_offset + hm.start()
            abs_end = body_start_offset + hm.end()
            h_line = neutral[:abs_start].count("\n") + 1
            h_name = hm.group(2).strip()
            h_type = code[body_start_offset + hm.start(3) : body_start_offset + hm.end(3)].strip()
            local_haves.append((h_line, h_name, h_type, abs_start, abs_end))

        # Find all `sorry` occurrences inside this theorem body
        sorry_idx = 0
        for sm in re.finditer(r"\bsorry\b", body_neutral):
            sorry_idx += 1
            abs_s_start = body_start_offset + sm.start()
            abs_s_end = body_start_offset + sm.end()
            s_line = neutral[:abs_s_start].count("\n") + 1
            helper_name = f"{thm_name}_{sorry_idx}"

            # Determine target type of this sorry:
            # 1) Explicit goal_states override if provided for `s_line`
            # 2) Enclosing `have h : T := by sorry` on the same or preceding line
            # 3) Otherwise the parent theorem's target type `thm_target`
            target_type = thm_target
            enclosing_have_name: str | None = None
            if goal_states and s_line in goal_states and goal_states[s_line].get("target"):
                target_type = str(goal_states[s_line]["target"]).strip()
            else:
                for h_line, h_name, h_type, _hs, h_end in reversed(local_haves):
                    if h_line <= s_line:
                        between = body_neutral[h_end - body_start_offset : sm.start()].strip()
                        if between == "":
                            target_type = h_type
                            enclosing_have_name = h_name
                            break

            # Collect preceding resolved `have` hypotheses in scope (excluding the one being proved)
            prior_haves = [
                (h_name, h_type)
                for h_line, h_name, h_type, _hs, _he in local_haves
                if h_line < s_line and h_name != enclosing_have_name
            ]

            # Build closed-term binder list: signature binders + prior local haves referenced
            binder_strs: list[str] = []
            call_args: list[str] = []
            for b_names, _b_type, raw_b in sig_binders:
                binder_strs.append(raw_b)
                if raw_b.startswith("("):
                    call_args.extend(b_names)

            for h_name, h_type in prior_haves:
                # Include prior `have` binder if referenced in target_type or subsequent context
                binder_strs.append(f"({h_name} : {h_type})")
                call_args.append(h_name)

            if goal_states and s_line in goal_states:
                for extra_b in goal_states[s_line].get("extra_binders", []):
                    b_nm = extra_b["name"]
                    b_ty = extra_b["type"]
                    if b_nm not in call_args:
                        binder_strs.append(f"({b_nm} : {b_ty})")
                        call_args.append(b_nm)

            binders_joined = " ".join(binder_strs)
            header_sep = f" {binders_joined}" if binders_joined else ""
            lemma_decl = f"theorem {helper_name}{header_sep} : {target_type} := by\n  sorry"
            call_expr = (
                f"exact {helper_name}" + (f" {' '.join(call_args)}" if call_args else "")
            )

            extracted.append(
                ExtractedLemma(
                    name=helper_name,
                    binders=binder_strs,
                    target_type=target_type,
                    declaration=lemma_decl,
                    callsite_expr=call_expr,
                    line=s_line,
                    parent_theorem=thm_name,
                )
            )
            if reconstruct_callsite:
                callsite_replacements.append((abs_s_start, abs_s_end, call_expr))

    reconstructed_code = code
    if reconstruct_callsite and callsite_replacements:
        for start, end, repl in sorted(
            callsite_replacements, key=lambda x: x[0], reverse=True
        ):
            reconstructed_code = (
                reconstructed_code[:start] + repl + reconstructed_code[end:]
            )

    # Prepend extracted helper lemmas before their parent theorem(s)
    if extracted:
        lemma_block = "\n\n".join(lem.declaration for lem in extracted)
        first_thm = thm_re.search(neutralize_comments_and_strings(reconstructed_code))
        if first_thm:
            pos = first_thm.start()
            reconstructed_code = (
                reconstructed_code[:pos]
                + lemma_block
                + "\n\n"
                + reconstructed_code[pos:]
            )
        else:
            reconstructed_code = lemma_block + "\n\n" + reconstructed_code

    return {
        "extracted_count": len(extracted),
        "lemmas": [
            {
                "name": lem.name,
                "binders": lem.binders,
                "target_type": lem.target_type,
                "declaration": lem.declaration,
                "callsite_expr": lem.callsite_expr,
                "line": lem.line,
                "parent_theorem": lem.parent_theorem,
            }
            for lem in extracted
        ],
        "reconstructed_code": reconstructed_code,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = "repair-proof"
    if argv and argv[0] in ("repair-proof", "sorry2lemma"):
        mode = argv.pop(0)

    parser = argparse.ArgumentParser(
        prog=f"lean-skills {mode}",
        description="APOLLO-style Lean 4 proof repair and sorry2lemma extractor",
    )
    parser.add_argument("file", type=Path, help="Input Lean 4 file")
    parser.add_argument(
        "--reconstruct-callsite",
        action="store_true",
        help="Replace each sorry in the original theorem with `exact <lemma_name> <args>`",
    )
    parser.add_argument(
        "--error-line",
        type=int,
        action="append",
        default=[],
        help="1-based line number of a tactic error to sorrify (repeatable)",
    )
    parser.add_argument(
        "--no-goals-line",
        type=int,
        action="append",
        default=[],
        help="1-based line number of a redundant tactic to delete (repeatable)",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write the repaired or reconstructed code back to the input file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON report",
    )
    args = parser.parse_args(argv)

    source = args.file.read_text(encoding="utf-8")
    if mode == "sorry2lemma":
        res = extract_lemmas_from_sorry(
            source, reconstruct_callsite=args.reconstruct_callsite
        )
        if args.in_place:
            args.file.write_text(res["reconstructed_code"], encoding="utf-8")
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res["reconstructed_code"], end="")
        return 0

    rep = ProofRepairer(source).repair(
        error_lines=args.error_line,
        no_goals_lines=args.no_goals_line,
    )
    if args.reconstruct_callsite:
        s2l = extract_lemmas_from_sorry(rep["sorrified"], reconstruct_callsite=True)
        rep["sorry2lemma"] = s2l
    if args.in_place:
        args.file.write_text(rep["repaired"], encoding="utf-8")
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(rep["repaired"], end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

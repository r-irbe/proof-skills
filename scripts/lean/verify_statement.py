#!/usr/bin/env python3
"""Statement-preservation kernel sandbox (`verify-statement`) and fast `<5ms` header check (`validate-patch`) (Proposals 7A & 7B).

Implements two complementary statement-integrity gates:
  1. `validate-patch` (`AI4Math-Lean-Agents` fast regex/lexer gate, `<5ms`):
     Verifies that a candidate file preserves the exact `import`, `open`, `variable`,
     and theorem signature header up to `:= by` (modulo comments/whitespace inside proof
     bodies) with zero forbidden axioms/escape commands.
  2. `verify-statement` (`rocq-mcp` `Module M.` Lean 4 `namespace Candidate ... end Candidate`
     definitional equality sandbox + `MenTaL` concept-symbol drift audit `2604.01483`):
     - Neutralizes comments and strings before scanning for forbidden escape tokens
       (`axiom`, `sorry`, `admit`, `unsafe`, `implemented_by`, `csimp`, `extern`,
       `native_decide`, premature `end Candidate`, macro/notation overrides).
     - Verifies `MenTaL` concept-symbol preservation: every domain constant/type symbol
       in the specification theorem signature must be preserved in the candidate theorem
       signature without silent symbol drift or constant substitution.
     - Emits a self-contained Lean 4 sandbox harness that hoists shared definitions from
       `<spec.lean>`, strips duplicate/decoy definitions from `<candidate.lean>`, wraps the
       candidate theorem inside `namespace Candidate ... end Candidate`, and checks
       definitional type equality via `example : @SpecType = @Candidate.ThmType := rfl`
       plus `#print axioms Candidate.<thm>`.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from apollo_repair import neutralize_comments_and_strings

FORBIDDEN_CANDIDATE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("SORRY_OR_ADMIT", re.compile(r"\b(?:sorry|admit)\b")),
    ("AXIOM_DECLARATION", re.compile(r"\baxiom\b")),
    ("UNSAFE_OR_PARTIAL", re.compile(r"\b(?:unsafe|partial)\b")),
    (
        "COMPILER_TRUST_ESCAPE",
        re.compile(r"\b(?:implemented_by|csimp|extern| lcProof)\b"),
    ),
    ("NATIVE_DECIDE", re.compile(r"\bnative_decide\b")),
    ("NAMESPACE_ESCAPE", re.compile(r"\bend\s+Candidate\b")),
    (
        "NOTATION_OR_MACRO_OVERRIDE",
        re.compile(r"\b(?:local\s+notation|scoped\s+notation|macro_rules|elab_rules|notation)\b"),
    ),
]

ALLOWED_STANDARD_AXIOMS: frozenset[str] = frozenset(
    {"propext", "Classical.choice", "Quot.sound"}
)

LEAN_BUILTIN_TOKENS: frozenset[str] = frozenset(
    {
        "theorem",
        "lemma",
        "example",
        "def",
        "abbrev",
        "private",
        "protected",
        "public",
        "scoped",
        "noncomputable",
        "by",
        "fun",
        "forall",
        "exists",
        "if",
        "then",
        "else",
        "let",
        "in",
        "have",
        "show",
        "from",
        "match",
        "with",
        "do",
        "Type",
        "Sort",
        "Prop",
        "true",
        "false",
    }
)


def _extract_theorem_signature(code: str, target_name: str | None = None) -> dict | None:
    """Extract `(name, full_sig, header_before_decl, target_type, binders_raw)` for `target_name`
    (or the first theorem/lemma when `target_name` is None)."""
    neutral = neutralize_comments_and_strings(code)
    decl_re = re.compile(
        r"^([ \t]*)(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)",
        re.MULTILINE,
    )
    m = None
    first_m = None
    for cand_m in decl_re.finditer(neutral):
        if first_m is None:
            first_m = cand_m
        if target_name is None or cand_m.group(3) == target_name:
            m = cand_m
            break
    if m is None:
        return None
    name = m.group(3)
    start_pos = m.start()
    first_start_pos = first_m.start() if first_m else start_pos
    rest_neutral = neutral[m.end() :]

    depth = 0
    in_str = False
    assign_pos = -1
    top_colon_pos = -1
    i = 0
    while i < len(rest_neutral):
        c = rest_neutral[i]
        if c == '"':
            in_str = not in_str
        elif not in_str:
            if c in "([{⟨⦃":
                depth += 1
            elif c in ")]}⟩⦄":
                depth -= 1
            elif c == ":" and depth == 0:
                if i + 1 < len(rest_neutral) and rest_neutral[i + 1] == "=":
                    assign_pos = i
                    break
                if top_colon_pos < 0:
                    top_colon_pos = i
        i += 1

    if assign_pos < 0:
        return None

    sig_end = m.end() + assign_pos
    full_sig = code[start_pos:sig_end].strip()
    neutral_sig = neutral[start_pos:sig_end].strip()
    # Normalize `lemma <name>` vs `theorem <name>` for signature comparison
    neutral_sig_norm = re.sub(
        r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*(?:theorem|lemma)\b",
        "theorem",
        neutral_sig,
    )
    binders_raw = (
        code[m.end() : m.end() + top_colon_pos].strip()
        if top_colon_pos >= 0
        else ""
    )
    target_type = (
        code[m.end() + top_colon_pos + 1 : sig_end].strip()
        if top_colon_pos >= 0
        else ""
    )
    return {
        "name": name,
        "start_pos": start_pos,
        "first_decl_pos": first_start_pos,
        "sig_end": sig_end,
        "full_sig": full_sig,
        "neutral_sig": neutral_sig_norm,
        "binders_raw": binders_raw,
        "target_type": target_type,
        "header_prefix": neutral[:first_start_pos].strip(),
    }


def _extract_first_theorem_signature(code: str) -> dict | None:
    return _extract_theorem_signature(code, target_name=None)


def _extract_bound_names(binders_raw: str) -> set[str]:
    names: set[str] = set()
    for m in re.finditer(r"[\(\{\[⦃]\s*([^\):\}\]⦄]+?)\s*:\s*[^\)\}\]⦄]+[\)\}\]⦄]", binders_raw):
        for tok in m.group(1).split():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
                names.add(tok)
    return names


def _extract_explicit_binder_names(binders_raw: str) -> list[str]:
    """Return ordered explicit `(x y : T)` binder variable names for applying `Candidate.<thm>`."""
    names: list[str] = []
    i = 0
    n = len(binders_raw)
    while i < n:
        ch = binders_raw[i]
        if ch in "({[⦃":
            close_ch = {"(": ")", "{": "}", "[": "]", "⦃": "⦄"}[ch]
            d = 1
            j = i + 1
            top_colon = -1
            while j < n and d > 0:
                if binders_raw[j] == ch:
                    d += 1
                elif binders_raw[j] == close_ch:
                    d -= 1
                    if d == 0:
                        break
                elif binders_raw[j] == ":" and d == 1 and top_colon < 0:
                    top_colon = j
                j += 1
            if d == 0 and ch == "(" and top_colon > i:
                lhs = binders_raw[i + 1 : top_colon].strip()
                for tok in lhs.split():
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
                        names.append(tok)
            i = j + 1
        else:
            i += 1
    return names


def extract_concept_symbols(signature_info: dict) -> set[str]:
    """Extract domain/concept constant symbols (`MenTaL` `2604.01483`) from a theorem signature,
    excluding bound variable names and Lean keywords."""
    bound = _extract_bound_names(signature_info["binders_raw"])
    bound.add(signature_info["name"])
    body_text = signature_info["binders_raw"] + " " + signature_info["target_type"]
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_'.]*\b", body_text))
    return {
        tok
        for tok in tokens
        if tok not in bound
        and tok not in LEAN_BUILTIN_TOKENS
        and not tok.isdigit()
    }


def scan_forbidden_constructs(candidate_code: str) -> list[dict]:
    """Scan comment/string-neutralized candidate code for forbidden escape constructs."""
    neutral = neutralize_comments_and_strings(candidate_code)
    violations: list[dict] = []
    for code_name, rx in FORBIDDEN_CANDIDATE_PATTERNS:
        for m in rx.finditer(neutral):
            line = neutral[: m.start()].count("\n") + 1
            violations.append(
                {
                    "code": code_name,
                    "token": m.group(0),
                    "line": line,
                }
            )
    return violations


def _extract_top_level_defs(preamble_neutral: str) -> dict[str, str]:
    """Extract `{def_name: normalized_full_block}` for all `def`/`abbrev`/`structure`/`inductive`
    blocks in `preamble_neutral` (supporting multi-line definitions)."""
    lines = preamble_neutral.splitlines()
    def_re = re.compile(
        r"^[ \t]*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(def|abbrev|structure|inductive)\s+([A-Za-z_][A-Za-z0-9_']*)\b"
    )
    top_re = re.compile(
        r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|example|def|abbrev|structure|inductive|namespace|end|section)\b"
    )
    defs: dict[str, str] = {}
    i = 0
    n = len(lines)
    while i < n:
        m = def_re.match(lines[i])
        if not m:
            i += 1
            continue
        dname = m.group(2)
        block_lines = [lines[i]]
        j = i + 1
        while j < n:
            ln = lines[j]
            if ln and ln[0] not in (" ", "\t") and top_re.match(ln):
                break
            block_lines.append(ln)
            j += 1
        defs[dname] = " ".join("\n".join(block_lines).split())
        i = j
    return defs


def validate_patch(spec_code: str, candidate_code: str) -> dict:
    """Fast `<5ms` header and statement integrity check (`AI4Math-Lean-Agents` pattern).

    Verifies:
      1. Zero forbidden escape constructs (`sorry`, `axiom`, `native_decide`, etc.) in candidate.
      2. Preamble before the first theorem (`import`, `open`, `variable`, `def`) is unmodified.
      3. Target theorem name and normalized signature before `:=` match 100% (even if candidate
         prepends helper lemmas before the target theorem).
    """
    violations = scan_forbidden_constructs(candidate_code)
    spec_sig = _extract_theorem_signature(spec_code)
    if spec_sig is None:
        return {
            "ok": False,
            "reason": "MISSING_SPEC_THEOREM",
            "violations": violations,
        }
    cand_sig = _extract_theorem_signature(candidate_code, target_name=spec_sig["name"])
    if cand_sig is None:
        cand_sig = _extract_theorem_signature(candidate_code)
    if cand_sig is None:
        return {
            "ok": False,
            "reason": "MISSING_CANDIDATE_THEOREM",
            "violations": violations,
        }

    norm_ws = lambda s: " ".join(s.split())
    header_matches = norm_ws(spec_sig["header_prefix"]) == norm_ws(
        cand_sig["header_prefix"]
    )
    sig_matches = norm_ws(spec_sig["neutral_sig"]) == norm_ws(
        cand_sig["neutral_sig"]
    )

    spec_concepts = extract_concept_symbols(spec_sig)
    cand_concepts = extract_concept_symbols(cand_sig)
    missing_concepts = sorted(spec_concepts - cand_concepts)
    added_concepts = sorted(cand_concepts - spec_concepts)

    ok = (
        len(violations) == 0
        and header_matches
        and sig_matches
        and not missing_concepts
    )
    reason = "OK"
    if violations:
        reason = f"FORBIDDEN_CONSTRUCT:{violations[0]['code']}"
    elif not header_matches:
        reason = "HEADER_PREAMBLE_MODIFIED"
    elif missing_concepts:
        reason = f"CONCEPT_SYMBOL_DRIFT:missing={missing_concepts}"
    elif not sig_matches:
        reason = "THEOREM_SIGNATURE_MODIFIED"

    return {
        "ok": ok,
        "reason": reason,
        "theorem": spec_sig["name"],
        "header_matches": header_matches,
        "signature_matches": sig_matches,
        "missing_concepts": missing_concepts,
        "added_concepts": added_concepts,
        "violations": violations,
    }


def _strip_leading_headers_and_shared_defs(
    candidate_code: str, shared_def_names: set[str]
) -> str:
    """Strip `import`/`open`/`set_option` and duplicate `def`/`abbrev`/`structure`/`inductive`
    blocks from `candidate_code` so it can be embedded inside `namespace Candidate ... end Candidate`."""
    lines = candidate_code.splitlines()
    neutral_lines = neutralize_comments_and_strings(candidate_code).splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    def_re = re.compile(
        r"^[ \t]*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(def|abbrev|structure|inductive)\s+([A-Za-z_][A-Za-z0-9_']*)\b"
    )
    top_re = re.compile(
        r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|scoped|noncomputable)\s+)*"
        r"(?:theorem|lemma|example|def|abbrev|structure|inductive|namespace|end|section)\b"
    )
    while i < n:
        nl = neutral_lines[i]
        stripped = nl.strip()
        if stripped.startswith(("import ", "open ", "set_option ", "variable ")):
            i += 1
            continue
        m_def = def_re.match(nl)
        if m_def and m_def.group(2) in shared_def_names:
            # Skip this duplicate/decoy definition block until the next top-level declaration
            i += 1
            while i < n:
                nl_next = neutral_lines[i]
                if nl_next and nl_next[0] not in (" ", "\t") and top_re.match(nl_next):
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def build_sandbox_harness(spec_code: str, candidate_code: str) -> dict:
    """Build the `namespace Candidate ... end Candidate` definitional-equality Lean 4 harness."""
    spec_sig = _extract_theorem_signature(spec_code)
    if spec_sig is None:
        return {
            "ok": False,
            "reason": "MISSING_THEOREM_DECLARATION",
            "harness": "",
        }
    cand_sig = _extract_theorem_signature(candidate_code, target_name=spec_sig["name"])
    if cand_sig is None:
        cand_sig = _extract_theorem_signature(candidate_code)
    if cand_sig is None:
        return {
            "ok": False,
            "reason": "MISSING_THEOREM_DECLARATION",
            "harness": "",
        }

    # Extract shared definitions from spec preamble
    spec_preamble = spec_code[: spec_sig["start_pos"]].rstrip()
    shared_defs = _extract_top_level_defs(neutralize_comments_and_strings(spec_preamble))
    shared_def_names = set(shared_defs.keys())

    cand_body_clean = _strip_leading_headers_and_shared_defs(
        candidate_code, shared_def_names
    )
    thm_name = spec_sig["name"]
    binders = spec_sig["binders_raw"]
    target = spec_sig["target_type"]
    cand_binders = cand_sig["binders_raw"]
    cand_target = cand_sig["target_type"]

    explicit_args = _extract_explicit_binder_names(binders)
    args_suffix = (" " + " ".join(explicit_args)) if explicit_args else ""
    binders_space = f" {binders}" if binders else ""
    cand_binders_space = f" {cand_binders}" if cand_binders else ""

    # When binders do not use `Type*`, we can also form `forall <binders>, <target>`
    has_type_star = "Type*" in binders or "Sort*" in binders or "Type*" in cand_binders
    if not has_type_star:
        spec_prop_expr = f"forall {binders}, {target}" if binders else target
        cand_prop_expr = f"forall {cand_binders}, {cand_target}" if cand_binders else cand_target
        spec_stmt_line = f"def __SpecStatement_{thm_name} : Prop := {spec_prop_expr}"
        cand_stmt_line = f"def __CandStatement_{thm_name} : Prop := {cand_prop_expr}"
        rfl_line = f"example : @__SpecStatement_{thm_name} = @Candidate.__CandStatement_{thm_name} := rfl"
    else:
        spec_stmt_line = f"def __SpecStatement_{thm_name}{binders_space} : Prop := {target}"
        cand_stmt_line = f"def __CandStatement_{thm_name}{cand_binders_space} : Prop := {cand_target}"
        rfl_line = f"theorem __SpecCheck_{thm_name}{binders_space} : {target} := Candidate.{thm_name}{args_suffix}"

    harness_lines = [
        spec_preamble,
        "set_option linter.unusedVariables false",
        "",
        spec_stmt_line,
        "",
        "namespace Candidate",
        cand_body_clean,
        cand_stmt_line,
        "end Candidate",
        "",
        rfl_line,
        f"theorem __SpecBridge_{thm_name}{binders_space} : {target} := Candidate.{thm_name}{args_suffix}",
        f"#check @Candidate.{thm_name}",
        f"#print axioms Candidate.{thm_name}",
        "",
    ]
    return {
        "ok": True,
        "theorem": thm_name,
        "shared_defs": sorted(shared_def_names),
        "harness": "\n".join(harness_lines),
    }


def verify_statement(
    spec_code: str,
    candidate_code: str,
    run_kernel: bool = False,
    project_root: Path | None = None,
) -> dict:
    """Full statement-preservation verifier combining static sandbox checks, `MenTaL`
    concept-symbol drift detection, and optional `lake env lean` kernel execution."""
    patch_res = validate_patch(spec_code, candidate_code)
    harness_res = build_sandbox_harness(spec_code, candidate_code)

    # Even if formatting/binder-names differ slightly, check if the normalized statement
    # and concept symbols match and no forbidden constructs exist.
    violations = patch_res.get("violations", [])
    missing_concepts = patch_res.get("missing_concepts", [])
    added_concepts = patch_res.get("added_concepts", [])

    # Check if candidate tried to redefine any shared spec `def`/`abbrev`/`structure` differently
    # across single-line or multi-line declarations.
    spec_sig = _extract_theorem_signature(spec_code)
    cand_sig = (
        _extract_theorem_signature(candidate_code, target_name=spec_sig["name"])
        if spec_sig
        else None
    )
    if cand_sig is None:
        cand_sig = _extract_theorem_signature(candidate_code)
    redefined_defs: list[str] = []
    if spec_sig and cand_sig:
        spec_pre = neutralize_comments_and_strings(spec_code[: spec_sig["start_pos"]])
        cand_pre = neutralize_comments_and_strings(
            candidate_code[: cand_sig["start_pos"]]
        )
        spec_defs = _extract_top_level_defs(spec_pre)
        cand_defs = _extract_top_level_defs(cand_pre)
        for dname, spec_dbody in spec_defs.items():
            if dname in cand_defs and cand_defs[dname] != spec_dbody:
                redefined_defs.append(dname)

    static_ok = (
        bool(harness_res.get("ok"))
        and len(violations) == 0
        and len(missing_concepts) == 0
        and len(added_concepts) == 0
        and len(redefined_defs) == 0
        and bool(patch_res.get("signature_matches"))
    )

    kernel_ok = True
    kernel_output = ""
    disallowed_axioms: list[str] = []
    if run_kernel and static_ok and harness_res.get("harness"):
        tmp_dir = Path(project_root) if project_root else Path.cwd()
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".lean",
            dir=str(tmp_dir),
            delete=False,
            encoding="utf-8",
        ) as tf:
            tf.write(harness_res["harness"])
            tmp_path = Path(tf.name)
        try:
            proc = subprocess.run(
                ["lake", "env", "lean", str(tmp_path)],
                cwd=str(tmp_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
            kernel_output = (proc.stdout or "") + (proc.stderr or "")
            kernel_ok = proc.returncode == 0
            for ax_m in re.finditer(
                r"depends on axioms:\s*\[([^\]]+)\]", kernel_output
            ):
                axs = [a.strip() for a in ax_m.group(1).split(",") if a.strip()]
                for a in axs:
                    if a not in ALLOWED_STANDARD_AXIOMS:
                        disallowed_axioms.append(a)
            if disallowed_axioms:
                kernel_ok = False
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass

    ok = static_ok and kernel_ok
    reason = "OK"
    if violations:
        reason = f"FORBIDDEN_CONSTRUCT:{violations[0]['code']}"
    elif redefined_defs:
        reason = f"SHARED_DEF_TAMPERED:{redefined_defs}"
    elif missing_concepts or added_concepts:
        reason = f"CONCEPT_SYMBOL_DRIFT:missing={missing_concepts},added={added_concepts}"
    elif not patch_res.get("signature_matches"):
        reason = "STATEMENT_TYPE_MISMATCH"
    elif not kernel_ok:
        reason = "KERNEL_VERIFICATION_FAILED"

    return {
        "ok": ok,
        "reason": reason,
        "theorem": harness_res.get("theorem", ""),
        "static_ok": static_ok,
        "kernel_ok": kernel_ok,
        "redefined_defs": redefined_defs,
        "missing_concepts": missing_concepts,
        "added_concepts": added_concepts,
        "violations": violations,
        "disallowed_axioms": disallowed_axioms,
        "harness": harness_res.get("harness", ""),
        "kernel_output": kernel_output,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = "verify-statement"
    if argv and argv[0] in ("verify-statement", "validate-patch"):
        mode = argv.pop(0)

    parser = argparse.ArgumentParser(
        prog=f"lean-skills {mode}",
        description="Lean 4 statement-preservation sandbox and fast patch header validator",
    )
    parser.add_argument("spec", type=Path, help="Original specification .lean file")
    parser.add_argument("candidate", type=Path, help="Candidate proof .lean file")
    parser.add_argument(
        "--run-kernel",
        action="store_true",
        help="Execute `lake env lean` on the generated `namespace Candidate` sandbox",
    )
    parser.add_argument(
        "--emit-harness",
        action="store_true",
        help="Print the generated Lean 4 sandbox harness instead of JSON",
    )
    args = parser.parse_args(argv)

    spec_text = args.spec.read_text(encoding="utf-8")
    cand_text = args.candidate.read_text(encoding="utf-8")

    if mode == "validate-patch":
        res = validate_patch(spec_text, cand_text)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1

    res = verify_statement(
        spec_text,
        cand_text,
        run_kernel=args.run_kernel,
        project_root=args.spec.resolve().parent,
    )
    if args.emit_harness:
        print(res["harness"], end="")
    else:
        print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

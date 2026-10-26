#!/usr/bin/env python3
"""Acceptance probes for `proof_quality.py`.

These cover the Wave-05 full-calibration suite (FQ-1..FQ-5):
  * term-mode proof parsing (`:= <term>`)
  * `example` + `private`/`protected`/`public` modifier coverage
  * the term-mode "swallow" non-regression (a term-mode signature must
    not absorb the following declaration)
  * term-mode truth-stub detection
  * concrete-vs-variable `decide` severity recalibration
  * the structural long-proof branch-point signal

Run as a script (no test framework required):

    python3 scripts/lean/proof_quality_test.py

Exits 0 on success, 1 on any check failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import the implementation alongside this script.
sys.path.insert(0, str(Path(__file__).parent))
from proof_quality import (
    _is_concrete_decide_target,
    _structural_branch_points,
    detect_hypothesis_echo,
    detect_misaligned_docstring,
    detect_nat_nonneg_triviality,
    detect_nat_sub_unguarded,
    detect_reflexive_tautology,
    extract_theorem_blocks,
    find_one_way_bool_checkers,
    find_tautology_candidates,
    find_unused_hypotheses,
    is_vacuous_candidate,
)


def _check(cond: bool, label: str) -> bool:
    print(f"{'PASS' if cond else 'FAIL'} {label}")
    return cond


def test_term_mode_parsed() -> bool:
    src = (
        "theorem foo : 1 = 1 := rfl\n"
        "lemma bar (n : Nat) : n + 0 = n := by simp\n"
    )
    blocks = extract_theorem_blocks(src)
    names = [b['name'] for b in blocks]
    ok = _check(names == ['foo', 'bar'], "term-mode + tactic-mode both parsed")
    foo = next((b for b in blocks if b['name'] == 'foo'), None)
    ok &= _check(foo is not None and foo['body'].strip() == 'rfl',
                 "term-mode body is the proof term")
    return ok


def test_modifiers_and_example() -> bool:
    src = (
        "protected theorem p : True := trivial\n"
        "public theorem q : 2 = 2 := rfl\n"
        "private lemma r : 3 = 3 := rfl\n"
        "example : 4 = 4 := rfl\n"
    )
    blocks = extract_theorem_blocks(src)
    names = {b['name'] for b in blocks}
    ok = _check({'p', 'q', 'r'}.issubset(names),
                "protected/public/private decls parsed")
    ok &= _check('(example)' in names, "example decls parsed")
    return ok


def test_swallow_nonregression() -> bool:
    # A term-mode signature must not keep scanning and swallow the
    # following declaration into its own body.
    src = (
        "theorem first : 1 = 1 := rfl\n"
        "theorem second : 2 = 2 := rfl\n"
    )
    blocks = extract_theorem_blocks(src)
    first = next((b for b in blocks if b['name'] == 'first'), None)
    ok = _check(len(blocks) == 2, "two declarations remain distinct")
    ok &= _check(first is not None and 'second' not in first['body'],
                 "first body does not swallow second decl")
    return ok


def test_truth_stub_term() -> bool:
    thm = {
        'name': 'stub',
        'line': 1,
        'signature': 'theorem stub : SomeProp x',
        'body': 'trivial',
    }
    findings = find_tautology_candidates(thm)
    types = {f['type'] for f in findings}
    ok = _check('truth-stub-term' in types,
                "term-mode `trivial` flagged as truth-stub-term")
    angle = find_tautology_candidates({**thm, 'body': '⟨⟩'})
    ok &= _check(any(f['type'] == 'truth-stub-term' for f in angle),
                 "empty anonymous constructor flagged")
    return ok


def test_decide_severity_recalibration() -> bool:
    concrete = {
        'name': 'c', 'line': 1,
        'signature': 'theorem c : 2 + 2 = 4', 'body': 'decide',
    }
    variable = {
        'name': 'v', 'line': 1,
        'signature': 'theorem v (n : Nat) : n % 2 = 0 ∨ n % 2 = 1',
        'body': 'decide',
    }
    cf = [f for f in find_tautology_candidates(concrete)
          if f['type'] == 'decide-closed-candidate']
    vf = [f for f in find_tautology_candidates(variable)
          if f['type'] == 'decide-closed-candidate']
    ok = _check(_is_concrete_decide_target(concrete['signature']),
                "closed statement recognised as concrete")
    ok &= _check(not _is_concrete_decide_target(variable['signature']),
                 "binder/quantifier statement recognised as non-concrete")
    ok &= _check(bool(cf) and cf[0]['severity'] == 'P3',
                 "concrete `decide` downgraded to P3 advisory")
    ok &= _check(bool(vf) and vf[0]['severity'] == 'P2',
                 "variable-bearing `decide` stays P2")
    return ok


def test_structural_branch_points() -> bool:
    flat = "calc a = b := by rw [h]\n  _ = c := by rw [g]\n"
    branchy = (
        "rcases h with h1 | h2\n"
        "· obtain ⟨x, hx⟩ := h1\n"
        "  cases hx <;> simp\n"
        "· induction h2 with\n"
        "  | zero => rfl\n"
        "  | succ n ih => simp [ih]\n"
    )
    ok = _check(_structural_branch_points(flat) == 0,
                "flat calc proof scores 0 branch points")
    ok &= _check(_structural_branch_points(branchy) >= 5,
                 "branchy proof scores multiple branch points")
    return ok


def test_seven_defect_detectors() -> bool:
    ok = True
    ok &= _check(
        bool(detect_hypothesis_echo("theorem t1 (x : Nat) (h : x > 0) : x > 0", "exact h")),
        "HYPOTHESIS_ECHO detected on exact h",
    )
    ok &= _check(
        bool(detect_hypothesis_echo("theorem t1b (a b : Nat) (h : a = b) : b = a", "h.symm")),
        "HYPOTHESIS_ECHO detected on h.symm",
    )
    ok &= _check(
        bool(detect_reflexive_tautology("theorem t2 (x : Nat) : x + 1 = x + 1", "rfl")),
        "REFLEXIVE_TAUTOLOGY detected on x + 1 = x + 1",
    )
    ok &= _check(
        bool(detect_nat_nonneg_triviality("theorem t3 (a b : Nat) : a - b >= 0", "omega")),
        "NAT_NONNEG_TRIVIALITY detected on a - b >= 0",
    )
    ok &= _check(
        bool(detect_nat_sub_unguarded("theorem t4 (a b : Nat) : a - b + b = a")),
        "NAT_SUB_UNGUARDED detected on unguarded a - b",
    )
    ok &= _check(
        not bool(detect_nat_sub_unguarded("theorem t4_ok (a b : Nat) (h : b <= a) : a - b + b = a")),
        "NAT_SUB_UNGUARDED clean when guarded by b <= a",
    )
    ok &= _check(
        bool(
            detect_misaligned_docstring(
                "/-- Proves Kuratowski planarity and Byzantine quorum safety. -/",
                "theorem t5 (n : Nat) : n = n",
                "rfl",
            )
        ),
        "MISALIGNED_DOCSTRING detected on overclaiming docstring + 1-line rfl",
    )
    ok &= _check(
        "x" in find_unused_hypotheses("theorem t6 (x : Nat) : 1 + 1 = 2", "omega"),
        "UNUSED_VALUE_OR_UNDERSCORE_BINDER flags unused value binder even with omega",
    )
    ok &= _check(
        "_h" in find_unused_hypotheses("theorem t6b (a : Nat) (_h : a > 0) : a = a", "rfl"),
        "UNUSED_VALUE_OR_UNDERSCORE_BINDER flags explicit underscore hypothesis binder",
    )
    src_bool = (
        "def isEvenCheck (n : Nat) : Bool := n % 2 == 0\n"
        "theorem isEvenCheck_sound (n : Nat) (h : isEvenCheck n = true) : n % 2 == 0 := by exact h\n"
    )
    blocks = extract_theorem_blocks(src_bool)
    ow = find_one_way_bool_checkers(src_bool, blocks)
    ok &= _check(
        len(ow) == 1 and ow[0]["type"] == "ONE_WAY_BOOL_CHECKER",
        "ONE_WAY_BOOL_CHECKER detected on one-way Bool soundness theorem",
    )
    ok &= _check(
        is_vacuous_candidate("theorem v (x : Nat) (h : x > 0) : x > 0", "exact h"),
        "is_vacuous_candidate expanded to catch hypothesis echo",
    )
    ok &= _check(
        bool(detect_nat_sub_unguarded("theorem t4_hyp (a b : Nat) (h : a - b = 3) : a >= 3")),
        "NAT_SUB_UNGUARDED detected when unguarded a - b is in hypothesis",
    )
    ok &= _check(
        not bool(detect_nat_sub_unguarded("theorem t4_add (a b : Nat) (h : b + 1 <= a) : a - b >= 1")),
        "NAT_SUB_UNGUARDED clean when guarded by b + 1 <= a",
    )
    ok &= _check(
        bool(detect_reflexive_tautology("theorem t2_iff (P : Prop) : P <-> P", "Iff.rfl")),
        "REFLEXIVE_TAUTOLOGY detected on ASCII <-> with Iff.rfl",
    )
    ok &= _check(
        "_h" in find_unused_hypotheses("theorem t6_imp {a : Nat} {_h : a > 0} (b : Nat) : b = b", "rfl"),
        "UNUSED_VALUE_OR_UNDERSCORE_BINDER flags implicit {_h : P}",
    )
    return ok


def main() -> int:
    print("=" * 60)
    print("proof_quality acceptance probes")
    print("=" * 60)
    results = [
        test_term_mode_parsed(),
        test_modifiers_and_example(),
        test_swallow_nonregression(),
        test_truth_stub_term(),
        test_decide_severity_recalibration(),
        test_structural_branch_points(),
        test_seven_defect_detectors(),
    ]
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"{passed}/{total} probes passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

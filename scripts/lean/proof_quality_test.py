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
from proof_quality import (  # noqa: E402
    _is_concrete_decide_target,
    _structural_branch_points,
    extract_theorem_blocks,
    find_tautology_candidates,
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
    ]
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"{passed}/{total} probes passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

"""Unit tests for Proposals 4B, 7A, 7B, and 7C (`apollo_repair.py`, `verify_statement.py`, `run_persist.py`).

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lean"))

from apollo_repair import (
    FORBIDDEN_REPAIR_TACTICS,
    KERNEL_SAFE_SOLVER_CASCADE,
    ProofRepairer,
    Sorrifier,
    SyntaxCorrector,
    build_solver_cascade_tactic,
    extract_lemmas_from_sorry,
    neutralize_comments_and_strings,
    parse_hint_suggestions,
)
from run_persist import (
    DisproveArtifactTxn,
    RunJournal,
    compute_blocker_signature,
    should_refine_informal,
    validate_structural_coord,
)
from verify_statement import (
    build_sandbox_harness,
    validate_patch,
    verify_statement,
)


def test_lexer_neutralizer_preserves_offsets_and_ignores_comments():
    raw = (
        "-- comment with rw h and , by and admit\n"
        "/- block comment\n"
        "   rw h_inside_comment\n"
        "-/\n"
        'def msg : String := "rw h_in_string , by"\n'
        "theorem foo (a b : Nat) (h : a = b) : b = a, by\n"
        "  rw h\n"
    )
    neutral = neutralize_comments_and_strings(raw)
    assert len(neutral) == len(raw)
    assert neutral.count("\n") == raw.count("\n")

    fixed = SyntaxCorrector(raw).correct_text()
    # Comment and string interiors must remain untouched
    assert "-- comment with rw h and , by and admit" in fixed
    assert "rw h_inside_comment" in fixed
    assert '"rw h_in_string , by"' in fixed
    # Actual code must be repaired
    assert ": b = a := by" in fixed
    assert "rw [h]" in fixed


def test_solver_cascade_strictly_excludes_native_decide():
    assert "native_decide" not in KERNEL_SAFE_SOLVER_CASCADE
    assert "native_decide" in FORBIDDEN_REPAIR_TACTICS
    cascade = build_solver_cascade_tactic(["native_decide", "ring"])
    assert "native_decide" not in cascade
    assert "(try omega)" in cascade
    # Every `try <tac>` clause must be parenthesized so Lean 4 parses `(try t1) ; (try t2)` sequentially
    for clause in cascade.split(" ; "):
        assert clause.startswith("(try ") and clause.endswith(")")


def test_sorrifier_and_sorry2lemma_reconstruct_callsite():
    code = (
        "import Mathlib.Tactic\n\n"
        "theorem demo_thm (n m : Nat) (h1 : n = m) : n + 1 = m + 1 := by\n"
        "  have h_step : n + 1 = m + 1 := by\n"
        "    broken_tactic_here\n"
        "  exact h_step\n"
    )
    sorrified = Sorrifier(code, error_lines=[5]).sorrify()
    assert "sorry" in sorrified
    assert "exact h_step" in sorrified

    s2l = extract_lemmas_from_sorry(sorrified, reconstruct_callsite=True)
    assert s2l["extracted_count"] == 1
    lem = s2l["lemmas"][0]
    assert lem["name"] == "demo_thm_1"
    assert "(n m : Nat)" in lem["declaration"]
    assert "(h1 : n = m)" in lem["declaration"]
    assert lem["target_type"] == "n + 1 = m + 1"
    assert "exact demo_thm_1 n m h1" in s2l["reconstructed_code"]


def test_sorrifier_bullet_case_and_no_goals_line_ordering():
    bullet_code = (
        "theorem t_bul (a b : Nat) : a = a /\\ b = b := by\n"
        "  constructor\n"
        "  · rw [bad_lemma]\n"
        "    rfl\n"
        "  · rfl\n"
    )
    s_bul = Sorrifier(bullet_code, error_lines=[3]).sorrify()
    assert "  · sorry\n  · rfl" in s_bul

    case_code = (
        "theorem t_case (a b : Nat) : a = a /\\ b = b := by\n"
        "  constructor\n"
        "  case left =>\n"
        "    rw [bad_lemma]\n"
        "    rfl\n"
        "  case right =>\n"
        "    rfl\n"
    )
    s_case = Sorrifier(case_code, error_lines=[4]).sorrify()
    assert "  case left =>\n    sorry\n  case right =>" in s_case

    # Combined no_goals_lines < error_lines must not shift indices and delete the wrong line
    order_code = (
        "theorem t_ord (a : Nat) : a = a := by\n"
        "  exact a\n"
        "  rfl\n"
        "  rw [bad]\n"
    )
    s_ord = Sorrifier(order_code, error_lines=[4], no_goals_lines=[3]).sorrify()
    assert "rw [bad]" not in s_ord
    assert "  exact a\n  sorry\n" in s_ord


def test_sorry2lemma_multi_have_target_types_and_prior_context():
    code = (
        "theorem t1 (a b : Nat) : a + b = b + a := by\n"
        "  have h1 : a + 0 = a := by\n"
        "    sorry\n"
        "  have h2 : b + 0 = b := by\n"
        "    sorry\n"
        "  sorry\n"
    )
    res = extract_lemmas_from_sorry(code, reconstruct_callsite=True)
    assert res["extracted_count"] == 3
    assert res["lemmas"][0]["target_type"] == "a + 0 = a"
    assert res["lemmas"][1]["target_type"] == "b + 0 = b"
    assert "(h1 : a + 0 = a)" in res["lemmas"][1]["binders"]
    assert res["lemmas"][2]["target_type"] == "a + b = b + a"
    assert "(h2 : b + 0 = b)" in res["lemmas"][2]["binders"]


def test_parse_hint_suggestions_filters_non_closers():
    raw_hint = "• intro x\n• omega\n• aesop\n• native_decide\n• ring_nf\n"
    sugs = parse_hint_suggestions(raw_hint)
    assert sugs == ["omega", "ring_nf"]


def test_validate_patch_and_verify_statement_sandbox():
    spec = (
        "import Mathlib.Tactic\n\n"
        "def myBonus (x : Nat) : Nat := x + 10\n\n"
        "theorem bonus_pos (x : Nat) : myBonus x >= 10 := by\n"
        "  sorry\n"
    )
    good_cand = (
        "import Mathlib.Tactic\n\n"
        "def myBonus (x : Nat) : Nat := x + 10\n\n"
        "theorem bonus_pos (x : Nat) : myBonus x >= 10 := by\n"
        "  unfold myBonus\n"
        "  omega\n"
    )
    res_good = verify_statement(spec, good_cand)
    assert res_good["ok"] is True
    assert "namespace Candidate" in res_good["harness"]
    assert "example : @__SpecStatement_bonus_pos = @Candidate.__CandStatement_bonus_pos := rfl" in res_good["harness"]

    # Candidate that prepends a valid helper lemma before the target theorem must still pass
    helper_cand = (
        "import Mathlib.Tactic\n\n"
        "def myBonus (x : Nat) : Nat := x + 10\n\n"
        "theorem bonus_helper (x : Nat) : x + 10 >= 10 := by omega\n\n"
        "theorem bonus_pos (x : Nat) : myBonus x >= 10 := by\n"
        "  exact bonus_helper x\n"
    )
    res_helper = verify_statement(spec, helper_cand)
    assert res_helper["ok"] is True

    # Candidate with Type* universe-polymorphic binder must generate a valid SpecCheck harness
    poly_spec = "theorem poly_id {alpha : Type*} (x : alpha) : x = x := by sorry\n"
    poly_cand = "theorem poly_id {alpha : Type*} (x : alpha) : x = x := by rfl\n"
    res_poly = verify_statement(poly_spec, poly_cand)
    assert res_poly["ok"] is True
    assert "theorem __SpecCheck_poly_id" in res_poly["harness"]

    # Candidate that tampers with single-line or multi-line `myBonus` must fail
    tampered_def = good_cand.replace("x + 10", "10")
    res_tampered = verify_statement(spec, tampered_def)
    assert res_tampered["ok"] is False
    assert "SHARED_DEF_TAMPERED" in res_tampered["reason"]

    multiline_spec = "def myFn (x : Nat) : Nat :=\n  x + 10\ntheorem t (x : Nat) : myFn x >= 10 := by sorry\n"
    multiline_tamper = "def myFn (x : Nat) : Nat :=\n  10\ntheorem t (x : Nat) : myFn x >= 10 := by unfold myFn; omega\n"
    res_ml_tamper = verify_statement(multiline_spec, multiline_tamper)
    assert res_ml_tamper["ok"] is False
    assert "SHARED_DEF_TAMPERED" in res_ml_tamper["reason"]

    concept_drift = (
        "import Mathlib.Tactic\n\n"
        "def myBonus (x : Nat) : Nat := x + 10\n\n"
        "theorem bonus_pos (x : Nat) : x + 10 >= 10 := by\n"
        "  omega\n"
    )
    res_drift = verify_statement(spec, concept_drift)
    assert res_drift["ok"] is False
    assert "CONCEPT_SYMBOL_DRIFT" in res_drift["reason"]


def test_run_persist_journal_blocker_hash_2n_and_structural_coords(tmp_path: Path):
    ok, _ = validate_structural_coord("theorem foo: induction n: succ case")
    assert ok is True
    bad_ok, bad_msg = validate_structural_coord("EASCI/Core.lean:142")
    assert bad_ok is False
    assert "LINE_NUMBER_FORBIDDEN" in bad_msg

    # 2^n checkpoints
    assert [n for n in range(1, 20) if should_refine_informal(n)] == [1, 2, 4, 8, 16]
    assert should_refine_informal(0) is False

    journal = RunJournal(tmp_path, run_id="test-run")
    d = journal.dispatch("thm_a", "theorem thm_a: root", route="omega")
    assert d["entry_id"] == "test-run#1"

    n1 = journal.note(
        "failed-avenue",
        goal_text="x + 1 <= x + 2",
        error_text="foo.lean:10:2: omega failed",
        coord="theorem thm_a: base case",
    )
    assert n1["rerun_forbidden"] is False
    assert n1["refine_informal_checkpoint"] is True  # attempt 1 == 2^0

    # Repeating the exact same goal shape + error at a different line must set rerun_forbidden = True
    n2 = journal.note(
        "failed-avenue",
        goal_text="x + 1   <= x + 2",
        error_text="bar.lean:99:4: omega failed",
        coord="theorem thm_a: step case",
    )
    assert n2["rerun_forbidden"] is True
    assert n2["refine_informal_checkpoint"] is True  # attempt 2 == 2^1

    # Premature blocked finish (< 30 attempts) must be rejected
    fin_early = journal.finish("blocked", min_attempts=30)
    assert fin_early["ok"] is False
    assert fin_early["error"] == "PREMATURE_BLOCKED_STOP"

    fin_ok = journal.finish("completed")
    assert fin_ok["ok"] is True


def test_disprove_artifact_txn_and_snapshot_restore(tmp_path: Path):
    target_file = tmp_path / "Spec.lean"
    target_file.write_text("theorem conj (n : Nat) : n < 10 := by sorry\n", encoding="utf-8")

    txn = DisproveArtifactTxn(tmp_path / "state", txn_id="cex-1")
    txn.begin("conj", target_files=[str(target_file)])

    # Commit without witness must fail
    assert txn.commit()["ok"] is False

    # Mutate file and abort -> file restored from snapshot
    target_file.write_text("-- corrupted\n", encoding="utf-8")
    ab = txn.abort(restore_snapshots=True)
    assert ab["ok"] is True
    assert "theorem conj" in target_file.read_text(encoding="utf-8")

    # Also test explicit snapshot_save and snapshot_restore
    txn2 = DisproveArtifactTxn(tmp_path / "state", txn_id="snap-2")
    s_save = txn2.snapshot_save(target_files=[str(target_file)])
    assert s_save["ok"] is True
    target_file.write_text("-- mutated again\n", encoding="utf-8")
    s_rest = txn2.snapshot_restore()
    assert s_rest["ok"] is True
    assert "theorem conj" in target_file.read_text(encoding="utf-8")

"""Tests for the extraction detector v0 (synthetic proof strings).

The duplicated-subterm heuristic is pinned on the shape golden
fixture 2 established (the same term computed twice); the have-block
heuristic on a standard have-intro pattern.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"))

from extraction_detector import detect, detect_duplicated_subterms, detect_have_blocks


def test_have_block_detected():
    proof = "  have h1 : x + x = 2 * x := by omega\n  calc x + x = 2 * x := h1"
    cands = detect_have_blocks(proof, theorem="t")
    assert len(cands) == 1
    assert cands[0].kind == "have-block"
    assert cands[0].details["name"] == "h1"


def test_no_have_blocks_is_empty():
    assert detect_have_blocks("  exact foo bar") == []


def test_duplicated_subterm_the_fixture_shape():
    # duplicated_square's shape: x * x computed twice+
    proof = "  have h1 : x * x + x * x = (x * x) + (x * x) := rfl\n  calc x * x + x * x = 2 * (x * x) := by omega"
    cands = detect_duplicated_subterms(proof, theorem="duplicated_square")
    assert cands, "the duplicated subterm must be detected"
    top = cands[0]
    assert top.kind == "duplicated-subterm"
    assert "x * x" in top.evidence
    assert top.occurrences >= 2
    assert top.estimated_lines_saved >= 1


def test_clean_proof_has_no_duplicates():
    proof = "  rw [Nat.add_comm]\n  exact h"
    assert detect_duplicated_subterms(proof) == []


def test_detect_runs_both_and_sorts_by_saving():
    proof = "  have h : a = a := rfl\n  calc f x x + f x x = g (f x x) := by omega"
    cands = detect(proof, theorem="t")
    kinds = {c.kind for c in cands}
    assert "have-block" in kinds and "duplicated-subterm" in kinds
    savings = [c.estimated_lines_saved for c in cands]
    assert savings == sorted(savings, reverse=True)


def test_empty_proof_is_empty():
    assert detect("") == []
    assert detect(None) == []


def test_v1_subsumption_pruning():
    # unit-sequence containment: a reported candidate's UNIT SEQUENCE
    # must not appear as a contiguous proper subsequence of another
    # reported candidate's units with at least as many occurrences.
    from extraction_detector import detect_duplicated_subterms

    proof = "  calc f (g x) (g x) + f (g x) (g x) = h (g x) := by omega"
    cands = detect_duplicated_subterms(proof, theorem="t")
    seqs = [tuple(c.details["units"]) for c in cands]
    for i, a in enumerate(seqs):
        for j, b in enumerate(seqs):
            if i == j or len(b) >= len(a):
                continue
            contained = any(a[k : k + len(b)] == b for k in range(len(a) - len(b) + 1))
            assert not (contained and cands[j].occurrences >= cands[i].occurrences), (a, b)


def test_v1_paren_group_is_a_unit():
    # (x * x) must be tokenized as ONE unit, so the duplication of the
    # group is found as a single-unit... (single units need len >= 2,
    # so the grouped form must repeat as part of a longer sequence)
    from extraction_detector import _units

    units = _units("f (x * x) (x * x)")
    assert "x * x" in units


def test_v2_gate_kills_short_and_operator_noise():
    from extraction_detector import Candidate, passes_v2_gate

    assert not passes_v2_gate(
        Candidate(
            theorem="t",
            kind="duplicated-subterm",
            evidence="u u",
            occurrences=2,
            details={"units": ["u", "u"]},
        )
    )
    assert not passes_v2_gate(
        Candidate(
            theorem="t",
            kind="duplicated-subterm",
            evidence="* s + * s",
            occurrences=2,
            details={"units": ["*", "s", "+", "*", "s"]},
        )
    )
    assert passes_v2_gate(
        Candidate(
            theorem="t",
            kind="duplicated-subterm",
            evidence="K k11 * u ^ 2 + K k22 * v ^ 2",
            occurrences=2,
            details={
                "units": ["K", "k11", "*", "u", "^", "2", "+", "K", "k22", "*", "v", "^", "2"]
            },
        )
    )


def test_v2_gate_keyword_denylist():
    from extraction_detector import Candidate, passes_v2_gate

    assert not passes_v2_gate(
        Candidate(
            theorem="t",
            kind="duplicated-subterm",
            evidence="intro n intro n intro n",
            occurrences=3,
            details={"units": ["intro", "n", "intro", "n", "intro", "n"]},
        )
    )


def test_v2b_comment_stripping():
    from extraction_detector import detect_v2

    proof = (
        "  -- pin lean-v4.34.1 here  -- pin lean-v4.34.1 here  calc x * x + x * x = y := by omega"
    )
    cands = [c for c in detect_v2(proof) if c.kind == "duplicated-subterm"]
    assert all("pin" not in c.evidence for c in cands)


def test_v2b_leading_colon_ascription_gated():
    from extraction_detector import Candidate, passes_v2_gate

    assert not passes_v2_gate(
        Candidate(
            theorem="t",
            kind="duplicated-subterm",
            evidence=": 2 * K.k12 * u * v =",
            occurrences=3,
            details={"units": [":", "2", "*", "K.k12", "*", "u", "*", "v", "="]},
        )
    )

def test_v3_named_term_demotion():
    from extraction_detector import detect_v3
    block = ("  let m_i := mElement τ D i h_nonempty h_M_nonempty"
             "  have h_max : isMaximalInMSet τ D i h_nonempty m_i :="
             "    m_element_is_maximal τ D i h_nonempty h_M_nonempty")
    syms = {"mElement", "m_element_is_maximal"}
    assert detect_v3(block, "t", file_symbols=syms) == []


def test_v3_keeps_genuinely_anonymous_duplication():
    from extraction_detector import detect_v3
    block = ("  calc norm_sq a b + norm_sq a b = 2 * norm_sq a b := by ring"
             "  where norm is not a module symbol here")
    cands = detect_v3(block, "t", file_symbols={"unrelated_def"})
    assert any("norm_sq a b" in c.evidence for c in cands)


def test_v31_named_argument_invocation_detected():
    """v3.1: spans containing named arguments (f := x) are valid
    extraction targets - the whole invocation gets named."""
    from extraction_detector import detect_v3
    block = ("  apply mul_le_mul_of_nonneg_left"
             "    (Finset.single_le_sum (f := fun j => |r j|)"
             "      (fun j _ => abs_nonneg _) (Finset.mem_univ i))"
             "  apply mul_le_mul_of_nonneg_left"
             "    (Finset.single_le_sum (f := fun j => |r j|)"
             "      (fun j _ => abs_nonneg _) (Finset.mem_univ i))")
    cs = detect_v3(block, "t", file_symbols=set())
    assert any(c.kind == "duplicated-subterm" and c.occurrences == 2 for c in cs)


def test_v31_head_binder_still_skipped():
    """v3.1: the := filter is head-anchored - a span that IS a binding
    (ident := ...) is still not proposed as a term."""
    from extraction_detector import detect_duplicated_subterms
    block = "  have h1 := f x" + chr(10) + "  have h2 := f x"
    # the spans starting `have`/`h1` `:=` heads are skipped; only the
    # payload `f x` may surface
    for c in detect_duplicated_subterms(block, "t"):
        units = c.details["units"]
        assert units[0] not in ("have", "h1", "h2")

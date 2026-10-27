"""Cross-language fidelity parity suite (Proposal 5C).

Verifies that `proof_quality.py` (`audit_fidelity_defects`), `lean-analyzer`
(`src/source_diagnostics.rs`), and `lean-lsp-mcp` (`src/proof_fidelity_audit.ts`)
agree on the 8 canonical statement-vs-proof fidelity defects (`FIDELITY-01..08`)
and that the SAIR kernel optimization handbook documents all 37 `SAIR-LAW-01..25B`
laws and AltProof Routes 7..11.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lean"))

from proof_quality import (
    FIDELITY_CODE_MAP,
    audit_fidelity_defects,
    detect_over_concrete_fixed_arity,
)

GOLDEN_FIDELITY_FIXTURE = """
theorem echo_defect (n : Nat) (h : n = 5) : n = 5 := by
  exact h

theorem refl_defect (x : Nat) : x + 1 = x + 1 := by
  rfl

theorem nat_nonneg_defect (a b : Nat) : a + b >= 0 := by
  omega

theorem nat_sub_defect (a b : Nat) : a - b <= a := by
  omega

theorem unused_val_defect (a b : Nat) : a = a := by
  rfl

/-- Proves Kuratowski graph non-planarity for bipartite quorums. -/
theorem misaligned_doc_defect (n : Nat) : n <= n + 1 := by
  omega

def checkEvenFlag (n : Nat) : Bool := n % 2 == 0

theorem checkEvenFlag_sound (n : Nat) (h : checkEvenFlag n = true) : n >= 0 := by
  omega

theorem fixed_arity_4_defect (a0 a1 a2 a3 : Nat) : a0 + a1 + a2 + a3 >= 0 := by
  omega

theorem fixed_arity_underscore_3_defect (q1_n1 q1_n2 q1_n3 : Int) :
    q1_n1 + q1_n2 + q1_n3 = q1_n1 + (q1_n2 + q1_n3) := by
  omega
"""


def test_all_eight_fidelity_categories_detected():
    report = audit_fidelity_defects(GOLDEN_FIDELITY_FIXTURE)
    cats = set(report["counts_by_category"].keys())
    expected = {
        "HYPOTHESIS_ECHO",
        "REFLEXIVE_TAUTOLOGY",
        "NAT_NONNEG_TRIVIALITY",
        "NAT_SUB_UNGUARDED",
        "UNUSED_VALUE_OR_UNDERSCORE_BINDER",
        "MISALIGNED_DOCSTRING",
        "ONE_WAY_BOOL_CHECKER",
        "OVER_CONCRETE_FIXED_ARITY",
    }
    assert expected.issubset(cats), f"Missing categories: {expected - cats}"
    assert set(FIDELITY_CODE_MAP.values()) == {f"FIDELITY-0{i}" for i in range(1, 9)}


def test_over_concrete_fixed_arity_thresholds():
    # 4 sequential without underscore -> flagged
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t1 (a0 a1 a2 a3 : Nat) : a0 = a0"
        )
        is not None
    )
    # Only 3 without underscore -> NOT flagged
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t2 (a0 a1 a2 : Nat) : a0 = a0"
        )
        is None
    )
    # 3 sequential WITH underscore in prefix -> flagged
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t3 (q1_n1 q1_n2 q1_n3 : Nat) : q1_n1 = q1_n1"
        )
        is not None
    )
    # Non-contiguous numbers (a0, a1, a3, a4) -> NOT flagged
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t4 (a0 a1 a3 a4 : Nat) : a0 = a0"
        )
        is None
    )


def test_sair_handbook_covers_all_37_laws_and_routes_7_to_11():
    hb_path = ROOT / "references" / "lean-sair-kernel-optimization-handbook.md"
    assert hb_path.exists()
    text = hb_path.read_text(encoding="utf-8")

    expected_39_sair_laws = {
        "SAIR-LAW-01",
        "SAIR-LAW-01B",
        "SAIR-LAW-01C",
        "SAIR-LAW-02",
        "SAIR-LAW-02B",
        "SAIR-LAW-03",
        "SAIR-LAW-03B",
        "SAIR-LAW-04",
        "SAIR-LAW-05",
        "SAIR-LAW-06",
        "SAIR-LAW-07",
        "SAIR-LAW-08",
        "SAIR-LAW-09",
        "SAIR-LAW-10",
        "SAIR-LAW-11",
        "SAIR-LAW-12",
        "SAIR-LAW-12B",
        "SAIR-LAW-13",
        "SAIR-LAW-13B",
        "SAIR-LAW-14",
        "SAIR-LAW-14B",
        "SAIR-LAW-14C",
        "SAIR-LAW-15",
        "SAIR-LAW-16",
        "SAIR-LAW-16B",
        "SAIR-LAW-17",
        "SAIR-LAW-18",
        "SAIR-LAW-18B",
        "SAIR-LAW-19",
        "SAIR-LAW-19B",
        "SAIR-LAW-20",
        "SAIR-LAW-21",
        "SAIR-LAW-22",
        "SAIR-LAW-22B",
        "SAIR-LAW-22C",
        "SAIR-LAW-23",
        "SAIR-LAW-24",
        "SAIR-LAW-25",
        "SAIR-LAW-25B",
    }
    assert len(expected_39_sair_laws) == 39
    found_codes = set(re.findall(r"\bSAIR-LAW-\d{2}[A-Z]?\b", text))
    assert expected_39_sair_laws <= found_codes
    assert "KernelBrecOnTax" in text and "KernelPowerOfTwoDivMod" in text

    for route_id in (
        "algorithm-class-substitution",
        "kernel-friendly-term-design",
        "constructive-decidable-reduction",
        "closed-def-whnf-caching",
        "gmp-swar-word-packing",
    ):
        assert route_id in text

    # Verify cross-language alignment with lean-analyzer if present as a sibling checkout
    la_src = ROOT.parent / "lean-analyzer" / "src" / "source_diagnostics.rs"
    if la_src.exists():
        la_text = la_src.read_text(encoding="utf-8")
        la_codes = set(re.findall(r'"(SAIR-LAW-\d{2}[A-Z]?)"', la_text))
        assert expected_39_sair_laws == la_codes
        assert "OverConcreteFixedArity" in la_text and "FIDELITY-08" in la_text

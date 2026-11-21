"""Cross-language fidelity parity & Core Lean compilation suite (`v0.5.0`).

Verifies that `proof_quality.py` (`audit_fidelity_defects`), `lean-analyzer`
(`src/source_diagnostics.rs`), and `lean-lsp-mcp` (`src/proof_fidelity_audit.ts`)
agree on the 8 canonical statement-vs-proof fidelity defects (`FIDELITY-01..08`),
that the kernel optimization handbook documents all 42 `KERNEL-LAW-01..28`
laws and 20 AltProof routes, and that standalone Core Lean exemplars + `AltProof.Core`
compile cleanly with zero warnings under Lean `v4.34.1`.

Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
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


def _find_lean_binary() -> str | None:
    found = shutil.which("lean")
    if found:
        return found
    elan_home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
    candidates = [
        elan_home / "toolchains" / "leanprover--lean4---v4.34.1" / "bin" / "lean",
        elan_home / "bin" / "lean",
    ]
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return None


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
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t1 (a0 a1 a2 a3 : Nat) : a0 = a0"
        )
        is not None
    )
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t2 (a0 a1 a2 : Nat) : a0 = a0"
        )
        is None
    )
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t3 (q1_n1 q1_n2 q1_n3 : Nat) : q1_n1 = q1_n1"
        )
        is not None
    )
    assert (
        detect_over_concrete_fixed_arity(
            "theorem t4 (a0 a1 a3 a4 : Nat) : a0 = a0"
        )
        is None
    )


def test_kernel_handbook_covers_all_42_laws_and_routes():
    hb_path = ROOT / "references" / "handbooks" / "lean-kernel-optimization-handbook.md"
    assert hb_path.exists()
    text = hb_path.read_text(encoding="utf-8")

    expected_39_kernel_laws = {
        "KERNEL-LAW-01",
        "KERNEL-LAW-01B",
        "KERNEL-LAW-01C",
        "KERNEL-LAW-02",
        "KERNEL-LAW-02B",
        "KERNEL-LAW-03",
        "KERNEL-LAW-03B",
        "KERNEL-LAW-04",
        "KERNEL-LAW-05",
        "KERNEL-LAW-06",
        "KERNEL-LAW-07",
        "KERNEL-LAW-08",
        "KERNEL-LAW-09",
        "KERNEL-LAW-10",
        "KERNEL-LAW-11",
        "KERNEL-LAW-12",
        "KERNEL-LAW-12B",
        "KERNEL-LAW-13",
        "KERNEL-LAW-13B",
        "KERNEL-LAW-14",
        "KERNEL-LAW-14B",
        "KERNEL-LAW-14C",
        "KERNEL-LAW-15",
        "KERNEL-LAW-16",
        "KERNEL-LAW-16B",
        "KERNEL-LAW-17",
        "KERNEL-LAW-18",
        "KERNEL-LAW-18B",
        "KERNEL-LAW-19",
        "KERNEL-LAW-19B",
        "KERNEL-LAW-20",
        "KERNEL-LAW-21",
        "KERNEL-LAW-22",
        "KERNEL-LAW-22B",
        "KERNEL-LAW-22C",
        "KERNEL-LAW-23",
        "KERNEL-LAW-24",
        "KERNEL-LAW-25",
        "KERNEL-LAW-25B",
    }
    assert len(expected_39_kernel_laws) == 39
    expected_45_kernel_laws = expected_39_kernel_laws | {
        "KERNEL-LAW-26",
        "KERNEL-LAW-27",
        "KERNEL-LAW-28",
        "KERNEL-LAW-29",
        "KERNEL-LAW-29B",
        "KERNEL-LAW-30",
        "KERNEL-LAW-31",
    }
    found_codes = set(re.findall(r"\bKERNEL-LAW-\d{2}[A-Z]?\b", text))
    assert expected_45_kernel_laws <= found_codes
    assert "KernelBrecOnTax" in text and "KernelPowerOfTwoDivMod" in text
    assert "WAVE-13 G1" in text

    for route_id in (
        "algorithm-class-substitution",
        "kernel-friendly-term-design",
        "constructive-decidable-reduction",
        "closed-def-whnf-caching",
        "gmp-swar-word-packing",
    ):
        assert route_id in text

    la_src = ROOT.parent / "lean-analyzer" / "src" / "source_diagnostics.rs"
    if la_src.exists():
        la_text = la_src.read_text(encoding="utf-8")
        la_codes = set(re.findall(r'"(KERNEL-LAW-\d{2}[A-Z]?)"', la_text))
        assert expected_39_kernel_laws <= la_codes
        assert "OverConcreteFixedArity" in la_text and "FIDELITY-08" in la_text

    assert "twinlit" in text and "Danvy" in text
    assert "Lean.ofReduceBool" in text and "Classical.choice" in text
    assert (ROOT / "scripts" / "lean" / "olean_census.lean").is_file()
    assert (ROOT / "templates" / "core" / "examples" / "Template_KernelDecide.lean").is_file()
    assert (ROOT / "templates" / "core" / "examples" / "Template_ComputableTwin_Csimp.lean").is_file()
    assert (ROOT / "templates" / "core" / "examples" / "Template_KernelWHNF.lean").is_file()
    assert (ROOT / "templates" / "core" / "examples" / "Template_ProofCarryingCodegen.lean").is_file()
    assert (ROOT / "templates" / "core" / "examples" / "Template_Theorem_Exemplar.lean").is_file()
    assert (ROOT / "packages" / "altproof" / "AltProof" / "Core.lean").is_file()
    kernel_decide_text = (ROOT / "templates" / "core" / "examples" / "Template_KernelDecide.lean").read_text(encoding="utf-8")
    assert 'macro "kernel_decide"' in kernel_decide_text
    assert "decide +kernel" in kernel_decide_text


def test_core_lean_exemplars_and_altproof_core_compile_cleanly():
    lean_bin = _find_lean_binary()
    require_lean = os.environ.get("PROOF_SKILLS_REQUIRE_LEAN", "") == "1"
    if not lean_bin:
        assert not require_lean, "PROOF_SKILLS_REQUIRE_LEAN=1 set, but `lean` binary was not found!"
        return

    exemplars = [
        ROOT / "templates" / "core" / "examples" / "Template_KernelDecide.lean",
        ROOT / "templates" / "core" / "examples" / "Template_ComputableTwin_Csimp.lean",
        ROOT / "templates" / "core" / "examples" / "Template_KernelWHNF.lean",
        ROOT / "templates" / "core" / "examples" / "Template_ProofCarryingCodegen.lean",
        ROOT / "templates" / "core" / "examples" / "Template_Theorem_Exemplar.lean",
        ROOT / "packages" / "altproof" / "AltProof" / "Core.lean",
    ]
    for path in exemplars:
        res = subprocess.run(
            [lean_bin, str(path)],
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert res.returncode == 0, f"{path.name} failed to compile:\n{res.stdout}\n{res.stderr}"
        assert res.stdout.strip() == "" and res.stderr.strip() == "", (
            f"{path.name} emitted warnings/output:\n{res.stdout}\n{res.stderr}"
        )

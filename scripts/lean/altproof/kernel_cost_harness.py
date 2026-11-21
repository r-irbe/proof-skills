"""AltProof Kernel Cost Measurement Harness (A2).

Profiles Lean 4 theorem elaboration and kernel reduction heartbeats
and wall-clock duration via `lake env lean`.
Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

import math
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

# Calibrated PMU cost prior constants (kernel Lean 4 v4.33.1 / v4.34.1 timer-kernel
# micro-probes: calibrated-cost-model-2026-11-17 & asymmetric-nat-pmu-2026-11-20).
LIMB_BITS = 64
PRIM_BASE = 4_000
LINEAR_PER_LIMB = 2
MUL_COEF = 870_000 / (1024 ** 1.42)
MUL_EXP = 1.42
# Nov 20 matched pow-vs-mul follow-up: Nat.pow x 2 vs Nat.mul x x measured
# 217,076 vs 344,330 (ratio 0.63) at 32,768 bits and 1,545,509 vs 2,990,651
# (ratio 0.52) at 131,072 bits; mean 0.58. Nat.mul x x matches balanced mul (~0.4%).
SQ_FACTOR_WIDE = 0.58
DIVMOD_FACTOR = 0.95
WIDE_CALIBRATED_MIN_BITS = 32_768
SUPERLINEAR_SCHOOLBOOK_LIMBS = 16


def _limb_count(bits: int) -> int:
    return max(1, math.ceil(max(1, int(bits)) / LIMB_BITS))


def estimate_nat_kernel_op_prior(
    op: str,
    lhs_bits: int,
    rhs_bits: int = 0,
    *,
    same_operand: bool = False,
) -> dict:
    """Opt-in PMU ranking prior for wide vs asymmetric Nat arithmetic.

    Models two Nov 20 calibrated regimes on top of the inherited superlinear prior:
      1. Single-limb x multi-limb ``Nat.mul`` (``min <= 64 < max`` bits): linear in limbs.
      2. Wide ``Nat.pow x 2`` (at >= 32,768 bits): ~0.58x cost factor vs balanced ``Nat.mul``,
         whereas ``Nat.mul x x`` (`same_operand=True`) receives NO square discount (1.0x).
    """
    if lhs_bits <= 0 or rhs_bits < 0:
        raise ValueError("bit widths must be positive (or rhs_bits == 0 for unary/pow2)")
    eff_rhs = lhs_bits if rhs_bits == 0 else rhs_bits
    la = _limb_count(lhs_bits)
    lb = _limb_count(eff_rhs)
    norm_op = op.strip()

    if norm_op in ("pow2", "Nat.pow_2", "sq"):
        L = la
        super_part = MUL_COEF * (L ** MUL_EXP) if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else 0.0
        cost = PRIM_BASE + SQ_FACTOR_WIDE * super_part
        return {
            "op": norm_op,
            "lhs_bits": lhs_bits,
            "rhs_bits": 2,
            "limbs_lhs": la,
            "limbs_rhs": 1,
            "regime": "wide_pow2_square" if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else "small_pow2",
            "factor": SQ_FACTOR_WIDE if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else 1.0,
            "calibrated_wide_regime": lhs_bits >= WIDE_CALIBRATED_MIN_BITS,
            "estimated_instructions": round(cost, 2),
            "evidence_tier": "calibrated_pmu_prior",
            "source": "kernel/asymmetric-nat-pmu-2026-11-20",
        }

    if norm_op in ("mul", "*", "Nat.mul"):
        if min(lhs_bits, eff_rhs) <= LIMB_BITS < max(lhs_bits, eff_rhs):
            cost = PRIM_BASE + LINEAR_PER_LIMB * (la + lb)
            return {
                "op": norm_op,
                "lhs_bits": lhs_bits,
                "rhs_bits": eff_rhs,
                "limbs_lhs": la,
                "limbs_rhs": lb,
                "regime": "asymmetric_single_x_multi_limb",
                "factor": 1.0,
                "calibrated_wide_regime": max(lhs_bits, eff_rhs) >= WIDE_CALIBRATED_MIN_BITS,
                "same_operand_discounted": False,
                "estimated_instructions": round(cost, 2),
                "evidence_tier": "calibrated_pmu_prior",
                "source": "kernel/asymmetric-nat-pmu-2026-11-20",
            }
        L = max(la, lb)
        super_part = MUL_COEF * (L ** MUL_EXP) if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else 0.0
        cost = PRIM_BASE + super_part
        return {
            "op": norm_op,
            "lhs_bits": lhs_bits,
            "rhs_bits": eff_rhs,
            "limbs_lhs": la,
            "limbs_rhs": lb,
            "regime": "same_operand_mul_no_sq_discount" if same_operand else "balanced_or_multi_limb_mul",
            "factor": 1.0,
            "calibrated_wide_regime": L * LIMB_BITS >= WIDE_CALIBRATED_MIN_BITS,
            "same_operand_discounted": False,
            "estimated_instructions": round(cost, 2),
            "evidence_tier": "calibrated_pmu_prior",
            "source": "kernel/asymmetric-nat-pmu-2026-11-20",
        }

    if norm_op in ("div", "mod", "Nat.div", "Nat.mod", "/", "%"):
        L = max(la, lb)
        super_part = MUL_COEF * (L ** MUL_EXP) if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else 0.0
        cost = PRIM_BASE + DIVMOD_FACTOR * super_part
        return {
            "op": norm_op,
            "lhs_bits": lhs_bits,
            "rhs_bits": eff_rhs,
            "limbs_lhs": la,
            "limbs_rhs": lb,
            "regime": "superlinear_divmod" if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else "small_divmod",
            "factor": DIVMOD_FACTOR if L > SUPERLINEAR_SCHOOLBOOK_LIMBS else 1.0,
            "calibrated_wide_regime": False,
            "estimated_instructions": round(cost, 2),
            "evidence_tier": "calibrated_pmu_prior",
            "source": "kernel/calibrated-cost-model-2026-11-17",
        }

    cost = PRIM_BASE + LINEAR_PER_LIMB * (la + lb)
    return {
        "op": norm_op,
        "lhs_bits": lhs_bits,
        "rhs_bits": eff_rhs,
        "limbs_lhs": la,
        "limbs_rhs": lb,
        "regime": "linear_fastpath",
        "factor": 1.0,
        "calibrated_wide_regime": False,
        "estimated_instructions": round(cost, 2),
        "evidence_tier": "calibrated_pmu_prior",
        "source": "kernel/calibrated-cost-model-2026-11-17",
    }


@dataclass
class KernelMeasurement:
    """Measurements for a kernel elaboration run."""

    success: bool
    wall_clock_sec: float
    heartbeats_consumed: int
    error_messages: list[str]
    warning_messages: list[str]


def parse_heartbeats_from_output(output: str) -> int:
    """Extract heartbeat counts from lean diagnostic output if present."""
    match = re.search(r"heartbeats\s+count:\s*(\d+)", output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Check for maxHeartbeats exceeded
    match_exceeded = re.search(r"maximum heartbeats\s*\((\d+)\)", output, re.IGNORECASE)
    if match_exceeded:
        return int(match_exceeded.group(1))
    return 0


def measure_lean_snippet(
    snippet: str,
    cwd: Path | str | None = None,
    timeout_sec: float = 30.0,
) -> KernelMeasurement:
    """Elaborate a self-contained Lean snippet and measure reduction cost."""
    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            ["lake", "env", "lean", "--stdin"],
            input=snippet,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
        elapsed = time.perf_counter() - start_time
        combined_output = proc.stdout + "\n" + proc.stderr
        heartbeats = parse_heartbeats_from_output(combined_output)

        errors = [line for line in combined_output.splitlines() if "error:" in line.lower()]
        warnings = [line for line in combined_output.splitlines() if "warning:" in line.lower()]

        return KernelMeasurement(
            success=(proc.returncode == 0),
            wall_clock_sec=round(elapsed, 4),
            heartbeats_consumed=heartbeats,
            error_messages=errors,
            warning_messages=warnings,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start_time
        return KernelMeasurement(
            success=False,
            wall_clock_sec=round(elapsed, 4),
            heartbeats_consumed=-1,
            error_messages=["Elaboration timed out"],
            warning_messages=[],
        )

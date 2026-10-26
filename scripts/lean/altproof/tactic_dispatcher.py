"""Tactic dispatcher v1 for AltProof automated tactic selection (A5).

Evaluates proof context, goal structure, and hypothesis types to recommend
optimal automated tactic substitutions (omega, aesop, solve_by_elim, linarith, decide)
ranked by estimated kernel heartbeats and legibility impact.
Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class TacticRecommendation:
    """A recommended tactic substitution candidate."""

    tactic: str
    target_pattern: str
    rationale: str
    estimated_heartbeats: int
    confidence: float
    parameters: dict = field(default_factory=dict)


# Goal and hypothesis classification patterns
NAT_TYPE_RE = re.compile(r"(?:\bNat\b|\bInt\b|\bdiv\b|\bmod\b|\u2115|\u2124)")
ARITH_OP_RE = re.compile(r"(?:\+|-|\*|<=|<|>=|>|\u2264|\u2265)")
PURE_NUM_ARITH_RE = re.compile(r"\b\d+\s*(?:\+|-|\*|<=|<|>=|>)\s*\d+\b")
REAL_LIN_RE = re.compile(r"(?:\bReal\b|\u211d|\blinarith\b)")
INDUCTIVE_RE = re.compile(r"\b(?:cases\b|rcases\b|induction\b|constructor\b)\b")
FINITE_RE = re.compile(r"(?:\bFin\s+\d+|\bFinset\b|\bdecide\b|\btrue\b|\bfalse\b)")
FINSET_SUM_RE = re.compile(r"(?:\bFinset\.sum\b|\u2211|\bsum_sub_distrib\b|\bsum_add_distrib\b|\bmul_sum\b|\bsum_mul\b)")
FINSET_NONNEG_RE = re.compile(
    r"(?:0\s*(?:<=|\u2264)\s*(?:Finset\.sum\b|\u2211)|\bFinset\.sum_nonneg\b)"
)
FINSET_MONO_RE = re.compile(
    r"(?:(?:Finset\.sum\b|\u2211).*?(?:<=|\u2264).*?(?:Finset\.sum\b|\u2211)|\bFinset\.sum_le_sum\b)",
    re.DOTALL,
)
WELLFORMED_RE = re.compile(r"(?:\bWellFormed\b|\bfin_cases\b.*?\bnorm_num\b)", re.DOTALL)
CHANNEL_RE = re.compile(r"(?:\bChannel\b|\bPrior\b|\bchannel_fields\b)")


SCALE100_RE = re.compile(r"(?:\bScale100\b|\beasci_omega\b|\bEASCI\b)")
BITVEC_RE = re.compile(
    r"(?:\bBitVec\b|&&&|\|\|\||\^\^\^|<<<|>>>|\bsshiftRight\b|\bushiftRight\b|\bzeroExtend\b|\bsignExtend\b|\bextractLsb'\b)"
)


def build_qf_bv_smt2_prescreen(goal_text: str, default_width: int = 64) -> str:
    """Generate a lightweight QF_BV SMT-LIB2 pre-screening script for a BitVec goal."""
    target = _extract_goal_target(goal_text)
    width_m = re.search(r"\bBitVec\s+(\d+)\b", goal_text or "")
    width = int(width_m.group(1)) if width_m else default_width
    raw_vars = sorted(
        {
            tok
            for tok in re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_']*\b", target)
            if tok
            not in {
                "BitVec",
                "Nat",
                "Int",
                "Bool",
                "true",
                "false",
                "ofNat",
                "toNat",
                "sshiftRight",
                "ushiftRight",
                "zeroExtend",
                "signExtend",
                "extractLsb",
                "fun",
                "let",
                "in",
            }
        }
    )
    lines = ["(set-logic QF_BV)"]
    for v in raw_vars[:12]:
        lines.append(f"(declare-const {v} (_ BitVec {width}))")
    lines.append(f"; Goal target: {target}")
    lines.append("; Negated verification condition for Z3/cvc5 pre-screening:")
    lines.append("(check-sat)")
    return "\n".join(lines)


def _extract_goal_target(goal_text: str) -> str:
    """Extract the target expression after the last `|-` or `\u22a2` turnstile if present."""
    raw = (goal_text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    parts = re.split(r"(?:\|-|\u22a2)", raw)
    return parts[-1].strip() if len(parts) > 1 else raw


def recommend_tactics(
    goal_text: str,
    current_proof_text: str = "",
    *,
    include_project_tactics: bool = True,
    custom_plugins: list[TacticRecommendation] | None = None,
) -> list[TacticRecommendation]:
    """Analyze goal and current proof script to recommend modernized tactic replacements."""
    recommendations: list[TacticRecommendation] = []
    goal = goal_text or ""
    target = _extract_goal_target(goal)
    proof = current_proof_text or ""

    # 0. Fixed-width BitVec / SWAR goals -> bv_decide (top-priority finisher)
    if BITVEC_RE.search(goal) or BITVEC_RE.search(proof) or "bv_decide" in proof:
        recommendations.append(
            TacticRecommendation(
                tactic="bv_decide",
                target_pattern="fixed-width-bitvec-sat-reflection",
                rationale="Bit-blasted CaDiCaL LRAT reflection finisher for fixed-width BitVec / SWAR goals; zero Classical.choice overhead.",
                estimated_heartbeats=60,
                confidence=0.97,
                parameters={"qf_bv_smt2": build_qf_bv_smt2_prescreen(goal)},
            )
        )

    # 1. Presburger / Discrete Integer Arithmetic -> omega (and easci_omega when Scale100/custom tactics enabled)
    target_no_arrows = target.replace("->", " ").replace("=>", " ")
    has_nat_context = bool(NAT_TYPE_RE.search(goal) or PURE_NUM_ARITH_RE.search(target_no_arrows))
    has_arith_op = bool(ARITH_OP_RE.search(target_no_arrows))
    if (
        (has_nat_context or (has_arith_op and not FINSET_SUM_RE.search(target) and not WELLFORMED_RE.search(target)))
        and has_arith_op
        and not REAL_LIN_RE.search(goal)
        and not FINSET_SUM_RE.search(target)
    ):
        recommendations.append(
            TacticRecommendation(
                tactic="omega",
                target_pattern="linear-nat-int-arithmetic",
                rationale="Native Lean 4 Presburger arithmetic decision procedure; eliminates manual induction on inequalities.",
                estimated_heartbeats=150,
                confidence=0.92,
            )
        )
        if include_project_tactics and (SCALE100_RE.search(goal) or SCALE100_RE.search(proof)):
            recommendations.append(
                TacticRecommendation(
                    tactic="easci_omega",
                    target_pattern="scaled-simplex-nat-arithmetic",
                    rationale="Project-specific Scale100 wrapper unfolding scaled-integer definitions before omega.",
                    estimated_heartbeats=170,
                    confidence=0.94,
                )
            )

    # 2. Linear Real Arithmetic -> linarith / nlinarith
    if REAL_LIN_RE.search(goal) or "\u211d" in goal:
        recommendations.append(
            TacticRecommendation(
                tactic="linarith",
                target_pattern="linear-real-inequalities",
                rationale="Fourier-Motzkin elimination over real linear combinations.",
                estimated_heartbeats=350,
                confidence=0.88,
            )
        )

    # 3. Finset.sum linearity + pointwise ring congruence -> sum_congr_ring
    if include_project_tactics and (FINSET_SUM_RE.search(target) or FINSET_SUM_RE.search(proof)):
        recommendations.append(
            TacticRecommendation(
                tactic="sum_congr_ring",
                target_pattern="finset-sum-linearity-pointwise-ring",
                rationale="Normalizes Finset.sum linearity (sum_add_distrib, sum_sub_distrib, mul_sum, sum_mul) and closes pointwise ring equalities via Finset.sum_congr.",
                estimated_heartbeats=260,
                confidence=0.91,
            )
        )

    # 4. Finset.sum non-negativity -> finset_nonneg
    if include_project_tactics and (FINSET_NONNEG_RE.search(target) or re.search(r"\b(?:Finset\.sum_nonneg|finset_nonneg)\b", proof)):
        recommendations.append(
            TacticRecommendation(
                tactic="finset_nonneg",
                target_pattern="finset-sum-nonneg-positivity",
                rationale="Discharges 0 <= sum_i f i via Finset.sum_nonneg followed by positivity/linarith/nlinarith/omega.",
                estimated_heartbeats=240,
                confidence=0.90,
            )
        )

    # 4b. Finset.sum pointwise monotonicity -> finset_mono
    if include_project_tactics and (FINSET_MONO_RE.search(target) or re.search(r"\b(?:Finset\.sum_le_sum|finset_mono)\b", proof)):
        recommendations.append(
            TacticRecommendation(
                tactic="finset_mono",
                target_pattern="finset-sum-pointwise-monotonicity",
                rationale="Discharges sum_i f i <= sum_i g i via Finset.sum_le_sum, pointwise hypothesis specialization, and ordered-ring monotonicity closers.",
                estimated_heartbeats=250,
                confidence=0.91,
            )
        )

    # 5. Five-field Opinion/RatOpinion WellFormed fixture -> wellformed_tac
    if include_project_tactics and (WELLFORMED_RE.search(target) or WELLFORMED_RE.search(proof)):
        recommendations.append(
            TacticRecommendation(
                tactic="wellformed_tac",
                target_pattern="finite-simplex-wellformed-conjunction",
                rationale="Discharges five-field WellFormed conjunctions over Fin 1..8 via fin_cases and Fin.sum_univ_one..eight + norm_num.",
                estimated_heartbeats=190,
                confidence=0.93,
            )
        )

    # 6. Channel / Prior constructor obligations -> channel_fields
    if include_project_tactics and (CHANNEL_RE.search(target) or CHANNEL_RE.search(proof)):
        recommendations.append(
            TacticRecommendation(
                tactic="channel_fields",
                target_pattern="channel-prior-constructor-obligations",
                rationale="Constructs Channel or Prior and discharges nonneg and rowMass/mass obligations over Fin 1..8.",
                estimated_heartbeats=180,
                confidence=0.92,
            )
        )

    # 7. Inductive reasoning and constructor search -> aesop
    if INDUCTIVE_RE.search(proof) or "constructor" in proof:
        recommendations.append(
            TacticRecommendation(
                tactic="aesop",
                target_pattern="whitebox-best-first-search",
                rationale="Best-first search over safe/unsafe rulesets; replaces manual intro/case/constructor chains.",
                estimated_heartbeats=800,
                confidence=0.85,
            )
        )

    # 8. Pure hypothesis elimination -> solve_by_elim
    if "apply" in proof and not INDUCTIVE_RE.search(proof):
        recommendations.append(
            TacticRecommendation(
                tactic="solve_by_elim",
                target_pattern="bounded-backtracking-unification",
                rationale="Backtracking unification over local hypotheses without expanding external lemmas.",
                estimated_heartbeats=220,
                confidence=0.80,
            )
        )

    # 9. Finite/computable decision -> decide
    if (
        FINITE_RE.search(target)
        and not CHANNEL_RE.search(target)
        and not WELLFORMED_RE.search(target)
        and (not FINSET_SUM_RE.search(target) or re.search(r"\b(?:decide|true|false)\b", target))
    ):
        recommendations.append(
            TacticRecommendation(
                tactic="decide",
                target_pattern="decidable-proposition-evaluation",
                rationale="Kernel reflection on Decidable instance; zero search branching.",
                estimated_heartbeats=80,
                confidence=0.95,
            )
        )

    if custom_plugins:
        recommendations.extend(custom_plugins)

    # Sort by estimated heartbeats ascending (lightest first)
    return sorted(recommendations, key=lambda r: r.estimated_heartbeats)


def dispatch_and_score(goal_text: str, current_proof_text: str = "") -> dict:
    """Combine tactic recommendations, legibility scoring, and two-axis cost estimation."""
    import sys as _sys
    from pathlib import Path as _Path
    _dir = str(_Path(__file__).resolve().parent)
    if _dir not in _sys.path:
        _sys.path.insert(0, _dir)
    from cost_ranker import cost
    from legibility import RENDERABLE_PATTERNS, score_block

    recs = recommend_tactics(goal_text, current_proof_text)
    leg = score_block(current_proof_text or "", RENDERABLE_PATTERNS)
    lines = max(1, leg["steps"])
    baseline_cost_x10 = round(cost(lines=lines, shared_lemmas=0, upstream=False, kernel_cost=0.0) * 10)
    best_tactic = recs[0].tactic if recs else None
    best_hb = recs[0].estimated_heartbeats if recs else 0
    return {
        "goal": goal_text or "",
        "recommendations": [
            {
                "tactic": r.tactic,
                "target_pattern": r.target_pattern,
                "rationale": r.rationale,
                "estimated_heartbeats": r.estimated_heartbeats,
                "confidence": r.confidence,
            }
            for r in recs
        ],
        "legibility": leg,
        "baseline_cost_x10": baseline_cost_x10,
        "best_tactic": best_tactic,
        "best_estimated_heartbeats": best_hb,
    }


def _cli_main() -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="AltProof Tactic Advisor & Two-Axis Scorer")
    parser.add_argument("--goal", default="", help="Lean 4 goal state string")
    parser.add_argument("--proof", default="", help="Current proof block string")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test suite")
    args = parser.parse_args()
    if args.self_test:
        r1 = dispatch_and_score("|- Finset.sum s (fun i => f i) <= Finset.sum s (fun i => g i)", "apply Finset.sum_le_sum")
        assert any(x["tactic"] == "finset_mono" for x in r1["recommendations"]), r1
        r2 = dispatch_and_score("|- 0 <= Finset.sum s (fun i => (f i)^2)", "apply Finset.sum_nonneg")
        assert any(x["tactic"] == "finset_nonneg" for x in r2["recommendations"]), r2
        r3 = dispatch_and_score("|- Finset.sum s (fun i => a * f i) = a * Finset.sum s (fun i => f i)", "rw [Finset.mul_sum]")
        assert any(x["tactic"] == "sum_congr_ring" for x in r3["recommendations"]), r3
        r4 = dispatch_and_score("x y : BitVec 64 |- (x ^^^ y) ^^^ y = x", "bv_decide")
        assert r4["best_tactic"] == "bv_decide", r4
        print("altproof_tactic_advisor: self-test PASSED (4/4 checks)")
        return 0
    print(json.dumps(dispatch_and_score(args.goal, args.proof), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())

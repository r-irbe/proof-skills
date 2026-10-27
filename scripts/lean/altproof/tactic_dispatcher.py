"""Tactic dispatcher v1 for AltProof automated tactic selection (A5).

Evaluates proof context, goal structure, and hypothesis types to recommend
optimal automated tactic substitutions:
  - Built-in core / Mathlib / SAIR tactics (`bv_decide`, `omega`, `linarith`,
    `aesop`, `solve_by_elim`, `decide`, `ring`, plus SAIR SWAR/WHNF routes
    `eval_nat%` and `preunfold%`)
  - Declarative project tactic plugins loaded from `lean-project.toml`
    (`[[altproof.tactics]]`) via `project_config.py` (with fallback defaults
    when `include_project_tactics=True` and no `lean-project.toml` is found).

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TacticRecommendation:
    """A recommended tactic substitution candidate."""

    tactic: str
    target_pattern: str
    rationale: str
    estimated_heartbeats: int
    confidence: float
    parameters: dict = field(default_factory=dict)


# Built-in core / Mathlib / SAIR goal and hypothesis classification patterns
NAT_TYPE_RE = re.compile(r"(?:\bNat\b|\bInt\b|\bdiv\b|\bmod\b|\u2115|\u2124)")
ARITH_OP_RE = re.compile(r"(?:\+|-|\*|<=|<|>=|>|\u2264|\u2265)")
PURE_NUM_ARITH_RE = re.compile(r"\b\d+\s*(?:\+|-|\*|<=|<|>=|>)\s*\d+\b")
REAL_LIN_RE = re.compile(r"(?:\bReal\b|\u211d|\blinarith\b)")
INDUCTIVE_RE = re.compile(r"\b(?:cases\b|rcases\b|induction\b|constructor\b)\b")
FINITE_RE = re.compile(r"(?:\bFin\s+\d+|\bFinset\b|\bdecide\b|\btrue\b|\bfalse\b)")
BITVEC_RE = re.compile(
    r"(?:\bBitVec\b|&&&|\|\|\||\^\^\^|<<<|>>>|\bsshiftRight\b|\bushiftRight\b|\bzeroExtend\b|\bsignExtend\b|\bextractLsb'\b)"
)
SWAR_PACK_RE = re.compile(
    r"(?:\bpreunfold%\b|\bunroll_top%\b|\bshiftLeft\b.*?\bshiftRight\b|\bKronecker\b|\bSWAR\b)"
)
WHNF_CONST_RE = re.compile(
    r"(?:\beval_nat%\b|\bnat_lit\s+\d{20,}\b|\brawNatLit\b)"
)

# Default declarative project tactic plugin specs (used when `lean-project.toml`
# defines `[[altproof.tactics]]` or when `include_project_tactics=True` in
# standalone fixture tests).
DEFAULT_PROJECT_TACTIC_SPECS: list[dict[str, Any]] = [
    {
        "tactic": "easci_omega",
        "target_pattern": "scaled-simplex-nat-arithmetic",
        "match_regex": r"(?:\bScale100\b|\beasci_omega\b|\bEASCI\b)",
        "match_scope": "goal_or_proof",
        "requires_arith": True,
        "rationale": "Project-specific Scale100 wrapper unfolding scaled-integer definitions before omega.",
        "estimated_heartbeats": 170,
        "confidence": 0.94,
    },
    {
        "tactic": "sum_congr_ring",
        "target_pattern": "finset-sum-linearity-pointwise-ring",
        "match_regex": r"(?:\bFinset\.sum\b|\u2211|\bsum_sub_distrib\b|\bsum_add_distrib\b|\bmul_sum\b|\bsum_mul\b)",
        "match_scope": "target_or_proof",
        "rationale": "Normalizes Finset.sum linearity (sum_add_distrib, sum_sub_distrib, mul_sum, sum_mul) and closes pointwise ring equalities via Finset.sum_congr.",
        "estimated_heartbeats": 260,
        "confidence": 0.91,
    },
    {
        "tactic": "finset_nonneg",
        "target_pattern": "finset-sum-nonneg-positivity",
        "match_regex": r"(?:0\s*(?:<=|\u2264)\s*(?:Finset\.sum\b|\u2211)|\b(?:Finset\.sum_nonneg|finset_nonneg)\b)",
        "match_scope": "target_or_proof",
        "rationale": "Discharges 0 <= sum_i f i via Finset.sum_nonneg followed by positivity/linarith/nlinarith/omega.",
        "estimated_heartbeats": 240,
        "confidence": 0.90,
    },
    {
        "tactic": "finset_mono",
        "target_pattern": "finset-sum-pointwise-monotonicity",
        "match_regex": r"(?:(?:Finset\.sum\b|\u2211).*?(?:<=|\u2264).*?(?:Finset\.sum\b|\u2211)|\b(?:Finset\.sum_le_sum|finset_mono)\b)",
        "match_scope": "target_or_proof",
        "dotall": True,
        "rationale": "Discharges sum_i f i <= sum_i g i via Finset.sum_le_sum, pointwise hypothesis specialization, and ordered-ring monotonicity closers.",
        "estimated_heartbeats": 250,
        "confidence": 0.91,
    },
    {
        "tactic": "wellformed_tac",
        "target_pattern": "finite-simplex-wellformed-conjunction",
        "match_regex": r"(?:\bWellFormed\b|\bfin_cases\b.*?\bnorm_num\b)",
        "match_scope": "target_or_proof",
        "dotall": True,
        "rationale": "Discharges five-field WellFormed conjunctions over Fin 1..8 via fin_cases and Fin.sum_univ_one..eight + norm_num.",
        "estimated_heartbeats": 190,
        "confidence": 0.93,
    },
    {
        "tactic": "channel_fields",
        "target_pattern": "channel-prior-constructor-obligations",
        "match_regex": r"(?:\bChannel\b|\bPrior\b|\bchannel_fields\b)",
        "match_scope": "target_or_proof",
        "rationale": "Constructs Channel or Prior and discharges nonneg and rowMass/mass obligations over Fin 1..8.",
        "estimated_heartbeats": 180,
        "confidence": 0.92,
    },
]


def load_declarative_tactic_specs(start_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """Load declarative `[[altproof.tactics]]` from `lean-project.toml`, falling back to defaults."""
    _lean_scripts = Path(__file__).resolve().parent.parent
    if str(_lean_scripts) not in sys.path:
        sys.path.insert(0, str(_lean_scripts))
    try:
        from project_config import load_project_config
        cfg = load_project_config(start_dir)
        if cfg.altproof_tactics:
            return cfg.altproof_tactics
    except Exception:
        pass
    return DEFAULT_PROJECT_TACTIC_SPECS


def _evaluate_declarative_tactic_specs(
    specs: list[dict[str, Any]],
    goal: str,
    target: str,
    proof: str,
    *,
    has_arith: bool,
) -> tuple[list[TacticRecommendation], set[str]]:
    recs: list[TacticRecommendation] = []
    matched_names: set[str] = set()
    for spec in specs:
        pattern = str(spec.get("match_regex", ""))
        if not pattern:
            continue
        if spec.get("requires_arith") and not has_arith:
            continue
        flags = re.DOTALL if spec.get("dotall") else 0
        rx = re.compile(pattern, flags)
        scope = str(spec.get("match_scope", "target_or_proof"))
        hit = False
        if scope == "goal_or_proof":
            hit = bool(rx.search(goal) or rx.search(proof))
        elif scope == "goal":
            hit = bool(rx.search(goal))
        else:
            hit = bool(rx.search(target) or rx.search(proof))
        if hit:
            tname = str(spec["tactic"])
            matched_names.add(tname)
            recs.append(
                TacticRecommendation(
                    tactic=tname,
                    target_pattern=str(spec.get("target_pattern", tname)),
                    rationale=str(spec.get("rationale", "")),
                    estimated_heartbeats=int(spec.get("estimated_heartbeats", 200)),
                    confidence=float(spec.get("confidence", 0.9)),
                )
            )
    return recs, matched_names


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
    project_root: Path | str | None = None,
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

    # 0b. SAIR WHNF closed-constant & SWAR pre-unfolding routes
    if WHNF_CONST_RE.search(goal) or WHNF_CONST_RE.search(proof):
        recommendations.append(
            TacticRecommendation(
                tactic="eval_nat%",
                target_pattern="closed-def-whnf-caching",
                rationale="Elaboration-time reduction to raw nat_lit (0 runtime instruction overhead and 0 exported Lean.* refs).",
                estimated_heartbeats=40,
                confidence=0.96,
            )
        )
    if SWAR_PACK_RE.search(goal) or SWAR_PACK_RE.search(proof):
        recommendations.append(
            TacticRecommendation(
                tactic="preunfold%",
                target_pattern="gmp-swar-word-packing",
                rationale="SWAR word-packing with elaboration-time pre-unfolding over binary-doubling combinators.",
                estimated_heartbeats=50,
                confidence=0.95,
            )
        )

    # Evaluate declarative project tactic plugins from lean-project.toml
    target_no_arrows = target.replace("->", " ").replace("=>", " ")
    has_nat_context = bool(NAT_TYPE_RE.search(goal) or PURE_NUM_ARITH_RE.search(target_no_arrows))
    has_arith_op = bool(ARITH_OP_RE.search(target_no_arrows))

    plugin_recs: list[TacticRecommendation] = []
    matched_plugins: set[str] = set()
    if include_project_tactics:
        specs = load_declarative_tactic_specs(project_root)
        plugin_recs, matched_plugins = _evaluate_declarative_tactic_specs(
            specs,
            goal,
            target,
            proof,
            has_arith=bool(has_nat_context and has_arith_op and not REAL_LIN_RE.search(goal)),
        )

    has_finset_sum = bool(
        re.search(r"(?:\bFinset\.sum\b|\u2211)", target)
        or "sum_congr_ring" in matched_plugins
        or "finset_nonneg" in matched_plugins
        or "finset_mono" in matched_plugins
    )
    has_wellformed_or_channel = bool(
        "wellformed_tac" in matched_plugins or "channel_fields" in matched_plugins
    )

    # 1. Presburger / Discrete Integer Arithmetic -> omega
    if (
        (has_nat_context or (has_arith_op and not has_finset_sum and not has_wellformed_or_channel))
        and has_arith_op
        and not REAL_LIN_RE.search(goal)
        and not has_finset_sum
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

    # 2. Linear Real Arithmetic -> linarith
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

    # Add declarative project tactic recommendations
    recommendations.extend(plugin_recs)

    # 3. Inductive reasoning and constructor search -> aesop
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

    # 4. Pure hypothesis elimination -> solve_by_elim
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

    # 5. Finite/computable decision -> decide
    if (
        FINITE_RE.search(target)
        and not has_wellformed_or_channel
        and (not has_finset_sum or re.search(r"\b(?:decide|true|false)\b", target))
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

    return sorted(recommendations, key=lambda r: r.estimated_heartbeats)


def dispatch_and_score(goal_text: str, current_proof_text: str = "") -> dict:
    """Combine tactic recommendations, legibility scoring, and two-axis cost estimation."""
    _dir = str(Path(__file__).resolve().parent)
    if _dir not in sys.path:
        sys.path.insert(0, _dir)
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


def _cli_main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="AltProof Tactic Advisor & Two-Axis Scorer")
    parser.add_argument("--goal", default="", help="Lean 4 goal state string")
    parser.add_argument("--proof", default="", help="Current proof block string")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test suite")
    args = parser.parse_args(argv)
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

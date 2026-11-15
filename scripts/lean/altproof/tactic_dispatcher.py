"""Tactic dispatcher v1 for AltProof automated tactic selection (A5).

Evaluates proof context, goal structure, and hypothesis types to recommend
optimal automated tactic substitutions:
  - Built-in core / Mathlib / SAIR tactics (`bv_decide`, `omega`, `linarith`,
    `aesop`, `solve_by_elim`, `decide`, `ring`, plus SAIR SWAR/WHNF routes
    `eval_nat%` and `preunfold%`)
  - Declarative project tactic plugins loaded from `lean-project.toml`
    (`[[altproof.tactics]]`) via `project_config.py` (with fallback defaults
    when `include_project_tactics=True` and no `lean-project.toml` is found).

Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

import math
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
WHNF_CONST_RE = re.compile(r"(?:\beval_nat%\b|\bnat_lit\s+\d{20,}\b|\brawNatLit\b)")

# Default declarative project tactic plugin specs (used when `lean-project.toml`
# defines `[[altproof.tactics]]` or when `include_project_tactics=True` in
# standalone fixture tests).
DEFAULT_PROJECT_TACTIC_SPECS: list[dict[str, Any]] = [
    {
        "tactic": "scaled_omega",
        "target_pattern": "scaled-simplex-nat-arithmetic",
        "match_regex": r"(?:\bScale100\b|\bscaled_omega\b|\bScaledInt\b)",
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
    if __package__:
        from .project_config import load_project_config
    else:
        from project_config import load_project_config
    cfg = load_project_config(start_dir)
    if cfg.altproof_tactics:
        return cfg.altproof_tactics
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
            heartbeat_value = spec.get("estimated_heartbeats", 200)
            confidence_value = spec.get("confidence", 0.9)
            try:
                if isinstance(heartbeat_value, bool) or not isinstance(heartbeat_value, (int, str)):
                    raise ValueError("heartbeats must be an integer")
                if isinstance(confidence_value, bool):
                    raise ValueError("confidence must be numeric")
                heartbeats = int(heartbeat_value)
                confidence = float(confidence_value)
                if heartbeats < 0 or not math.isfinite(confidence) or not 0 <= confidence <= 1:
                    raise ValueError("score out of range")
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"invalid tactic score for {tname}: {exc}") from exc
            matched_names.add(tname)
            recs.append(
                TacticRecommendation(
                    tactic=tname,
                    target_pattern=str(spec.get("target_pattern", tname)),
                    rationale=str(spec.get("rationale", "")),
                    estimated_heartbeats=heartbeats,
                    confidence=confidence,
                )
            )
    return recs, matched_names


def build_qf_bv_smt2_prescreen(goal_text: str, default_width: int = 64) -> str:
    """Generate declaration-only SMT scaffolding, not an encoded proof obligation."""
    target = _extract_goal_target(goal_text)
    explicit_widths = []
    for occurrence in re.finditer(r"\bBitVec\b", goal_text or ""):
        remainder = (goal_text or "")[occurrence.end() :]
        token = re.match(r"[ \t]+([^\s(),;:\[\]{}]+)", remainder)
        if token is None or re.fullmatch(r"[0-9]+", token.group(1)) is None:
            raise ValueError(
                "unsupported explicit BitVec width: expected a positive integer literal"
            )
        continuation = remainder[token.end() :].lstrip(" \t")
        if continuation.startswith(("+", "-", "*", "/", "%", "^", ".")):
            raise ValueError("unsupported explicit BitVec width expression")
        try:
            explicit_widths.append(int(token.group(1)))
        except ValueError as exc:
            raise ValueError("unsupported explicit BitVec width integer") from exc
    if len(set(explicit_widths)) > 1:
        raise ValueError("mixed BitVec widths are unsupported by this scaffold")
    width = explicit_widths[0] if explicit_widths else default_width
    if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
        raise ValueError("SMT BitVec width must be a positive integer")
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
    lines.append("; Goal target (comment only):")
    lines.extend("; " + line for line in target.splitlines())
    lines.append("; Advisory declaration-only scaffold.")
    lines.append("; No goal assertion is encoded; solver output cannot verify this goal.")
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
        try:
            scaffold_parameters = {
                "qf_bv_status": "declaration-only",
                "qf_bv_smt2": build_qf_bv_smt2_prescreen(goal),
            }
        except ValueError as exc:
            scaffold_parameters = {
                "qf_bv_status": "unsupported",
                "qf_bv_reason": str(exc),
            }
        recommendations.append(
            TacticRecommendation(
                tactic="bv_decide",
                target_pattern="fixed-width-bitvec-sat-reflection",
                rationale="Bit-blasted CaDiCaL LRAT reflection finisher for fixed-width BitVec / SWAR goals; zero Classical.choice overhead.",
                estimated_heartbeats=60,
                confidence=0.97,
                parameters=scaffold_parameters,
            )
        )

    # 0b. SAIR WHNF closed-constant, SWAR pre-unfolding, & 3-axiom sair_decide routes
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
    if re.search(r"\b(?:sair_decide|Lean\.ofReduceBool)\b", goal) or "sair_decide" in proof:
        recommendations.append(
            TacticRecommendation(
                tactic="sair_decide",
                target_pattern="sair_decide",
                rationale="Strict 3-axiom kernel-clean decision macro (rfl | decide +kernel | omega) with zero Lean.ofReduceBool.",
                estimated_heartbeats=70,
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

    # 2b. AltProof v0.5.0+ big-operator, monotonicity, congruence, redirect, & backchaining closers
    has_double_sum_side = any(
        len(re.findall(r"(?:\bFinset\.sum\b|\u2211)", side)) >= 2
        for side in re.split(r"(?:<=|\u2264|=)", target)
    )
    if (
        has_double_sum_side and not re.search(r"(?:<=|\u2264)", target_no_arrows)
    ) or re.search(r"\b(?:Finset\.sum_comm|calc_ring_sum)\b", proof):
        recommendations.append(
            TacticRecommendation(
                tactic="calc_ring_sum",
                target_pattern="double-sum-commutation-and-separable-product",
                rationale="Discharges swapped double sums (Finset.sum_comm) and separable double-sum factorizations in one step.",
                estimated_heartbeats=255,
                confidence=0.92,
            )
        )

    if (
        re.search(r"\bFinset\.sum_eq_single\b", proof)
        and re.search(r"\b(?:if|ite)\b", proof)
    ) or re.search(
        r"(?:\bFinset\.sum\b|\u2211)[\s\S]*?\bif\b[\s\S]*?\bthen\b[\s\S]*?\belse\s+0\b",
        target,
    ):
        recommendations.append(
            TacticRecommendation(
                tactic="simp only [Finset.sum_ite_eq, Finset.sum_ite_eq', Finset.mem_univ, \u2193reduceIte]",
                target_pattern="kronecker-delta-finset-sum-collapse",
                rationale="Collapses Kronecker-delta Finset.sum over if-then-else via Finset.sum_ite_eq without manual sum_eq_single case splits.",
                estimated_heartbeats=175,
                confidence=0.94,
            )
        )

    if (
        re.search(r"(?:<=|\u2264|<)", target_no_arrows)
        and re.search(r"(?:\*|/)", target_no_arrows)
        and not has_finset_sum
        and not has_nat_context
        and not has_wellformed_or_channel
    ) or re.search(r"\bgcongr_pos\b", proof):
        recommendations.append(
            TacticRecommendation(
                tactic="gcongr_pos",
                target_pattern="ordered-ring-monotonicity-congruence",
                rationale="Applies gcongr and automatically discharges positivity/arithmetic side-conditions.",
                estimated_heartbeats=230,
                confidence=0.89,
            )
        )

    has_pure_eq = bool(
        "=" in target_no_arrows
        and not re.search(r"(?:<=|>=|!=|\u2264|\u2265|\u2260)", target_no_arrows)
    )
    if (
        has_pure_eq
        and not has_finset_sum
        and not has_nat_context
        and not REAL_LIN_RE.search(goal)
        and not BITVEC_RE.search(goal)
        and not has_wellformed_or_channel
    ) or re.search(r"\b(?:eqsat_rw|egg_rw)\b", proof):
        recommendations.append(
            TacticRecommendation(
                tactic="eqsat_rw",
                target_pattern="eqsat-congruence-closure",
                rationale="Pure-Lean bidirectional congruence-closure rewrite saturation (Eq.trans / congrArg) with 0 external FFI.",
                estimated_heartbeats=200,
                confidence=0.87,
            )
        )

    if (
        (
            re.search(r"(?:\bby_contra\b|\bFalse\b|\bNot\b|\u00ac)", goal + " " + proof)
            or re.search(r"&&[\s\S]*?=\s*true\b", goal + " " + proof)
        )
        and not has_finset_sum
        and not has_wellformed_or_channel
    ) or re.search(r"\bcontra_direct\b", proof):
        recommendations.append(
            TacticRecommendation(
                tactic="contra_direct",
                target_pattern="redirect-by-contradiction",
                rationale="Constructive contradiction redirect normalizing decidable/Bool goals without Classical.choice.",
                estimated_heartbeats=165,
                confidence=0.90,
            )
        )

    if (
        len(re.findall(r"\bapply\b", proof)) >= 2 and not INDUCTIVE_RE.search(proof)
    ) or re.search(r"\bbackchain\b", proof):
        recommendations.append(
            TacticRecommendation(
                tactic="backchain",
                target_pattern="backchain-solve-by-elim",
                rationale="Core-only bounded SolveByElim backchaining (maxDepth := 6) without aesop import overhead.",
                estimated_heartbeats=210,
                confidence=0.86,
            )
        )

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
    if __package__:
        from .cost_ranker import cost
    else:
        from cost_ranker import cost
    if __package__:
        from .legibility import RENDERABLE_PATTERNS, score_block
    else:
        from legibility import RENDERABLE_PATTERNS, score_block

    recs = recommend_tactics(goal_text, current_proof_text)
    leg = score_block(current_proof_text or "", RENDERABLE_PATTERNS)
    lines = max(1, leg["steps"])
    baseline_cost_x10 = round(
        cost(lines=lines, shared_lemmas=0, upstream=False, kernel_cost=0.0) * 10
    )
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
        r1 = dispatch_and_score(
            "|- Finset.sum s (fun i => f i) <= Finset.sum s (fun i => g i)",
            "apply Finset.sum_le_sum",
        )
        assert any(x["tactic"] == "finset_mono" for x in r1["recommendations"]), r1
        r2 = dispatch_and_score(
            "|- 0 <= Finset.sum s (fun i => (f i)^2)", "apply Finset.sum_nonneg"
        )
        assert any(x["tactic"] == "finset_nonneg" for x in r2["recommendations"]), r2
        r3 = dispatch_and_score(
            "|- Finset.sum s (fun i => a * f i) = a * Finset.sum s (fun i => f i)",
            "rw [Finset.mul_sum]",
        )
        assert any(x["tactic"] == "sum_congr_ring" for x in r3["recommendations"]), r3
        r4 = dispatch_and_score("x y : BitVec 64 |- (x ^^^ y) ^^^ y = x", "bv_decide")
        assert r4["best_tactic"] == "bv_decide", r4
        r5 = dispatch_and_score(
            "|- Finset.sum s (fun i => Finset.sum t (fun j => f i * g j)) = (Finset.sum s f) * (Finset.sum t g)",
            "rw [Finset.sum_comm]",
        )
        assert r5["best_tactic"] == "calc_ring_sum", r5
        r6 = dispatch_and_score(
            "|- Finset.sum s (fun i => if i = j then f i else 0) = f j",
            "rw [Finset.sum_eq_single j]\nif h : j = j then simp else simp",
        )
        assert "Finset.sum_ite_eq" in (r6["best_tactic"] or ""), r6
        r7 = dispatch_and_score("a b c : Alpha |- f (g a) = f b", "eqsat_rw [h1, h2]")
        assert any(x["tactic"] == "eqsat_rw" for x in r7["recommendations"]), r7
        r8 = dispatch_and_score("P Q R : Prop |- R", "apply h2\napply h1\nexact hp")
        assert any(x["tactic"] == "backchain" for x in r8["recommendations"]), r8
        print("altproof_tactic_advisor: self-test PASSED (8/8 checks)")
        return 0
    print(json.dumps(dispatch_and_score(args.goal, args.proof), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())

"""Cost ranker v0 - the extraction-outranks heuristic (ballot B1).

The weights are a PLUGGABLE FAMILY (B1's amendment): this module
ships the v1 default member. The cost model per design note 3/10:

    cost = length_term - reuse_bonus - upstream_bonus

with the extraction-outranks property: a proof whose content moved
into named shared lemmas outranks a longer inline proof even at
modest line savings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Weights:
    """One member of the heuristic family. Experiment via subclasses."""

    per_line: float = 0.1  # cost per proof line
    per_shared_lemma: float = 5.0  # bonus per named shared lemma extracted
    upstream_bonus: float = 20.0  # extra bonus when Mathlib-absent (library-worthy)
    kernel_cost_weight: float = 1.0  # weight per kernel-cost second (SAIR bridge A1)


@dataclass
class TwoAxisScore:
    """Two-axis evaluation node per ALT_PROOF_SAIR_BRIDGE A1/A4."""

    elegance_cost: float
    kernel_cost: float
    legibility: str


def cost(
    lines: float,
    shared_lemmas: int = 0,
    upstream: bool = False,
    w: Weights | None = None,
    kernel_cost: float = 0.0,
) -> float:
    w = w or Weights()
    c = lines * w.per_line
    c -= shared_lemmas * w.per_shared_lemma
    if upstream:
        c -= w.upstream_bonus
    c += kernel_cost * w.kernel_cost_weight
    return c


def ranks_above(
    before_lines: float,
    after_lines: float,
    after_lemmas: int = 0,
    after_upstream: bool = False,
    w: Weights | None = None,
    before_kernel_cost: float = 0.0,
    after_kernel_cost: float = 0.0,
) -> bool:
    """The B1 calibration predicate: the AFTER state must cost less."""
    w = w or Weights()
    return cost(
        after_lines, after_lemmas, after_upstream, w, kernel_cost=after_kernel_cost
    ) < cost(before_lines, 0, False, w, kernel_cost=before_kernel_cost)


def evaluate_two_axis_candidate(
    before: TwoAxisScore,
    after: TwoAxisScore,
    w: Weights | None = None,
) -> dict:
    """Evaluates a candidate proof against its baseline across the two-axis model."""
    w = w or Weights()
    before_cost = before.elegance_cost + before.kernel_cost * w.kernel_cost_weight
    after_cost = after.elegance_cost + after.kernel_cost * w.kernel_cost_weight

    dominates = (
        (after.elegance_cost <= before.elegance_cost and after.kernel_cost < before.kernel_cost)
        or (after.elegance_cost < before.elegance_cost and after.kernel_cost <= before.kernel_cost)
    )
    regressed = (
        after.elegance_cost > before.elegance_cost and after.kernel_cost > before.kernel_cost
    )

    return {
        "before_total_cost": round(before_cost, 4),
        "after_total_cost": round(after_cost, 4),
        "improved": after_cost < before_cost,
        "dominates": dominates,
        "regressed": regressed,
        "tradeoff": not dominates and not regressed and (after_cost != before_cost),
        "elegance_delta": round(after.elegance_cost - before.elegance_cost, 4),
        "kernel_delta": round(after.kernel_cost - before.kernel_cost, 4),
        "legibility": after.legibility,
    }


# --------------------------------------------------------------------------
# Proposal 9B: `nanoproof` Hardest-Subgoal Bottleneck Scorer & `LeanProgress` Adapter
# --------------------------------------------------------------------------

import re as _re


def score_subgoal_bottleneck(subgoal_scores: list[float]) -> float:
    """`nanoproof` (`prover.py:138-159`) hardest-subgoal bottleneck transitions:
    an AND-node (tactic splitting a goal into k subgoals) is only as good as its
    HARDEST unsolved subgoal (`min(subgoal_scores)`). Returns 1.0 when `subgoal_scores`
    is empty (all subgoals solved)."""
    if not subgoal_scores:
        return 1.0
    return float(min(subgoal_scores))


def _normalize_goal_state_for_cycle(state_text: str) -> str:
    """Normalize whitespace and alpha-rename numeric hypothesis suffixes to detect semantic cycles."""
    lines = [
        " ".join(ln.strip().split())
        for ln in (state_text or "").splitlines()
        if ln.strip()
    ]
    return "\n".join(lines)


def is_cycling(state_history: list[str], current_state: str) -> bool:
    """`nanoproof` (`prover.py:210-241`) semantic cycle detector: returns True if
    `current_state` is equivalent to any ancestor state in `state_history`."""
    norm_curr = _normalize_goal_state_for_cycle(current_state)
    if not norm_curr:
        return False
    return any(
        _normalize_goal_state_for_cycle(prev) == norm_curr
        for prev in state_history
    )


def estimate_remaining_steps(goal_text: str) -> int:
    """Heuristic remaining-step estimator when no external `LeanProgress` endpoint is configured."""
    g = (goal_text or "").strip()
    if not g or g == "no goals":
        return 0
    steps = 1
    steps += len(_re.findall(r"(?:\bforall\b|\u2200|\bexists\b|\u2203)", g))
    steps += len(_re.findall(r"(?:/\\|\\/|&&|\|\||\u2227|\u2228|<->|\u2194)", g))
    steps += len(_re.findall(r"(?:\bFinset\.sum\b|\u2211|\bNat\.rec\b)", g))
    return max(1, min(steps, 20))


def leanprogress_scorer(
    goal: str,
    prefix: str = "",
    tactic: str = "",
    endpoint: str | None = None,
    model_fn=None,
) -> float:
    """`LeanDojo-v2` `LeanProgress` remaining-step predictor adapter (`lean_progress.py`).
    Returns a normalized progress score in `(0.0, 1.0]` where higher means fewer remaining
    steps (`1.0 / (1.0 + remaining_steps)`)."""
    if model_fn is not None:
        rem = float(model_fn(goal=goal, prefix=prefix, tactic=tactic))
        return round(1.0 / (1.0 + max(0.0, rem)), 4)
    rem_steps = estimate_remaining_steps(goal)
    return round(1.0 / (1.0 + float(rem_steps)), 4)


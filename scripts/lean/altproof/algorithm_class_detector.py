"""Algorithm-class candidate detector v1 (A7).

Detects algorithmic substitution opportunities in Lean 4 definitions and
proofs where alternative computation or proof strategies yield orders-of-magnitude
kernel-step or proof-complexity reductions.

Pattern classes:
1. EXPONENTIAL_ENUMERATION:
   Exhaustive permutation or power-set traversals (e.g. `Equiv.Perm`,
   `Finset.powerset`, naive tree recursion) that admit dynamic programming
   or closed-form combinatorial reduction.
2. NESTED_WELLFOUNDED_RECURSION:
   Repeated branching `WellFounded.fix` calls without memoization or accumulator,
   substitutable with tail-recursive or tabular loops.
3. LIST_PIPELINE_OVERHEAD:
   Hot-path chains of `List.range`, `List.map`, `List.foldl`, and `List.getD`
   substitutable with direct structural `Nat.rec` or `Array`/`Finset` folds.
4. INDUCTIVE_REDUCTION_CHAIN:
   Repeated inductive unwinding chains substitutable with single-step
   algebraic invariants or reflection lemmas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

PERM_ENUM_RE = re.compile(r"\b(?:Equiv\.Perm|Finset\.powerset|Finset\.univ\.filter)\b")
WF_BRANCH_RE = re.compile(r"\b(?:WellFounded\.fix|wfRec|decreasing_by)\b")
PIPELINE_RE = re.compile(r"\bList\.range\b[^\n]*?(?:List\.(?:map|foldl|filter)|\.(?:map|foldl|filter))\b")
ACC_OPP_RE = re.compile(r"\bdef\s+(\w+)[^:=]*?:=[^\n]*?\b(\1)\b[^\n]*?\b(\1)\b")
TYPE_SPECIALIZATION_RE = re.compile(r"\b\w+\s*:\s*(?:[αa-zA-Z0-9_]+\s*→\s*ℝ|\(g\s*:\s*[αa-zA-Z0-9_]+\s*→\s*ℝ\))\b")
TACTIC_BLOAT_RE = re.compile(r"\bunfold\s+\w+[^\n]*\n\s*refine\b")
SWAR_BIT_PACKING_SUBSTITUTION_RE = re.compile(
    r"(?:\bmatch\b[\s\S]{0,240}?\|[^\n]+=>[^\n]+\n\s*\|[^\n]+=>[^\n]+\n\s*\|[^\n]+=>|"
    r"\b(?:nibble|bitplane|grayCode|xorParity|packNibbles|unpackNibbles)\b|"
    r"(?:>>>|<<<)\s*(?:4|8|12|16|24|32)\b[^\n]*?(?:&&&|\|\|\||\^\^\^))"
)
CLASSICAL_SPLIT_LEAK_RE = re.compile(
    r"(?:\bsplit\b[\s\S]{0,120}?&&|\bClassical\.choice\b|\bby_cases\b[^\n]*\bdecide\b)"
)


@dataclass
class AlgorithmCandidate:
    """One algorithm-class substitution candidate."""

    theorem: str
    route: str = "algorithm-class-substitution"
    pattern: str = ""
    evidence: str = ""
    suggested_replacement: str = ""
    estimated_kernel_speedup: float = 1.0
    legibility_tradeoff: str = "medium"  # high | medium | low
    details: dict = field(default_factory=dict)


def detect_algorithm_opportunities(source_text: str, theorem: str = "") -> list[AlgorithmCandidate]:
    """Analyze Lean 4 text for algorithm-class substitution targets."""
    candidates: list[AlgorithmCandidate] = []
    text = source_text or ""

    # 1. Exponential enumeration
    for m in PERM_ENUM_RE.finditer(text):
        matched = m.group(0)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                pattern="exponential-enumeration",
                evidence=matched,
                suggested_replacement="dynamic-programming-or-row-factorization",
                estimated_kernel_speedup=20.0,
                legibility_tradeoff="low",  # usually less verbose, more compact
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 2. Nested WellFounded recursion
    for m in WF_BRANCH_RE.finditer(text):
        matched = m.group(0)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                pattern="nested-wf-recursion",
                evidence=matched,
                suggested_replacement="structural-nat-rec-or-accumulator-tailrec",
                estimated_kernel_speedup=5.0,
                legibility_tradeoff="medium",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 3. List pipeline overhead
    for m in PIPELINE_RE.finditer(text):
        matched = m.group(0)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                pattern="list-pipeline-overhead",
                evidence=matched,
                suggested_replacement="direct-finset-or-structural-fold",
                estimated_kernel_speedup=3.0,
                legibility_tradeoff="high",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 4. Binary branching without accumulator
    for m in ACC_OPP_RE.finditer(text):
        matched_fn = m.group(1)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem or matched_fn,
                pattern="binary-recursion-branching",
                evidence=matched_fn,
                suggested_replacement="linear-accumulator-tail-recursion",
                estimated_kernel_speedup=10.0,
                legibility_tradeoff="medium",
                details={"function": matched_fn, "line_offset": m.start()},
            )
        )

    # 5. Type specialization bottleneck (e.g. hardcoded Real instead of normed group E)
    for m in TYPE_SPECIALIZATION_RE.finditer(text):
        matched = m.group(0)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                pattern="type-specialization-bottleneck",
                evidence=matched,
                suggested_replacement="generalize-to-normed-group-or-monoid-E",
                estimated_kernel_speedup=1.8,
                legibility_tradeoff="high",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 6. Tactic step bloat (unfold + refine instead of direct term)
    for m in TACTIC_BLOAT_RE.finditer(text):
        matched = m.group(0)
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                pattern="tactic-step-bloat",
                evidence=matched,
                suggested_replacement="direct-term-exact-or-fun-composition",
                estimated_kernel_speedup=1.5,
                legibility_tradeoff="high",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 7. SWAR bit-packing substitution (multi-branch lookup tables, nibble/bitplane loops, Gray-code/XOR parity)
    for m in SWAR_BIT_PACKING_SUBSTITUTION_RE.finditer(text):
        matched = m.group(0).strip().splitlines()[0][:80]
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                route="algorithm-class-substitution",
                pattern="SWAR_BIT_PACKING_SUBSTITUTION",
                evidence=matched,
                suggested_replacement="branchless-swar-bitvec-packing-with-bv_decide",
                estimated_kernel_speedup=12.0,
                legibility_tradeoff="medium",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    # 8. Constructive decidable reduction (Classical.choice leakage from split on &&)
    for m in CLASSICAL_SPLIT_LEAK_RE.finditer(text):
        matched = m.group(0).strip().splitlines()[0][:80]
        candidates.append(
            AlgorithmCandidate(
                theorem=theorem,
                route="constructive-decidable-reduction",
                pattern="CONSTRUCTIVE_DECIDABLE_REDUCTION",
                evidence=matched,
                suggested_replacement="Bool.and_eq_true-or-decide_eq_true_eq-or-bv_decide",
                estimated_kernel_speedup=2.5,
                legibility_tradeoff="high",
                details={"match": matched, "line_offset": m.start()},
            )
        )

    return candidates

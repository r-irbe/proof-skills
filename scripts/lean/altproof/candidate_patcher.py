"""Candidate patcher v1 for AltProof algorithm-class substitution (A4).

Applies structural substitutions based on EvaluatedCandidate definitions,
producing candidate transformed Lean 4 sources with receipt manifests.
Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
import sys as _sys; from pathlib import Path as _Path
if str(_Path(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
if __package__:
    from .candidate_evaluator import EvaluatedCandidate
else:
    from candidate_evaluator import EvaluatedCandidate


@dataclass
class PatchReceipt:
    """Structural substitution receipt; no Lean verification is performed."""

    theorem: str
    pattern: str
    original_snippet: str
    patched_snippet: str
    lines_saved: float
    estimated_speedup: float
    status: str = "applied-unverified"


_PIPELINE_PATTERN = re.compile(
    r"\(List\.range\s+(\w+)\)\.map\s+([^\n|]+)\s*\|\>\.foldl\s*\(\s*\u00b7\s*\+\s*\u00b7\s*\)\s*0(?![\w.])"
)

def patch_list_pipeline(source_text: str) -> tuple[str, list[PatchReceipt]]:
    """Propose Finset folds; callers must verify types and equivalence with Lean."""
    receipts: list[PatchReceipt] = []
    
    # A mapped range folded with addition and zero becomes a proposed Finset sum.
    pipeline_pattern = _PIPELINE_PATTERN

    def repl(m: re.Match) -> str:
        var = m.group(1)
        f = m.group(2).strip()
        patched = f"Finset.sum (Finset.range {var}) {f}"
        receipts.append(
            PatchReceipt(
                theorem="inferred",
                pattern="list-pipeline-overhead",
                original_snippet=m.group(0),
                patched_snippet=patched,
                lines_saved=float(m.group(0).count("\n") - patched.count("\n")),
                estimated_speedup=3.5,
            )
        )
        return patched

    new_text = pipeline_pattern.sub(repl, source_text)
    return new_text, receipts


def apply_candidate_patch(
    source_text: str,
    evaluated_candidate: EvaluatedCandidate,
) -> tuple[str, PatchReceipt | None]:
    """Apply transformation corresponding to a specific evaluated candidate."""
    cand = evaluated_candidate.candidate
    text = source_text

    # Detector offsets are character positions in this exact source, not line numbers.
    # Refuse stale or unlocated candidates instead of searching other declarations.
    offset = cand.details.get("line_offset")
    if (cand.pattern == "list-pipeline-overhead" and type(offset) is int
            and 0 <= offset < len(text) and cand.evidence
            and text.startswith(cand.evidence, offset)):
        matches = [m for m in _PIPELINE_PATTERN.finditer(text)
                   if m.start() <= offset and offset + len(cand.evidence) <= m.end()]
        if len(matches) == 1:
            match = matches[0]
            replacement, receipts = patch_list_pipeline(match.group(0))
            if len(receipts) == 1:
                receipt = receipts[0]
                receipt.theorem = cand.theorem or receipt.theorem
                return text[:match.start()] + replacement + text[match.end():], receipt

    # Unsupported or unmatched candidates have no source transformation.
    receipt = PatchReceipt(
        theorem=cand.theorem,
        pattern=cand.pattern,
        original_snippet=cand.evidence,
        patched_snippet=cand.evidence,
        lines_saved=0.0,
        estimated_speedup=cand.estimated_kernel_speedup,
        status="not-applied",
    )
    return text, receipt


@dataclass
class SimplePatchResult:
    """Result of a direct candidate text replacement."""

    patched: bool
    transformed_text: str
    lines_before: int
    lines_after: int


def patch_candidate(source_text: str, target_pattern: str, replacement: str) -> SimplePatchResult:
    """Replace occurrences of target_pattern with replacement."""
    if target_pattern and target_pattern in source_text:
        new_text = source_text.replace(target_pattern, replacement)
        return SimplePatchResult(
            patched=new_text != source_text,
            transformed_text=new_text,
            lines_before=source_text.count("\n") + 1,
            lines_after=new_text.count("\n") + 1,
        )
    return SimplePatchResult(
        patched=False,
        transformed_text=source_text,
        lines_before=source_text.count("\n") + 1,
        lines_after=source_text.count("\n") + 1,
    )

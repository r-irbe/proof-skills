"""Deterministic regex-based grader.

Given an ``output_text`` (the model invocation result) and an ``expected``
dict from a YAML case, this grader checks:

* every pattern in ``expected.contains`` matches (regex, multiline);
* no pattern in ``expected.not_contains`` matches.

It does not call any LLM. It is intentionally dumb — the kind of grader
you wire up first because it has zero variance and zero cost.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GradeResult:
    """Outcome of grading a single case."""

    passed: bool
    score: float                       # 0.0 .. 1.0
    matched: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    forbidden_hit: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": round(self.score, 4),
            "matched": self.matched,
            "missing": self.missing,
            "forbidden_hit": self.forbidden_hit,
            "notes": self.notes,
        }


def _as_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    return [str(x) for x in v]


def grade(output_text: str, expected: dict[str, Any]) -> GradeResult:
    """Apply the deterministic contract.

    ``expected`` shape::

        contains:        [regex, regex, ...]   # all must match
        not_contains:    [regex, regex, ...]   # none may match

    A case with neither key trivially passes (score=1.0) but is flagged
    in ``notes`` so it shows up in summaries as a smoke-only case.
    """
    contains = _as_list(expected.get("contains"))
    not_contains = _as_list(expected.get("not_contains"))

    matched: list[str] = []
    missing: list[str] = []
    for pat in contains:
        if re.search(pat, output_text, flags=re.MULTILINE | re.DOTALL):
            matched.append(pat)
        else:
            missing.append(pat)

    forbidden_hit: list[str] = []
    for pat in not_contains:
        if re.search(pat, output_text, flags=re.MULTILINE | re.DOTALL):
            forbidden_hit.append(pat)

    total = len(contains) + len(not_contains)
    if total == 0:
        return GradeResult(
            passed=True, score=1.0,
            notes="no assertions: smoke-only case",
        )

    correct = len(matched) + (len(not_contains) - len(forbidden_hit))
    score = correct / total
    passed = (not missing) and (not forbidden_hit)
    return GradeResult(
        passed=passed,
        score=score,
        matched=matched,
        missing=missing,
        forbidden_hit=forbidden_hit,
    )

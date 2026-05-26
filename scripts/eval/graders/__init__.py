"""Graders for the prototype eval runner.

Each grader is a callable: ``grade(output_text, expected) -> GradeResult``.
"""

from .deterministic import GradeResult, grade as deterministic_grade

__all__ = ["GradeResult", "deterministic_grade"]

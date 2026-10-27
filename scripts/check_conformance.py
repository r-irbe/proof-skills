#!/usr/bin/env python3
"""Compatibility entrypoint forwarding to scripts/skill-audit/check_conformance.py."""
from __future__ import annotations
import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "skill-audit" / "check_conformance.py"
    runpy.run_path(str(target), run_name="__main__")

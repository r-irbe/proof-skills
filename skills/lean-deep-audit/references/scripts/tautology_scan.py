#!/usr/bin/env python3
"""Thin wrapper delegating to canonical scripts/lean/tautology_scan.py."""
import importlib.util
from pathlib import Path
import runpy
import sys

CANONICAL = Path(__file__).resolve().parents[4] / "scripts" / "lean" / "tautology_scan.py"
if __name__ == "__main__":
    runpy.run_path(str(CANONICAL), run_name="__main__")
else:
    _spec = importlib.util.spec_from_file_location("_canonical_tautology_scan", CANONICAL)
    _mod = importlib.util.module_from_spec(_spec)
    assert _spec and _spec.loader
    _spec.loader.exec_module(_mod)
    globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})

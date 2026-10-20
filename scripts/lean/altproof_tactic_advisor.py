#!/usr/bin/env python3
"""Backward-compatible shim -> scripts/lean/altproof/tactic_dispatcher.py."""
from pathlib import Path as _Path
import sys as _sys

_ALTPROOF_DIR = _Path(__file__).resolve().parent / "altproof"
if str(_ALTPROOF_DIR) not in _sys.path:
    _sys.path.insert(0, str(_ALTPROOF_DIR))
_CANON_FILE = _ALTPROOF_DIR / "tactic_dispatcher.py"
exec(compile(_CANON_FILE.read_text(encoding="utf-8"), str(_CANON_FILE), "exec"), globals())

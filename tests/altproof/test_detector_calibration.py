"""Detector calibration regression (S12): pinned samples, pinned verdicts.

Every detector change must keep these classifications stable. Each
sample was classified in a measured audit (65% v1 noise audit, the
pilot reviews, the v2/v3 gates); the fixture pins the verdicts so a
future detector version that flips one fails here with the sample
name. Add samples when a new measured class appears.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
_mod_spec = importlib.util.spec_from_file_location(
    "extraction_detector", _TOOLS / "extraction_detector.py"
)
assert _mod_spec is not None and _mod_spec.loader is not None
ed = importlib.util.module_from_spec(_mod_spec)
sys.modules["extraction_detector"] = ed
_mod_spec.loader.exec_module(ed)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "calibration_samples.json"
SAMPLES = json.loads(FIXTURE.read_text(encoding="utf-8"))["samples"]


def _verdict(sample):
    cands = ed.detect_v3(
        sample["block"], "calibration",
        file_symbols=set(sample.get("file_symbols", [])),
    )
    return "candidate" if cands else "clean"


@pytest.mark.parametrize("sample", SAMPLES, ids=[s["name"] for s in SAMPLES])
def test_calibration_sample(sample):
    if sample.get("known_gap") and _verdict(sample) != sample["expect"]:
        pytest.xfail(sample["known_gap"])
    assert _verdict(sample) == sample["expect"], (
        f"detector flipped on {sample['name']}: expected {sample['expect']}"
    )

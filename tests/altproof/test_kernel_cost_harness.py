"""Unit tests for tools/altproof/kernel_cost_harness.py (A2).
Strict 7-bit ASCII only (INV-001).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"))

from kernel_cost_harness import (  # noqa: E402
    KernelMeasurement,
    parse_heartbeats_from_output,
)


def test_parse_heartbeats_from_output():
    out1 = "info: elaboration complete\nheartbeats count: 14285\nok"
    assert parse_heartbeats_from_output(out1) == 14285

    out2 = "(deterministic) maximum heartbeats (50000) exceeded"
    assert parse_heartbeats_from_output(out2) == 50000

    out3 = "no heartbeat info present"
    assert parse_heartbeats_from_output(out3) == 0


def test_kernel_measurement_dataclass():
    m = KernelMeasurement(
        success=True,
        wall_clock_sec=0.1234,
        heartbeats_consumed=542,
        error_messages=[],
        warning_messages=["unused variable x"],
    )
    assert m.success is True
    assert m.heartbeats_consumed == 542
    assert len(m.warning_messages) == 1

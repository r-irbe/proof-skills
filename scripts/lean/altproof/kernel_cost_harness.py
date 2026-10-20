"""AltProof Kernel Cost Measurement Harness (A2).

Profiles Lean 4 theorem elaboration and kernel reduction heartbeats
and wall-clock duration via `lake env lean`.
Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KernelMeasurement:
    """Measurements for a kernel elaboration run."""

    success: bool
    wall_clock_sec: float
    heartbeats_consumed: int
    error_messages: list[str]
    warning_messages: list[str]


def parse_heartbeats_from_output(output: str) -> int:
    """Extract heartbeat counts from lean diagnostic output if present."""
    match = re.search(r"heartbeats\s+count:\s*(\d+)", output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Check for maxHeartbeats exceeded
    match_exceeded = re.search(r"maximum heartbeats\s*\((\d+)\)", output, re.IGNORECASE)
    if match_exceeded:
        return int(match_exceeded.group(1))
    return 0


def measure_lean_snippet(
    snippet: str,
    cwd: Path | str | None = None,
    timeout_sec: float = 30.0,
) -> KernelMeasurement:
    """Elaborate a self-contained Lean snippet and measure reduction cost."""
    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            ["lake", "env", "lean", "--stdin"],
            input=snippet,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
        elapsed = time.perf_counter() - start_time
        combined_output = proc.stdout + "\n" + proc.stderr
        heartbeats = parse_heartbeats_from_output(combined_output)

        errors = [line for line in combined_output.splitlines() if "error:" in line.lower()]
        warnings = [line for line in combined_output.splitlines() if "warning:" in line.lower()]

        return KernelMeasurement(
            success=(proc.returncode == 0),
            wall_clock_sec=round(elapsed, 4),
            heartbeats_consumed=heartbeats,
            error_messages=errors,
            warning_messages=warnings,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start_time
        return KernelMeasurement(
            success=False,
            wall_clock_sec=round(elapsed, 4),
            heartbeats_consumed=-1,
            error_messages=["Elaboration timed out"],
            warning_messages=[],
        )

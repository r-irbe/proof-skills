"""Golden tests for the teaching-priority ranking (S7 completion)."""

import importlib.util
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
_mod_spec = importlib.util.spec_from_file_location(
    "teaching_priority", _TOOLS / "teaching_priority.py"
)
assert _mod_spec is not None and _mod_spec.loader is not None
tp = importlib.util.module_from_spec(_mod_spec)
sys.modules["teaching_priority"] = tp
_mod_spec.loader.exec_module(tp)


def _report(tmp_path: Path, verbose_a: str, saves_a: int, saves_b: int) -> Path:
    d = tmp_path / "reports"
    d.mkdir()
    (d / "F.lean.md").write_text(
        "#### `thmA` (lines 1-10)"
        + verbose_a
        + chr(10)
        + "  - could be named once"
        + chr(10)
        + f"    (estimated saving ~{saves_a} lines; cost 1.00 -> 0.00)."
        + chr(10)
        + "#### `thmB` (lines 20-30)"
        + chr(10)
        + "  - could be named once"
        + chr(10)
        + f"    (estimated saving ~{saves_b} lines; cost 1.00 -> 0.00)."
        + chr(10),
        encoding="utf-8",
    )
    (d / "INDEX.md").write_text("# index" + chr(10), encoding="utf-8")
    return d


def test_low_verbose_multiplies_priority(tmp_path):
    d = _report(tmp_path, " . verbose score 0.20", 10, 10)
    rows = tp.priority_list(d)
    # same saving; the low-verbose block (default 0.5 for unscored) wins
    assert rows[0]["theorem"] == "thmA"
    assert rows[0]["priority"] > rows[1]["priority"]


def test_index_md_skipped(tmp_path):
    d = _report(tmp_path, "", 5, 3)
    files = {r["file"] for r in tp.priority_list(d)}
    assert "INDEX" not in str(files)


def test_sair_kernel_cost_priority(tmp_path):
    d = tmp_path / "reports_sair"
    d.mkdir()
    (d / "G.lean.md").write_text(
        "#### `thmSmall` (lines 1-10) . verbose score 0.10\n"
        "  - route: algorithm-class-substitution\n"
        "    (estimated saving ~2 lines; cost 1.00 -> 0.00; kernel delta ~50.0).\n"
        "#### `thmLarge` (lines 20-30) . verbose score 0.10\n"
        "  - route: extraction-general\n"
        "    (estimated saving ~10 lines; cost 1.00 -> 0.00).\n",
        encoding="utf-8",
    )
    rows_std = tp.priority_list(d, kernel_weight=1.0)
    # With kernel delta ~50.0 added to saving ~2 lines (total 52), thmSmall outranks thmLarge (saving 10)
    assert rows_std[0]["theorem"] == "thmSmall"
    assert rows_std[0]["kernel_saving"] == 50.0

    rendered = tp.render(rows_std)
    assert "kernel_saving" in rendered
    assert "~50.0" in rendered

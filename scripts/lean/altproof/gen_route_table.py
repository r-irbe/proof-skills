"""Generate route-table.json from route_definitions (design note 5b).

The generated artifact is pinned by tests/tools/test_altproof_route_table.py;
hand-edited route-table.json is a defect by construction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from route_definitions import ROUTES


def generate() -> dict:
    by_family: dict[str, list[dict]] = {}
    for r in ROUTES:
        by_family.setdefault(r["family"], []).append(r)
    return {
        "version": 1,
        "families": by_family,
        "total": len(ROUTES),
    }


def main() -> int:
    payload = json.dumps(generate(), indent=2, sort_keys=True) + "\n"
    out1 = Path(__file__).resolve().parent / "route-table.json"
    out1.write_text(payload, encoding="utf-8")
    for p in Path(__file__).resolve().parents:
        cand_garden = p / "docs" / "investigation-garden" / "altproof" / "route-table.json"
        if cand_garden.parent.exists():
            cand_garden.write_text(payload, encoding="utf-8")
        cand_tools = p / "tools" / "altproof" / "route-table.json"
        if cand_tools.parent.exists() and cand_tools.resolve() != out1.resolve():
            cand_tools.write_text(payload, encoding="utf-8")
    print(f"wrote {out1} ({len(ROUTES)} routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

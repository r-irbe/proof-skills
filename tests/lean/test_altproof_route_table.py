"""Pin the generated route-table artifact (design note 5b discipline)."""

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
sys.path.insert(0, str(TOOLS))

from gen_route_table import generate  # noqa: E402


def test_generated_artifact_matches_definitions():
    """The committed route-table.json is exactly what the definitions generate."""
    pinned = json.loads((TOOLS / "route-table.json").read_text())
    assert pinned == generate(), "route-table.json is stale: run gen_route_table.py"
    garden_pinned = json.loads((Path(__file__).resolve().parents[2] / "docs" / "investigation-garden" / "altproof" / "route-table.json").read_text())
    assert garden_pinned == generate(), "docs/investigation-garden/altproof/route-table.json is stale: run gen_route_table.py"


def test_families_present():
    g = generate()
    assert set(g["families"].keys()) >= {
        "extraction",
        "reflection",
        "redirect",
        "algorithm-class-substitution",
        "kernel-friendly-term-design",
    }
    assert g["total"] == sum(len(routes) for routes in g["families"].values())


def test_every_route_has_provenance():
    g = generate()
    for family, routes in g["families"].items():
        for r in routes:
            assert r["family"] == family
            assert r.get("provenance"), f"{r['id']} lacks provenance"

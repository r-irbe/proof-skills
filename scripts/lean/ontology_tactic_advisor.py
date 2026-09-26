#!/usr/bin/env python3
"""
ontology_tactic_advisor.py - Tactic strategy advisor powered by the ITP Master Authority Ontology.

Provides autonomous proof agents with canonical tactic recommendations, cross-prover
correspondences, statutory intervals, and proof-quality guardrail advisories.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def find_ontology_index(start_path: Optional[Path] = None) -> Optional[Path]:
    """Resolve master-authority-index.json across standard repository locations."""
    candidates = [
        Path("docs/investigation-garden/source-materials/indexes/master-authority-index.json"),
        Path("../../../../docs/investigation-garden/source-materials/indexes/master-authority-index.json"),
        Path("../docs/investigation-garden/source-materials/indexes/master-authority-index.json"),
        Path(os.environ.get("HOME", "")) / "code/tacit-mui/docs/investigation-garden/source-materials/indexes/master-authority-index.json",
    ]
    if start_path:
        candidates.insert(0, start_path)

    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


class OntologyTacticAdvisor:
    """Advises Lean 4 proof tactics using the canonical ITP ontology."""

    def __init__(self, index_path: Optional[Path] = None) -> None:
        resolved = find_ontology_index(index_path)
        if not resolved:
            raise FileNotFoundError("Could not locate master-authority-index.json")
        self.index_path = resolved
        with open(resolved, "r", encoding="ascii") as f:
            self.data = json.load(f)
        self.concepts: List[Dict[str, Any]] = self.data.get("master_concepts", [])

    def search_concepts(self, query: str, prover: str = "lean4") -> List[Dict[str, Any]]:
        """Search ontology concepts matching a keyword, symbol, tactic, or MSC code."""
        q = query.strip().lower()
        if not q:
            return []

        results: List[Dict[str, Any]] = []
        for c in self.concepts:
            cid = c.get("concept_id", "").lower()
            name = c.get("canonical_name", "").lower()
            msc = [m.lower() for m in c.get("msc2020", [])]
            synonyms = [s.lower() for s in c.get("synonyms", [])]
            facet = c.get("ranganathan_facet", {})
            domain = facet.get("domain_theory", "").lower()

            mappings = c.get("prover_mappings", {})
            prover_map = mappings.get(prover, {})
            primary_tactics = [t.lower() for t in prover_map.get("primary_tactics", [])]
            syntax = prover_map.get("syntax_pattern", "").lower()

            if (
                q in cid
                or q in name
                or any(q in m for m in msc)
                or any(q in s for s in synonyms)
                or q in domain
                or any(q in t for t in primary_tactics)
                or q in syntax
            ):
                results.append(c)

        return results

    def advise(self, goal_or_keyword: str) -> Dict[str, Any]:
        """Generate structured strategy card for a given proof context or domain."""
        matches = self.search_concepts(goal_or_keyword)
        if not matches:
            return {
                "query": goal_or_keyword,
                "matches_found": 0,
                "strategy": "Fallback to standard general automation (aesop, simp, grind).",
                "recommended_tactics": ["aesop", "simp", "grind"],
                "guardrails": [
                    "G-1: Verify proof state after each tactic.",
                    "G-13: Do not reference inaccessible variables directly.",
                ],
            }

        top = matches[0]
        lean_map = top.get("prover_mappings", {}).get("lean4", {})
        tactics = lean_map.get("primary_tactics", [])

        # Cross-prover transfer info
        cross_prover = {}
        for p in ["coq", "isabelle_hol", "hol_light", "metamath"]:
            if p in top.get("prover_mappings", {}):
                cross_prover[p] = top["prover_mappings"][p].get("primary_tactics", [])

        # Guardrails specific to domain
        domain = top.get("ranganathan_facet", {}).get("domain_theory", "")
        guardrails = [
            "G-1: Write one tactic, then inspect live LSP goal state before advancing.",
            "G-8: Clean up proof (eliminate redundant rewrites) before declaring complete.",
            "G-13: Avoid inaccessible hygienic variables (x+); bind explicitly with intro/rcases.",
        ]
        if "algebra" in domain.lower() or "geometry" in domain.lower():
            guardrails.append(
                "G-14: Anti-unbundling: do not reduce structured morphisms into bare evaluations."
            )
        if "category" in domain.lower() or "homotopy" in domain.lower():
            guardrails.append(
                "G-16: Use show horizons on multi-step rewrites to eliminate higher-order ambiguity."
            )

        return {
            "query": goal_or_keyword,
            "matches_found": len(matches),
            "primary_concept": {
                "concept_id": top.get("concept_id"),
                "canonical_name": top.get("canonical_name"),
                "domain_theory": domain,
                "msc2020": top.get("msc2020", []),
                "authoritative_intervals": top.get("authoritative_intervals", []),
            },
            "recommended_tactics": tactics,
            "syntax_pattern": lean_map.get("syntax_pattern", ""),
            "semantics": lean_map.get("semantics", ""),
            "cross_prover_transfer": cross_prover,
            "guardrails": guardrails,
        }

    def format_card(self, advice: Dict[str, Any]) -> str:
        """Format advice dictionary as clean markdown strategy card."""
        lines = []
        lines.append(f"# Proof Strategy Advisory: `{advice['query']}`")
        lines.append("")
        if advice.get("matches_found", 0) == 0:
            lines.append("No specialized canonical ITP ontology concept matched.")
            lines.append(f"**Strategy**: {advice.get('strategy')}")
            lines.append(f"**Recommended Tactics**: {', '.join(advice.get('recommended_tactics', []))}")
            return "\n".join(lines)

        concept = advice["primary_concept"]
        lines.append(f"- **Concept ID**: `{concept['concept_id']}`")
        lines.append(f"- **Canonical Name**: {concept['canonical_name']}")
        lines.append(f"- **Domain Theory**: {concept['domain_theory']}")
        lines.append(f"- **MSC2020**: {', '.join(concept['msc2020'])}")
        lines.append("")
        lines.append("## Recommended Lean 4 Tactics")
        for t in advice.get("recommended_tactics", []):
            lines.append(f"- `{t}`")
        if advice.get("syntax_pattern"):
            lines.append(f"\n**Syntax Pattern**:\n```lean\n{advice['syntax_pattern']}\n```")
        if advice.get("semantics"):
            lines.append(f"\n**Semantics**: {advice['semantics']}")

        lines.append("\n## Cross-Prover Transfer")
        for prover, tactics in advice.get("cross_prover_transfer", {}).items():
            lines.append(f"- **{prover}**: {', '.join(f'`{t}`' for t in tactics)}")

        lines.append("\n## Operational Guardrails")
        for g in advice.get("guardrails", []):
            lines.append(f"- {g}")

        return "\n".join(lines)


def self_test() -> bool:
    """Execute self-test ensuring advisor correctly identifies canonical concepts."""
    advisor = OntologyTacticAdvisor()
    assert len(advisor.concepts) >= 90, f"Expected at least 90 concepts, got {len(advisor.concepts)}"

    # Test Hoare logic
    advice = advisor.advise("Hoare")
    assert advice["matches_found"] > 0
    assert "wp" in advice["recommended_tactics"] or "vcgen" in advice["recommended_tactics"]

    # Test Liquid vector spaces
    advice_liquid = advisor.advise("liquid")
    assert advice_liquid["matches_found"] > 0
    assert "CONCEPT-CONDENSED-MATHEMATICS-LIQUID-VECTOR-SPACES" == advice_liquid["primary_concept"]["concept_id"]

    # Test non-matching query
    fallback = advisor.advise("nonexistent_concept_xyz_123")
    assert fallback["matches_found"] == 0
    assert "aesop" in fallback["recommended_tactics"]

    # Test markdown formatting
    card = advisor.format_card(advice)
    assert "# Proof Strategy Advisory" in card

    print("OntologyTacticAdvisor: All tests PASS (100% clean)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="ITP Ontology Tactic Strategy Advisor")
    parser.add_argument("query", nargs="?", help="Theorem keyword, tactic, domain, or MSC code")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="Run advisor unit tests")
    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    if not args.query:
        parser.print_help()
        return 2

    advisor = OntologyTacticAdvisor()
    advice = advisor.advise(args.query)

    if args.json:
        print(json.dumps(advice, indent=2))
    else:
        print(advisor.format_card(advice))

    return 0


if __name__ == "__main__":
    sys.exit(main())

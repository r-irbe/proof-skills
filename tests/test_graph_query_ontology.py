"""Unit test for Procedural Graph Query Ontology integration."""

import pytest
from pathlib import Path
import sys

# Add graph directory to sys.path
graph_dir = Path(__file__).resolve().parents[1] / "graph"
sys.path.insert(0, str(graph_dir))

from graph_query import query_ontology, load_graph, query_neighborhood


def test_query_ontology_concept_lookup():
    results = query_ontology("Presburger")
    assert len(results) >= 1
    found = any(r["concept_id"] == "CONCEPT-PRESBURGER-ARITHMETIC" for r in results)
    assert found, "Expected CONCEPT-PRESBURGER-ARITHMETIC in results"


def test_query_ontology_prover_filter():
    results = query_ontology("Presburger", prover="lean4")
    assert len(results) >= 1
    for r in results:
        for m in r["prover_mappings"]:
            assert m["prover"] == "lean4"


def test_query_ontology_cubical():
    results = query_ontology("Cubical")
    assert len(results) >= 1
    assert results[0]["concept_id"] == "CONCEPT-CUBICAL-TYPE-THEORY-KAN-FIBRATIONS"
    assert len(results[0]["statutory_intervals"]) >= 1

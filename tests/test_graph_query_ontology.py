"""Unit tests for Procedural Graph Query Ontology integration and WAL rejection memory."""

from pathlib import Path
import sys

# Add graph directory to sys.path
graph_dir = Path(__file__).resolve().parents[1] / "graph"
sys.path.insert(0, str(graph_dir))

from graph_query import (
    CANONICAL_SEED_GRAPH,
    hydrate_ontology_memory_db,
    is_rejected,
    load_graph,
    query_neighborhood,
    query_ontology,
    record_rejection,
)


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


def test_query_ontology_memory_sqlite_hydration():
    conn = hydrate_ontology_memory_db()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM master_concept")
    assert cur.fetchone()[0] >= 100
    cur.execute("SELECT count(*) FROM cross_itp_concordance")
    assert cur.fetchone()[0] >= 20
    conn.close()

    res = query_ontology("Presburger", prover="lean4", db_path=":memory:")
    assert any(r["concept_id"] == "CONCEPT-PRESBURGER-ARITHMETIC" for r in res)


def test_wal_rejection_memory_does_not_dirty_seed_graph(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOMDB_RUNTIME_DIR", str(tmp_path))
    seed_before = CANONICAL_SEED_GRAPH.read_text(encoding="ascii")

    entry = record_rejection(
        CANONICAL_SEED_GRAPH,
        goal_sig="forall x : Nat, x + 0 = x",
        tactic="linarith",
        reason="linarith failed to find contradiction",
    )
    assert entry["rejected_tactic"] == "linarith"
    assert (tmp_path / "loom_proving_state.db").is_file()

    seed_after = CANONICAL_SEED_GRAPH.read_text(encoding="ascii")
    assert seed_before == seed_after, "Canonical seed graph must not be dirtied by runtime rejections"

    assert is_rejected({}, "forall x : Nat, x + 0 = x", "linarith") is True
    assert is_rejected({}, "forall x : Nat, x + 0 = x", "omega") is False

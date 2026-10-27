#!/usr/bin/env python3
"""
Procedural Knowledge Graph Query Engine for Lean 4 Formalization (arXiv:2609.09153)

Provides localized neighborhood extraction (h <= 2), WAL-guarded runtime Rejection Memory
filtering, and zero-disk-DB ontology querying (with <2ms :memory: SQLite hydration)
to supply precise tactic guidance to formalization agents without context collapse.

Usage:
  python3 graph_query.py --node P_SIMP --hops 1
  python3 graph_query.py --reject --signature "x + 0 = x" --tactic "linarith" --reason "syntax error"
  python3 graph_query.py --ontology "Presburger" --prover lean4
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SEED_GRAPH = (Path(__file__).resolve().parent / "formalization_seed_graph.json").resolve()
DEFAULT_INDEX_PATH = REPO_ROOT / "vendor" / "itp-ontology" / "master-authority-index.json"
DEFAULT_CONCORDANCE_PATH = REPO_ROOT / "vendor" / "itp-ontology" / "cross-itp-concordance.v1.json"


def get_runtime_state_db_path() -> Path:
    """Resolve the WAL-guarded runtime proving state SQLite path."""
    env_dir = os.environ.get("LOOMDB_RUNTIME_DIR", "").strip()
    if env_dir:
        base = Path(env_dir).expanduser().resolve()
    else:
        base = Path.home() / ".cache" / "proof-skills"
    base.mkdir(parents=True, exist_ok=True)
    return base / "loom_proving_state.db"


def _open_rejection_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target = db_path or get_runtime_state_db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rejection_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_signature TEXT NOT NULL,
            rejected_tactic TEXT NOT NULL,
            error_reason TEXT NOT NULL,
            recorded_at REAL NOT NULL,
            UNIQUE(goal_signature, rejected_tactic)
        )
        """
    )
    return conn


def get_rejection_memory(db_path: Optional[Path] = None) -> List[Dict[str, str]]:
    """Read all recorded tactic rejections from the WAL-guarded runtime SQLite store."""
    try:
        conn = _open_rejection_db(db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT goal_signature, rejected_tactic, error_reason FROM rejection_memory ORDER BY id ASC"
        )
        rows = [
            {
                "goal_signature": r[0],
                "rejected_tactic": r[1],
                "error_reason": r[2],
            }
            for r in cur.fetchall()
        ]
        conn.close()
        return rows
    except Exception:
        return []


def load_graph(graph_path: Path) -> dict:
    if not graph_path.is_file():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")
    with open(graph_path, encoding="ascii") as f:
        return json.load(f)


def save_graph(graph_path: Path, data: dict):
    with open(graph_path, "w", encoding="ascii") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")


def query_neighborhood(graph: dict, start_node_id: str, max_hops: int = 2) -> dict:
    nodes_by_id = {n["id"]: n for n in graph.get("nodes", [])}
    if start_node_id not in nodes_by_id:
        return {"error": f"Node {start_node_id} not found in graph"}

    visited_nodes = {start_node_id}
    frontier = {start_node_id}
    matched_triplets = []

    for _ in range(max_hops):
        next_frontier = set()
        for t in graph.get("triplets", []):
            src, tgt = t["source"], t["target"]
            if src in frontier or tgt in frontier:
                if t not in matched_triplets:
                    matched_triplets.append(t)
                if src not in visited_nodes:
                    visited_nodes.add(src)
                    next_frontier.add(src)
                if tgt not in visited_nodes:
                    visited_nodes.add(tgt)
                    next_frontier.add(tgt)
        frontier = next_frontier
        if not frontier:
            break

    result_nodes = [nodes_by_id[nid] for nid in visited_nodes if nid in nodes_by_id]
    mem_entries = list(graph.get("rejection_memory", []))
    runtime_entries = get_rejection_memory()
    return {
        "start_node": start_node_id,
        "max_hops": max_hops,
        "nodes": result_nodes,
        "triplets": matched_triplets,
        "rejection_memory_size": len(mem_entries) + len(runtime_entries),
    }


def record_rejection(
    graph_path: Optional[Union[Path, str]] = None,
    goal_sig: str = "",
    tactic: str = "",
    reason: str = "",
    runtime_db_path: Optional[Path] = None,
) -> Dict[str, str]:
    """Record a rejected tactic into the WAL-guarded runtime SQLite store.

    Never mutates the git-tracked graph/formalization_seed_graph.json file.
    If a caller explicitly passes a custom non-tracked JSON file (e.g. in a temp dir),
    it updates both the WAL-guarded runtime store and that custom JSON file.
    """
    entry = {
        "goal_signature": goal_sig,
        "rejected_tactic": tactic,
        "error_reason": reason,
    }
    conn = _open_rejection_db(runtime_db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO rejection_memory (goal_signature, rejected_tactic, error_reason, recorded_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(goal_signature, rejected_tactic)
            DO UPDATE SET error_reason = excluded.error_reason, recorded_at = excluded.recorded_at
            """,
            (goal_sig, tactic, reason, time.time()),
        )
    conn.close()

    if graph_path is not None:
        gpath = Path(graph_path).resolve()
        if gpath != CANONICAL_SEED_GRAPH and gpath.is_file():
            try:
                graph = load_graph(gpath)
                mem = graph.setdefault("rejection_memory", [])
                mem.append(entry)
                save_graph(gpath, graph)
            except Exception:
                pass

    return entry


def is_rejected(
    graph: Optional[Union[dict, Path, str]],
    goal_sig: str,
    tactic: str,
    runtime_db_path: Optional[Path] = None,
) -> bool:
    """Check whether (goal_sig, tactic) is rejected in either the graph dict or WAL runtime DB."""
    if isinstance(graph, dict):
        for entry in graph.get("rejection_memory", []):
            if (
                entry.get("goal_signature") == goal_sig
                and entry.get("rejected_tactic") == tactic
            ):
                return True
    elif isinstance(graph, (Path, str)):
        gpath = Path(graph)
        if gpath.is_file() and gpath.suffix == ".json":
            try:
                gdata = load_graph(gpath)
                for entry in gdata.get("rejection_memory", []):
                    if (
                        entry.get("goal_signature") == goal_sig
                        and entry.get("rejected_tactic") == tactic
                    ):
                        return True
            except Exception:
                pass

    try:
        conn = _open_rejection_db(runtime_db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM rejection_memory WHERE goal_signature = ? AND rejected_tactic = ? LIMIT 1",
            (goal_sig, tactic),
        )
        hit = cur.fetchone() is not None
        conn.close()
        return hit
    except Exception:
        return False


def hydrate_ontology_memory_db(
    index_path: Optional[Path] = None,
    concordance_path: Optional[Path] = None,
) -> sqlite3.Connection:
    """Hydrate an ephemeral in-memory SQLite database from JSON ontology artifacts in <2ms."""
    idx_file = index_path or DEFAULT_INDEX_PATH
    conc_file = concordance_path or DEFAULT_CONCORDANCE_PATH

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE master_concept (
            concept_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            msc2020 TEXT,
            domain_theory TEXT
        );
        CREATE TABLE prover_mapping (
            concept_id TEXT NOT NULL,
            prover TEXT NOT NULL,
            primary_tactic TEXT,
            syntax_pattern TEXT
        );
        CREATE TABLE statutory_interval (
            concept_id TEXT NOT NULL,
            urn TEXT NOT NULL
        );
        CREATE TABLE cross_itp_concordance (
            mechanism_id TEXT NOT NULL,
            canonical_name TEXT NOT NULL,
            prover TEXT NOT NULL,
            primary_tactic TEXT,
            syntax_pattern TEXT
        );
        """
    )

    if idx_file.is_file():
        with open(idx_file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        concept_rows = []
        mapping_rows = []
        urn_rows = []
        for c in data.get("master_concepts", []):
            cid = c.get("concept_id", "")
            name = c.get("canonical_name", "")
            msc = json.dumps(c.get("msc2020", []), ensure_ascii=True)
            domain = c.get("ranganathan_facet", {}).get("domain_theory", "")
            concept_rows.append((cid, name, msc, domain))
            for p_name, p_val in c.get("prover_mappings", {}).items():
                tactics_str = ";".join(p_val.get("primary_tactics", []))
                syntax_str = p_val.get("syntax_pattern", "")
                mapping_rows.append((cid, p_name, tactics_str, syntax_str))
            for urn in c.get("authoritative_intervals", []):
                urn_rows.append((cid, urn))
        cur.executemany("INSERT OR REPLACE INTO master_concept VALUES (?, ?, ?, ?)", concept_rows)
        cur.executemany("INSERT INTO prover_mapping VALUES (?, ?, ?, ?)", mapping_rows)
        cur.executemany("INSERT INTO statutory_interval VALUES (?, ?)", urn_rows)

    if conc_file.is_file():
        with open(conc_file, "r", encoding="utf-8") as fp:
            cdata = json.load(fp)
        conc_rows = []
        for m in cdata.get("mechanisms", cdata.get("canonical_mechanisms", [])):
            mid = m.get("id") or m.get("mechanism_id") or ""
            mname = m.get("canonical_name", "")
            for p_name, p_val in m.get("provers", {}).items():
                if isinstance(p_val, dict):
                    tactics = p_val.get("tactics", p_val.get("primary_tactics", []))
                    tactics_str = ";".join(tactics) if isinstance(tactics, list) else str(tactics)
                    syntax_str = str(p_val.get("idiom") or p_val.get("syntax_pattern") or "")
                    conc_rows.append((mid, mname, p_name, tactics_str, syntax_str))
        cur.executemany(
            "INSERT INTO cross_itp_concordance VALUES (?, ?, ?, ?, ?)", conc_rows
        )

    conn.commit()
    return conn


def _query_sqlite_connection(
    conn: sqlite3.Connection,
    query_str: str,
    prover: Optional[str] = None,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    cur = conn.cursor()
    pattern = f"%{query_str}%"
    cur.execute(
        """
        SELECT c.concept_id, c.canonical_name, c.msc2020, c.domain_theory
        FROM master_concept c
        WHERE c.concept_id LIKE ? OR c.canonical_name LIKE ? OR c.domain_theory LIKE ?
        """,
        (pattern, pattern, pattern),
    )
    for row in cur.fetchall():
        cid, name, msc, domain = row
        if prover:
            cur.execute(
                """
                SELECT prover, primary_tactic, syntax_pattern
                FROM prover_mapping
                WHERE concept_id = ? AND prover = ?
                """,
                (cid, prover),
            )
        else:
            cur.execute(
                """
                SELECT prover, primary_tactic, syntax_pattern
                FROM prover_mapping
                WHERE concept_id = ?
                """,
                (cid,),
            )
        mappings = [
            {"prover": r[0], "primary_tactic": r[1], "syntax_pattern": r[2]}
            for r in cur.fetchall()
        ]
        cur.execute("SELECT urn FROM statutory_interval WHERE concept_id = ?", (cid,))
        urns = [r[0] for r in cur.fetchall()]
        results.append(
            {
                "concept_id": cid,
                "canonical_name": name,
                "msc2020": json.loads(msc) if msc else [],
                "domain_theory": domain,
                "prover_mappings": mappings,
                "statutory_intervals": urns,
            }
        )
    return results


def query_ontology(
    query_str: str,
    prover: Optional[str] = None,
    db_path: Optional[Union[Path, str]] = None,
    index_path: Optional[Path] = None,
    use_memory_sqlite: bool = False,
) -> List[Dict[str, Any]]:
    """Query canonical ITP concepts, tactics, and intervals directly from JSON or :memory: SQLite."""
    if index_path is None:
        index_path = DEFAULT_INDEX_PATH

    if db_path is not None and str(db_path) == ":memory:":
        use_memory_sqlite = True
        db_path = None

    if db_path is not None:
        resolved_db = Path(db_path)
        if resolved_db.is_file():
            conn = sqlite3.connect(str(resolved_db))
            try:
                return _query_sqlite_connection(conn, query_str, prover=prover)
            finally:
                conn.close()

    if use_memory_sqlite:
        conn = hydrate_ontology_memory_db(index_path=index_path)
        try:
            return _query_sqlite_connection(conn, query_str, prover=prover)
        finally:
            conn.close()

    results: List[Dict[str, Any]] = []
    if index_path.is_file():
        with open(index_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        q = query_str.lower()
        for c in data.get("master_concepts", []):
            cid = c.get("concept_id", "")
            name = c.get("canonical_name", "")
            domain = c.get("ranganathan_facet", {}).get("domain_theory", "")
            synonyms = c.get("synonyms", [])
            tactics_match = any(
                any(q in t.lower() for t in p_val.get("primary_tactics", []))
                for p_val in c.get("prover_mappings", {}).values()
            )
            match = (
                q in cid.lower()
                or q in name.lower()
                or q in domain.lower()
                or any(q in s.lower() for s in synonyms)
                or tactics_match
            )
            if match:
                mappings = []
                for p_name, p_val in c.get("prover_mappings", {}).items():
                    if not prover or p_name == prover:
                        mappings.append(
                            {
                                "prover": p_name,
                                "primary_tactic": ";".join(p_val.get("primary_tactics", [])),
                                "syntax_pattern": p_val.get("syntax_pattern", ""),
                            }
                        )
                results.append(
                    {
                        "concept_id": cid,
                        "canonical_name": name,
                        "msc2020": c.get("msc2020", []),
                        "domain_theory": domain,
                        "prover_mappings": mappings,
                        "statutory_intervals": c.get("authoritative_intervals", []),
                    }
                )

    return results


def ingest_ontology(
    graph_path: Path,
    master_json_path: Optional[Path] = None,
) -> int:
    """Ingest master authority index concepts into procedural graph nodes and triplets."""
    if master_json_path is None:
        master_json_path = DEFAULT_INDEX_PATH
    if not master_json_path.is_file():
        raise FileNotFoundError(f"Master index not found at {master_json_path}")

    with open(master_json_path, "r", encoding="ascii") as fp:
        master_data = json.load(fp)

    graph = load_graph(graph_path)
    existing_node_ids = {n["id"] for n in graph.get("nodes", [])}
    added_count = 0

    for c in master_data.get("master_concepts", []):
        cid = c["concept_id"]
        if cid not in existing_node_ids:
            domain = c.get("ranganathan_facet", {}).get("domain_theory", "ITP Concept")
            graph.setdefault("nodes", []).append(
                {
                    "id": cid,
                    "name": c["canonical_name"],
                    "category": domain,
                    "description": f"ITP canonical concept. MSC2020: {', '.join(c.get('msc2020', []))}",
                    "reversibility": "full",
                }
            )
            added_count += 1
            existing_node_ids.add(cid)

            lean_map = c.get("prover_mappings", {}).get("lean4", {})
            for tac in lean_map.get("primary_tactics", []):
                tac_node_id = f"P_{tac.upper().replace(' ', '_')}"
                if tac_node_id in existing_node_ids:
                    graph.setdefault("triplets", []).append(
                        {
                            "source": tac_node_id,
                            "relation": "solves_concept",
                            "target": cid,
                            "condition": f"Goal instantiates {c['canonical_name']}",
                            "guidance": f"Dispatch {tac} for {c['canonical_name']}",
                            "pitfalls": "Check prerequisites and typeclass assumptions.",
                        }
                    )

    save_graph(graph_path, graph)
    return added_count


def main():
    parser = argparse.ArgumentParser(description="Lean 4 Procedural Graph Query Engine")
    parser.add_argument("--graph", type=str, default="formalization_seed_graph.json")
    parser.add_argument(
        "--node",
        type=str,
        help="Start node ID (e.g. P_SIMP or CONCEPT-PRESBURGER-ARITHMETIC)",
    )
    parser.add_argument("--hops", type=int, default=1, help="Max graph hops (default: 1, max: 2)")
    parser.add_argument("--reject", action="store_true", help="Record a rejected tactic mutation")
    parser.add_argument("--signature", type=str, help="Goal signature for rejection memory")
    parser.add_argument("--tactic", type=str, help="Rejected tactic name")
    parser.add_argument("--reason", type=str, help="Reason or error output for rejection")
    parser.add_argument(
        "--ontology",
        type=str,
        help="Query ITP master ontology by concept, tactic, or keyword",
    )
    parser.add_argument(
        "--prover",
        type=str,
        default=None,
        help="Filter ontology mappings by prover (e.g. lean4, coq)",
    )
    parser.add_argument(
        "--memory-sqlite",
        action="store_true",
        help="Hydrate ephemeral :memory: SQLite database for ontology query",
    )
    parser.add_argument(
        "--ingest-ontology",
        action="store_true",
        help="Ingest master authority ontology concepts into graph",
    )
    args = parser.parse_args()

    graph_file = Path(args.graph)
    if not graph_file.is_file():
        script_dir = Path(__file__).resolve().parent
        graph_file = script_dir / args.graph

    if args.ingest_ontology:
        added = ingest_ontology(graph_file)
        print(
            f"[ONTOLOGY INGESTION] Added {added} concept nodes and semantic triplets to {graph_file}"
        )
        sys.exit(0)

    if args.ontology:
        res = query_ontology(
            args.ontology,
            prover=args.prover,
            use_memory_sqlite=args.memory_sqlite,
        )
        print(json.dumps(res, indent=2, ensure_ascii=True))
        sys.exit(0)

    if args.reject:
        if not (args.signature and args.tactic and args.reason):
            print(
                "Error: --reject requires --signature, --tactic, and --reason",
                file=sys.stderr,
            )
            sys.exit(1)
        entry = record_rejection(graph_file, args.signature, args.tactic, args.reason)
        print(f"[REJECTION RECORDED] {entry}")
        sys.exit(0)

    if args.node:
        graph = load_graph(graph_file)
        res = query_neighborhood(graph, args.node, max_hops=min(args.hops, 2))
        print(json.dumps(res, indent=2, ensure_ascii=True))
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()

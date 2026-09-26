#!/usr/bin/env python3
"""
Procedural Knowledge Graph Query Engine for Lean 4 Formalization (arXiv:2609.09153)

Provides localized neighborhood extraction (h <= 2) and Rejection Memory filtering
to supply precise tactic guidance to formalization agents without context collapse.

Usage:
  python3 graph_query.py --node P_SIMP --hops 1
  python3 graph_query.py --reject --signature "x + 0 = x" --tactic "linarith" --reason "syntax error"
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_graph(graph_path: Path) -> dict:
    if not graph_path.is_file():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")
    with open(graph_path, encoding="ascii") as f:
        return json.load(f)


def save_graph(graph_path: Path, data: dict):
    with open(graph_path, "w", encoding="ascii") as f:
        json.dump(data, f, indent=2)
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
    return {
        "start_node": start_node_id,
        "max_hops": max_hops,
        "nodes": result_nodes,
        "triplets": matched_triplets,
        "rejection_memory_size": len(graph.get("rejection_memory", []))
    }


def record_rejection(graph_path: Path, goal_sig: str, tactic: str, reason: str):
    graph = load_graph(graph_path)
    mem = graph.setdefault("rejection_memory", [])
    entry = {
        "goal_signature": goal_sig,
        "rejected_tactic": tactic,
        "error_reason": reason
    }
    mem.append(entry)
    save_graph(graph_path, graph)
    return entry


def is_rejected(graph: dict, goal_sig: str, tactic: str) -> bool:
    for entry in graph.get("rejection_memory", []):
        if entry.get("goal_signature") == goal_sig and entry.get("rejected_tactic") == tactic:
            return True
    return False


def query_ontology(
    query_str: str,
    prover: Optional[str] = None,
    db_path: Optional[Path] = None,
    index_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Query canonical ITP concepts, tactics, and intervals from the SQLite DB or JSON index."""
    results = []
    if db_path is None:
        db_path = (
            Path(__file__).resolve().parents[5]
            / "docs"
            / "investigation-garden"
            / "source-materials"
            / "itp_ontology_graph.db"
        )
    if index_path is None:
        index_path = (
            Path(__file__).resolve().parents[5]
            / "docs"
            / "investigation-garden"
            / "source-materials"
            / "indexes"
            / "master-authority-index.json"
        )

    if db_path.is_file():
        conn = sqlite3.connect(str(db_path))
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
            cur.execute(
                """
                SELECT urn FROM statutory_interval WHERE concept_id = ?
            """,
                (cid,),
            )
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
        conn.close()
    elif index_path.is_file():
        with open(index_path, "r", encoding="ascii") as fp:
            data = json.load(fp)
        q = query_str.lower()
        for c in data.get("master_concepts", []):
            cid = c.get("concept_id", "")
            name = c.get("canonical_name", "")
            domain = c.get("ranganathan_facet", {}).get("domain_theory", "")
            synonyms = c.get("synonyms", [])
            match = (
                q in cid.lower()
                or q in name.lower()
                or q in domain.lower()
                or any(q in s.lower() for s in synonyms)
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
        master_json_path = (
            Path(__file__).resolve().parents[5]
            / "docs"
            / "investigation-garden"
            / "source-materials"
            / "indexes"
            / "master-authority-index.json"
        )
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

            # Link with primary Lean 4 tactics if present
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
    parser.add_argument("--node", type=str, help="Start node ID (e.g. P_SIMP or CONCEPT-PRESBURGER-ARITHMETIC)")
    parser.add_argument("--hops", type=int, default=1, help="Max graph hops (default: 1, max: 2)")
    parser.add_argument("--reject", action="store_true", help="Record a rejected tactic mutation")
    parser.add_argument("--signature", type=str, help="Goal signature for rejection memory")
    parser.add_argument("--tactic", type=str, help="Rejected tactic name")
    parser.add_argument("--reason", type=str, help="Reason or error output for rejection")
    parser.add_argument("--ontology", type=str, help="Query ITP master ontology by concept, tactic, or keyword")
    parser.add_argument("--prover", type=str, default=None, help="Filter ontology mappings by prover (e.g. lean4, coq)")
    parser.add_argument("--ingest-ontology", action="store_true", help="Ingest master authority ontology concepts into graph")
    args = parser.parse_args()

    graph_file = Path(args.graph)
    if not graph_file.is_file():
        # Fallback relative to script dir
        script_dir = Path(__file__).resolve().parent
        graph_file = script_dir / args.graph

    if args.ingest_ontology:
        added = ingest_ontology(graph_file)
        print(f"[ONTOLOGY INGESTION] Added {added} concept nodes and semantic triplets to {graph_file}")
        sys.exit(0)

    if args.ontology:
        res = query_ontology(args.ontology, prover=args.prover)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.reject:
        if not (args.signature and args.tactic and args.reason):
            print("Error: --reject requires --signature, --tactic, and --reason", file=sys.stderr)
            sys.exit(1)
        entry = record_rejection(graph_file, args.signature, args.tactic, args.reason)
        print(f"[REJECTION RECORDED] {entry}")
        sys.exit(0)

    if args.node:
        graph = load_graph(graph_file)
        res = query_neighborhood(graph, args.node, max_hops=min(args.hops, 2))
        print(json.dumps(res, indent=2))
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()

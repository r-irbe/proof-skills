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
import os
import sys
from pathlib import Path


def load_graph(graph_path: Path) -> dict:
    if not graph_path.is_file():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")
    with open(graph_path, "r", encoding="ascii") as f:
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


def main():
    parser = argparse.ArgumentParser(description="Lean 4 Procedural Graph Query Engine")
    parser.add_argument("--graph", type=str, default="formalization_seed_graph.json")
    parser.add_argument("--node", type=str, help="Start node ID (e.g. P_SIMP)")
    parser.add_argument("--hops", type=int, default=1, help="Max graph hops (default: 1, max: 2)")
    parser.add_argument("--reject", action="store_true", help="Record a rejected tactic mutation")
    parser.add_argument("--signature", type=str, help="Goal signature for rejection memory")
    parser.add_argument("--tactic", type=str, help="Rejected tactic name")
    parser.add_argument("--reason", type=str, help="Reason or error output for rejection")
    args = parser.parse_args()

    graph_file = Path(args.graph)
    if not graph_file.is_file():
        # Fallback relative to script dir
        script_dir = Path(__file__).resolve().parent
        graph_file = script_dir / args.graph

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

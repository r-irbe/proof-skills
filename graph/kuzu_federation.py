#!/usr/bin/env python3
# graph/kuzu_federation.py
# Multi-database parallel federated query engine for Kuzu (TASK-LIB-07).
# Strict 7-bit ASCII only (INV-001).

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import kuzu
    HAS_KUZU = True
except ImportError:
    HAS_KUZU = False


class FederatedKuzuEngine:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = self._resolve_config(config_path)
        self.config = self._load_config()
        self.databases: dict[str, dict[str, Any]] = {}
        self.connections: dict[str, Any] = {}
        self._init_databases()

    def _resolve_config(self, config_path: str | Path | None) -> Path:
        if config_path and Path(config_path).exists():
            return Path(config_path).resolve()
        env_cfg = os.environ.get("LEAN_KUZU_CONFIG_PATH")
        candidates = (
            [Path(env_cfg)] if env_cfg else []
        ) + [
            Path(".kuzu-config.json"),
            Path(__file__).resolve().parents[1] / ".kuzu-config.json",
            Path(__file__).resolve().parents[2] / ".kuzu-config.json",
        ]
        for c in candidates:
            if c.exists():
                return c.resolve()
        return Path(".kuzu-config.json").resolve()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {
                "version": "1.0",
                "databases": [
                    {
                        "id": "prover",
                        "name": "Public Prover Knowledge",
                        "path": os.environ.get("LEAN_KUZU_DB_PATH", "kuzu/prover_knowledge.kuzu"),
                        "scope": "public_prover",
                        "priority": 10,
                        "enabled": True,
                    }
                ],
                "federation": {"parallel_queries": True, "max_workers": 4, "timeout_ms": 3000},
            }
        try:
            return json.loads(self.config_path.read_text(encoding="ascii"))
        except Exception:
            return json.loads(self.config_path.read_text(encoding="utf-8"))

    def _init_databases(self) -> None:
        if not HAS_KUZU:
            return
        root = self.config_path.parent
        for db_meta in self.config.get("databases", []):
            if not db_meta.get("enabled", True):
                continue
            db_id = db_meta["id"]
            rel_path = db_meta.get("path", "")
            full_path = (root / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)

            if full_path.exists():
                try:
                    read_only = bool(db_meta.get("read_only", False))
                    kdb = kuzu.Database(str(full_path), read_only=read_only)
                    kconn = kuzu.Connection(kdb)
                    self.databases[db_id] = db_meta
                    self.connections[db_id] = kconn
                except Exception as exc:
                    self.databases[db_id] = {**db_meta, "error": str(exc)}
            else:
                self.databases[db_id] = {**db_meta, "error": "file_not_found"}

    def query_single_db(self, db_id: str, cypher: str) -> list[dict[str, Any]]:
        conn = self.connections.get(db_id)
        if not conn:
            return []
        meta = self.databases.get(db_id, {})
        priority = meta.get("priority", 0)
        scope = meta.get("scope", "custom")

        try:
            res = conn.execute(cypher)
            rows: list[dict[str, Any]] = []
            while res.has_next():
                row_vals = res.get_next()
                rows.append({
                    "_db_id": db_id,
                    "_db_scope": scope,
                    "_priority": priority,
                    "row": row_vals,
                })
            return rows
        except Exception as exc:
            return [{"_db_id": db_id, "_db_scope": scope, "_error": str(exc)}]

    def execute_federated(
        self,
        cypher: str,
        target_db_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not HAS_KUZU:
            return [{"_error": "kuzu python library not available"}]

        active_ids = [d for d in self.connections.keys() if (target_db_ids is None or d in target_db_ids)]
        if not active_ids:
            return []

        parallel = self.config.get("federation", {}).get("parallel_queries", True)
        max_workers = min(len(active_ids), self.config.get("federation", {}).get("max_workers", 4))
        timeout = self.config.get("federation", {}).get("timeout_ms", 3000) / 1000.0

        all_results: list[dict[str, Any]] = []

        if parallel and len(active_ids) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_db = {
                    executor.submit(self.query_single_db, db_id, cypher): db_id
                    for db_id in active_ids
                }
                for future in concurrent.futures.as_completed(future_to_db, timeout=timeout):
                    db_id = future_to_db[future]
                    try:
                        res = future.result()
                        all_results.extend(res)
                    except Exception as exc:
                        all_results.append({"_db_id": db_id, "_error": str(exc)})
        else:
            for db_id in active_ids:
                res = self.query_single_db(db_id, cypher)
                all_results.extend(res)

        # Sort by priority descending
        all_results.sort(key=lambda r: r.get("_priority", 0), reverse=True)
        return all_results

    def search_concept(self, term: str) -> list[dict[str, Any]]:
        clean = term.replace("\"", "\\\"").strip()
        results: list[dict[str, Any]] = []

        # 1. Query Prover DB for concepts
        if "prover" in self.connections:
            q_prover = (
                f"MATCH (c:Concept) WHERE c.name CONTAINS \"{clean}\" OR c.id CONTAINS \"{clean}\" "
                f"RETURN c.id, c.name, c.domain_theory LIMIT 10"
            )
            res_p = self.query_single_db("prover", q_prover)
            for r in res_p:
                if "row" in r:
                    results.append({
                        "source": "prover_knowledge",
                        "type": "concept",
                        "id": r["row"][0],
                        "name": r["row"][1],
                        "detail": r["row"][2],
                    })

        # 2. Query Internal DB for MOCs and Artifacts
        if "project_internal" in self.connections:
            q_int = (
                f"MATCH (m:MOC) WHERE m.title CONTAINS \"{clean}\" OR m.id CONTAINS \"{clean}\" "
                f"RETURN m.id, m.title, m.file_path LIMIT 5"
            )
            res_i = self.query_single_db("project_internal", q_int)
            for r in res_i:
                if "row" in r:
                    results.append({
                        "source": "project_internal",
                        "type": "moc",
                        "id": r["row"][0],
                        "name": r["row"][1],
                        "detail": r["row"][2],
                    })

        # 3. Query Cache DB for Elaborated Symbols
        if "lsp_cache" in self.connections:
            q_cache = (
                f"MATCH (s:ElaboratedSymbol) WHERE s.symbol_name CONTAINS \"{clean}\" "
                f"RETURN s.id, s.symbol_name, s.type_signature LIMIT 5"
            )
            res_c = self.query_single_db("lsp_cache", q_cache)
            for r in res_c:
                if "row" in r:
                    results.append({
                        "source": "lsp_cache",
                        "type": "symbol",
                        "id": r["row"][0],
                        "name": r["row"][1],
                        "detail": r["row"][2],
                    })

        return results

    def lookup_anchor(self, term: str) -> list[dict[str, Any]]:
        clean = term.replace("\"", "\\\"").strip()
        if "prover" not in self.connections:
            return []
        q = (
            f"MATCH (a:Anchor) WHERE a.heading CONTAINS \"{clean}\" OR a.id CONTAINS \"{clean}\" "
            f"RETURN a.id, a.book_id, a.heading, a.page LIMIT 15"
        )
        res = self.query_single_db("prover", q)
        out = []
        for r in res:
            if "row" in r:
                out.append({
                    "anchor": r["row"][0],
                    "book": r["row"][1],
                    "heading": r["row"][2],
                    "page": r["row"][3],
                })
        return out

    def cache_symbol(self, module: str, symbol: str, type_sig: str) -> bool:
        if "lsp_cache" not in self.connections:
            return False
        clean_mod = module.replace("\"", "\\\"")
        clean_sym = symbol.replace("\"", "\\\"")
        clean_sig = type_sig.replace("\"", "\\\"")
        s_id = f"{clean_mod}.{clean_sym}"
        q = (
            f"MERGE (s:ElaboratedSymbol {{id: \"{s_id}\"}}) "
            f"ON MATCH SET s.module_name = \"{clean_mod}\", s.symbol_name = \"{clean_sym}\", s.type_signature = \"{clean_sig}\" "
            f"ON CREATE SET s.module_name = \"{clean_mod}\", s.symbol_name = \"{clean_sym}\", s.type_signature = \"{clean_sig}\""
        )
        try:
            self.connections["lsp_cache"].execute(q)
            return True
        except Exception:
            return False

    def query_traceability(self, req_id: str) -> list[dict[str, Any]]:
        clean_req = req_id.replace("\"", "\\\"").strip()
        if "project_internal" not in self.connections:
            return []
        q = (
            f"MATCH (req:Requirement) WHERE req.id = \"{clean_req}\" OR req.title CONTAINS \"{clean_req}\" "
            f"OPTIONAL MATCH (adr:ADR)-[:ADR_SATISFIES_REQUIREMENT]->(req) "
            f"OPTIONAL MATCH (lean:LeanDeclaration)-[:LEAN_VERIFIES_ADR]->(adr) "
            f"OPTIONAL MATCH (adr)-[:ADR_GROUNDED_IN_EVIDENCE]->(ev:EvidenceCard) "
            f"RETURN req.id, req.title, adr.id, adr.title, lean.name, lean.module, ev.id, ev.title LIMIT 25"
        )
        res = self.query_single_db("project_internal", q)
        out = []
        for r in res:
            if "row" in r:
                row = r["row"]
                out.append({
                    "requirement_id": row[0],
                    "requirement_title": row[1],
                    "adr_id": row[2],
                    "adr_title": row[3],
                    "lean_declaration": row[4],
                    "lean_module": row[5],
                    "evidence_id": row[6],
                    "evidence_title": row[7],
                })
        return out

    def query_epistemic_chain(self, term: str) -> list[dict[str, Any]]:
        clean = term.replace("\"", "\\\"").strip()
        if "prover" not in self.connections:
            return []
        q = (
            f"MATCH (c:Concept) WHERE c.id CONTAINS \"{clean}\" OR c.name CONTAINS \"{clean}\" "
            f"OPTIONAL MATCH (z:Zettel)-[:ZETTEL_EXEMPLIFIES_CONCEPT]->(c) "
            f"OPTIONAL MATCH (z)-[:ZETTEL_IN_BOOK]->(b:Book) "
            f"OPTIONAL MATCH (z)-[:ZETTEL_ANCHORS_AT]->(a:Anchor) "
            f"RETURN c.id, c.name, z.id, z.title, b.id, b.title, a.id, a.heading LIMIT 25"
        )
        res = self.query_single_db("prover", q)
        out = []
        for r in res:
            if "row" in r:
                row = r["row"]
                out.append({
                    "concept_id": row[0],
                    "concept_name": row[1],
                    "zettel_id": row[2],
                    "zettel_title": row[3],
                    "book_id": row[4],
                    "book_title": row[5],
                    "anchor_id": row[6],
                    "anchor_heading": row[7],
                })
        return out

    def verify_integrity(self) -> dict[str, Any]:
        results: dict[str, Any] = {"prover": {}, "project_internal": {}, "verified": False}
        if "prover" in self.connections:
            conn = self.connections["prover"]
            for tbl in ["Book", "Anchor", "Concept", "Zettel", "StitchedText"]:
                res = conn.execute(f"MATCH (n:{tbl}) RETURN count(n)")
                if res.has_next():
                    results["prover"][tbl] = res.get_next()[0]

        if "project_internal" in self.connections:
            conn = self.connections["project_internal"]
            for tbl in ["Requirement", "ADR", "EvidenceCard", "LeanDeclaration", "MOC"]:
                res = conn.execute(f"MATCH (n:{tbl}) RETURN count(n)")
                if res.has_next():
                    results["project_internal"][tbl] = res.get_next()[0]

        trace = self.query_traceability("FUNC-107")
        epistemic = self.query_epistemic_chain("Induction")

        results["traceability_samples"] = len(trace)
        results["epistemic_chain_samples"] = len(epistemic)

        ok = (
            results["prover"].get("Book", 0) == 34 and
            results["prover"].get("Concept", 0) == 100 and
            results["prover"].get("Zettel", 0) >= 455 and
            results["project_internal"].get("Requirement", 0) >= 150 and
            results["project_internal"].get("ADR", 0) >= 20 and
            results["project_internal"].get("LeanDeclaration", 0) >= 100 and
            len(trace) > 0 and
            len(epistemic) > 0
        )
        results["verified"] = ok
        return results

    def status_report(self) -> dict[str, Any]:
        report = {
            "config_file": str(self.config_path),
            "kuzu_installed": HAS_KUZU,
            "databases": {},
        }
        for db_id, meta in self.databases.items():
            conn_ok = db_id in self.connections
            report["databases"][db_id] = {
                "name": meta.get("name"),
                "scope": meta.get("scope"),
                "priority": meta.get("priority"),
                "connected": conn_ok,
                "error": meta.get("error"),
            }
        return report


def self_test() -> None:
    print("Running kuzu_federation self-test...")
    engine = FederatedKuzuEngine()
    status = engine.status_report()
    assert status["kuzu_installed"], "Kuzu must be installed"
    print("Database Status:")
    for db_id, info in status["databases"].items():
        print(f"  [{db_id}] {info['name']} (scope: {info['scope']}, connected: {info['connected']})")

    # 1. Test search
    res = engine.search_concept("Induction")
    print(f"Search 'Induction' returned {len(res)} results:")
    for r in res[:5]:
        print(f"  [{r['source']}] {r['type']}: {r['name']} ({r['id']})")
    assert len(res) > 0, "Expected non-empty search results for 'Induction'"

    # 2. Test anchor lookup
    anchors = engine.lookup_anchor("Inductive")
    print(f"Lookup anchor 'Inductive' returned {len(anchors)} anchors:")
    for a in anchors[:3]:
        print(f"  {a['anchor']} ({a['book']}): {a['heading']}")
    assert len(anchors) > 0, "Expected non-empty anchor results"

    # 3. Test Traceability Query
    trace = engine.query_traceability("FUNC-107")
    print(f"Traceability 'FUNC-107' returned {len(trace)} paths:")
    for t in trace[:3]:
        print(f"  Req: {t['requirement_id']} -> ADR: {t['adr_id']} -> Lean: {t['lean_declaration']} -> Ev: {t['evidence_id']}")
    assert len(trace) > 0, "Expected non-empty traceability paths"

    # 4. Test Epistemic Chain Query
    chain = engine.query_epistemic_chain("Induction")
    print(f"Epistemic chain 'Induction' returned {len(chain)} paths:")
    for c in chain[:3]:
        print(f"  Concept: {c['concept_name']} -> Zettel: {c['zettel_title']} -> Book: {c['book_id']}")
    assert len(chain) > 0, "Expected non-empty epistemic chain"

    # 5. Test Integrity Verification
    integ = engine.verify_integrity()
    print("Integrity Report:", json.dumps(integ, indent=2))
    assert integ["verified"], "Integrity verification must pass"

    print("ALL SELF-TEST ASSERTIONS PASSED CLEANLY.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Database Federated Kuzu Query Engine (TASK-LIB-07)")
    parser.add_argument("--self-test", action="store_true", help="Run self-test assertions")
    parser.add_argument("--status", action="store_true", help="Print status report of configured databases")
    parser.add_argument("--search", help="Search for a concept or term across all databases")
    parser.add_argument("--anchor", help="Lookup statutory anchor by term in prover database")
    parser.add_argument("--traceability", help="Query requirement-to-evidence traceability by requirement ID")
    parser.add_argument("--epistemic-chain", help="Query concept-to-zettel-to-book epistemic chain by concept name/ID")
    parser.add_argument("--verify-integrity", action="store_true", help="Verify full garden graph integrity")
    parser.add_argument("--query", help="Execute Cypher query across federated databases")
    parser.add_argument("--config", help="Path to .kuzu-config.json")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    engine = FederatedKuzuEngine(args.config)

    if args.status:
        print(json.dumps(engine.status_report(), indent=2))
        return

    if args.verify_integrity:
        res = engine.verify_integrity()
        print(json.dumps(res, indent=2))
        sys.exit(0 if res.get("verified") else 1)

    if args.traceability:
        results = engine.query_traceability(args.traceability)
        print(json.dumps(results, indent=2))
        return

    if args.epistemic_chain:
        results = engine.query_epistemic_chain(args.epistemic_chain)
        print(json.dumps(results, indent=2))
        return

    if args.search:
        results = engine.search_concept(args.search)
        print(json.dumps(results, indent=2))
        return

    if args.anchor:
        results = engine.lookup_anchor(args.anchor)
        print(json.dumps(results, indent=2))
        return

    if args.query:
        results = engine.execute_federated(args.query)
        print(json.dumps(results, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()

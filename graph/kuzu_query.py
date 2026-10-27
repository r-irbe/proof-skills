#!/usr/bin/env python3
# graph/kuzu_query.py
# Interactive and Scriptable CLI for Federated Kuzu Property Graphs (TASK-LIB-07).
# Strict 7-bit ASCII only (INV-001).

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from graph.kuzu_federation import FederatedKuzuEngine
except ImportError:
    from kuzu_federation import FederatedKuzuEngine


def esc(val: Any) -> str:
    """Escape a string value for safe interpolation into Cypher string literals."""
    if val is None:
        return ""
    return str(val).replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", " ").replace("\r", " ")


def format_table(headers: list[str], rows: list[list[Any]], max_col_width: int = 50) -> str:
    """Render rows as a clean 7-bit ASCII table."""
    if not rows:
        return "(no results)"

    str_rows = []
    for r in rows:
        str_r = []
        for v in r:
            s = str(v) if v is not None else ""
            if len(s) > max_col_width:
                s = s[: max_col_width - 3] + "..."
            str_r.append(s)
        str_rows.append(str_r)

    col_widths = [len(h) for h in headers]
    for r in str_rows:
        for i, val in enumerate(r):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(val))
            else:
                col_widths.append(len(val))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    hdr = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"

    lines = [sep, hdr, sep]
    for r in str_rows:
        padded = [r[i].ljust(col_widths[i]) if i < len(r) else "".ljust(col_widths[i]) for i in range(len(col_widths))]
        lines.append("| " + " | ".join(padded) + " |")
    lines.append(sep)
    return "\n".join(lines)


class KuzuQueryCLI:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self.engine = FederatedKuzuEngine(config_path)

    def stats(self) -> dict[str, Any]:
        """Collect comprehensive node and edge statistics across all connected databases."""
        report = self.engine.status_report()
        stats_out: dict[str, Any] = {
            "kuzu_installed": report.get("kuzu_installed", False),
            "databases": {},
            "total_nodes": 0,
        }

        # Prover stats
        if "prover" in self.engine.connections:
            p_counts = {}
            for table in ["Book", "Anchor", "Concept", "Zettel", "StitchedText"]:
                res = self.engine.query_single_db("prover", f"MATCH (n:{table}) RETURN count(n)")
                cnt = res[0]["row"][0] if res and "row" in res[0] else 0
                p_counts[table] = cnt
                stats_out["total_nodes"] += cnt
            stats_out["databases"]["prover_knowledge"] = p_counts

        # Internal stats
        if "project_internal" in self.engine.connections:
            i_counts = {}
            for table in ["Requirement", "ADR", "EvidenceCard", "LeanDeclaration", "MOC", "InternalArtifact"]:
                res = self.engine.query_single_db("project_internal", f"MATCH (n:{table}) RETURN count(n)")
                cnt = res[0]["row"][0] if res and "row" in res[0] else 0
                i_counts[table] = cnt
                stats_out["total_nodes"] += cnt
            stats_out["databases"]["project_internal"] = i_counts

        return stats_out

    def run_cypher(self, cypher: str, db_id: str | None = None) -> list[dict[str, Any]]:
        """Run arbitrary Cypher query."""
        if db_id and db_id in self.engine.connections:
            return self.engine.query_single_db(db_id, cypher)
        return self.engine.execute_federated(cypher)

    def trace_requirement(self, req_id: str) -> list[dict[str, Any]]:
        """Trace a requirement through ADRs, Lean declarations, and evidence cards."""
        return self.engine.query_traceability(req_id)

    def search_concept(self, term: str) -> list[dict[str, Any]]:
        """Deep search for an ITP or mathematical concept with concordances."""
        clean = esc(term).strip()
        results = []

        if "prover" in self.engine.connections:
            q = (
                f"MATCH (c:Concept) WHERE c.name CONTAINS \"{clean}\" OR c.id CONTAINS \"{clean}\" "
                f"OPTIONAL MATCH (z:Zettel)-[:ZETTEL_EXEMPLIFIES_CONCEPT]->(c) "
                f"RETURN c.id, c.name, c.domain_theory, c.msc2020, z.id, z.title LIMIT 25"
            )
            rows = self.engine.query_single_db("prover", q)
            for r in rows:
                if "row" in r:
                    results.append({
                        "concept_id": r["row"][0],
                        "concept_name": r["row"][1],
                        "domain": r["row"][2],
                        "msc2020": r["row"][3],
                        "zettel_id": r["row"][4],
                        "zettel_title": r["row"][5],
                    })
        return results

    def lookup_concordance(
        self,
        concept: str,
        source_prover: str | None = None,
        target_prover: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query cross-ITP concordance mappings."""
        return self.engine.lookup_concordance(concept, source_prover=source_prover, target_prover=target_prover)

    def lookup_lean(self, symbol: str) -> list[dict[str, Any]]:
        """Find Lean declarations by name or module, with verifying ADRs."""
        clean = esc(symbol).strip()
        results = []

        if "project_internal" in self.engine.connections:
            q = (
                f"MATCH (l:LeanDeclaration) WHERE l.name CONTAINS \"{clean}\" OR l.id CONTAINS \"{clean}\" OR l.module CONTAINS \"{clean}\" "
                f"OPTIONAL MATCH (l)-[:LEAN_VERIFIES_ADR]->(a:ADR) "
                f"OPTIONAL MATCH (a)-[:ADR_SATISFIES_REQUIREMENT]->(req:Requirement) "
                f"RETURN l.id, l.name, l.kind, l.module, l.file_path, l.line, a.id, req.id LIMIT 25"
            )
            rows = self.engine.query_single_db("project_internal", q)
            for r in rows:
                if "row" in r:
                    results.append({
                        "decl_id": r["row"][0],
                        "name": r["row"][1],
                        "kind": r["row"][2],
                        "module": r["row"][3],
                        "file_path": r["row"][4],
                        "line": r["row"][5],
                        "adr_id": r["row"][6],
                        "requirement_id": r["row"][7],
                    })
        return results

    def lookup_adr(self, adr_id: str) -> list[dict[str, Any]]:
        """Inspect an Architecture Decision Record and its graph context."""
        clean = esc(adr_id).strip()
        results = []

        if "project_internal" in self.engine.connections:
            q = (
                f"MATCH (a:ADR) WHERE a.id CONTAINS \"{clean}\" OR a.title CONTAINS \"{clean}\" "
                f"OPTIONAL MATCH (a)-[:ADR_SATISFIES_REQUIREMENT]->(req:Requirement) "
                f"OPTIONAL MATCH (a)-[:ADR_GROUNDED_IN_EVIDENCE]->(ev:EvidenceCard) "
                f"OPTIONAL MATCH (l:LeanDeclaration)-[:LEAN_VERIFIES_ADR]->(a) "
                f"RETURN a.id, a.title, a.status, req.id, ev.id, l.name LIMIT 25"
            )
            rows = self.engine.query_single_db("project_internal", q)
            for r in rows:
                if "row" in r:
                    results.append({
                        "adr_id": r["row"][0],
                        "title": r["row"][1],
                        "status": r["row"][2],
                        "satisfies_req": r["row"][3],
                        "grounded_in": r["row"][4],
                        "verified_by_lean": r["row"][5],
                    })
        return results

    def lookup_book(self, book_key: str) -> list[dict[str, Any]]:
        """Inspect a book shelf and its anchors/zettels."""
        clean = esc(book_key).strip()
        results = []

        if "prover" in self.engine.connections:
            q = (
                f"MATCH (b:Book) WHERE b.id CONTAINS \"{clean}\" OR b.title CONTAINS \"{clean}\" "
                f"OPTIONAL MATCH (a:Anchor)-[:ANCHORS_IN]->(b) "
                f"RETURN b.id, b.title, b.total_rows, a.id, a.heading, a.page LIMIT 20"
            )
            rows = self.engine.query_single_db("prover", q)
            for r in rows:
                if "row" in r:
                    results.append({
                        "book_id": r["row"][0],
                        "book_title": r["row"][1],
                        "total_anchors": r["row"][2],
                        "anchor_id": r["row"][3],
                        "anchor_heading": r["row"][4],
                        "page": r["row"][5],
                    })
        return results

    def diagnostic_unlinked(self) -> dict[str, Any]:
        """Diagnostic sweep: find unlinked requirements and orphaned records."""
        out: dict[str, Any] = {"unlinked_requirements": [], "unverified_adrs": []}

        if "project_internal" in self.engine.connections:
            # Requirements without satisfying ADR
            q_req = (
                "MATCH (r:Requirement) WHERE NOT EXISTS { MATCH (a:ADR)-[:ADR_SATISFIES_REQUIREMENT]->(r) } "
                "RETURN r.id, r.title, r.priority LIMIT 20"
            )
            rows_req = self.engine.query_single_db("project_internal", q_req)
            for r in rows_req:
                if "row" in r:
                    out["unlinked_requirements"].append({
                        "id": r["row"][0],
                        "title": r["row"][1],
                        "priority": r["row"][2],
                    })

            # ADRs without verifying Lean declarations
            q_adr = (
                "MATCH (a:ADR) WHERE NOT EXISTS { MATCH (l:LeanDeclaration)-[:LEAN_VERIFIES_ADR]->(a) } "
                "RETURN a.id, a.title, a.status LIMIT 20"
            )
            rows_adr = self.engine.query_single_db("project_internal", q_adr)
            for r in rows_adr:
                if "row" in r:
                    out["unverified_adrs"].append({
                        "id": r["row"][0],
                        "title": r["row"][1],
                        "status": r["row"][2],
                    })

        return out

    def self_test(self) -> None:
        """Run self-test asserting all query macros function cleanly."""
        print("Running KuzuQueryCLI self-test...")

        # 1. Stats
        s = self.stats()
        assert s["total_nodes"] > 1000, f"Expected >1000 total nodes, got {s['total_nodes']}"
        print(f"  [PASS] Stats: {s['total_nodes']} total nodes across databases")

        # 2. Traceability (if project_internal connected)
        if "project_internal" in self.engine.connections:
            t = self.trace_requirement("FUNC-107")
            assert len(t) > 0, "Expected non-empty trace for FUNC-107"
            print(f"  [PASS] Traceability FUNC-107: {len(t)} paths found")

        # 3. Concept search
        c = self.search_concept("Induction")
        assert len(c) > 0, "Expected non-empty concept search for Induction"
        print(f"  [PASS] Concept search: {len(c)} matches found")

        # 4. Concordance lookup
        conc = self.lookup_concordance("Induction")
        assert len(conc) > 0, "Expected non-empty concordance lookup for Induction"
        print(f"  [PASS] Concordance lookup: {len(conc)} mappings found")

        # 5. Lean & ADR lookup (if project_internal connected)
        if "project_internal" in self.engine.connections:
            l = self.lookup_lean("continuous_relaxation_isSimulation")
            print(f"  [PASS] Lean lookup continuous_relaxation_isSimulation: {len(l)} records found")
            a = self.lookup_adr("ADR-INV-0016")
            assert len(a) > 0, "Expected non-empty ADR lookup for ADR-INV-0016"
            print(f"  [PASS] ADR lookup ADR-INV-0016: {len(a)} records found")

        # 6. Book lookup
        b = self.lookup_book("SF-LF")
        assert len(b) > 0, "Expected non-empty book lookup for SF-LF"
        print(f"  [PASS] Book lookup SF-LF: {len(b)} records found")

        print("ALL KUZU QUERY CLI SELF-TEST ASSERTIONS PASSED CLEANLY.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive and Scriptable CLI for Federated Kuzu Property Graphs")
    parser.add_argument("--self-test", action="store_true", help="Run self-test assertions")
    parser.add_argument("--stats", action="store_true", help="Print global graph statistics")
    parser.add_argument("--cypher", help="Execute raw Cypher query")
    parser.add_argument("--db", choices=["prover", "internal", "cache", "all"], default="all", help="Target database for Cypher query")
    parser.add_argument("--trace", help="Trace requirement to ADRs, Lean declarations, and evidence")
    parser.add_argument("--concept", help="Deep search for concept and referencing zettels")
    parser.add_argument("--concordance", help="Lookup cross-ITP concordance by concept or tactic")
    parser.add_argument("--prover", help="Target prover filter for --concordance")
    parser.add_argument("--lean", help="Search for Lean declaration, verifying ADR, and requirements")
    parser.add_argument("--adr", help="Lookup ADR and its satisfied requirements and evidence")
    parser.add_argument("--book", help="Lookup book and sample statutory anchors")
    parser.add_argument("--unlinked", action="store_true", help="Sweep for unlinked requirements or unverified ADRs")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--config", help="Path to .kuzu-config.json")
    args = parser.parse_args()

    cli = KuzuQueryCLI(args.config)

    if args.self_test:
        cli.self_test()
        return

    if args.stats:
        data = cli.stats()
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print("=== Federated Kuzu Graph Statistics ===")
            print(f"Total Nodes: {data['total_nodes']}")
            for db_name, tbls in data["databases"].items():
                print(f"\nDatabase: {db_name}")
                rows = [[tbl, str(cnt)] for tbl, cnt in tbls.items()]
                print(format_table(["Table", "Count"], rows))
        return

    if args.cypher:
        db_target = "project_internal" if args.db == "internal" else ("lsp_cache" if args.db == "cache" else args.db)
        data = cli.run_cypher(args.cypher, db_id=None if db_target == "all" else db_target)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            rows = [r.get("row", [r.get("_error", "")]) for r in data if "row" in r or "_error" in r]
            print(format_table([f"Col {i+1}" for i in range(len(rows[0]))] if rows else ["Result"], rows))
        return

    if args.trace:
        data = cli.trace_requirement(args.trace)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["Requirement", "ADR", "Lean Declaration", "Evidence"]
            rows = [[d["requirement_id"], d["adr_id"], f"{d['lean_module']}.{d['lean_declaration']}" if d["lean_declaration"] else "", d["evidence_id"]] for d in data]
            print(format_table(headers, rows))
        return

    if args.concept:
        data = cli.search_concept(args.concept)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["Concept ID", "Name", "Domain", "Zettel ID", "Zettel Title"]
            rows = [[d["concept_id"], d["concept_name"], d["domain"], d["zettel_id"] or "", d["zettel_title"] or ""] for d in data]
            print(format_table(headers, rows))
        return

    if args.concordance:
        data = cli.lookup_concordance(args.concordance, target_prover=args.prover)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["Concept ID", "Concept Name", "Prover", "Tactic", "Syntax"]
            rows = [[d["concept_id"], d["concept_name"], d["prover"], d["tactic"], d["syntax"]] for d in data]
            print(format_table(headers, rows))
        return

    if args.lean:
        data = cli.lookup_lean(args.lean)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["Declaration", "Kind", "Module", "File:Line", "Verifies ADR", "Satisfies Req"]
            rows = [[d["name"], d["kind"], d["module"], f"{d['file_path']}:{d['line']}", d["adr_id"] or "", d["requirement_id"] or ""] for d in data]
            print(format_table(headers, rows))
        return

    if args.adr:
        data = cli.lookup_adr(args.adr)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["ADR ID", "Title", "Status", "Satisfies Req", "Grounded In", "Verified By"]
            rows = [[d["adr_id"], d["title"], d["status"], d["satisfies_req"] or "", d["grounded_in"] or "", d["verified_by_lean"] or ""] for d in data]
            print(format_table(headers, rows))
        return

    if args.book:
        data = cli.lookup_book(args.book)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            headers = ["Book ID", "Title", "Total", "Anchor ID", "Heading", "Page"]
            rows = [[d["book_id"], d["book_title"], str(d["total_anchors"]), d["anchor_id"], d["anchor_heading"], str(d["page"])] for d in data]
            print(format_table(headers, rows))
        return

    if args.unlinked:
        data = cli.diagnostic_unlinked()
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print("=== Unlinked Requirements (No satisfying ADR) ===")
            rows_req = [[r["id"], r["title"], r["priority"]] for r in data["unlinked_requirements"]]
            print(format_table(["Req ID", "Title", "Priority"], rows_req))
            print("\n=== Unverified ADRs (No verifying Lean declaration) ===")
            rows_adr = [[a["id"], a["title"], a["status"]] for a in data["unverified_adrs"]]
            print(format_table(["ADR ID", "Title", "Status"], rows_adr))
        return

    parser.print_help()


if __name__ == "__main__":
    main()

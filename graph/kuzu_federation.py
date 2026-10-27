#!/usr/bin/env python3
# graph/kuzu_federation.py
# Multi-database parallel federated query engine for Kuzu (TASK-LIB-07).
# Strict 7-bit ASCII only (INV-001).

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import io
import json
import os
import re
import sqlite3
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

try:
    import kuzu
    HAS_KUZU = True
except ImportError:
    HAS_KUZU = False

REPO_ROOT = Path(__file__).resolve().parents[1]


class _FallbackQueryResult:
    def __init__(self, rows: list[list[Any]]) -> None:
        self._rows = rows
        self._idx = 0

    def has_next(self) -> bool:
        return self._idx < len(self._rows)

    def get_next(self) -> list[Any]:
        row = self._rows[self._idx]
        self._idx += 1
        return row


class ArchiveFallbackConnection:
    """Zero-dependency in-memory SQLite + CSV reader for .kz archives when kuzu is absent."""

    def __init__(self, kz_path: Path | None, ontology_dir: Path | None = None) -> None:
        self.kz_path = kz_path if (kz_path and kz_path.is_file()) else None
        self.ontology_dir = ontology_dir or (REPO_ROOT / "vendor" / "itp-ontology")
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_tables()
        self._load_archive()

    def execute(self, cypher: str) -> _FallbackQueryResult:
        q = cypher.strip()
        cur = self.conn.cursor()
        m_cnt = re.search(r"MATCH\s+\(n:(\w+)\)\s+RETURN\s+count\(n\)", q, re.IGNORECASE)
        if m_cnt:
            tbl = m_cnt.group(1)
            try:
                cur.execute(f"SELECT count(*) FROM {tbl}")
                return _FallbackQueryResult([[cur.fetchone()[0]]])
            except Exception:
                return _FallbackQueryResult([[0]])

        if "MATCH (c:Concept)" in q and "OPTIONAL MATCH (z:Zettel)" in q and "ZETTEL_IN_BOOK" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                """
                SELECT c.id, c.name, z.id, z.title, b.id, b.title, a.id, a.heading
                FROM Concept c
                LEFT JOIN Zettel z ON z.master_concept = c.id OR z.master_concept LIKE '%' || c.name || '%'
                LEFT JOIN Book b ON b.id = z.source_book
                LEFT JOIN Anchor a ON a.id = z.source_anchor
                WHERE c.id LIKE ? OR c.name LIKE ?
                LIMIT 25
                """,
                (like, like),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        if "MATCH (c:Concept)" in q and "OPTIONAL MATCH (z:Zettel)" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                """
                SELECT c.id, c.name, c.domain_theory, c.msc2020, z.id, z.title
                FROM Concept c
                LEFT JOIN Zettel z ON z.master_concept = c.id
                WHERE c.name LIKE ? OR c.id LIKE ?
                LIMIT 25
                """,
                (like, like),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        if "MATCH (c:Concept)" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                "SELECT id, name, domain_theory FROM Concept WHERE name LIKE ? OR id LIKE ? LIMIT 10",
                (like, like),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        if "MATCH (b:Book)" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                """
                SELECT b.id, b.title, b.total_rows, a.id, a.heading, a.page
                FROM Book b
                LEFT JOIN Anchor a ON a.book_id = b.id
                WHERE b.id LIKE ? OR b.title LIKE ?
                LIMIT 20
                """,
                (like, like),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        if "MATCH (a:Anchor)" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                "SELECT id, book_id, heading, page FROM Anchor WHERE heading LIKE ? OR id LIKE ? OR leittext LIKE ? LIMIT 15",
                (like, like, like),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        if "MERGE (s:ElaboratedSymbol" in q:
            m_id = re.search(r'id:\s*"([^"]*)"', q)
            m_mod = re.search(r'module_name\s*=\s*"([^"]*)"', q)
            m_sym = re.search(r'symbol_name\s*=\s*"([^"]*)"', q)
            m_sig = re.search(r'type_signature\s*=\s*"([^"]*)"', q)
            if m_id:
                cur.execute(
                    "INSERT OR REPLACE INTO ElaboratedSymbol VALUES (?, ?, ?, ?)",
                    (
                        m_id.group(1),
                        m_mod.group(1) if m_mod else "",
                        m_sym.group(1) if m_sym else "",
                        m_sig.group(1) if m_sig else "",
                    ),
                )
                self.conn.commit()
            return _FallbackQueryResult([])

        if "MATCH (s:ElaboratedSymbol)" in q:
            m_term = re.search(r'CONTAINS\s+"([^"]*)"', q)
            term = m_term.group(1) if m_term else ""
            like = f"%{term}%"
            cur.execute(
                "SELECT id, symbol_name, type_signature FROM ElaboratedSymbol WHERE symbol_name LIKE ? LIMIT 5",
                (like,),
            )
            return _FallbackQueryResult([list(r) for r in cur.fetchall()])

        return _FallbackQueryResult([])

    def _init_tables(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE Book (
                id TEXT PRIMARY KEY,
                title TEXT,
                total_rows INTEGER,
                license TEXT,
                format TEXT
            );
            CREATE TABLE Anchor (
                id TEXT PRIMARY KEY,
                book_id TEXT,
                heading TEXT,
                leittext TEXT,
                page INTEGER
            );
            CREATE TABLE Concept (
                id TEXT PRIMARY KEY,
                name TEXT,
                msc2020 TEXT,
                domain_theory TEXT
            );
            CREATE TABLE Concordance (
                concept_id TEXT,
                prover TEXT,
                tactic TEXT,
                syntax TEXT
            );
            CREATE TABLE Zettel (
                id TEXT PRIMARY KEY,
                title TEXT,
                layer INTEGER,
                status TEXT,
                maturity TEXT,
                verification TEXT,
                source_book TEXT,
                source_anchor TEXT,
                master_concept TEXT,
                file_path TEXT
            );
            CREATE TABLE StitchedText (
                id TEXT PRIMARY KEY,
                title TEXT,
                file_path TEXT
            );
            CREATE TABLE ElaboratedSymbol (
                id TEXT PRIMARY KEY,
                module_name TEXT,
                symbol_name TEXT,
                type_signature TEXT
            );
            """
        )

    def _load_archive(self) -> None:
        cur = self.conn.cursor()
        if self.kz_path is not None:
            try:
                with zipfile.ZipFile(self.kz_path, "r") as zf:
                    names = set(zf.namelist())
                    if "Book.csv" in names:
                        raw = zf.read("Book.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            hdr = [h.strip().lower() for h in rows[0]]
                            has_hdr = bool(hdr and hdr[0] in ("id", "key"))
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) < 2:
                                    continue
                                bid = r[0].strip()
                                btitle = r[1].strip()
                                if has_hdr and "total_rows" in hdr:
                                    t_idx = hdr.index("total_rows")
                                    total_r = int(r[t_idx]) if t_idx < len(r) and r[t_idx].isdigit() else 0
                                    lic = r[hdr.index("license")].strip() if "license" in hdr and hdr.index("license") < len(r) else "Unknown"
                                    fmt = r[hdr.index("format")].strip() if "format" in hdr and hdr.index("format") < len(r) else "Markdown"
                                else:
                                    total_r = int(r[2]) if len(r) > 2 and r[2].strip().isdigit() else 0
                                    lic = r[2].strip() if len(r) > 2 and not r[2].strip().isdigit() else "Unknown"
                                    fmt = r[3].strip() if len(r) > 3 else "Markdown"
                                cur.execute("INSERT OR REPLACE INTO Book VALUES (?, ?, ?, ?, ?)", (bid, btitle, total_r, lic, fmt))

                    if "Section.csv" in names:
                        raw = zf.read("Section.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            hdr = [h.strip().lower() for h in rows[0]]
                            has_hdr = bool(hdr and hdr[0] in ("id", "anchor"))
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) < 4:
                                    continue
                                sid = r[0].strip()
                                sbook = r[1].strip()
                                if has_hdr and "heading" in hdr:
                                    h_idx = hdr.index("heading")
                                    l_idx = hdr.index("leittext") if "leittext" in hdr else 3
                                    p_idx = hdr.index("page") if "page" in hdr else 4
                                    heading = r[h_idx].strip() if h_idx < len(r) else ""
                                    leit = r[l_idx].strip() if l_idx < len(r) else ""
                                    page = int(r[p_idx]) if p_idx < len(r) and r[p_idx].strip().lstrip("-").isdigit() else 0
                                else:
                                    if r[2].strip().lstrip("-").isdigit():
                                        page = int(r[2].strip())
                                        leit = r[3].strip()
                                        heading = leit[:120]
                                    else:
                                        heading = r[2].strip()
                                        leit = r[3].strip()
                                        page = int(r[4].strip()) if len(r) > 4 and r[4].strip().lstrip("-").isdigit() else 0
                                cur.execute("INSERT OR REPLACE INTO Anchor VALUES (?, ?, ?, ?, ?)", (sid, sbook, heading, leit, page))

                    if "Concept.csv" in names:
                        raw = zf.read("Concept.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            has_hdr = rows[0][0].strip().lower() == "id"
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) >= 2:
                                    cur.execute(
                                        "INSERT OR REPLACE INTO Concept VALUES (?, ?, ?, ?)",
                                        (r[0].strip(), r[1].strip(), r[2].strip() if len(r) > 2 else "", r[3].strip() if len(r) > 3 else ""),
                                    )

                    if "Concordance.csv" in names:
                        raw = zf.read("Concordance.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            has_hdr = rows[0][0].strip().lower() == "concept_id"
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) >= 3:
                                    cur.execute(
                                        "INSERT INTO Concordance VALUES (?, ?, ?, ?)",
                                        (r[0].strip(), r[1].strip(), r[2].strip(), r[3].strip() if len(r) > 3 else ""),
                                    )

                    if "Zettel.csv" in names:
                        raw = zf.read("Zettel.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            has_hdr = rows[0][0].strip().lower() == "id"
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) >= 2:
                                    layer = int(r[2]) if len(r) > 2 and r[2].strip().isdigit() else 4
                                    cur.execute(
                                        "INSERT OR REPLACE INTO Zettel VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (
                                            r[0].strip(),
                                            r[1].strip(),
                                            layer,
                                            r[3].strip() if len(r) > 3 else "verified",
                                            r[4].strip() if len(r) > 4 else "seedling",
                                            r[5].strip() if len(r) > 5 else "anchor-resolved",
                                            r[6].strip() if len(r) > 6 else "",
                                            r[7].strip() if len(r) > 7 else "",
                                            r[8].strip() if len(r) > 8 else "",
                                            r[9].strip() if len(r) > 9 else "",
                                        ),
                                    )

                    if "StitchedText.csv" in names:
                        raw = zf.read("StitchedText.csv").decode("utf-8", errors="replace")
                        rows = list(csv.reader(io.StringIO(raw)))
                        if rows:
                            has_hdr = rows[0][0].strip().lower() == "id"
                            for r in (rows[1:] if has_hdr else rows):
                                if len(r) >= 2:
                                    bsize = int(r[4]) if len(r) > 4 and r[4].strip().isdigit() else 0
                                    cur.execute(
                                        "INSERT OR REPLACE INTO StitchedText VALUES (?, ?, ?, ?, ?)",
                                        (
                                            r[0].strip(),
                                            r[1].strip(),
                                            r[2].strip() if len(r) > 2 else "",
                                            r[3].strip() if len(r) > 3 else "",
                                            bsize,
                                        ),
                                    )
            except Exception:
                pass

        cur.execute(
            """
            UPDATE Book
            SET total_rows = (SELECT count(*) FROM Anchor WHERE Anchor.book_id = Book.id)
            WHERE total_rows = 0
            """
        )

        cur.execute("SELECT count(*) FROM Concept")
        if cur.fetchone()[0] == 0 and self.ontology_dir.is_dir():
            idx_p = self.ontology_dir / "master-authority-index.json"
            if idx_p.is_file():
                try:
                    mdata = json.loads(idx_p.read_text(encoding="utf-8"))
                    for c in mdata.get("master_concepts", []):
                        cid = c.get("concept_id", "")
                        cname = c.get("canonical_name", "")
                        msc = json.dumps(c.get("msc2020", []), ensure_ascii=True)
                        dom = c.get("ranganathan_facet", {}).get("domain_theory", "")
                        cur.execute("INSERT OR REPLACE INTO Concept VALUES (?, ?, ?, ?)", (cid, cname, msc, dom))
                        for p_name, p_val in c.get("prover_mappings", {}).items():
                            if isinstance(p_val, dict):
                                cur.execute(
                                    "INSERT INTO Concordance VALUES (?, ?, ?, ?)",
                                    (cid, p_name, ";".join(p_val.get("primary_tactics", [])), p_val.get("syntax_pattern", "")),
                                )
                except Exception:
                    pass

            conc_p = self.ontology_dir / "cross-itp-concordance.v1.json"
            if conc_p.is_file():
                try:
                    cdata = json.loads(conc_p.read_text(encoding="utf-8"))
                    for m in cdata.get("mechanisms", cdata.get("canonical_mechanisms", [])):
                        mid = m.get("id") or m.get("mechanism_id") or ""
                        mname = m.get("canonical_name", "")
                        if mid:
                            cur.execute("INSERT OR IGNORE INTO Concept VALUES (?, ?, ?, ?)", (mid, mname, "", m.get("category", "cross-itp")))
                            for p_name, p_val in m.get("provers", {}).items():
                                if isinstance(p_val, dict):
                                    tacs = p_val.get("tactics", p_val.get("primary_tactics", []))
                                    tacs_str = ";".join(tacs) if isinstance(tacs, list) else str(tacs)
                                    syn = p_val.get("idiom") or p_val.get("syntax_pattern") or ""
                                    cur.execute("INSERT INTO Concordance VALUES (?, ?, ?, ?)", (mid, p_name, tacs_str, str(syn)))
                except Exception:
                    pass

        self.conn.commit()



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
        root = self.config_path.parent
        for db_meta in self.config.get("databases", []):
            if not db_meta.get("enabled", True):
                continue
            db_id = db_meta["id"]
            rel_path = db_meta.get("path", "")
            full_path = (root / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)
            arch_rel = db_meta.get("archive_path") or db_meta.get("archivePath") or "kuzu/prover_knowledge.kz"
            arch_path = (root / arch_rel).resolve() if not Path(arch_rel).is_absolute() else Path(arch_rel)
            if not arch_path.is_file():
                cand_kz = REPO_ROOT / "kuzu" / "prover_knowledge.kz"
                if cand_kz.is_file():
                    arch_path = cand_kz

            if HAS_KUZU and full_path.exists():
                try:
                    read_only = bool(db_meta.get("read_only", False))
                    kdb = kuzu.Database(str(full_path), read_only=read_only)
                    kconn = kuzu.Connection(kdb)
                    self.databases[db_id] = db_meta
                    self.connections[db_id] = kconn
                    continue
                except Exception as exc:
                    self.databases[db_id] = {**db_meta, "error": str(exc)}

            if db_id in ("prover", "lsp_cache") and (arch_path.is_file() or (REPO_ROOT / "vendor" / "itp-ontology").is_dir()):
                try:
                    fb_conn = ArchiveFallbackConnection(arch_path if db_id == "prover" else None, REPO_ROOT / "vendor" / "itp-ontology")
                    self.databases[db_id] = {**db_meta, "backend": "archive_fallback"}
                    self.connections[db_id] = fb_conn
                except Exception as exc:
                    self.databases[db_id] = {**db_meta, "error": str(exc)}
            else:
                self.databases[db_id] = {**db_meta, "error": "file_not_found"}

    def lookup_concordance(
        self,
        concept: str,
        source_prover: str | None = None,
        target_prover: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query cross-ITP concordance mappings from the prover knowledge base or JSON index."""
        conn = self.connections.get("prover")
        if isinstance(conn, ArchiveFallbackConnection):
            cur = conn.conn.cursor()
            like = f"%{concept.strip()}%"
            sql = (
                "SELECT c.id, c.name, k.prover, k.tactic, k.syntax "
                "FROM Concordance k JOIN Concept c ON c.id = k.concept_id "
                "WHERE (c.id LIKE ? OR c.name LIKE ? OR k.tactic LIKE ?)"
            )
            params: list[Any] = [like, like, like]
            if target_prover:
                sql += " AND lower(k.prover) = lower(?)"
                params.append(target_prover.strip())
            sql += " LIMIT 30"
            cur.execute(sql, params)
            return [
                {
                    "concept_id": r[0],
                    "concept_name": r[1],
                    "prover": r[2],
                    "tactic": r[3],
                    "syntax": r[4],
                }
                for r in cur.fetchall()
            ]
        # Fallback to reading cross-itp-concordance.v1.json directly
        conc_p = REPO_ROOT / "vendor" / "itp-ontology" / "cross-itp-concordance.v1.json"
        out: list[dict[str, Any]] = []
        if conc_p.is_file():
            q = concept.strip().lower()
            cdata = json.loads(conc_p.read_text(encoding="utf-8"))
            for m in cdata.get("mechanisms", cdata.get("canonical_mechanisms", [])):
                mid = str(m.get("id") or m.get("mechanism_id") or "")
                mname = str(m.get("canonical_name") or "")
                if q in mid.lower() or q in mname.lower():
                    for p_name, p_val in m.get("provers", {}).items():
                        if target_prover and p_name.lower() != target_prover.strip().lower():
                            continue
                        if isinstance(p_val, dict):
                            tacs = p_val.get("tactics", p_val.get("primary_tactics", []))
                            out.append({
                                "concept_id": mid,
                                "concept_name": mname,
                                "prover": p_name,
                                "tactic": ";".join(tacs) if isinstance(tacs, list) else str(tacs),
                                "syntax": str(p_val.get("idiom") or p_val.get("syntax_pattern") or ""),
                            })
        return out

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

        has_internal = "project_internal" in self.connections
        prover_ok = (
            results["prover"].get("Book", 0) >= 29 and
            results["prover"].get("Concept", 0) >= 100 and
            results["prover"].get("Zettel", 0) >= 455 and
            len(epistemic) > 0
        )
        internal_ok = (
            results["project_internal"].get("Requirement", 0) >= 150 and
            results["project_internal"].get("ADR", 0) >= 20 and
            results["project_internal"].get("LeanDeclaration", 0) >= 100 and
            len(trace) > 0
        ) if has_internal else True
        ok = prover_ok and internal_ok
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
                "backend": meta.get("backend", "kuzu" if HAS_KUZU else "archive_fallback"),
                "error": meta.get("error"),
            }
        return report


def self_test() -> None:
    print("Running kuzu_federation self-test...")
    engine = FederatedKuzuEngine()
    status = engine.status_report()
    print(f"Kuzu native installed: {status['kuzu_installed']}")
    print("Database Status:")
    for db_id, info in status["databases"].items():
        print(f"  [{db_id}] {info['name']} (scope: {info['scope']}, connected: {info['connected']}, backend: {info.get('backend')})")

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

    # 3. Test Traceability Query (if project_internal connected)
    if "project_internal" in engine.connections:
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

    # 5. Test Concordance Lookup
    conc = engine.lookup_concordance("Induction")
    print(f"Concordance 'Induction' returned {len(conc)} mappings.")
    assert len(conc) > 0, "Expected non-empty concordance mappings"

    # 6. Test Integrity Verification
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

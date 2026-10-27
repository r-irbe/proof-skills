#!/usr/bin/env python3
# graph/export_kuzu.py
# Kuzu Embedded Property Graph Compiler and Exporter (TASK-LIB-07).
# Strict 7-bit ASCII only (INV-001).

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from typing import Any

try:
    import kuzu
    HAS_KUZU = True
except ImportError:
    HAS_KUZU = False


def to_ascii(s: Any) -> str:
    if s is None:
        return ""
    st = str(s)
    nfkd = unicodedata.normalize("NFKD", st)
    return nfkd.encode("ASCII", "ignore").decode("ASCII").strip()


def sanitize_val(s: Any) -> str:
    return to_ascii(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")


def remove_path(p: Path) -> None:
    wal = Path(str(p) + ".wal")
    if wal.exists():
        wal.unlink()
    if not p.exists():
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()


def extract_frontmatter(txt: str) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if not txt.startswith("---"):
        return meta
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return meta
    fm = parts[1]
    current_key = None
    for line in fm.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- ") and current_key:
            val = s[2:].strip().strip('"').strip("'")
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(val)
        elif ":" in s:
            k, v = s.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            current_key = k
            meta[k] = v if v else []
    return meta


def build_prover_graph(garden_root: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / "prover_knowledge.kuzu"
    zip_path = out_dir / "prover_knowledge.kz"
    remove_path(db_path)
    remove_path(zip_path)

    books_dir = garden_root / "source-materials" / "books"
    books: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []

    if books_dir.exists():
        for bdir in sorted(books_dir.iterdir()):
            if not bdir.is_dir():
                continue
            afile = bdir / "anchors.v1.json"
            if not afile.exists():
                continue
            try:
                adata = json.loads(afile.read_text(encoding="utf-8"))
                rows = adata.get("rows", [])
                b_id = bdir.name
                first_h = rows[0].get("heading_text", b_id) if rows else b_id
                pfile = bdir / "provenance.json"
                prov: dict[str, Any] = {}
                if pfile.exists():
                    try:
                        prov = json.loads(pfile.read_text(encoding="utf-8"))
                    except Exception:
                        prov = {}
                full_title = prov.get("title") or first_h
                raw_lic = prov.get("license", "Unknown")
                lic = raw_lic.get("spdx", "Unknown") if isinstance(raw_lic, dict) else str(raw_lic or "Unknown")
                raw_real = prov.get("realization", "Markdown")
                fmt = raw_real.get("files", "Markdown") if isinstance(raw_real, dict) else "Markdown"
                books.append({
                    "id": b_id,
                    "title": to_ascii(full_title),
                    "total_rows": len(rows),
                    "license": to_ascii(lic),
                    "format": to_ascii(fmt),
                })
                for r in rows:
                    anchors.append({
                        "id": to_ascii(r.get("anchor", "")),
                        "book_id": b_id,
                        "heading": to_ascii(r.get("heading_text", "")),
                        "leittext": to_ascii(r.get("leittext", ""))[:200],
                        "page": int(r.get("print_page", 0)),
                    })
            except Exception as exc:
                print("Warning: failed reading " + str(afile) + ": " + str(exc))

    concepts: list[dict[str, Any]] = []
    concordances: list[dict[str, Any]] = []

    idx_candidates = [
        garden_root / "source-materials" / "indexes" / "master-authority-index.json",
        Path(__file__).resolve().parent.parent / "vendor" / "itp-ontology" / "master-authority-index.json",
    ]
    master_idx_path = next((p for p in idx_candidates if p.exists()), None)
    if master_idx_path is not None:
        try:
            mdata = json.loads(master_idx_path.read_text(encoding="utf-8"))
            for c in mdata.get("master_concepts", []):
                cid = to_ascii(c.get("concept_id", ""))
                cname = to_ascii(c.get("canonical_name", ""))
                msc_list = c.get("msc2020", [])
                msc_str = to_ascii(json.dumps(msc_list) if isinstance(msc_list, list) else str(msc_list))
                dom = to_ascii(c.get("ranganathan_facet", {}).get("domain_theory", ""))
                concepts.append({
                    "id": cid,
                    "name": cname,
                    "msc2020": msc_str,
                    "domain_theory": dom,
                })
                for p_name, p_val in c.get("prover_mappings", {}).items():
                    if isinstance(p_val, dict):
                        tacs = ";".join(p_val.get("primary_tactics", []))
                        syn = p_val.get("syntax_pattern", "")
                        concordances.append({
                            "concept_id": cid,
                            "prover": to_ascii(p_name),
                            "tactic": to_ascii(tacs),
                            "syntax": to_ascii(syn),
                        })
        except Exception as exc:
            print("Warning: failed reading master-authority-index.json: " + str(exc))

    conc_candidates = [
        garden_root / "source-materials" / "indexes" / "cross-itp-concordance.v1.json",
        Path(__file__).resolve().parent.parent / "vendor" / "itp-ontology" / "cross-itp-concordance.v1.json",
    ]
    conc_json_path = next((p for p in conc_candidates if p.exists()), None)
    if conc_json_path is not None:
        try:
            cdata = json.loads(conc_json_path.read_text(encoding="utf-8"))
            for m in cdata.get("mechanisms", cdata.get("canonical_mechanisms", [])):
                mid = to_ascii(m.get("id") or m.get("mechanism_id") or "")
                mname = to_ascii(m.get("canonical_name", ""))
                if not mid:
                    continue
                if not any(c["id"] == mid for c in concepts):
                    concepts.append({
                        "id": mid,
                        "name": mname,
                        "msc2020": "",
                        "domain_theory": to_ascii(m.get("category", "cross-itp")),
                    })
                for p_name, p_val in m.get("provers", {}).items():
                    if isinstance(p_val, dict):
                        raw_tacs = p_val.get("tactics", p_val.get("primary_tactics", []))
                        tacs = ";".join(raw_tacs) if isinstance(raw_tacs, list) else str(raw_tacs)
                        syn = p_val.get("idiom") or p_val.get("syntax_pattern") or ""
                        concordances.append({
                            "concept_id": mid,
                            "prover": to_ascii(p_name),
                            "tactic": to_ascii(tacs),
                            "syntax": to_ascii(syn),
                        })
        except Exception:
            pass


    stitched_dir = garden_root / "source-materials" / "stitched"
    stitched: list[dict[str, Any]] = []
    if stitched_dir.exists():
        for sfile in sorted(stitched_dir.glob("*.md")):
            s_id = sfile.stem
            stitched.append({
                "id": s_id,
                "title": to_ascii(s_id),
                "file_path": str(sfile.relative_to(garden_root.parent.parent)),
            })

    # Ingest Zettels (books, itp, derived, concepts, invariants)
    zettels_dir = garden_root / "zettels"
    zettels: list[dict[str, Any]] = []
    seen_zids: set[str] = set()
    if zettels_dir.exists():
        for zf in sorted(zettels_dir.glob("**/*.md")):
            txt = zf.read_text(encoding="utf-8", errors="ignore")
            fm = extract_frontmatter(txt)
            zid = to_ascii(fm.get("id") or zf.stem)
            if zid in seen_zids:
                continue
            seen_zids.add(zid)
            ztitle = fm.get("title") or zf.stem
            zlayer = 4
            try:
                zlayer = int(fm.get("layer", 4))
            except Exception:
                zlayer = 4
            zstatus = fm.get("status", "verified")
            zmat = fm.get("maturity", "seedling")
            zver = fm.get("verification", "anchor-resolved")
            zbook = fm.get("source_book", "")
            zanchor = fm.get("source_anchor", "")
            zconcept = fm.get("master_concept", "")
            rel_list = fm.get("related", [])
            if isinstance(rel_list, str):
                rel_list = [rel_list]
            zettels.append({
                "id": to_ascii(zid),
                "title": to_ascii(ztitle),
                "layer": zlayer,
                "status": to_ascii(zstatus),
                "maturity": to_ascii(zmat),
                "verification": to_ascii(zver),
                "source_book": to_ascii(zbook),
                "source_anchor": to_ascii(zanchor),
                "master_concept": to_ascii(zconcept),
                "related": [to_ascii(r) for r in rel_list if r],
                "file_path": str(zf.relative_to(garden_root.parent.parent)),
            })

    kuzu_built = False
    if HAS_KUZU:
        try:
            kdb = kuzu.Database(str(db_path))
            kconn = kuzu.Connection(kdb)

            kconn.execute("CREATE NODE TABLE Book (id STRING, title STRING, total_rows INT64, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE Concept (id STRING, name STRING, msc2020 STRING, domain_theory STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE Anchor (id STRING, book_id STRING, heading STRING, leittext STRING, page INT64, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE StitchedText (id STRING, title STRING, file_path STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE Zettel (id STRING, title STRING, layer INT64, status STRING, maturity STRING, verification STRING, source_book STRING, source_anchor STRING, master_concept STRING, file_path STRING, PRIMARY KEY(id))")

            kconn.execute("CREATE REL TABLE ANCHORS_IN (FROM Anchor TO Book)")
            kconn.execute("CREATE REL TABLE ZETTEL_IN_BOOK (FROM Zettel TO Book)")
            kconn.execute("CREATE REL TABLE ZETTEL_ANCHORS_AT (FROM Zettel TO Anchor)")
            kconn.execute("CREATE REL TABLE ZETTEL_EXEMPLIFIES_CONCEPT (FROM Zettel TO Concept)")
            kconn.execute("CREATE REL TABLE ZETTEL_RELATES_TO (FROM Zettel TO Zettel)")

            book_ids = set()
            for b in books:
                safe_id = sanitize_val(b["id"])
                safe_title = sanitize_val(b["title"])
                kconn.execute('CREATE (b:Book {id: "' + safe_id + '", title: "' + safe_title + '", total_rows: ' + str(b["total_rows"]) + '})')
                book_ids.add(safe_id)

            concept_ids = set()
            for c in concepts:
                safe_id = sanitize_val(c["id"])
                safe_name = sanitize_val(c["name"])
                safe_msc = sanitize_val(c["msc2020"])
                safe_dom = sanitize_val(c["domain_theory"])
                kconn.execute('CREATE (c:Concept {id: "' + safe_id + '", name: "' + safe_name + '", msc2020: "' + safe_msc + '", domain_theory: "' + safe_dom + '"})')
                concept_ids.add(safe_id)

            for s in stitched:
                safe_id = sanitize_val(s["id"])
                safe_title = sanitize_val(s["title"])
                safe_path = sanitize_val(s["file_path"])
                kconn.execute('CREATE (s:StitchedText {id: "' + safe_id + '", title: "' + safe_title + '", file_path: "' + safe_path + '"})')

            anchor_ids = set()
            for a in anchors:
                safe_id = sanitize_val(a["id"])
                safe_bid = sanitize_val(a["book_id"])
                safe_h = sanitize_val(a["heading"])
                safe_l = sanitize_val(a["leittext"])
                kconn.execute('CREATE (a:Anchor {id: "' + safe_id + '", book_id: "' + safe_bid + '", heading: "' + safe_h + '", leittext: "' + safe_l + '", page: ' + str(a["page"]) + '})')
                anchor_ids.add(safe_id)
                if safe_bid in book_ids:
                    kconn.execute('MATCH (a:Anchor {id: "' + safe_id + '"}), (b:Book {id: "' + safe_bid + '"}) CREATE (a)-[:ANCHORS_IN]->(b)')

            zettel_ids = set()
            for z in zettels:
                safe_zid = sanitize_val(z["id"])
                safe_ztitle = sanitize_val(z["title"])
                safe_zstatus = sanitize_val(z["status"])
                safe_zmat = sanitize_val(z["maturity"])
                safe_zver = sanitize_val(z["verification"])
                safe_zb = sanitize_val(z["source_book"])
                safe_za = sanitize_val(z["source_anchor"])
                safe_zc = sanitize_val(z["master_concept"])
                safe_zp = sanitize_val(z["file_path"])
                kconn.execute('CREATE (z:Zettel {id: "' + safe_zid + '", title: "' + safe_ztitle + '", layer: ' + str(z["layer"]) + ', status: "' + safe_zstatus + '", maturity: "' + safe_zmat + '", verification: "' + safe_zver + '", source_book: "' + safe_zb + '", source_anchor: "' + safe_za + '", master_concept: "' + safe_zc + '", file_path: "' + safe_zp + '"})')
                zettel_ids.add(safe_zid)

            # Build Zettel relationships
            for z in zettels:
                safe_zid = sanitize_val(z["id"])
                if z["source_book"] in book_ids:
                    safe_bid = sanitize_val(z["source_book"])
                    kconn.execute('MATCH (z:Zettel {id: "' + safe_zid + '"}), (b:Book {id: "' + safe_bid + '"}) CREATE (z)-[:ZETTEL_IN_BOOK]->(b)')
                if z["source_anchor"] in anchor_ids:
                    safe_aid = sanitize_val(z["source_anchor"])
                    kconn.execute('MATCH (z:Zettel {id: "' + safe_zid + '"}), (a:Anchor {id: "' + safe_aid + '"}) CREATE (z)-[:ZETTEL_ANCHORS_AT]->(a)')
                if z["master_concept"] in concept_ids:
                    safe_cid = sanitize_val(z["master_concept"])
                    kconn.execute('MATCH (z:Zettel {id: "' + safe_zid + '"}), (c:Concept {id: "' + safe_cid + '"}) CREATE (z)-[:ZETTEL_EXEMPLIFIES_CONCEPT]->(c)')
                for rel in z.get("related", []):
                    safe_rel = sanitize_val(rel)
                    if safe_rel in zettel_ids and safe_rel != safe_zid:
                        kconn.execute('MATCH (z1:Zettel {id: "' + safe_zid + '"}), (z2:Zettel {id: "' + safe_rel + '"}) CREATE (z1)-[:ZETTEL_RELATES_TO]->(z2)')

            kuzu_built = True
        except Exception as exc:
            print("Warning during Kuzu native population: " + str(exc))

    with zipfile.ZipFile(str(zip_path), "w", compression=zipfile.ZIP_DEFLATED) as zf:
        b_buf = io.StringIO()
        b_writer = csv.writer(b_buf)
        b_writer.writerow(["id", "title", "total_rows", "license", "format"])
        for b in books:
            b_writer.writerow([
                b["id"],
                b["title"],
                b["total_rows"],
                b.get("license", "Unknown"),
                b.get("format", "Markdown"),
            ])
        zf.writestr("Book.csv", b_buf.getvalue().encode("ascii"))

        s_buf = io.StringIO()
        s_writer = csv.writer(s_buf)
        s_writer.writerow(["id", "book_id", "heading", "leittext", "page"])
        for a in anchors:
            s_writer.writerow([a["id"], a["book_id"], a["heading"], a["leittext"], a["page"]])
        zf.writestr("Section.csv", s_buf.getvalue().encode("ascii"))

        contains_buf = io.StringIO()
        contains_writer = csv.writer(contains_buf)
        contains_writer.writerow(["from", "to"])
        for a in anchors:
            contains_writer.writerow([a["book_id"], a["id"]])
        zf.writestr("CONTAINS_Book_Section.csv", contains_buf.getvalue().encode("ascii"))

        c_buf = io.StringIO()
        c_writer = csv.writer(c_buf)
        c_writer.writerow(["id", "name", "msc2020", "domain_theory"])
        for c in concepts:
            c_writer.writerow([c["id"], c["name"], c["msc2020"], c["domain_theory"]])
        zf.writestr("Concept.csv", c_buf.getvalue().encode("ascii"))

        cd_buf = io.StringIO()
        cd_writer = csv.writer(cd_buf)
        cd_writer.writerow(["concept_id", "prover", "tactic", "syntax"])
        for cd in concordances:
            cd_writer.writerow([cd["concept_id"], cd["prover"], cd["tactic"], cd["syntax"]])
        zf.writestr("Concordance.csv", cd_buf.getvalue().encode("ascii"))

        z_buf = io.StringIO()
        z_writer = csv.writer(z_buf)
        z_writer.writerow(["id", "title", "layer", "status", "maturity", "verification", "source_book", "source_anchor", "master_concept", "file_path"])
        for z in zettels:
            z_writer.writerow([z["id"], z["title"], z["layer"], z["status"], z["maturity"], z["verification"], z["source_book"], z["source_anchor"], z["master_concept"], z["file_path"]])
        zf.writestr("Zettel.csv", z_buf.getvalue().encode("ascii"))

        st_buf = io.StringIO()
        st_writer = csv.writer(st_buf)
        st_writer.writerow(["id", "book_id", "title", "file_path", "byte_size"])
        for st in stitched:
            st_writer.writerow([
                st["id"],
                st.get("book_id", ""),
                st.get("title", ""),
                st.get("file_path", ""),
                st.get("byte_size", 0),
            ])
        zf.writestr("StitchedText.csv", st_buf.getvalue().encode("ascii"))

        schema_cypher = (
            "CREATE NODE TABLE Book(id STRING, title STRING, total_rows INT64, license STRING, format STRING, PRIMARY KEY (id));\n"
            "CREATE NODE TABLE Section(id STRING, book_id STRING, heading STRING, leittext STRING, page INT64, PRIMARY KEY (id));\n"
            "CREATE NODE TABLE Concept(id STRING, name STRING, msc2020 STRING, domain_theory STRING, PRIMARY KEY (id));\n"
            "CREATE NODE TABLE Concordance(concept_id STRING, prover STRING, tactic STRING, syntax STRING);\n"
            "CREATE NODE TABLE Zettel(id STRING, title STRING, layer INT64, status STRING, maturity STRING, verification STRING, source_book STRING, source_anchor STRING, master_concept STRING, file_path STRING, PRIMARY KEY (id));\n"
            "CREATE NODE TABLE StitchedText(id STRING, book_id STRING, title STRING, file_path STRING, byte_size INT64, PRIMARY KEY (id));\n"
            "CREATE REL TABLE CONTAINS(FROM Book TO Section);\n"
        )
        zf.writestr("schema.cypher", schema_cypher.encode("ascii"))
        copy_cypher = (
            'COPY Book FROM "Book.csv" (HEADER=true);\n'
            'COPY Section FROM "Section.csv" (HEADER=true);\n'
            'COPY CONTAINS FROM "CONTAINS_Book_Section.csv" (HEADER=true);\n'
            'COPY Concept FROM "Concept.csv" (HEADER=true);\n'
            'COPY Concordance FROM "Concordance.csv" (HEADER=true);\n'
            'COPY Zettel FROM "Zettel.csv" (HEADER=true);\n'
            'COPY StitchedText FROM "StitchedText.csv" (HEADER=true);\n'
        )
        zf.writestr("copy.cypher", copy_cypher.encode("ascii"))
        zf.writestr("index.cypher", b"")

        manifest = {
            "version": "1.1.0",
            "scope": "public_prover",
            "total_books": len(books),
            "total_anchors": len(anchors),
            "total_concepts": len(concepts),
            "total_concordances": len(concordances),
            "total_stitched": len(stitched),
            "total_zettels": len(zettels),
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2).encode("ascii"))

    return {
        "status": "success",
        "scope": "public_prover",
        "kuzu_native": kuzu_built,
        "db_path": str(db_path),
        "zip_path": str(zip_path),
        "books": len(books),
        "anchors": len(anchors),
        "concepts": len(concepts),
        "concordances": len(concordances),
        "zettels": len(zettels),
    }


def build_internal_graph(garden_root: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / "project_internal.kuzu"
    remove_path(db_path)

    mocs_dir = garden_root / "mocs"
    inbox_dir = garden_root / "inbox"
    mocs: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    if mocs_dir.exists():
        for mfile in sorted(mocs_dir.glob("*.md")):
            mocs.append({
                "id": mfile.stem,
                "title": to_ascii(mfile.stem),
                "file_path": str(mfile.relative_to(garden_root.parent.parent)),
            })

    if inbox_dir.exists():
        for ifile in sorted(inbox_dir.glob("*.md")):
            artifacts.append({
                "id": ifile.stem,
                "title": to_ascii(ifile.stem),
                "size_bytes": ifile.stat().st_size,
                "file_path": str(ifile.relative_to(garden_root.parent.parent)),
            })

    # Ingest Requirements from system_requirements_final.md
    req_file = garden_root.parent / "system_requirements_final.md"
    requirements: list[dict[str, Any]] = []
    if req_file.exists():
        txt = req_file.read_text(encoding="utf-8")
        for m in re.finditer(r'^\|\s*(FUNC-\d+)\s*\|\s*\*\*?([^*|]+)\*\*?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', txt, re.MULTILINE):
            requirements.append({
                "id": to_ascii(m.group(1).strip()),
                "title": to_ascii(m.group(2).strip()),
                "description": to_ascii(m.group(3).strip())[:200],
                "priority": to_ascii(m.group(4).strip()),
                "source": to_ascii(m.group(5).strip())[:100],
            })

    # Ingest ADRs
    adrs: list[dict[str, Any]] = []
    adr_dirs = [garden_root / "adrs", garden_root.parent.parent / "specs" / "adr"]
    for adir in adr_dirs:
        if adir.exists():
            for af in sorted(adir.glob("*.md")):
                txt = af.read_text(encoding="utf-8", errors="ignore")
                fm = extract_frontmatter(txt)
                aid = fm.get("id") or af.stem
                title = fm.get("title") or af.stem
                stat = fm.get("status") or fm.get("disposition") or "active"
                mat = fm.get("maturity") or "seedling"
                adrs.append({
                    "id": to_ascii(aid),
                    "title": to_ascii(title),
                    "status": to_ascii(stat),
                    "maturity": to_ascii(mat),
                    "file_path": str(af.relative_to(garden_root.parent.parent)),
                    "text": txt,
                })

    # Ingest Evidence Cards (Claims and Dossiers)
    evidence: list[dict[str, Any]] = []
    ev_dir = garden_root / "evidence"
    if ev_dir.exists():
        for ef in sorted(ev_dir.glob("*.md")):
            txt = ef.read_text(encoding="utf-8", errors="ignore")
            fm = extract_frontmatter(txt)
            eid = fm.get("id") or ef.stem
            title = fm.get("title") or ef.stem
            kind = "dossier" if ef.stem.startswith("DOSSIER") else "claim"
            evidence.append({
                "id": to_ascii(eid),
                "title": to_ascii(title),
                "kind": kind,
                "file_path": str(ef.relative_to(garden_root.parent.parent)),
                "text": txt,
            })

    # Ingest Landmark Lean Declarations
    lean_root = garden_root.parent / "easci" / "lean" / "EASCI"
    lean_decls: list[dict[str, Any]] = []
    key_modules = [
        "Synthesis/ContinuousRelaxationTree.lean",
        "Synthesis/SimulationPreorder.lean",
        "Synthesis/RefinementTower.lean",
        "Synthesis/CoupledDynamics.lean",
        "Synthesis/HybridDynamics.lean",
        "Synthesis/TensorUnification.lean",
        "Synthesis/ProductState.lean",
        "QualityGates.lean",
        "AgenticSafety/Core/TrustVector.lean",
        "AgenticSafety/Core/TrustDynamics.lean",
        "ProvenanceChain/Core.lean",
        "PhasePortrait/Core.lean",
        "Logic/DynamicEpistemicAndRevision.lean",
        "Logic/TopologicalEpistemic.lean",
        "Logic/UnawarenessAndTacitKnowledge.lean",
        "Logic/HMSUnawarenessLattice.lean",
        "Logic/NominalEpistemicNabla.lean",
        "Logic/ProofTheoreticSemantics.lean",
        "Logic/BMSActionModelLogic.lean",
        "Logic/TopologicalEpistemicPlanning.lean",
        "Synthesis/LyapunovIncentive.lean",
        "CuspCatastrophe/Core.lean",
        "StochasticCCV/Doeblin.lean",
        "CCVEContraction.lean",
        "ReinforcementLearning/SymbioticPOMDP.lean",
        "TensorNetwork/TensorMDP.lean",
        "TensorNetwork/JunctionTree.lean",
        "AgenticSafety/KalmanConsensus.lean",
        "Logic/AumannAgreement.lean",
    ]
    decl_re = re.compile(r'^(theorem|lemma|def|structure|class)\s+([A-Za-z0-9_.\']+)', re.MULTILINE)
    for mod_rel in key_modules:
        lf = lean_root / mod_rel
        if lf.exists():
            lines = lf.read_text(encoding="utf-8", errors="ignore").splitlines()
            for idx, line in enumerate(lines, start=1):
                m = decl_re.match(line)
                if m:
                    kind, name = m.group(1), m.group(2)
                    mod_name = mod_rel.replace('/', '.').replace('.lean', '')
                    decl_id = f"EASCI.{mod_name}.{name}"
                    lean_decls.append({
                        "id": to_ascii(decl_id),
                        "name": to_ascii(name),
                        "kind": to_ascii(kind),
                        "module": to_ascii(mod_name),
                        "file_path": f"docs/easci/lean/EASCI/{mod_rel}",
                        "line": idx,
                    })

    kuzu_built = False
    if HAS_KUZU:
        try:
            kdb = kuzu.Database(str(db_path))
            kconn = kuzu.Connection(kdb)

            kconn.execute("CREATE NODE TABLE MOC (id STRING, title STRING, file_path STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE InternalArtifact (id STRING, title STRING, size_bytes INT64, file_path STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE Requirement (id STRING, title STRING, description STRING, priority STRING, source STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE ADR (id STRING, title STRING, status STRING, maturity STRING, file_path STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE EvidenceCard (id STRING, title STRING, kind STRING, file_path STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE LeanDeclaration (id STRING, name STRING, kind STRING, module STRING, file_path STRING, line INT64, PRIMARY KEY(id))")

            kconn.execute("CREATE REL TABLE ADR_SATISFIES_REQUIREMENT (FROM ADR TO Requirement)")
            kconn.execute("CREATE REL TABLE ADR_GROUNDED_IN_EVIDENCE (FROM ADR TO EvidenceCard)")
            kconn.execute("CREATE REL TABLE LEAN_VERIFIES_ADR (FROM LeanDeclaration TO ADR)")
            kconn.execute("CREATE REL TABLE LEAN_IMPLEMENTS_REQUIREMENT (FROM LeanDeclaration TO Requirement)")
            kconn.execute("CREATE REL TABLE EVIDENCE_SUPPORTS_REQUIREMENT (FROM EvidenceCard TO Requirement)")
            kconn.execute("CREATE REL TABLE EVIDENCE_SUPPORTS_DOSSIER (FROM EvidenceCard TO EvidenceCard)")
            kconn.execute("CREATE REL TABLE MOC_INDEXES_RECORD (FROM MOC TO ADR)")

            for m in mocs:
                safe_id = sanitize_val(m["id"])
                safe_title = sanitize_val(m["title"])
                safe_p = sanitize_val(m["file_path"])
                kconn.execute('CREATE (m:MOC {id: "' + safe_id + '", title: "' + safe_title + '", file_path: "' + safe_p + '"})')

            for a in artifacts:
                safe_id = sanitize_val(a["id"])
                safe_title = sanitize_val(a["title"])
                safe_p = sanitize_val(a["file_path"])
                kconn.execute('CREATE (a:InternalArtifact {id: "' + safe_id + '", title: "' + safe_title + '", size_bytes: ' + str(a["size_bytes"]) + ', file_path: "' + safe_p + '"})')

            req_ids = set()
            for r in requirements:
                rid = sanitize_val(r["id"])
                rtitle = sanitize_val(r["title"])
                rdesc = sanitize_val(r["description"])
                rprio = sanitize_val(r["priority"])
                rsrc = sanitize_val(r["source"])
                kconn.execute('CREATE (r:Requirement {id: "' + rid + '", title: "' + rtitle + '", description: "' + rdesc + '", priority: "' + rprio + '", source: "' + rsrc + '"})')
                req_ids.add(rid)

            adr_ids = set()
            for adr in adrs:
                aid = sanitize_val(adr["id"])
                atitle = sanitize_val(adr["title"])
                astat = sanitize_val(adr["status"])
                amat = sanitize_val(adr["maturity"])
                apath = sanitize_val(adr["file_path"])
                kconn.execute('CREATE (a:ADR {id: "' + aid + '", title: "' + atitle + '", status: "' + astat + '", maturity: "' + amat + '", file_path: "' + apath + '"})')
                adr_ids.add(aid)

            ev_ids = set()
            for ev in evidence:
                eid = sanitize_val(ev["id"])
                etitle = sanitize_val(ev["title"])
                ekind = sanitize_val(ev["kind"])
                epath = sanitize_val(ev["file_path"])
                kconn.execute('CREATE (e:EvidenceCard {id: "' + eid + '", title: "' + etitle + '", kind: "' + ekind + '", file_path: "' + epath + '"})')
                ev_ids.add(eid)

            for ld in lean_decls:
                did = sanitize_val(ld["id"])
                dname = sanitize_val(ld["name"])
                dkind = sanitize_val(ld["kind"])
                dmod = sanitize_val(ld["module"])
                dpath = sanitize_val(ld["file_path"])
                kconn.execute('CREATE (l:LeanDeclaration {id: "' + did + '", name: "' + dname + '", kind: "' + dkind + '", module: "' + dmod + '", file_path: "' + dpath + '", line: ' + str(ld["line"]) + '})')

            # Traceability: ADR -> Requirement
            canonical_adr_req: dict[str, list[str]] = {
                "ADR-INV-0001": ["FUNC-117", "FUNC-118"],
                "ADR-INV-0002": ["FUNC-04", "FUNC-115"],
                "ADR-INV-0004": ["FUNC-119", "FUNC-162"],
                "ADR-INV-0006": ["FUNC-07"],
                "ADR-INV-0008": ["FUNC-127"],
                "ADR-INV-0009": ["FUNC-125"],
                "ADR-INV-0016": ["FUNC-105", "FUNC-106", "FUNC-107", "FUNC-188", "FUNC-189", "FUNC-190", "FUNC-191"],
                "adr-001-frozen-epistemic-formal-core": ["FUNC-01"],
                "adr-002-tamper-evident-hash-chain-custody": ["FUNC-116"],
                "adr-004-subjective-logic-belief-fusion": ["FUNC-09", "FUNC-10"],
                "adr-inv-0015-multi-agent-cognitive-governance": ["FUNC-105"],
            }
            for adr in adrs:
                aid = sanitize_val(adr["id"])
                txt = adr.get("text", "")
                found_reqs = set(re.findall(r'FUNC-\d+', txt))
                if aid in canonical_adr_req:
                    found_reqs.update(canonical_adr_req[aid])
                for rid in found_reqs:
                    if rid in req_ids:
                        kconn.execute('MATCH (a:ADR {id: "' + aid + '"}), (r:Requirement {id: "' + rid + '"}) CREATE (a)-[:ADR_SATISFIES_REQUIREMENT]->(r)')

            # Traceability: ADR -> Evidence
            canonical_adr_ev: dict[str, list[str]] = {
                "ADR-INV-0016": ["DOSSIER-ALGOS-TENTH-LOOK"],
                "ADR-INV-0001": ["DOSSIER-INV-NST-2024-0847"],
                "ADR-INV-0002": ["DOSSIER-04-REDLINED-TACTICAL-ENCLAVE"],
                "ADR-INV-0003": ["DOSSIER-FILAB-AI-VIBES-FIRST-LOOK"],
            }
            for aid, evs in canonical_adr_ev.items():
                if aid in adr_ids:
                    for eid in evs:
                        if eid in ev_ids:
                            kconn.execute('MATCH (a:ADR {id: "' + aid + '"}), (e:EvidenceCard {id: "' + eid + '"}) CREATE (a)-[:ADR_GROUNDED_IN_EVIDENCE]->(e)')

            # Traceability: LeanDeclaration -> ADR
            for ld in lean_decls:
                did = sanitize_val(ld["id"])
                mod = ld["module"]
                target_adr = None
                if "SimulationPreorder" in mod or "ContinuousRelaxationTree" in mod or "RefinementTower" in mod or "CoupledDynamics" in mod or "HybridDynamics" in mod or "LyapunovIncentive" in mod:
                    target_adr = "ADR-INV-0016"
                elif "QualityGates" in mod:
                    target_adr = "ADR-INV-0002"
                elif "ProvenanceChain" in mod:
                    target_adr = "adr-002-tamper-evident-hash-chain-custody"
                elif "TrustVector" in mod or "TrustDynamics" in mod or "KalmanConsensus" in mod:
                    target_adr = "adr-inv-0015-multi-agent-cognitive-governance"
                elif "PhasePortrait" in mod:
                    target_adr = "ADR-INV-0001"
                elif "UnawarenessAndTacitKnowledge" in mod or "HMSUnawarenessLattice" in mod or "DynamicEpistemicAndRevision" in mod or "NominalEpistemicNabla" in mod or "ProofTheoreticSemantics" in mod or "BMSActionModelLogic" in mod or "TopologicalEpistemicPlanning" in mod or "JunctionTree" in mod or "AumannAgreement" in mod:
                    target_adr = "ADR-INV-0016"

                if target_adr and target_adr in adr_ids:
                    kconn.execute('MATCH (l:LeanDeclaration {id: "' + did + '"}), (a:ADR {id: "' + target_adr + '"}) CREATE (l)-[:LEAN_VERIFIES_ADR]->(a)')

            # Traceability: Evidence -> Requirement
            canonical_ev_req: dict[str, list[str]] = {
                "CLAIM-INV-NST-001": ["FUNC-14"],
                "CLAIM-INV-NST-002": ["FUNC-14"],
                "CLAIM-INV-NST-003": ["FUNC-14"],
                "DOSSIER-INV-NST-2024-0847": ["FUNC-14", "FUNC-118"],
                "DOSSIER-ALGOS-TENTH-LOOK": ["FUNC-105", "FUNC-106", "FUNC-107"],
            }
            for eid, rlist in canonical_ev_req.items():
                if eid in ev_ids:
                    for rid in rlist:
                        if rid in req_ids:
                            kconn.execute('MATCH (e:EvidenceCard {id: "' + eid + '"}), (r:Requirement {id: "' + rid + '"}) CREATE (e)-[:EVIDENCE_SUPPORTS_REQUIREMENT]->(r)')

            # Evidence -> Dossier
            for cid in ["CLAIM-INV-NST-001", "CLAIM-INV-NST-002", "CLAIM-INV-NST-003"]:
                if cid in ev_ids and "DOSSIER-INV-NST-2024-0847" in ev_ids:
                    kconn.execute('MATCH (c:EvidenceCard {id: "' + cid + '"}), (d:EvidenceCard {id: "DOSSIER-INV-NST-2024-0847"}) CREATE (c)-[:EVIDENCE_SUPPORTS_DOSSIER]->(d)')

            kuzu_built = True
        except Exception as exc:
            print("Warning during internal Kuzu population: " + str(exc))

    return {
        "status": "success",
        "scope": "project_internal",
        "kuzu_native": kuzu_built,
        "db_path": str(db_path),
        "mocs": len(mocs),
        "artifacts": len(artifacts),
        "requirements": len(requirements),
        "adrs": len(adrs),
        "evidence": len(evidence),
        "lean_declarations": len(lean_decls),
    }


def init_cache_graph(cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    db_path = cache_dir / "lsp_cache.kuzu"
    remove_path(db_path)

    kuzu_built = False
    if HAS_KUZU:
        try:
            kdb = kuzu.Database(str(db_path))
            kconn = kuzu.Connection(kdb)

            kconn.execute("CREATE NODE TABLE ElaboratedSymbol (id STRING, module_name STRING, symbol_name STRING, type_signature STRING, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE GoalCache (id STRING, goal_hash STRING, goal_state STRING, success_count INT64, PRIMARY KEY(id))")
            kconn.execute("CREATE NODE TABLE QueryCache (id STRING, query_hash STRING, result_json STRING, timestamp INT64, PRIMARY KEY(id))")

            kuzu_built = True
        except Exception as exc:
            print("Warning during cache Kuzu initialization: " + str(exc))

    return {
        "status": "success",
        "scope": "cache",
        "kuzu_native": kuzu_built,
        "db_path": str(db_path),
    }


def collect_librarian_corpus(
    books_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[tuple[str, str]]]:
    """Collect Book nodes, Section nodes, and CONTAINS edges from books_root."""
    books: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    contains: list[tuple[str, str]] = []
    seen_anchors: set[str] = set()

    for prov_path in sorted(books_root.glob("*/provenance.json")):
        book_id = prov_path.parent.name
        try:
            prov = json.loads(prov_path.read_text(encoding="utf-8"))
        except Exception:
            prov = {}

        title = to_ascii(prov.get("title", book_id))
        raw_lic = prov.get("license", "Unknown")
        lic = to_ascii(raw_lic.get("spdx", "Unknown") if isinstance(raw_lic, dict) else str(raw_lic))
        raw_real = prov.get("realization", "Markdown")
        fmt = to_ascii(raw_real.get("files", "Markdown") if isinstance(raw_real, dict) else "Markdown")

        anchors_path = prov_path.parent / "anchors.v1.json"
        row_count = 0
        if anchors_path.exists():
            try:
                table = json.loads(anchors_path.read_text(encoding="utf-8"))
            except Exception:
                table = {}
            rows = table.get("rows", [])
            row_count = len(rows)
            for row in rows:
                anchor = to_ascii(row.get("anchor", "")).strip()
                if not anchor or anchor in seen_anchors:
                    continue
                seen_anchors.add(anchor)

                page = int(row.get("print_page", 0))
                heading = to_ascii(row.get("heading_text", ""))
                leittext = to_ascii(row.get("leittext", ""))[:400].replace("\r", " ").replace("\n", " ")

                sections.append(
                    {
                        "anchor": anchor,
                        "id": anchor,
                        "book": book_id,
                        "book_id": book_id,
                        "heading": heading or leittext[:120],
                        "page": page,
                        "leittext": leittext,
                    }
                )
                contains.append((book_id, anchor))

        books.append(
            {
                "id": book_id,
                "title": title,
                "license": lic,
                "format": fmt,
                "total_rows": row_count,
            }
        )

    return books, sections, contains


def export_kuzu_database(
    books_root: Path,
    output_path: Path,
    export_format: str = "csv",
) -> dict[str, Any]:
    """Build Kuzu database from librarian corpus and export as a .kz archive."""
    books, sections, contains = collect_librarian_corpus(books_root)

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_KUZU:
        with tempfile.TemporaryDirectory() as td:
            tmp_dir = Path(td)
            db_path = tmp_dir / "kuzu_db"
            exp_dir = tmp_dir / "export"

            db = kuzu.Database(str(db_path))
            conn = kuzu.Connection(db)

            conn.execute(
                "CREATE NODE TABLE Book(id STRING, title STRING, license STRING, format STRING, PRIMARY KEY (id))"
            )
            conn.execute(
                "CREATE NODE TABLE Section(anchor STRING, book STRING, page INT64, leittext STRING, PRIMARY KEY (anchor))"
            )
            conn.execute("CREATE REL TABLE CONTAINS(FROM Book TO Section)")

            books_csv = tmp_dir / "books.csv"
            with open(books_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "title", "license", "format"])
                for b in books:
                    writer.writerow([b["id"], b["title"], b["license"], b["format"]])

            sections_csv = tmp_dir / "sections.csv"
            with open(sections_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["anchor", "book", "page", "leittext"])
                for s in sections:
                    writer.writerow([s["anchor"], s["book"], s["page"], s["leittext"]])

            contains_csv = tmp_dir / "contains.csv"
            with open(contains_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["from", "to"])
                for c in contains:
                    writer.writerow([c[0], c[1]])

            conn.execute(f'COPY Book FROM "{books_csv}" (HEADER=true)')
            conn.execute(f'COPY Section FROM "{sections_csv}" (HEADER=true)')
            conn.execute(f'COPY CONTAINS FROM "{contains_csv}" (HEADER=true)')

            conn.execute(f'EXPORT DATABASE "{exp_dir}" (format="{export_format}")')

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for p in sorted(exp_dir.rglob("*")):
                    if p.is_file():
                        zf.write(p, p.relative_to(exp_dir))
    else:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            b_buf = io.StringIO()
            b_writer = csv.writer(b_buf)
            b_writer.writerow(["id", "title", "total_rows", "license", "format"])
            for b in books:
                b_writer.writerow([b["id"], b["title"], b.get("total_rows", 0), b["license"], b["format"]])
            zf.writestr("Book.csv", b_buf.getvalue().encode("ascii"))

            s_buf = io.StringIO()
            s_writer = csv.writer(s_buf)
            s_writer.writerow(["id", "book_id", "heading", "leittext", "page"])
            for s in sections:
                s_writer.writerow([s["anchor"], s["book"], s.get("heading", ""), s["leittext"], s["page"]])
            zf.writestr("Section.csv", s_buf.getvalue().encode("ascii"))

            c_buf = io.StringIO()
            c_writer = csv.writer(c_buf)
            c_writer.writerow(["from", "to"])
            for c in contains:
                c_writer.writerow([c[0], c[1]])
            zf.writestr("CONTAINS_Book_Section.csv", c_buf.getvalue().encode("ascii"))

            schema_cypher = (
                "CREATE NODE TABLE Book(id STRING, title STRING, total_rows INT64, license STRING, format STRING, PRIMARY KEY (id));\n"
                "CREATE NODE TABLE Section(id STRING, book_id STRING, heading STRING, leittext STRING, page INT64, PRIMARY KEY (id));\n"
                "CREATE REL TABLE CONTAINS(FROM Book TO Section);\n"
            )
            zf.writestr("schema.cypher", schema_cypher.encode("ascii"))
            zf.writestr("copy.cypher", b'COPY Book FROM "Book.csv" (HEADER=true);\nCOPY Section FROM "Section.csv" (HEADER=true);\nCOPY CONTAINS FROM "CONTAINS_Book_Section.csv" (HEADER=true);\n')
            zf.writestr("index.cypher", b"")

    return {
        "status": "PASS",
        "books_count": len(books),
        "sections_count": len(sections),
        "relations_count": len(contains),
        "output_file": str(output_path),
        "size_bytes": output_path.stat().st_size,
    }



def self_test() -> None:
    """Validate end-to-end functionality on a synthetic test corpus."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "books"
        book_dir = root / "TESTBOOK"
        book_dir.mkdir(parents=True, exist_ok=True)

        (book_dir / "provenance.json").write_text(
            json.dumps(
                {
                    "title": "Test Book",
                    "license": {"spdx": "Apache-2.0"},
                    "realization": {"files": "test.md"},
                }
            ),
            encoding="utf-8",
        )
        (book_dir / "anchors.v1.json").write_text(
            json.dumps(
                {
                    "rows": [
                        {
                            "anchor": "TESTBOOK s1 p1",
                            "print_page": 1,
                            "leittext": "Sample section text",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        out_kz = Path(td) / "test.kz"
        result = export_kuzu_database(root, out_kz)
        assert result["status"] == "PASS"
        assert result["books_count"] == 1
        assert result["sections_count"] == 1
        assert out_kz.exists()
        assert out_kz.stat().st_size > 0

        with zipfile.ZipFile(out_kz) as zf:
            names = set(zf.namelist())
            assert "schema.cypher" in names
            assert "Book.csv" in names
            assert "Section.csv" in names


def main() -> None:
    parser = argparse.ArgumentParser(description="Kuzu Property Graph Compiler & Exporter (TASK-LIB-07)")
    parser.add_argument("--profile", choices=["prover", "internal", "cache", "all"], default="all", help="Graph profile to build")
    parser.add_argument("--garden-root", default=os.environ.get("KUZU_GARDEN_ROOT", "."), help="Path to knowledge/garden root directory")
    parser.add_argument("--out-dir", default=os.environ.get("KUZU_OUT_DIR", "kuzu"), help="Output directory for databases")
    parser.add_argument("--cache-dir", default=".cache/kuzu", help="Output directory for transient cache database")
    parser.add_argument("--export-public", help="Optional copy destination for public prover database (e.g. proof-skills/kuzu)")
    args = parser.parse_args()

    garden_root = Path(args.garden_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    cache_dir = Path(args.cache_dir).resolve()

    print("Building Kuzu graph databases (profile: " + args.profile + ")...")

    if args.profile in ("prover", "all"):
        res = build_prover_graph(garden_root, out_dir)
        print("Prover Graph: " + str(res["books"]) + " books, " + str(res["anchors"]) + " anchors, " + str(res["concepts"]) + " concepts, " + str(res["zettels"]) + " zettels (native: " + str(res["kuzu_native"]) + ")")
        if args.export_public:
            dest = Path(args.export_public).resolve()
            dest.mkdir(parents=True, exist_ok=True)
            zip_src = out_dir / "prover_knowledge.kz"
            if zip_src.exists():
                shutil.copy2(zip_src, dest / "prover_knowledge.kz")
                print("  -> Exported public archive to " + str(dest / "prover_knowledge.kz"))

    if args.profile in ("internal", "all"):
        res = build_internal_graph(garden_root, out_dir)
        print("Internal Graph: " + str(res["requirements"]) + " requirements, " + str(res["adrs"]) + " ADRs, " + str(res["evidence"]) + " evidence cards, " + str(res["lean_declarations"]) + " Lean decls (native: " + str(res["kuzu_native"]) + ")")

    if args.profile in ("cache", "all"):
        res = init_cache_graph(cache_dir)
        print("LSP Cache Graph initialized: " + str(res["db_path"]) + " (native: " + str(res["kuzu_native"]) + ")")

    print("ALL REQUESTED KUZU PROFILES COMPILED SUCCESSFULLY.")


if __name__ == "__main__":
    main()

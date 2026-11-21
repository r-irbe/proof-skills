#!/usr/bin/env python3
# graph/export_kuzu.py
# Kuzu Embedded Property Graph Compiler and Exporter (TASK-LIB-07).
# Scoped Unicode policy (INV-001; typographic-free by default).

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


VENDORED_ONTOLOGY = Path(__file__).resolve().parent.parent / "vendor" / "itp-ontology"


def read_concordances(
    index_roots: list[Path], *, strict: bool = False
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    concepts: list[dict[str, Any]] = []
    concordances: list[dict[str, Any]] = []

    master_idx_path = next((p / "master-authority-index.json" for p in index_roots
                            if (p / "master-authority-index.json").is_file()), None)
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
            if strict:
                raise
            print("Warning: failed reading master-authority-index.json: " + str(exc))

    conc_json_path = next((p / "cross-itp-concordance.v1.json" for p in index_roots
                           if (p / "cross-itp-concordance.v1.json").is_file()), None)
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
            if strict:
                raise
    return concepts, concordances


def public_archive_bytes() -> bytes:
    # Release inputs are limited to the checked-in generic ontology. Never
    # read the configured garden or scan the workstation's book/zettel roots.
    for name in ("master-authority-index.json", "cross-itp-concordance.v1.json"):
        if not (VENDORED_ONTOLOGY / name).is_file():
            raise FileNotFoundError(VENDORED_ONTOLOGY / name)
    concepts, concordances = read_concordances([VENDORED_ONTOLOGY], strict=True)
    if not concepts or not concordances:
        raise ValueError("Release ontology has no concepts or concordances")
    tables = [
        ("Book.csv", ("id", "title", "total_rows", "license", "format"), []),
        ("Section.csv", ("id", "book_id", "heading", "leittext", "page"), []),
        ("Concept.csv", ("id", "name", "msc2020", "domain_theory"), concepts),
        ("Concordance.csv", ("concept_id", "prover", "tactic", "syntax"), concordances),
    ]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, fields, rows in tables:
            content = io.StringIO()
            writer = csv.DictWriter(content, fields)
            writer.writeheader()
            writer.writerows(rows)
            archive.writestr(zipfile.ZipInfo(name), content.getvalue().encode("ascii"),
                             compress_type=zipfile.ZIP_DEFLATED)
    return buffer.getvalue()


def write_public_archive(path: Path) -> None:
    content = public_archive_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def check_public_archive(path: Path) -> None:
    with zipfile.ZipFile(io.BytesIO(public_archive_bytes())) as expected, zipfile.ZipFile(path) as actual:
        if actual.namelist() != expected.namelist() or any(
            actual.read(name) != expected.read(name) for name in expected.namelist()
        ):
            raise ValueError("Release Kuzu archive differs from the allowlisted ontology projection")


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

    concepts, concordances = read_concordances(
        [garden_root / "source-materials" / "indexes", VENDORED_ONTOLOGY]
    )

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

    # Ingest Zettels (garden zettels + repository zettelkasten/permanent/*.md)
    zettels_dirs = [
        garden_root / "zettels",
        Path(__file__).resolve().parent.parent / "zettelkasten" / "permanent",
    ]
    zettels: list[dict[str, Any]] = []
    seen_zids: set[str] = set()
    repo_root = Path(__file__).resolve().parent.parent
    for zettels_dir in zettels_dirs:
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
                zmat = fm.get("maturity", "evergreen" if "zettelkasten" in str(zf) else "seedling")
                zver = fm.get("verification", "lint-verified" if "zettelkasten" in str(zf) else "anchor-resolved")
                zbook = fm.get("source_book", "")
                zanchor = fm.get("source_anchor", "")
                zconcept = fm.get("master_concept", "")
                rel_list = fm.get("related", fm.get("refs", []))
                if isinstance(rel_list, str):
                    rel_list = [rel_list]
                try:
                    rel_fp = str(zf.relative_to(repo_root))
                except ValueError:
                    try:
                        rel_fp = str(zf.relative_to(garden_root.parent.parent))
                    except ValueError:
                        rel_fp = zf.name
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
                    "file_path": to_ascii(rel_fp),
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


def build_project_graph(project_root: Path, out_dir: Path) -> dict[str, Any]:
    """Generic project-level Lean declaration graph builder."""
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / "project_declarations.kuzu"
    remove_path(db_path)

    lean_decls: list[dict[str, Any]] = []
    decl_re = re.compile(r"^(theorem|lemma|def|structure|class)\s+([A-Za-z0-9_.']+)", re.MULTILINE)
    for lf in sorted(project_root.rglob("*.lean")):
        if ".lake" in lf.parts or "node_modules" in lf.parts:
            continue
        lines = lf.read_text(encoding="utf-8", errors="ignore").splitlines()
        rel_path = str(lf.relative_to(project_root))
        mod_name = rel_path.replace("/", ".").removesuffix(".lean")
        for idx, line in enumerate(lines, start=1):
            m = decl_re.match(line)
            if m:
                kind, name = m.group(1), m.group(2)
                lean_decls.append({
                    "id": to_ascii(f"{mod_name}.{name}"),
                    "name": to_ascii(name),
                    "kind": to_ascii(kind),
                    "module": to_ascii(mod_name),
                    "file_path": to_ascii(rel_path),
                    "line": idx,
                })

    kuzu_built = False
    if HAS_KUZU:
        try:
            kdb = kuzu.Database(str(db_path))
            kconn = kuzu.Connection(kdb)
            kconn.execute("CREATE NODE TABLE LeanDeclaration (id STRING, name STRING, kind STRING, module STRING, file_path STRING, line INT64, PRIMARY KEY(id))")
            for ld in lean_decls:
                did = sanitize_val(ld["id"])
                dname = sanitize_val(ld["name"])
                dkind = sanitize_val(ld["kind"])
                dmod = sanitize_val(ld["module"])
                dpath = sanitize_val(ld["file_path"])
                kconn.execute("CREATE (l:LeanDeclaration {id: \"" + did + "\", name: \"" + dname + "\", kind: \"" + dkind + "\", module: \"" + dmod + "\", file_path: \"" + dpath + "\", line: " + str(ld["line"]) + "})")
            kuzu_built = True
        except Exception as exc:
            print("Warning during project Kuzu population: " + str(exc))

    return {
        "status": "success",
        "scope": "project_declarations",
        "kuzu_native": kuzu_built,
        "db_path": str(db_path),
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
    parser.add_argument("--profile", choices=["release", "prover", "project", "cache", "all"], default="release", help="Graph profile to build")
    parser.add_argument("--garden-root", default=os.environ.get("KUZU_GARDEN_ROOT", "."), help="Path to knowledge/garden root directory")
    parser.add_argument("--out-dir", default=os.environ.get("KUZU_OUT_DIR", "kuzu"), help="Output directory for databases")
    parser.add_argument("--cache-dir", default=".cache/kuzu", help="Output directory for transient cache database")
    parser.add_argument("--export-public", help="Optional output directory for the allowlisted release archive")
    parser.add_argument("--check-public", type=Path, help="Verify a shipped release archive and exit")
    args = parser.parse_args()

    if args.check_public:
        check_public_archive(args.check_public)
        print("Release Kuzu archive matches the allowlisted ontology projection.")
        return

    garden_root = Path(args.garden_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    cache_dir = Path(args.cache_dir).resolve()

    public_dir = Path(args.export_public).resolve() if args.export_public else None
    if args.profile == "release":
        write_public_archive((public_dir or out_dir) / "prover_knowledge.kz")
        return
    if public_dir == out_dir and args.profile in ("prover", "all"):
        parser.error("Choose separate directories for the local graph and the release archive")

    print("Building Kuzu graph databases (profile: " + args.profile + ")...")

    if args.profile in ("prover", "all"):
        res = build_prover_graph(garden_root, out_dir)
        print("Prover Graph: " + str(res["books"]) + " books, " + str(res["anchors"]) + " anchors, " + str(res["concepts"]) + " concepts, " + str(res["zettels"]) + " zettels (native: " + str(res["kuzu_native"]) + ")")
    if public_dir:
        write_public_archive(public_dir / "prover_knowledge.kz")

    if args.profile in ("project", "all"):
        res = build_project_graph(garden_root, out_dir)
        print("Project Graph: " + str(res["lean_declarations"]) + " Lean decls (native: " + str(res["kuzu_native"]) + ")")

    if args.profile in ("cache", "all"):
        res = init_cache_graph(cache_dir)
        print("LSP Cache Graph initialized: " + str(res["db_path"]) + " (native: " + str(res["kuzu_native"]) + ")")

    print("ALL REQUESTED KUZU PROFILES COMPILED SUCCESSFULLY.")


if __name__ == "__main__":
    main()

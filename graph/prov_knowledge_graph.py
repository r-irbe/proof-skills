#!/usr/bin/env python3
"""
tools/garden/prov_knowledge_graph.py
SQLite-Backed W3C PROV-DM Knowledge Graph Engine with Recursive CTE Traversals.
Adapted from ai-visioon knowledge_graph.py and REF-KNOWLEDGE-GRAPH-INTELLIGENCE.

Implements Track I (Task I-1, Task I-2) per PLAN-AI-VISIOON-INTEGRATION:
- Task I-1: 7 canonical entity types and 9 directed relationship types schema:
    * Entities: DOCUMENT, ANALYSIS, FINDING, REQUIREMENT, CONCEPT, AUTHOR, TOPIC
    * Relations: ANALYZES, CONTAINS, REFERENCES, DERIVES_FROM, SUPPORTS,
                 CONTRADICTS, RELATED_TO, AUTHORED_BY, CATEGORIZED_AS
- Task I-2: Recursive Common Table Expressions (CTEs) for in-process graph analysis:
    * Transitive closure derivation / evidence spine
    * Cycle detection
    * Common neighbor discovery
    * Bounded-hop pathfinding (< 2ms latency)

Strict 7-bit ASCII only (INV-001). Zero network egress (INV-011).
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("garden.prov_knowledge_graph")


class EntityType(str, Enum):
    """The seven canonical entity types per REF-KNOWLEDGE-GRAPH-INTELLIGENCE."""

    DOCUMENT = "DOCUMENT"
    ANALYSIS = "ANALYSIS"
    FINDING = "FINDING"
    REQUIREMENT = "REQUIREMENT"
    CONCEPT = "CONCEPT"
    AUTHOR = "AUTHOR"
    TOPIC = "TOPIC"


class RelationshipType(str, Enum):
    """The nine directed relationship types per REF-KNOWLEDGE-GRAPH-INTELLIGENCE."""

    ANALYZES = "ANALYZES"
    CONTAINS = "CONTAINS"
    REFERENCES = "REFERENCES"
    DERIVES_FROM = "DERIVES_FROM"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    RELATED_TO = "RELATED_TO"
    AUTHORED_BY = "AUTHORED_BY"
    CATEGORIZED_AS = "CATEGORIZED_AS"


@dataclass
class Entity:
    """Node in the PROV-DM knowledge graph."""

    entity_id: str
    entity_type: EntityType
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "label": self.label,
            "attributes": self.attributes,
            "created_at": self.created_at,
        }


@dataclass
class Relationship:
    """Directed edge in the PROV-DM knowledge graph."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0
    relationship_id: str = field(
        default_factory=lambda: f"rel_{uuid.uuid4().hex[:12]}"
    )
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "weight": self.weight,
            "attributes": self.attributes,
            "created_at": self.created_at,
        }


class ProvKnowledgeGraph:
    """
    SQLite-backed in-process W3C PROV-DM Knowledge Graph Engine.
    Leverages recursive CTEs for fast sub-millisecond graph traversals.
    """

    SCHEMA_SQL = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        label TEXT NOT NULL,
        attributes_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS relationships (
        relationship_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        weight REAL NOT NULL DEFAULT 1.0,
        attributes_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        FOREIGN KEY (source_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
        FOREIGN KEY (target_id) REFERENCES entities(entity_id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
    CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id);
    CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id);
    CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relationship_type);
    CREATE INDEX IF NOT EXISTS idx_rel_source_type ON relationships(source_id, relationship_type);
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.executescript(self.SCHEMA_SQL)

    def close(self) -> None:
        self.conn.close()

    # -- Entity Operations --

    def add_entity(self, entity: Entity) -> None:
        """Insert or replace an entity in the graph."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO entities (entity_id, entity_type, label, attributes_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    entity.entity_id,
                    entity.entity_type.value,
                    entity.label,
                    json.dumps(entity.attributes, sort_keys=True),
                    entity.created_at,
                ),
            )

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Fetch an entity by ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT entity_id, entity_type, label, attributes_json, created_at FROM entities WHERE entity_id = ?",
            (entity_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Entity(
            entity_id=row["entity_id"],
            entity_type=EntityType(row["entity_type"]),
            label=row["label"],
            attributes=json.loads(row["attributes_json"]),
            created_at=row["created_at"],
        )

    def count_entities(self, entity_type: Optional[EntityType] = None) -> int:
        cursor = self.conn.cursor()
        if entity_type:
            cursor.execute(
                "SELECT COUNT(*) FROM entities WHERE entity_type = ?",
                (entity_type.value,),
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM entities")
        return cursor.fetchone()[0]

    # -- Relationship Operations --

    def add_relationship(self, rel: Relationship) -> None:
        """Insert a relationship edge between two existing entities."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO relationships (
                    relationship_id, source_id, target_id, relationship_type, weight, attributes_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rel.relationship_id,
                    rel.source_id,
                    rel.target_id,
                    rel.relationship_type.value,
                    rel.weight,
                    json.dumps(rel.attributes, sort_keys=True),
                    rel.created_at,
                ),
            )

    def count_relationships(self, rel_type: Optional[RelationshipType] = None) -> int:
        cursor = self.conn.cursor()
        if rel_type:
            cursor.execute(
                "SELECT COUNT(*) FROM relationships WHERE relationship_type = ?",
                (rel_type.value,),
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM relationships")
        return cursor.fetchone()[0]

    # -- Recursive CTE Graph Traversals (Task I-2) --

    def get_evidence_spine(
        self, claim_id: str, max_depth: int = 10
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Traverses upstream evidence supporting or deriving claim_id via recursive CTE.
        Only traverses DERIVES_FROM and SUPPORTS edges.
        Returns: (spine_rows, latency_ms)
        """
        t0 = time.perf_counter()
        query = """
        WITH RECURSIVE evidence_spine(entity_id, parent_id, rel_type, depth, path) AS (
            SELECT source_id, target_id, relationship_type, 1, source_id || '->' || target_id
            FROM relationships
            WHERE source_id = ? AND relationship_type IN ('DERIVES_FROM', 'SUPPORTS')
            UNION ALL
            SELECT r.source_id, r.target_id, r.relationship_type, s.depth + 1, s.path || '->' || r.target_id
            FROM relationships r
            JOIN evidence_spine s ON r.source_id = s.parent_id
            WHERE s.depth < ? AND instr('->' || s.path || '->', '->' || r.target_id || '->') = 0
              AND r.relationship_type IN ('DERIVES_FROM', 'SUPPORTS')
        )
        SELECT entity_id, parent_id, rel_type, depth, path FROM evidence_spine ORDER BY depth ASC;
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (claim_id, max_depth))
        rows = [dict(r) for r in cursor.fetchall()]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return rows, elapsed_ms

    def get_transitive_closure(
        self,
        start_id: str,
        relationship_types: Optional[List[RelationshipType]] = None,
        max_depth: int = 10,
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Computes forward transitive closure reachable from start_id.
        Returns: (closure_rows, latency_ms)
        """
        t0 = time.perf_counter()
        if relationship_types:
            type_placeholders = ",".join("?" for _ in relationship_types)
            type_filter = f"AND relationship_type IN ({type_placeholders})"
            params: List[Any] = [start_id] + [t.value for t in relationship_types] + [max_depth] + [t.value for t in relationship_types]
            query = f"""
            WITH RECURSIVE closure(entity_id, target_id, rel_type, depth, path) AS (
                SELECT source_id, target_id, relationship_type, 1, source_id || '->' || target_id
                FROM relationships
                WHERE source_id = ? {type_filter}
                UNION ALL
                SELECT r.source_id, r.target_id, r.relationship_type, c.depth + 1, c.path || '->' || r.target_id
                FROM relationships r
                JOIN closure c ON r.source_id = c.target_id
                WHERE c.depth < ? AND instr('->' || c.path || '->', '->' || r.target_id || '->') = 0
                  AND r.relationship_type IN ({type_placeholders})
            )
            SELECT entity_id, target_id, rel_type, depth, path FROM closure ORDER BY depth ASC;
            """
        else:
            params = [start_id, max_depth]
            query = """
            WITH RECURSIVE closure(entity_id, target_id, rel_type, depth, path) AS (
                SELECT source_id, target_id, relationship_type, 1, source_id || '->' || target_id
                FROM relationships
                WHERE source_id = ?
                UNION ALL
                SELECT r.source_id, r.target_id, r.relationship_type, c.depth + 1, c.path || '->' || r.target_id
                FROM relationships r
                JOIN closure c ON r.source_id = c.target_id
                WHERE c.depth < ? AND instr('->' || c.path || '->', '->' || r.target_id || '->') = 0
            )
            SELECT entity_id, target_id, rel_type, depth, path FROM closure ORDER BY depth ASC;
            """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return rows, elapsed_ms

    def detect_cycles(self, max_depth: int = 15) -> Tuple[List[str], float]:
        """
        Detects directed cycles in the graph using CTE path tracking.
        Returns: (cycle_paths, latency_ms)
        """
        t0 = time.perf_counter()
        query = """
        WITH RECURSIVE cycle_finder(source_id, current_id, depth, path, is_cycle) AS (
            SELECT source_id, target_id, 1, source_id || '->' || target_id, 0
            FROM relationships
            UNION ALL
            SELECT c.source_id, r.target_id, c.depth + 1, c.path || '->' || r.target_id,
                   CASE WHEN r.target_id = c.source_id THEN 1 ELSE 0 END
            FROM relationships r
            JOIN cycle_finder c ON r.source_id = c.current_id
            WHERE c.depth < ? AND c.is_cycle = 0 AND (instr('->' || c.path || '->', '->' || r.target_id || '->') = 0 OR r.target_id = c.source_id)
        )
        SELECT path FROM cycle_finder WHERE is_cycle = 1;
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (max_depth,))
        rows = [r["path"] for r in cursor.fetchall()]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return rows, elapsed_ms

    def find_common_neighbors(
        self, entity_a: str, entity_b: str
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Finds all entities connected to both entity_a and entity_b.
        Returns: (common_nodes, latency_ms)
        """
        t0 = time.perf_counter()
        query = """
        SELECT e.entity_id, e.entity_type, e.label
        FROM entities e
        WHERE e.entity_id IN (
            SELECT target_id FROM relationships WHERE source_id = ?
            UNION
            SELECT source_id FROM relationships WHERE target_id = ?
        )
        INTERSECT
        SELECT e.entity_id, e.entity_type, e.label
        FROM entities e
        WHERE e.entity_id IN (
            SELECT target_id FROM relationships WHERE source_id = ?
            UNION
            SELECT source_id FROM relationships WHERE target_id = ?
        );
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (entity_a, entity_a, entity_b, entity_b))
        rows = [dict(r) for r in cursor.fetchall()]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return rows, elapsed_ms

    def find_bounded_path(
        self, source_id: str, target_id: str, max_depth: int = 6
    ) -> Tuple[Optional[List[str]], float]:
        """
        Finds the shortest directed path between source_id and target_id.
        Returns: (path_node_ids, latency_ms)
        """
        t0 = time.perf_counter()
        query = """
        WITH RECURSIVE path_finder(current_id, depth, path) AS (
            SELECT target_id, 1, source_id || '->' || target_id
            FROM relationships
            WHERE source_id = ?
            UNION ALL
            SELECT r.target_id, p.depth + 1, p.path || '->' || r.target_id
            FROM relationships r
            JOIN path_finder p ON r.source_id = p.current_id
            WHERE p.depth < ? AND instr('->' || p.path || '->', '->' || r.target_id || '->') = 0
        )
        SELECT path, depth FROM path_finder WHERE current_id = ? ORDER BY depth ASC LIMIT 1;
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (source_id, max_depth, target_id))
        row = cursor.fetchone()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if not row:
            return None, elapsed_ms
        path_nodes = row["path"].split("->")
        return path_nodes, elapsed_ms


def run_self_test() -> None:
    """Executes automated self-test and latency benchmark."""
    print("=== Running W3C PROV-DM Knowledge Graph Engine Self-Test ===")
    kg = ProvKnowledgeGraph(":memory:")

    # 1. Populate 7 canonical entity types
    doc1 = Entity("doc_001", EntityType.DOCUMENT, "Financial Transfer Register 2026", {"sha256": "abc12345"})
    doc2 = Entity("doc_002", EntityType.DOCUMENT, "Secondary Audit Exhibit 2026")
    analysis1 = Entity("ana_001", EntityType.ANALYSIS, "VLM Forensic Extraction Pass")
    finding1 = Entity("fnd_001", EntityType.FINDING, "Shell Company Transfer of 5M EUR", {"confidence": 0.96})
    req1 = Entity("req_001", EntityType.REQUIREMENT, "AML Directive Art 12 Verification")
    concept1 = Entity("cpt_001", EntityType.CONCEPT, "Conduit Velocity Metric")
    author1 = Entity("aut_001", EntityType.AUTHOR, "Lead Forensic Investigator")
    topic1 = Entity("top_001", EntityType.TOPIC, "Offshore Illicit Money Flows")

    for e in [doc1, doc2, analysis1, finding1, req1, concept1, author1, topic1]:
        kg.add_entity(e)

    assert kg.count_entities() == 8
    for et in EntityType:
        assert kg.count_entities(et) >= 1, f"Missing entity of type {et}"

    # 2. Add 9 relationship types
    # ANALYZES: analysis1 -> doc1
    kg.add_relationship(Relationship("ana_001", "doc_001", RelationshipType.ANALYZES))
    # CONTAINS: doc2 -> finding1 (avoids cycle with analysis1 and doc1)
    kg.add_relationship(Relationship("doc_002", "fnd_001", RelationshipType.CONTAINS))
    # REFERENCES: finding1 -> doc1
    kg.add_relationship(Relationship("fnd_001", "doc_001", RelationshipType.REFERENCES))
    # DERIVES_FROM: finding1 -> analysis1
    kg.add_relationship(Relationship("fnd_001", "ana_001", RelationshipType.DERIVES_FROM))
    # SUPPORTS: finding1 -> req1
    kg.add_relationship(Relationship("fnd_001", "req_001", RelationshipType.SUPPORTS))
    # CONTRADICTS: finding1 -> concept1
    kg.add_relationship(Relationship("fnd_001", "cpt_001", RelationshipType.CONTRADICTS))
    # RELATED_TO: concept1 -> topic1
    kg.add_relationship(Relationship("cpt_001", "top_001", RelationshipType.RELATED_TO))
    # AUTHORED_BY: analysis1 -> author1
    kg.add_relationship(Relationship("ana_001", "aut_001", RelationshipType.AUTHORED_BY))
    # CATEGORIZED_AS: finding1 -> topic1
    kg.add_relationship(Relationship("fnd_001", "top_001", RelationshipType.CATEGORIZED_AS))

    assert kg.count_relationships() == 9
    for rt in RelationshipType:
        assert kg.count_relationships(rt) == 1, f"Missing relation of type {rt}"

    # 3. Evidence Spine Recursive CTE Traversal
    spine, spine_lat = kg.get_evidence_spine("fnd_001")
    assert len(spine) >= 2, "Expected evidence spine to traverse DERIVES_FROM and SUPPORTS"
    print(f"Evidence spine traversal: {len(spine)} hops in {spine_lat:.3f} ms")
    assert spine_lat < 20.0, f"Spine latency {spine_lat}ms exceeds threshold"

    # 4. Transitive Closure
    closure, clos_lat = kg.get_transitive_closure("fnd_001")
    assert len(closure) >= 3, "Expected multi-hop transitive closure"
    print(f"Transitive closure: {len(closure)} edges in {clos_lat:.3f} ms")

    # 5. Cycle Detection (currently acyclic)
    cycles, cyc_lat = kg.detect_cycles()
    assert len(cycles) == 0, "Graph should have no cycles initially"

    # Inject intentional cycle to verify detection: top_001 -> cpt_001 -> top_001
    kg.add_relationship(Relationship("top_001", "cpt_001", RelationshipType.RELATED_TO))
    cycles, _ = kg.detect_cycles()
    assert len(cycles) >= 1, "Cycle should be detected"
    print(f"Cycle successfully detected: {cycles[0]}")

    # 6. Common Neighbors
    # Both fnd_001 and cpt_001 are connected to top_001
    common, cn_lat = kg.find_common_neighbors("fnd_001", "cpt_001")
    assert any(n["entity_id"] == "top_001" for n in common)
    print(f"Common neighbor discovery: found {len(common)} in {cn_lat:.3f} ms")

    # 7. Bounded-Hop Pathfinding (< 2ms benchmark)
    path, path_lat = kg.find_bounded_path("ana_001", "req_001")
    # ana_001 is parent of fnd_001 via DERIVES_FROM (fnd_001 -> ana_001), let's test forward path:
    # fnd_001 -> req_001 exists
    path, path_lat = kg.find_bounded_path("fnd_001", "req_001")
    assert path == ["fnd_001", "req_001"]
    print(f"Bounded pathfinding: {path} in {path_lat:.3f} ms (sub-2ms target)")
    assert path_lat < 5.0

    # 8. Prefix-collision regression test (doc_10 -> doc_1 must not collide on substring 'doc_1')
    kg.add_entity(Entity("doc_10", EntityType.DOCUMENT, "Prefix Doc 10"))
    kg.add_entity(Entity("doc_1", EntityType.DOCUMENT, "Prefix Doc 1"))
    kg.add_relationship(Relationship("doc_10", "doc_1", RelationshipType.DERIVES_FROM))
    spine_pref, _ = kg.get_evidence_spine("doc_10")
    assert len(spine_pref) == 1 and spine_pref[0]["parent_id"] == "doc_1", (
        f"Prefix collision truncated evidence spine: {spine_pref}"
    )
    closure_pref, _ = kg.get_transitive_closure("doc_10")
    assert len(closure_pref) == 1 and closure_pref[0]["target_id"] == "doc_1", (
        f"Prefix collision truncated transitive closure: {closure_pref}"
    )
    path_pref, _ = kg.find_bounded_path("doc_10", "doc_1")
    assert path_pref == ["doc_10", "doc_1"], f"Prefix collision broke pathfinding: {path_pref}"

    kg.close()
    print("PASS: W3C PROV-DM Knowledge Graph Engine self-tests completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="W3C PROV-DM SQLite Knowledge Graph Engine")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-test and latency benchmark")
    parser.add_argument("--db", type=str, default=":memory:", help="SQLite database path (default: in-memory)")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()

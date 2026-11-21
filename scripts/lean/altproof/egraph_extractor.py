"""Exact sharing-aware E-Graph DAG extractor with Fraction signed-cost BnB.

Ported from kernel m6-sota-research superoptimizer + signed-bnb-fix-2026-11-20.
Handles delayed negative-cost credits, exact binary float accumulation via
``fractions.Fraction``, cycle rejection on assignment completion, and honest
status reporting (``OPTIMAL | FEASIBLE | UNKNOWN | INFEASIBLE``).

Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import heapq
import itertools
import math
import time
from typing import Any, Callable, Dict, List, Optional, Set

KERNEL_STEP_BASE_COST = 10500
KERNEL_INST_PER_NODE_COST = 4
CONSTANT_LEFT_REWARD = 16
GMP_HEAP_ALLOC_PENALTY = 100
GMP_PER_LIMB_COST = 10


@dataclass
class ENode:
    """An e-node representing an operator applied to child e-classes."""

    id: int
    op: str
    owner: int
    children: List[int] = field(default_factory=list)
    open_nodes: int = 0
    is_constant_left: bool = False
    static_bitwidth: Optional[int] = None
    literal_value: Optional[int] = None

    @property
    def is_literal(self) -> bool:
        return self.literal_value is not None or self.op.isdigit()


@dataclass
class EClass:
    """An equivalence class of e-nodes with optional known bitwidth."""

    id: int
    nodes: List[int] = field(default_factory=list)
    known_bitwidth: Optional[int] = None


@dataclass
class EGraph:
    """E-Graph container for sharing-aware DAG extraction."""

    classes: Dict[int, EClass] = field(default_factory=dict)
    nodes: Dict[int, ENode] = field(default_factory=dict)
    root: int = 0

    def add_class(self, cid: int, known_bitwidth: Optional[int] = None) -> EClass:
        cls = EClass(id=cid, known_bitwidth=known_bitwidth)
        self.classes[cid] = cls
        return cls

    def add_node(
        self,
        nid: int,
        op: str,
        owner: int,
        children: List[int],
        open_nodes: int = 0,
        is_constant_left: bool = False,
        static_bitwidth: Optional[int] = None,
        literal_value: Optional[int] = None,
    ) -> ENode:
        node = ENode(
            id=nid,
            op=op,
            owner=owner,
            children=list(children),
            open_nodes=open_nodes,
            is_constant_left=is_constant_left,
            static_bitwidth=static_bitwidth,
            literal_value=literal_value,
        )
        self.nodes[nid] = node
        if owner not in self.classes:
            self.add_class(owner)
        self.classes[owner].nodes.append(nid)
        return node


@dataclass
class ExtractionResult:
    """Outcome of sharing-aware DAG extraction."""

    backend: str
    status: str  # OPTIMAL | FEASIBLE | UNKNOWN | INFEASIBLE
    objective_value: float
    selected_nodes: List[int]
    selected_classes: List[int]
    dag_size: int
    tree_size: int
    gmp_heap_limbs: int
    unboxed_immediate: bool
    runtime_ms: float
    extracted_ast: Dict[str, Any] = field(default_factory=dict)


def compute_tree_size(egraph: EGraph, selected_nodes: Set[int], root_class: int) -> int:
    """Compute unfolded tree size of an acyclic selected DAG from ``root_class``."""
    class_to_node = {egraph.nodes[nid].owner: egraph.nodes[nid] for nid in selected_nodes}

    def visit(cid: int) -> int:
        if cid not in class_to_node:
            return 1
        node = class_to_node[cid]
        return 1 + sum(visit(child) for child in node.children)

    return visit(root_class)


def build_extracted_ast(egraph: EGraph, selected_nodes: Set[int], cid: int) -> Dict[str, Any]:
    """Reconstruct hierarchical AST dictionary from selected DAG e-nodes."""
    class_to_node = {egraph.nodes[nid].owner: egraph.nodes[nid] for nid in selected_nodes}
    if cid not in class_to_node:
        return {"class": cid, "op": f"var_{cid}", "children": []}
    node = class_to_node[cid]
    return {
        "class": cid,
        "node_id": node.id,
        "op": node.op,
        "literal": node.literal_value,
        "children": [build_extracted_ast(egraph, selected_nodes, c) for c in node.children],
    }


def _default_node_cost(node: ENode) -> float:
    cost = KERNEL_STEP_BASE_COST + KERNEL_INST_PER_NODE_COST * node.open_nodes
    if node.is_constant_left:
        cost -= CONSTANT_LEFT_REWARD
    if (node.static_bitwidth or 0) >= 63:
        cost += GMP_HEAP_ALLOC_PENALTY
    return float(cost)


class SignedCostBnBExtractor:
    """Self-contained exact Fraction signed-cost Branch-and-Bound DAG extractor."""

    def __init__(
        self,
        egraph: EGraph,
        cost_fn: Optional[Callable[[ENode, EGraph], float]] = None,
    ) -> None:
        self.egraph = egraph
        self.cost_fn = cost_fn

    def _node_cost(self, node: ENode) -> Fraction:
        if self.cost_fn is not None:
            value = float(self.cost_fn(node, self.egraph))
            if not math.isfinite(value):
                raise ValueError("branch-and-bound requires finite node costs")
            return Fraction(value)
        return Fraction(_default_node_cost(node))

    def solve_bnb(self, time_limit_sec: float = 1.0) -> ExtractionResult:
        """Solve non-additive signed-cost DAG extraction with topological acyclicity."""
        started = time.monotonic()
        deadline = started + time_limit_sec
        classes = self.egraph.classes
        nodes = self.egraph.nodes
        root = self.egraph.root

        best_cost: float | Fraction = math.inf
        best_selection: Optional[Dict[int, Optional[int]]] = None
        timed_out = False

        costs = {nid: self._node_cost(node) for nid, node in nodes.items()}
        minimum = {
            cid: min(costs[nid] for nid in cls.nodes)
            for cid, cls in classes.items()
            if cls.nodes
        }
        credit = {cid: min(Fraction(0), cost) for cid, cost in minimum.items()}
        counter = itertools.count()
        queue: list = []
        if root in minimum:
            lower_bound = sum(credit.values()) + minimum[root] - credit[root]
            queue.append((lower_bound, next(counter), Fraction(0), {root: None}, [root]))

        while queue:
            if queue[0][0] >= best_cost:
                break
            if time.monotonic() >= deadline:
                timed_out = True
                break

            lower_bound, _, cost_so_far, assignment, pending = heapq.heappop(queue)

            if not pending:
                is_dag = True
                visited: Dict[int, int] = {}

                def dfs(u: int) -> bool:
                    visited[u] = 0
                    nid = assignment[u]
                    if nid is not None:
                        for v in nodes[nid].children:
                            if v in assignment:
                                if visited.get(v) == 0:
                                    return False
                                if v not in visited and not dfs(v):
                                    return False
                    visited[u] = 1
                    return True

                for u in assignment:
                    if u not in visited and not dfs(u):
                        is_dag = False
                        break

                if is_dag and cost_so_far < best_cost:
                    best_cost = cost_so_far
                    best_selection = dict(assignment)
                continue

            cid = pending[0]
            rest_pending = pending[1:]
            for nid in classes[cid].nodes:
                node = nodes[nid]
                new_cost = cost_so_far + costs[nid]
                bound = lower_bound + costs[nid] - minimum[cid]

                new_assignment = dict(assignment)
                new_assignment[cid] = nid
                new_pending = list(rest_pending)

                for child in node.children:
                    if child not in minimum:
                        break
                    if child not in new_assignment:
                        new_assignment[child] = None
                        new_pending.append(child)
                        bound += minimum[child] - credit[child]
                else:
                    if bound < best_cost:
                        heapq.heappush(
                            queue,
                            (bound, next(counter), new_cost, new_assignment, new_pending),
                        )

        if best_selection is None:
            return ExtractionResult(
                backend="branch_and_bound",
                status="UNKNOWN" if timed_out else "INFEASIBLE",
                objective_value=math.inf,
                selected_nodes=[],
                selected_classes=[],
                dag_size=0,
                tree_size=0,
                gmp_heap_limbs=0,
                unboxed_immediate=False,
                runtime_ms=(time.monotonic() - started) * 1000,
            )

        selected_nids = [nid for nid in best_selection.values() if nid is not None]
        selected_cids = list(best_selection.keys())
        sel_set = set(selected_nids)
        tree_sz = compute_tree_size(self.egraph, sel_set, root)
        ast_dict = build_extracted_ast(self.egraph, sel_set, root)
        heap_active = any((nodes[nid].static_bitwidth or 0) >= 63 for nid in selected_nids)

        return ExtractionResult(
            backend="branch_and_bound",
            status="FEASIBLE" if timed_out else "OPTIMAL",
            objective_value=float(best_cost),
            selected_nodes=selected_nids,
            selected_classes=selected_cids,
            dag_size=len(selected_nids),
            tree_size=tree_sz,
            gmp_heap_limbs=1 if heap_active else 0,
            unboxed_immediate=not heap_active,
            runtime_ms=(time.monotonic() - started) * 1000,
            extracted_ast=ast_dict,
        )

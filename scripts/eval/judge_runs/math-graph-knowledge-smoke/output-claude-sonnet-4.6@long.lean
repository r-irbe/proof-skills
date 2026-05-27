A directed knowledge graph can have cycles even when intended to be acyclic, so the traversal must enforce acyclicity dynamically using a visited set and a recursion stack. The visited set prevents re-processing nodes entirely. The recursion stack detects back edges, which indicate cycles in the current DFS path.

Here is a complete Python implementation:

```python
from collections import defaultdict
from typing import Any, Iterator

class KnowledgeGraph:
    def __init__(self):
        self.adjacency: dict[str, list[str]] = defaultdict(list)
        self.nodes: dict[str, Any] = {}

    def add_node(self, node_id: str, data: Any = None):
        self.nodes[node_id] = data
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []

    def add_edge(self, from_id: str, to_id: str):
        self.adjacency[from_id].append(to_id)

    def dfs(self, seed: str) -> Iterator[tuple[str, Any]]:
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def _dfs(node: str) -> Iterator[tuple[str, Any]]:
            visited.add(node)
            rec_stack.add(node)
            yield node, self.nodes.get(node)

            for neighbor in self.adjacency.get(node, []):
                if neighbor in rec_stack:
                    continue
                if neighbor not in visited:
                    yield from _dfs(neighbor)

            rec_stack.discard(node)

        if seed not in self.nodes:
            raise KeyError(f"Seed node '{seed}' not in graph")

        yield from _dfs(seed)
```

The visited set ensures each node is processed exactly once across the entire traversal. The rec_stack tracks nodes on the current active call path. When a neighbor is in rec_stack, the edge is a back edge and following it would create a cycle, so it is skipped. When a neighbor is in visited but not in rec_stack, it was already fully explored via a different path, so it is also skipped. This distinction is the critical correctness point.

Nodes are yielded in pre-order, meaning a node is emitted before its descendants, which is the natural DFS traversal order for a knowledge graph where you want to process ancestors before derived facts.

The rec_stack.discard call on return is the backtracking step. It removes the node from the current path when all its descendants have been explored, allowing the same node to appear in other DFS paths without being treated as a cycle.

For an iterative version that avoids Python's recursion limit on deep graphs:

```python
def dfs_iterative(self, seed: str) -> Iterator[tuple[str, Any]]:
    if seed not in self.nodes:
        raise KeyError(f"Seed node '{seed}' not in graph")

    visited: set[str] = set()
    path_set: set[str] = set()
    stack: list[tuple[str, Iterator[str]]] = [
        (seed, iter(self.adjacency.get(seed, [])))
    ]
    visited.add(seed)
    path_set.add(seed)
    yield seed, self.nodes.get(seed)

    while stack:
        node, children = stack[-1]
        try:
            child = next(children)
            if child in path_set:
                continue
            if child in visited:
                continue
            visited.add(child)
            path_set.add(child)
            yield child, self.nodes.get(child)
            stack.append((child, iter(self.adjacency.get(child, []))))
        except StopIteration:
            stack.pop()
            path_set.discard(node)
```

Time complexity is O(V + E) where V is the number of reachable nodes from the seed and E is the number of edges among them. Space complexity is O(V) for the visited and recursion stack sets plus O(depth) for the call stack. The iterative version bounds stack depth to the longest simple path, which in a DAG is at most O(V).

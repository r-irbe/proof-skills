Use a visited set to track seen nodes and prevent re-traversal; this handles cycles even in graphs that may not be strictly acyclic. Maintain a recursion stack (or explicit stack for iterative DFS) to detect back-edges if you need to enforce or verify DAG invariants.

```python
def dfs(graph: dict[str, list[str]], seed: str):
    visited = set()
    stack = [seed]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        yield node
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)
```

`reversed()` preserves left-to-right child order since `pop()` takes from the tail. To detect a cycle (back-edge) during traversal, maintain a `in_stack` set: add the node on entry and remove it on exit (recursive version). For a true DAG guarantee, run topological sort (Kahn's algorithm) as a pre-check; if it can't drain all nodes, a cycle exists and you abort. This gives O(V + E) time and O(V) space.
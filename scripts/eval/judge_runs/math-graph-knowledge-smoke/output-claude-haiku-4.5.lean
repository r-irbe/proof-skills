Use a recursive DFS with two tracking sets: visited (for all-time visited nodes) and recursion_stack (for current path nodes). Check the recursion_stack to detect cycles—if the current node exists in it, skip traversal. Add the node to recursion_stack before recursing, then remove it after. Here's the implementation:

```python
def dfs_traverse(graph: dict, seed: str, visited: set = None, rec_stack: set = None) -> list:
    visited = visited or set()
    rec_stack = rec_stack or set()
    if seed in rec_stack: return []  # cycle detected
    if seed in visited: return []
    visited.add(seed)
    rec_stack.add(seed)
    result = [seed]
    for neighbor in graph.get(seed, []):
        result.extend(dfs_traverse(graph, neighbor, visited, rec_stack))
    rec_stack.remove(seed)
    return result
```

The visited set prevents re-exploring nodes; recursion_stack detects cycles within the current traversal path. This ensures acyclic traversal while discovering all reachable nodes from the seed in O(V+E) time.
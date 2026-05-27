def dfs(graph, seed):
    visited, order, stack = set(), [], [seed]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph.get(node, ())):
            if neighbor not in visited:
                stack.append(neighbor)
    return order

Uses an explicit stack to avoid recursion limits on deep graphs. The `visited` set enforces acyclicity by skipping already-expanded nodes, safe even if the graph contains cycles despite the DAG assumption. `reversed(...)` preserves natural left-to-right child ordering when popping. Runs in O(V+E) time and O(V) space; assumes `graph` is an adjacency map of node → iterable of successors.
def solve_minty(edges, start_node=1):
    """Обчислює найкоротші шляхи методом Мінті.

    Повертає:
        h (dict): Позначки найкоротших відстаней до вершин.
        shortest_edges (list): Дуги, що входять до оптимальних шляхів.
        all_nodes (set): Усі вершини графа.
    """
    all_nodes = set()
    for u, v, _ in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    I = {start_node}
    h = {start_node: 0}
    shortest_edges = []

    while len(I) < len(all_nodes):
        min_val = float("inf")
        best_edge = None

        for u, v, w in edges:
            if u in I and v not in I:
                val = h[u] + w
                if val < min_val:
                    min_val = val
                    best_edge = (u, v)

        if best_edge is None:
            break

        u, v = best_edge
        h[v] = min_val
        I.add(v)
        shortest_edges.append((u, v))

    return h, shortest_edges, all_nodes
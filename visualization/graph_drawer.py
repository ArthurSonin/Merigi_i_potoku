import matplotlib.pyplot as plt
import networkx as nx

def build_figure(edges, h, shortest_edges, title="Розв'язок задачі", 
                 show_red_shortest=True, show_blue_absolute=True, target_edges=None):
    G = nx.DiGraph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    is_planar, _ = nx.check_planarity(G.to_undirected())
    pos = nx.planar_layout(G) if is_planar else nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(6, 5))
    node_size = 700

    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color="lightblue", ax=ax)

    # 1. Пошук найкоротшого шляху серед усіх (абсолютний мінімум за значенням h)
    # Шукаємо досяжну вершину v != start з мінімальним h[v]
    min_node = None
    min_h_val = float('inf')
    for node, h_val in h.items():
        if h_val > 0 and h_val < min_h_val:
            min_h_val = h_val
            min_node = node

    # Знаходимо ребро(а), яке веде до цієї найближчої вершини в дереві найкоротших шляхів
    abs_min_edges = set()
    if min_node is not None:
        for u, v in shortest_edges:
            if v == min_node:
                abs_min_edges.add((u, v))

    shortest_set = set(shortest_edges) if shortest_edges else set()
    target_set = set(target_edges) if target_edges else set()

    # Розподіляємо ребра по категоріях
    gray_edges = []
    red_edges = []
    blue_edges = []
    purple_edges = []

    for e in G.edges():
        # Пріоритет 1: Фіолетовий (обраний шлях)
        if e in target_set:
            purple_edges.append(e)
        # Пріоритет 2: Синій (абсолютно найкоротший шлях), якщо увімкнений
        elif show_blue_absolute and e in abs_min_edges:
            blue_edges.append(e)
        # Пріоритет 3: Червоний (усі найкоротші), якщо увімкнений
        elif show_red_shortest and e in shortest_set:
            red_edges.append(e)
        # Решта: Сірі (звичайні або приховані найкоротші)
        else:
            gray_edges.append(e)

    # Малюємо ребра шар за шаром
    if gray_edges:
        nx.draw_networkx_edges(G, pos, edgelist=gray_edges, edge_color="gray", 
                              width=1.5, arrows=True, arrowsize=15, node_size=node_size, ax=ax)

    if red_edges:
        nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color="red", 
                              width=2.5, arrows=True, arrowsize=18, node_size=node_size, ax=ax)

    if blue_edges:
        nx.draw_networkx_edges(G, pos, edgelist=blue_edges, edge_color="blue", 
                              width=3.0, arrows=True, arrowsize=20, node_size=node_size, ax=ax)

    if purple_edges:
        nx.draw_networkx_edges(G, pos, edgelist=purple_edges, edge_color="purple", 
                              width=3.5, arrows=True, arrowsize=22, node_size=node_size, ax=ax)

    labels = {i: f"{i}\n h={h[i]}" if i in h else f"{i}\n(недос.)" for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", ax=ax)

    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges().data()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

    ax.set_title(title)
    ax.axis("off")

    ax.set_clip_on(False)
    for artist in ax.get_children():
        artist.set_clip_on(False)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.margins(0.10)

    return fig
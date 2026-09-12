import matplotlib.pyplot as plt
import networkx as nx

def build_figure(edges, h, shortest_edges, title="Розв'язок задачі"):
    """Створює об'єкт Figure Matplotlib для інтерактивного відображення."""
    G = nx.DiGraph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    is_planar, _ = nx.check_planarity(G.to_undirected())
    if is_planar:
        pos = nx.planar_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(6, 5))

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue", ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="gray", arrows=True, arrowsize=15, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=shortest_edges, edge_color="red", width=2.5, arrows=True, arrowsize=20, ax=ax)

    labels = {i: f"{i}\n(h={h[i]})" if i in h else f"{i}\n(недос.)" for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", ax=ax)

    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges().data()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

    ax.set_title(title)
    ax.axis("off")
    
    # Відступи для комфортного панорамування
    fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05)
    return fig
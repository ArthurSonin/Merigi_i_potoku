import matplotlib.pyplot as plt
import networkx as nx

def build_figure(edges, h, shortest_edges, title="Розв'язок задачі"):
    G = nx.DiGraph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    is_planar, _ = nx.check_planarity(G.to_undirected())
    pos = nx.planar_layout(G) if is_planar else nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(6, 5))

    node_size = 700

    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color="lightblue", ax=ax)

    nx.draw_networkx_edges(
        G, pos, 
        edgelist=G.edges(), 
        edge_color="gray", 
        arrows=True, 
        arrowsize=15, 
        node_size=node_size, 
        ax=ax
    )
    
    if shortest_edges:
        nx.draw_networkx_edges(
            G, pos, 
            edgelist=shortest_edges, 
            edge_color="red", 
            width=2.5, 
            arrows=True, 
            arrowsize=20, 
            node_size=node_size, 
            ax=ax
        )

    labels = {i: f"{i}\n h={h[i]}" if i in h else f"{i}\n(недос.)" for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", ax=ax)

    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges().data()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

    ax.set_title(title)
    ax.axis("off")
    
    # 1. Вимикаємо обрізання вузлів та ліній за межами осей
    ax.set_clip_on(False)
    for artist in ax.get_children():
        artist.set_clip_on(False)

    # 2. РОЗШИРЮЄМО ОБЛАСТЬ: прибираємо білі відступи навколо осей
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)

    # 3. Додаємо автоматичний 10% запас координат, щоб вершини не липли до самих країв
    ax.margins(0.10)

    return fig
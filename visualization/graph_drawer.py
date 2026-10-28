import itertools
import random

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


# ----------------------------------------------------------------------
#  Розташування вершин із мінімальною кількістю перетинів дуг
# ----------------------------------------------------------------------
def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(p1, p2, p3, p4):
    """Чи перетинаються відрізки p1p2 і p3p4 у внутрішніх точках."""
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return d1 * d2 < -1e-12 and d3 * d4 < -1e-12


def _point_near_segment(p, a, b, tol):
    """Чи проходить відрізок ab впритул до вершини p (дуга 'наїжджає' на вершину)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    if length2 == 0:
        return False
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / length2))
    cx, cy = ax + t * dx, ay + t * dy
    return (p[0] - cx) ** 2 + (p[1] - cy) ** 2 < tol * tol


def layout_score(pos, pairs):
    """Повертає (перетини, накладання): кількість справжніх перетинів дуг та
    кількість випадків, коли дуга проходить через чужу вершину або вершини злиплись."""
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
    tol = 0.03 * span

    cross = 0
    for (a, b), (c, d) in itertools.combinations(pairs, 2):
        if len({a, b, c, d}) == 4 and _segments_cross(pos[a], pos[b], pos[c], pos[d]):
            cross += 1
    bad = 0
    for a, b in pairs:
        for n, p in pos.items():
            if n not in (a, b) and _point_near_segment(p, pos[a], pos[b], tol):
                bad += 1
    for n1, n2 in itertools.combinations(pos, 2):
        if (pos[n1][0] - pos[n2][0]) ** 2 + (pos[n1][1] - pos[n2][1]) ** 2 < (2 * tol) ** 2:
            bad += 1
    return cross, bad


def count_crossings(pos, pairs):
    """Єдина оцінка для пошуку: справжні перетини важать значно більше за накладання."""
    cross, bad = layout_score(pos, pairs)
    return cross * 100 + bad


def _dist_point_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy
    if length2 == 0:
        return ((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length2))
    cx, cy = a[0] + t * dx, a[1] + t * dy
    return ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5


def clearance(pos, pairs):
    """Наскільки 'просторо' на малюнку: мінімальна відстань між вершинами та між вершиною
    і чужою дугою, у частках розміру малюнка (більше - читабельніше)."""
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
    best = float("inf")
    for n1, n2 in itertools.combinations(pos, 2):
        best = min(best, _dist_point_segment(pos[n1], pos[n2], pos[n2]))
    for a, b in pairs:
        for n, p in pos.items():
            if n not in (a, b):
                best = min(best, _dist_point_segment(p, pos[a], pos[b]))
    return best / span


def _relax(U, start, iterations):
    """Силове вирівнювання (Фрухтерман-Рейнгольд) від заданої початкової укладки."""
    return nx.spring_layout(U, pos=start, iterations=iterations, seed=1, k=None)


def _build_layers(G, source, sink):
    """Шари зліва направо: шар = відстань від джерела, стік - в окремому крайньому шарі."""
    dist = nx.single_source_shortest_path_length(G, source)
    unreachable = [n for n in G.nodes() if n not in dist]
    layers = {}
    for n, d in dist.items():
        if n != sink:
            layers.setdefault(d, []).append(n)
    last = (max(layers) if layers else 0) + 1
    if unreachable:
        layers.setdefault(last, []).extend(unreachable)
        last += 1
    layers = [sorted(layers[d]) for d in sorted(layers)]
    layers.append([sink])
    return layers


def _layers_to_pos(layers):
    pos = {}
    for x, nodes in enumerate(layers):
        for i, n in enumerate(nodes):
            pos[n] = (float(x), (len(nodes) - 1) / 2 - i)
    return pos


def _minimize_crossings_layered(layers, pairs, seed=0):
    """Підбирає порядок вершин у шарах так, щоб дуг перетиналося якомога менше."""
    rnd = random.Random(seed)
    best_layers = [list(l) for l in layers]
    best = count_crossings(_layers_to_pos(best_layers), pairs)
    if best == 0:
        return best_layers, 0

    movable = [i for i, l in enumerate(layers) if len(l) > 1]
    if not movable:
        return best_layers, best

    budget = int(max(400, min(30000, 1_500_000 // max(1, len(pairs) ** 2))))
    restarts = 20
    per_restart = budget // restarts

    for r in range(restarts):
        cur = [list(l) for l in (best_layers if r == 0 else layers)]
        if r > 0:
            for i in movable:
                rnd.shuffle(cur[i])
        cur_score = count_crossings(_layers_to_pos(cur), pairs)
        for _ in range(per_restart):
            i = rnd.choice(movable)
            a, b = rnd.sample(range(len(cur[i])), 2)
            cur[i][a], cur[i][b] = cur[i][b], cur[i][a]
            score = count_crossings(_layers_to_pos(cur), pairs)
            if score <= cur_score:
                cur_score = score
            else:
                cur[i][a], cur[i][b] = cur[i][b], cur[i][a]
            if cur_score < best:
                best, best_layers = cur_score, [list(l) for l in cur]
                if best == 0:
                    return best_layers, 0
    return best_layers, best


def _faces(embedding):
    faces, seen = [], set()
    for u, v in embedding.edges():
        if (u, v) in seen:
            continue
        faces.append(embedding.traverse_face(u, v, mark_half_edges=seen))
    return faces


def _tutte_layout(U, outer, source, sink):
    """Укладка Тутта: вершини грані `outer` стоять на колі (джерело - ліворуч, стік -
    праворуч, якщо вони на цій грані), решта - у центрі ваги сусідів.
    Для планарних графів перетинів немає (для 3-зв'язних це гарантовано)."""
    import math
    import numpy as np

    cycle = []
    for n in outer:
        if n not in cycle:
            cycle.append(n)
    if source in cycle:
        k = cycle.index(source)
        cycle = cycle[k:] + cycle[:k]

    fixed = {}
    if source in cycle and sink in cycle:
        j = cycle.index(sink)
        upper = cycle[:j + 1]                      # source ... sink
        lower = cycle[j:] + [cycle[0]]             # sink ... source
        for i, n in enumerate(upper):
            ang = math.pi - math.pi * i / max(1, len(upper) - 1)
            fixed[n] = (math.cos(ang), math.sin(ang))
        for i, n in enumerate(lower):
            ang = -math.pi * i / max(1, len(lower) - 1)
            fixed.setdefault(n, (math.cos(ang), math.sin(ang)))
    else:
        for k, n in enumerate(cycle):
            ang = math.pi + 2 * math.pi * k / len(cycle)
            fixed[n] = (math.cos(ang), math.sin(ang))

    nodes = list(U.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    n_total = len(nodes)
    A = np.zeros((n_total, n_total))
    bx = np.zeros(n_total)
    by = np.zeros(n_total)
    for n in nodes:
        i = idx[n]
        if n in fixed:
            A[i, i] = 1
            bx[i], by[i] = fixed[n]
        else:
            nb = list(U.neighbors(n))
            A[i, i] = len(nb)
            for m in nb:
                A[i, idx[m]] -= 1
    x = np.linalg.lstsq(A, bx, rcond=None)[0]
    y = np.linalg.lstsq(A, by, rcond=None)[0]
    return {n: (float(x[idx[n]]), float(y[idx[n]])) for n in nodes}


def _layout_key(pos, pairs):
    """Чим менше, тим краще: спершу перетини, потім тісновість (до порога), потім довжина дуг."""
    cross, bad = layout_score(pos, pairs)
    clear = min(clearance(pos, pairs), 0.12)
    length = sum(((pos[a][0] - pos[b][0]) ** 2 + (pos[a][1] - pos[b][1]) ** 2) ** 0.5 for a, b in pairs)
    return (cross, bad, -round(clear, 3), length)


def _refine_free(start, pairs, source, sink, rnd, iterations):
    """Покращує розташування випадковими зсувами вершин (джерело й стік лишаються
    крайніми зліва/справа). Приймається лише не гірший за ключем варіант."""
    pos = dict(start)
    xs = [p[0] for p in pos.values()]
    x_min, x_max = min(xs), max(xs)
    cur = _layout_key(pos, pairs)
    movable = list(pos)
    for _ in range(iterations):
        n = rnd.choice(movable)
        old = pos[n]
        if n == source:
            new = (x_min, old[1] + rnd.gauss(0, 0.6))
        elif n == sink:
            new = (x_max, old[1] + rnd.gauss(0, 0.6))
        else:
            nx_ = min(x_max - 0.2, max(x_min + 0.2, old[0] + rnd.gauss(0, 0.3)))
            new = (nx_, old[1] + rnd.gauss(0, 0.6))
        pos[n] = new
        k = _layout_key(pos, pairs)
        if k <= cur:
            cur = k
        else:
            pos[n] = old
    return pos, cur


def compute_layout(edges, source, sink):
    """Повертає (pos, crossings, is_planar).

    Мережа малюється зліва направо (джерело зліва, стік справа). Порядок вершин у
    шарах підбирається так, щоб перетинів було мінімум, далі вершини вільно
    зсуваються для усунення перетинів і тісноти. Для планарної мережі як запасні
    варіанти розглядаються укладки Тутта та планарна укладка networkx, які за
    теорією не мають перетинів. Для непланарної мережі (є підграф K5 або K3,3)
    повністю уникнути перетинів неможливо - повертається варіант з мінімумом.
    """
    pairs = []
    seen = set()
    for u, v, _ in edges:
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            pairs.append((u, v))

    G = nx.DiGraph()
    G.add_edges_from((u, v) for u, v, _ in edges)
    U = nx.Graph()
    U.add_edges_from(pairs)
    is_planar, embedding = nx.check_planarity(U)

    layers = _build_layers(G, source, sink)
    best_layers, _ = _minimize_crossings_layered(layers, pairs)
    base = _layers_to_pos(best_layers)

    rnd = random.Random(7)
    candidates = [base]
    iters = int(max(300, min(2500, 400_000 // max(1, len(pairs) ** 2 + len(pairs) * len(base)))))
    for _ in range(4):
        pos, _k = _refine_free(base, pairs, source, sink, rnd, iters)
        candidates.append(pos)
        if _layout_key(pos, pairs)[0] == 0 and _layout_key(pos, pairs)[1] == 0 \
                and clearance(pos, pairs) >= 0.07:
            break

    best = min(candidates, key=lambda p: _layout_key(p, pairs))
    if is_planar and (layout_score(best, pairs)[0] > 0 or clearance(best, pairs) < 0.05):
        starts = []
        if nx.is_connected(U):
            faces = _faces(embedding)
            both = [f for f in faces if source in f and sink in f]
            pool = both or [f for f in faces if source in f] or faces
            for face in sorted(pool, key=len, reverse=True)[:8]:
                try:
                    starts.append(_tutte_layout(U, face, source, sink))
                except Exception:
                    pass
        starts.append(nx.planar_layout(U))
        starts.sort(key=lambda p: _layout_key(p, pairs))
        refined = []
        for st in starts[:3]:
            refined.append(st)
            if layout_score(st, pairs)[0] == 0:
                pos, _k = _refine_free(st, pairs, source, sink, rnd, 500)
                refined.append(pos)
        best = min(refined + [best], key=lambda p: _layout_key(p, pairs))

    return best, layout_score(best, pairs)[0], is_planar


# ----------------------------------------------------------------------
#  Малювання
# ----------------------------------------------------------------------
def build_flow_figure(edges, flow, source, sink, I_star, cut_edges, pos,
                      title="Максимальний потік", show_cut=True, fake_nodes=()):
    """Малює мережу з потоком: підписи дуг 'x/r', мінімальний переріз червоним.

    Кольори дуг: червоний - дуга мінімального перерізу, синій - ненульовий потік,
    сірий - порожня дуга. Вершини з I* - зелені, інші - блакитні.
    Протилежні дуги (u,v) і (v,u) малюються вигнутими, щоб не накладатися.
    """
    # Зводимо паралельні дуги (u, v) в одну для малювання
    cap_map, flow_map = {}, {}
    for (u, v, c), x in zip(edges, flow):
        cap_map[(u, v)] = cap_map.get((u, v), 0) + c
        flow_map[(u, v)] = flow_map.get((u, v), 0) + x

    G = nx.DiGraph()
    G.add_nodes_from(pos)
    G.add_edges_from(cap_map)

    fig, ax = plt.subplots(figsize=(6, 5))
    node_size = 700

    nodes = list(G.nodes())
    nx.draw_networkx_nodes(
        G, pos, nodelist=nodes, node_size=node_size,
        node_color=["lightgreen" if n in I_star else "lightblue" for n in nodes],
        edgecolors=["black" if n in (source, sink) else "gray" for n in nodes],
        linewidths=[2.5 if n in (source, sink) else 1 for n in nodes], ax=ax)

    cut_set = {(u, v) for u, v, _ in cut_edges} if show_cut else set()

    def group(e):
        if e in cut_set:
            return "red"
        return "blue" if flow_map[e] > 0 else "gray"

    styles = {"gray": 1.5, "blue": 2.5, "red": 3.0}
    for color in ("gray", "blue", "red"):          # червоні малюються поверх
        for curved in (False, True):
            el = [e for e in G.edges()
                  if group(e) == color and ((e[1], e[0]) in cap_map) == curved]
            if el:
                nx.draw_networkx_edges(
                    G, pos, edgelist=el, edge_color=color, width=styles[color],
                    arrows=True, arrowsize=18, node_size=node_size, ax=ax,
                    connectionstyle="arc3,rad=0.2" if curved else "arc3,rad=0.0")

    def fmt(x):
        return int(x) if float(x).is_integer() else round(x, 3)

    def node_label(n):
        if n in fake_nodes:                       # службові вершини S і T
            return "S" if n == source else "T"
        return f"{n}\nст." if n == sink else (f"{n}\nдж." if n == source else str(n))

    labels = {n: node_label(n) for n in nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", ax=ax)

    edge_labels = {e: (f"{fmt(flow_map[e])}/∞" if (e[0] in fake_nodes or e[1] in fake_nodes)
                       else f"{fmt(flow_map[e])}/{fmt(cap_map[e])}")
                   for e in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8,
                                 label_pos=0.35, ax=ax, rotate=False,
                                 bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    ax.set_title(title, fontsize=9)
    ax.axis("off")
    for artist in ax.get_children():
        artist.set_clip_on(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.margins(0.10)
    return fig

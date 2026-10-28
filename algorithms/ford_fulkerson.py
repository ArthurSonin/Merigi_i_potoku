from collections import deque


def solve_ford_fulkerson(edges, source, sink):
    """Максимальний потік і мінімальний переріз методом Форда-Фалкерсона
    (алгоритм розстановки позначок із методички).

    Кожна вершина отримує позначку (N, theta):
      N > 0  - прямі дуги: прийшли з вершини N по дузі (N, j), потік збільшуємо;
      N < 0  - зворотні дуги: прийшли з вершини -N по зворотній дузі, потік зменшуємо;
      theta  - на скільки можна змінити потік уздовж ланцюга до цієї вершини.
    Вершини розглядаються в порядку позначення (черга), тому алгоритм
    завжди завершується, навіть для дробових пропускних здатностей.

    Параметри:
        edges: список дуг (u, v, capacity).
        source: джерело. sink: стік (витік).

    Повертає dict:
        flow          - список потоків x_ij у тому ж порядку, що й edges;
        max_flow      - величина максимального потоку;
        I_star        - множина позначених вершин I* (джерельна частина перерізу);
        cut_edges     - дуги мінімального перерізу [(u, v, capacity), ...];
        cut_capacity  - пропускна здатність перерізу (= max_flow);
        iterations    - детальний журнал кроків для звіту.
    """
    nodes = set()
    for u, v, c in edges:
        if c < 0:
            raise ValueError(f"Від'ємна пропускна здатність у дузі {u}->{v}: {c}")
        nodes.add(u)
        nodes.add(v)

    if source not in nodes:
        raise ValueError(f"Джерело {source} відсутнє в мережі.")
    if sink not in nodes:
        raise ValueError(f"Стік {sink} відсутній у мережі.")
    if source == sink:
        raise ValueError("Джерело і стік мають бути різними вершинами.")

    flow = [0] * len(edges)
    out_edges = {n: [] for n in nodes}   # індекси дуг, що виходять з n
    in_edges = {n: [] for n in nodes}    # індекси дуг, що входять у n
    for idx, (u, v, _) in enumerate(edges):
        out_edges[u].append(idx)
        in_edges[v].append(idx)

    iterations = []
    max_flow = 0

    while True:
        labels = {source: (0, float("inf"))}
        order = [source]
        queue = deque([source])

        while queue and sink not in labels:
            i = queue.popleft()
            theta_i = labels[i][1]

            # Прямі дуги (i, j): залишкова здатність r_ij - x_ij > 0
            for idx in sorted(out_edges[i], key=lambda k: edges[k][1]):
                _, j, cap = edges[idx]
                if j not in labels and cap - flow[idx] > 0:
                    labels[j] = (i, min(theta_i, cap - flow[idx]))
                    order.append(j)
                    queue.append(j)

            # Зворотні дуги (j, i): потік x_ji > 0, можна зменшити
            for idx in sorted(in_edges[i], key=lambda k: edges[k][0]):
                j, _, _ = edges[idx]
                if j not in labels and flow[idx] > 0:
                    labels[j] = (-i, min(theta_i, flow[idx]))
                    order.append(j)
                    queue.append(j)

        if sink not in labels:
            # Стік не позначено - потік максимальний, I* = позначені вершини
            I_star = set(labels)
            cut_edges = [(u, v, c) for u, v, c in edges
                         if u in I_star and v not in I_star]
            cut_capacity = sum(c for _, _, c in cut_edges)
            iterations.append({
                "labels": {n: labels[n] for n in order},
                "path": None,
                "theta": 0,
                "flow_after": list(flow),
                "value_after": max_flow,
            })
            return {
                "flow": flow,
                "max_flow": max_flow,
                "I_star": I_star,
                "cut_edges": cut_edges,
                "cut_capacity": cut_capacity,
                "iterations": iterations,
            }

        # Стік позначено - будуємо ланцюг від стоку до джерела й змінюємо потік
        theta = labels[sink][1]
        path = [sink]
        cur = sink
        while cur != source:
            prev = abs(labels[cur][0])
            sign = 1 if labels[cur][0] > 0 else -1
            if sign > 0:
                # пряма дуга prev -> cur: шукаємо дугу з залишком
                idx = next(k for k in out_edges[prev]
                           if edges[k][1] == cur and edges[k][2] - flow[k] >= theta)
                flow[idx] += theta
            else:
                # зворотна дуга: фактична дуга cur -> prev з потоком
                idx = next(k for k in out_edges[cur]
                           if edges[k][1] == prev and flow[k] >= theta)
                flow[idx] -= theta
            path.append(prev)
            cur = prev
        path.reverse()

        max_flow += theta
        iterations.append({
            "labels": {n: labels[n] for n in order},
            "path": path,
            "theta": theta,
            "flow_after": list(flow),
            "value_after": max_flow,
        })


def add_super_nodes(edges, sources, sinks):
    """Зводить мережу з кількома джерелами й стоками до звичайної.

    Додає фіктивне джерело S і фіктивний стік T та дуги (S, s) для кожного
    джерела s і (t, T) для кожного стоку t з "нескінченною" пропускною
    здатністю. Далі алгоритм запускається від S до T.

    Повертає (нові_дуги, S, T, службові_вершини), де службові_вершини - це
    множина {S, T} (порожня, якщо джерело й стік по одному і нічого не додавали).
    """
    sources = list(dict.fromkeys(sources))   # без дублікатів, зі збереженням порядку
    sinks = list(dict.fromkeys(sinks))
    if not sources or not sinks:
        raise ValueError("Потрібно вказати хоча б одне джерело і хоча б один стік.")

    # Звичайний випадок: одне джерело і один стік - нічого не змінюємо
    if len(sources) == 1 and len(sinks) == 1:
        return list(edges), sources[0], sinks[0], set()

    nodes = {n for u, v, _ in edges for n in (u, v)}
    for n in sources:
        if n not in nodes:
            raise ValueError(f"Джерело {n} відсутнє в мережі.")
    for n in sinks:
        if n not in nodes:
            raise ValueError(f"Стік {n} відсутній у мережі.")
    common = set(sources) & set(sinks)
    if common:
        raise ValueError(f"Вершина не може бути і джерелом, і стоком: {sorted(common)}.")

    S = max(nodes) + 1
    T = S + 1
    inf = sum(c for _, _, c in edges) + 1    # більше за будь-який переріз

    new_edges = list(edges)
    new_edges += [(S, s, inf) for s in sources]
    new_edges += [(t, T, inf) for t in sinks]
    return new_edges, S, T, {S, T}

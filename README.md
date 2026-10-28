# Ford-Fulkerson Flow Solver

Програма знаходить максимальний потік і мінімальний переріз у мережі методом Форда-Фалкерсона
(алгоритм розстановки позначок), показує хід розв'язання та малює мережу з потоком
із мінімальною кількістю перетинів дуг.

## Запуск
    pip install matplotlib networkx pillow
    python main.py

## Формат даних
Кожен рядок - одна дуга: `звідки куди пропускна_здатність`, наприклад `1 2 3`.

## Структура
- `algorithms/ford_fulkerson.py` - алгоритм (без залежності від інтерфейсу)
- `visualization/graph_drawer.py` - розташування вершин і малювання
- `ui/` - інтерфейс (Tkinter)
- `tests/test_ford_fulkerson.py` - тести (`python tests/test_ford_fulkerson.py`)

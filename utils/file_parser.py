import os

def parse_edges_from_file(filepath):
    """Зчитує список дуг із текстового файлу та повертає назву файлу і дані."""
    edges = []
    filename = os.path.basename(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Рядок {line_num}: некоректний формат '{line}'. Очікується 3 числа.")
            
            u, v = int(parts[0]), int(parts[1])
            w = float(parts[2])
            if w.is_integer():
                w = int(w)
            edges.append((u, v, w))
            
    if not edges:
        raise ValueError("Файл порожній або не містить коректних даних!")
        
    return filename, edges

def save_edges_to_file(filepath, edges):
    """Зберігає список дуг графа у текстовий файл у форматі 'u v w'."""
    if not edges:
        raise ValueError("Список дуг порожній, немає даних для збереження!")

    # Створюємо директорію, якщо вказаного шляху ще не існує
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        for u, v, w in edges:
            # Форматування ваги: якщо ціле число — записуємо як int, інакше як float
            if isinstance(w, float) and w.is_integer():
                w = int(w)
            
            f.write(f"{u} {v} {w}\n")

    return os.path.basename(filepath)

def save_results_to_file(filepath, source_name, algorithm_name, results_data):
    """
    Зберігає текстові результати виконання алгоритму у файл.
    
    :param filepath: Шлях до файлу для збереження
    :param source_name: Назва вхідного файлу/джерела даних
    :param algorithm_name: Назва виконаного алгоритму (наприклад, "Алгоритм Мінті")
    :param results_data: Рядок або список рядків із результатами
    """
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write(f"РЕЗУЛЬТАТИ ОБЧИСЛЕНЬ\n")
        f.write(f"Алгоритм: {algorithm_name}\n")
        f.write(f"Джерело даних: {source_name}\n")
        f.write("=" * 50 + "\n\n")

        if isinstance(results_data, (list, tuple)):
            for line in results_data:
                f.write(f"{line}\n")
        else:
            f.write(str(results_data).strip() + "\n")

    return os.path.basename(filepath)
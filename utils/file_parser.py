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
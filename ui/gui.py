import sys
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.minty import solve_minty
from config import EDGES as DEFAULT_EDGES, START_NODE as DEFAULT_START
from visualization.graph_drawer import build_figure
from utils.file_parser import parse_edges_from_file, save_edges_to_file, save_results_to_file
from utils.helpers import resource_path
from ui.about_dialog import AboutDialog
from ui.guide_dialog import GuideDialog


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minty Graph Solver")
        self.geometry("1000x680")

        try:
            icon_path = resource_path("assets/icon.png")
            icon_img = Image.open(icon_path)
            icon_img_resized = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            self._icon_photo = ImageTk.PhotoImage(icon_img_resized)
            self.iconphoto(True, self._icon_photo)
        except Exception as e:
            print(f"Не вдалося завантажити іконку: {e}")

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.canvas_widget = None
        self.current_source_name = None
        
        self.pan_start_x = None
        self.pan_start_y = None

        self.last_edges = None
        self.last_h = None
        self.last_shortest_edges = None
        self.last_start_node = None
        
        self._setup_ui()

    def _setup_ui(self):
        left_frame = ttk.Frame(self, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        start_subframe = ttk.Frame(input_frame)
        start_subframe.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))

        ttk.Label(start_subframe, text="Початкова вершина:").pack(anchor=tk.W)
        self.start_entry = ttk.Entry(start_subframe, width=8)
        self.start_entry.pack(anchor=tk.W, pady=(2, 0))

        action_btn_frame = ttk.Frame(input_frame)
        action_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(action_btn_frame, text="Завантажити з файлу", command=self.load_from_file).pack(fill=tk.X, pady=1)
        ttk.Button(action_btn_frame, text="Розрахувати (Мінті)", command=self.calculate).pack(fill=tk.X, pady=1)

        ttk.Button(left_frame, text="Зберегти граф", command=self.save_to_file).pack(fill=tk.X, pady=1)
        ttk.Button(left_frame, text="Зберегти результати", command=self.save_results).pack(fill=tk.X, pady=1)

        ttk.Label(left_frame, text="Дуги (звідки куди вага):").pack(anchor=tk.W, pady=(5, 0))
        self.edges_text = tk.Text(left_frame, width=32, height=9)
        self.edges_text.pack(pady=(0, 5))

        self.file_label = ttk.Label(left_frame, text="Джерело: Тестові дані", font=("Arial", 8, "italic"), foreground="gray")
        self.file_label.pack(anchor=tk.W, pady=(0, 5))

        # --- НАЛАШТУВАННЯ ВІДОБРАЖЕННЯ (КЕРУВАННЯ КОЛЬОРАМИ) ---
        view_frame = ttk.LabelFrame(left_frame, text=" Налаштування відображення ", padding=5)
        view_frame.pack(fill=tk.X, pady=(0, 10))

        self.show_red_var = tk.BooleanVar(value=True)
        self.chk_show_red = ttk.Checkbutton(
            view_frame, 
            text="Усі найкоротші шляхи (червоні)", 
            variable=self.show_red_var,
            command=self.update_graph_display
        )
        self.chk_show_red.pack(anchor=tk.W, pady=1)

        self.show_blue_var = tk.BooleanVar(value=True)
        self.chk_show_blue = ttk.Checkbutton(
            view_frame, 
            text="Перший найкоротший (синій)", 
            variable=self.show_blue_var,
            command=self.update_graph_display
        )
        self.chk_show_blue.pack(anchor=tk.W, pady=1)

        ttk.Label(view_frame, text="Цільова вершина (фіолетовий шлях):").pack(anchor=tk.W, pady=(5, 2))
        self.target_node_cb = ttk.Combobox(view_frame, state="readonly")
        self.target_node_cb.bind("<<ComboboxSelected>>", lambda e: self.update_graph_display())
        self.target_node_cb.pack(fill=tk.X, pady=2)

        # Кнопки
        bottom_btn_frame = ttk.Frame(left_frame)
        bottom_btn_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(bottom_btn_frame, text="Інструкція", command=self.show_guide_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(bottom_btn_frame, text="Про програму", command=self.show_about_dialog).pack(fill=tk.X, pady=2)

        # Результати
        ttk.Label(left_frame, text="Результати:").pack(anchor=tk.W, pady=(5, 0))

        # Фрейм-контейнер для текстового поля та полос прокрутки
        result_frame = ttk.Frame(left_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # Текстове поле з wrap=tk.NONE (вимикає перенос слів)
        self.result_text = tk.Text(
            result_frame, 
            width=32, 
            height=5, 
            wrap=tk.NONE,  # <--- Ключовий параметр: вимикає примусовий перенос
            state=tk.DISABLED
        )

        # Скроллбари (вертикальний та горизонтальний)
        v_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        h_scrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)

        self.result_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Розміщення елементів у контейнері
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _update_results_report(self, selected_target_str):
        if not hasattr(self, 'last_h') or not self.last_h:
            return

        h = self.last_h
        shortest_edges = self.last_shortest_edges
        start_node = self.last_start_node
        edges = self.last_edges
        weights_map = {(u, v): w for u, v, w in edges}

        total_nodes = len(h)
        reachable_count = sum(1 for v in h.values() if v < float('inf'))

        report = []
        report.append("=== РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ (АЛГОРИТМ МІНТІ) ===")
        report.append(f"Джерело даних: {self.current_source_name}")
        report.append(f"Початкова вершина: {start_node}")
        report.append(f"Досяжно вершин: {reachable_count} з {total_nodes}\n")

        # 1. Абсолютно найкоротший шлях серед усіх вершин (Синій колір на графі)
        valid_distances = {node: dist for node, dist in h.items() if node != start_node and dist < float('inf')}
        if valid_distances:
            min_node = min(valid_distances, key=valid_distances.get)
            min_dist = valid_distances[min_node]
            min_path_edges = self._get_path_to_node(min_node)
            min_path_str = f"{min_path_edges[0][0]}" + "".join([f" -> {v}" for _, v in min_path_edges])
            report.append("--- ПЕРШИЙ НАЙКОРОТШИЙ ШЛЯХ (СИНІЙ) ---")
            report.append(f"• До вершини {min_node}: довжина = {min_dist} | Маршрут: [{min_path_str}]\n")

        # 2. Обраний цільовий шлях (Фіолетовий колір на графі)
        report.append("--- ОБРАНИЙ ЦІЛЬОВИЙ ШЛЯХ (ФІОЛЕТОВИЙ) ---")
        if selected_target_str and selected_target_str != "Не обрано":
            target_node = int(selected_target_str)
            target_dist = h.get(target_node, float('inf'))
            target_path_edges = self._get_path_to_node(target_node)
            if target_path_edges:
                target_path_str = f"{target_path_edges[0][0]}" + "".join([f" -> {v}" for _, v in target_path_edges])
                report.append(f"• Ціль: Вершина {target_node}")
                report.append(f"• Загальна вартість: {target_dist}")
                report.append(f"• Повний маршрут: [{target_path_str}]\n")
            else:
                report.append(f"• Ціль: Вершина {target_node} (Маршрут відсутній)\n")
        else:
            report.append("• Цільова вершина не обрана\n")

        # 3. Відстані та маршрути до всіх вершин
        report.append("--- НАЙКОРОТШІ ВІДСТАНІ ТА МАРШРУТИ ДО ВСІХ ВЕРШИН ---")
        for node in sorted(h.keys()):
            dist = h[node]
            if node == start_node:
                report.append(f"• В. {node}: h_{node} = 0 (Старт)")
                continue

            if dist == float('inf'):
                report.append(f"• В. {node}: Недосяжна з вершини {start_node}")
            else:
                path_edges = self._get_path_to_node(node)
                if path_edges:
                    path_str = f"{path_edges[0][0]}" + "".join([f" -> {v}" for _, v in path_edges])
                else:
                    path_str = "Прямого шляху немає"
                report.append(f"• В. {node}: h_{node} = {dist} | Шлях: [{path_str}]")

        # 4. Дерево найкоротших шляхів
        report.append("\n--- ДЕРЕВО НАЙКОРОТШИХ ШЛЯХІВ (ДУГИ ТА ЦІНА) ---")
        if shortest_edges:
            for u, v in sorted(shortest_edges):
                weight = weights_map.get((u, v), "?")
                report.append(f"  {u} -> {v} (ціна: {weight})")
        else:
            report.append("  (дуги відсутні)")

        # Оновлення текстового поля
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "\n".join(report))
        self.result_text.config(state=tk.DISABLED)

    def on_exit(self):
        if messagebox.askokcancel("Вихід", "Ви дійсно бажаєте вийти з програми?"):
            plt.close('all')
            self.quit()
            self.destroy()
            sys.exit(0)

    def show_about_dialog(self):
        AboutDialog(self)

    def show_guide_dialog(self):
        GuideDialog(self)

    def load_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Оберіть файл із даними графа",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            filename, edges = parse_edges_from_file(filepath)
            self.edges_text.delete("1.0", tk.END)
            lines = [f"{u} {v} {w}" for u, v, w in edges]
            self.edges_text.insert("1.0", "\n".join(lines))
            
            self.current_source_name = filename
            self.file_label.config(text=f"Джерело: {self.current_source_name}")
            messagebox.showinfo("Успіх", f"Дані з файлу '{filename}' успішно завантажено!")
        except Exception as e:
            messagebox.showerror("Помилка файлу", str(e))

    def save_to_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Зберегти дані графа",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            raw_lines = self.edges_text.get("1.0", tk.END).strip().split("\n")
            edges = []
            for line_num, line in enumerate(raw_lines, 1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Рядок {line_num}: некоректний формат '{line}'. Очікується 3 числа.")
                
                u, v = int(parts[0]), int(parts[1])
                w = float(parts[2])
                edges.append((u, v, w))

            filename = save_edges_to_file(filepath, edges)
            self.current_source_name = filename
            self.file_label.config(text=f"Джерело: {self.current_source_name}")
            messagebox.showinfo("Успіх", f"Дані успішно збережено у файл '{filename}'!")

        except Exception as e:
            messagebox.showerror("Помилка збереження", str(e))

    def save_results(self):
        results_text = self.result_text.get("1.0", tk.END).strip()
        if not results_text:
            messagebox.showwarning("Увага", "Немає результатів для збереження! Спочатку запустіть обчислення.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Зберегти результати обчислень",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            source = getattr(self, 'current_source_name', 'Введено вручну')
            filename = save_results_to_file(
                filepath=filepath,
                source_name=source,
                algorithm_name="Алгоритм Мінті",
                results_data=results_text
            )
            messagebox.showinfo("Успіх", f"Результати успішно збережено у файл '{filename}'!")
        except Exception as e:
            messagebox.showerror("Помилка збереження", f"Не вдалося зберегти результати:\n{str(e)}")

    def _setup_mouse_navigation(self, canvas, fig, ax):
        def on_scroll(event):
            base_scale = 1.2
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                return

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - event.xdata) / (cur_xlim[1] - cur_xlim[0]) if event.xdata else 0.5
            rely = (cur_ylim[1] - event.ydata) / (cur_ylim[1] - cur_ylim[0]) if event.ydata else 0.5

            if event.xdata is not None and event.ydata is not None:
                ax.set_xlim([event.xdata - new_width * (1 - relx), event.xdata + new_width * relx])
                ax.set_ylim([event.ydata - new_height * (1 - rely), event.ydata + new_height * rely])
                canvas.draw_idle()

        def on_press(event):
            if event.button == 1 and event.inaxes == ax:
                self.pan_start_x = event.xdata
                self.pan_start_y = event.ydata

        def on_motion(event):
            if self.pan_start_x is None or self.pan_start_y is None or event.inaxes != ax:
                return
            
            dx = event.xdata - self.pan_start_x
            dy = event.ydata - self.pan_start_y

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            ax.set_xlim([cur_xlim[0] - dx, cur_xlim[1] - dx])
            ax.set_ylim([cur_ylim[0] - dy, cur_ylim[1] - dy])
            canvas.draw_idle()

        def on_release(event):
            if event.button == 1:
                self.pan_start_x = None
                self.pan_start_y = None

        initial_xlim = ax.get_xlim()
        initial_ylim = ax.get_ylim()

        def on_double_click(event):
            if event.dblclick and event.button == 1:
                ax.set_xlim(initial_xlim)
                ax.set_ylim(initial_ylim)
                canvas.draw_idle()

        fig.canvas.mpl_connect('scroll_event', on_scroll)
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('button_press_event', on_double_click)

    def _get_path_to_node(self, target_node):
        if not self.last_shortest_edges or target_node == self.last_start_node:
            return []

        parent_map = {}
        for u, v in self.last_shortest_edges:
            parent_map[v] = u

        path_edges = []
        curr = target_node
        visited = set()

        while curr in parent_map and curr not in visited:
            visited.add(curr)
            prev = parent_map[curr]
            path_edges.append((prev, curr))
            if prev == self.last_start_node:
                break
            curr = prev

        path_edges.reverse()
        return path_edges

    def update_graph_display(self):
        if not self.last_edges:
            return

        show_red = self.show_red_var.get()
        show_blue = self.show_blue_var.get()
        selected_target_str = self.target_node_cb.get()

        self._update_results_report(selected_target_str)

        target_edges = []
        if selected_target_str and selected_target_str != "Не обрано":
            target_node = int(selected_target_str)
            target_edges = self._get_path_to_node(target_node)

        if self.canvas_widget:
            self.canvas_widget.destroy()
        plt.close('all')

        chart_title = f"Розв'язок (початок з в. {self.last_start_node}) | Файл: {self.current_source_name}"
        fig = build_figure(
            edges=self.last_edges, 
            h=self.last_h, 
            shortest_edges=self.last_shortest_edges, 
            title=chart_title,
            show_red_shortest=show_red,
            show_blue_absolute=show_blue,
            target_edges=target_edges
        )
        ax = fig.gca()

        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        self._setup_mouse_navigation(canvas, fig, ax)

        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def calculate(self):
        try:
            start_node = int(self.start_entry.get().strip())
        except ValueError:
            messagebox.showerror("Помилка", "Початкова вершина має бути цілим числом!")
            return

        raw_edges = self.edges_text.get("1.0", tk.END).strip().split("\n")
        edges = []
        for line in raw_edges:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 3:
                messagebox.showerror("Помилка", f"Некоректний рядок дуги: '{line}'\nФормат: звідки куди вага")
                return
            try:
                u, v = int(parts[0]), int(parts[1])
                w = float(parts[2])
                if w.is_integer():
                    w = int(w)
                edges.append((u, v, w))
            except ValueError:
                messagebox.showerror("Помилка", f"Некоректні значення в рядку: '{line}'")
                return

        if not edges:
            messagebox.showerror("Помилка", "Введіть або завантажте хоча б одну дугу!")
            return

        h, shortest_edges, _ = solve_minty(edges, start_node=start_node)

        # Зберігаємо стан для інтерактивного оновлення
        self.last_edges = edges
        self.last_h = h
        self.last_shortest_edges = shortest_edges
        self.last_start_node = start_node

        # Оновлюємо список досяжних вершин у Combobox
        reachable_nodes = [str(node) for node in sorted(h.keys()) if node != start_node]
        self.target_node_cb['values'] = ["Не обрано"] + reachable_nodes
        self.target_node_cb.set("Не обрано")

        # Створюємо словник ваг дуг для швидкого пошуку ціни: (u, v) -> weight
        weights_map = {(u, v): w for u, v, w in edges}

        # --- ФОРМУВАННЯ ІНФОРМАТИВНОГО ЗВІТУ ---
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)

        total_nodes = len(h)
        reachable_count = sum(1 for v in h.values() if v < float('inf'))
        
        report = []
        report.append("=== РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ (АЛГОРИТМ МІНТІ) ===")
        report.append(f"Джерело даних: {self.current_source_name}")
        report.append(f"Початкова вершина: {start_node}")
        report.append(f"Досяжно вершин: {reachable_count} з {total_nodes}\n")

        # 1. Відстані та маршрути до кожної вершини
        report.append("--- НАЙКОРОТШІ ВІДСТАНІ ТА МАРШРУТИ ---")
        for node in sorted(h.keys()):
            dist = h[node]
            if node == start_node:
                report.append(f"• В. {node}: h_{node} = 0 (Старт)")
                continue

            if dist == float('inf'):
                report.append(f"• В. {node}: Недосяжна з вершини {start_node}")
            else:
                path_edges = self._get_path_to_node(node)
                if path_edges:
                    path_str = f"{path_edges[0][0]}" + "".join([f" -> {v}" for _, v in path_edges])
                else:
                    path_str = "Прямого шляху немає"
                
                report.append(f"• В. {node}: h_{node} = {dist} | Шлях: [{path_str}]")

        # 2. Дерево найкоротших шляхів із вагами (цінами) дуг
        report.append("\n--- ДЕРЕВО НАЙКОРОТШИХ ШЛЯХІВ (ДУГИ ТА ЦІНА) ---")
        if shortest_edges:
            for u, v in sorted(shortest_edges):
                weight = weights_map.get((u, v), "?")
                report.append(f"  {u} -> {v} (ціна: {weight})")
        else:
            report.append("  (дуги відсутні)")

        self.result_text.insert(tk.END, "\n".join(report))
        self.result_text.config(state=tk.DISABLED)

        # Відображення графа
        self.update_graph_display()


def run_app():
    app = App()
    app.mainloop()
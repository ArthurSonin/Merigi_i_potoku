import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.minty import solve_minty
from config import EDGES as DEFAULT_EDGES, START_NODE as DEFAULT_START
from visualization.graph_drawer import build_figure
from utils.file_parser import parse_edges_from_file
from ui.about_dialog import AboutDialog


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Метод Мінті — Найкоротші шляхи")
        self.geometry("1000x650")

        self.canvas_widget = None
        self.current_source_name = "Тестові дані"
        
        # Змінні для трекінгу перетягування мишею
        self.pan_start_x = None
        self.pan_start_y = None
        
        self._setup_ui()
        self._load_default_data()

    def _setup_ui(self):
        # Ліва панель
        left_frame = ttk.Frame(self, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_frame, text="Початкова вершина:").pack(anchor=tk.W)
        self.start_entry = ttk.Entry(left_frame, width=10)
        self.start_entry.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(left_frame, text="Дуги (звідки куди вага):").pack(anchor=tk.W)
        self.edges_text = tk.Text(left_frame, width=32, height=12)
        self.edges_text.pack(pady=(0, 5))

        self.file_label = ttk.Label(left_frame, text="Джерело: Тестові дані", font=("Arial", 8, "italic"), foreground="gray")
        self.file_label.pack(anchor=tk.W, pady=(0, 10))

        # Панель кнопок
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Розрахувати", command=self.calculate).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Завантажити з файлу", command=self.load_from_file).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Тестові дані", command=self._load_default_data).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Про програму", command=self.show_about_dialog).pack(fill=tk.X, pady=(10, 2))

        # Результати
        ttk.Label(left_frame, text="Результати:").pack(anchor=tk.W, pady=(5, 0))
        self.result_text = tk.Text(left_frame, width=32, height=7, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Права панель
        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def show_about_dialog(self):
        AboutDialog(self)

    def _load_default_data(self):
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str(DEFAULT_START))

        self.edges_text.delete("1.0", tk.END)
        lines = [f"{u} {v} {w}" for u, v, w in DEFAULT_EDGES]
        self.edges_text.insert("1.0", "\n".join(lines))
        
        self.current_source_name = "Тестові дані"
        self.file_label.config(text=f"Джерело: {self.current_source_name}")

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

    # --- Логіка вбудованого керування мишею ---

    def _setup_mouse_navigation(self, canvas, fig, ax):
        """Підключає події миші для панорамування, зумування та скидання масштабу."""
        
        # 1. Зум коліщатком миші
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

        # 2. Перетягування графа (Панорама)
        def on_press(event):
            if event.button == 1 and event.inaxes == ax:  # Ліва кнопка миші
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

        # 3. Скидання вигляду за подвійним кліком
        # Зберігаємо початкові межі осей для скидання
        initial_xlim = ax.get_xlim()
        initial_ylim = ax.get_ylim()

        def on_double_click(event):
            if event.dblclick and event.button == 1:
                ax.set_xlim(initial_xlim)
                ax.set_ylim(initial_ylim)
                canvas.draw_idle()

        # Зв'язуємо події Matplotlib з обробниками
        fig.canvas.mpl_connect('scroll_event', on_scroll)
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('button_press_event', on_double_click)

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

        # Результати
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Джерело: {self.current_source_name}\n")
        self.result_text.insert(tk.END, f"Позначки h_i:\n")
        for node in sorted(h.keys()):
            self.result_text.insert(tk.END, f"  h_{node} = {h[node]}\n")

        self.result_text.insert(tk.END, f"\nНайкоротші дуги:\n")
        for u, v in shortest_edges:
            self.result_text.insert(tk.END, f"  {u} -> {v}\n")
        self.result_text.config(state=tk.DISABLED)

        # Очищення полотна
        if self.canvas_widget:
            self.canvas_widget.destroy()

        chart_title = f"Розв'язок (початок з в. {start_node}) | Файл: {self.current_source_name}"
        fig = build_figure(edges, h, shortest_edges, title=chart_title)
        ax = fig.gca()

        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        self._setup_mouse_navigation(canvas, fig, ax)

        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()


def run_app():
    app = App()
    app.mainloop()
import sys
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.ford_fulkerson import solve_ford_fulkerson, add_super_nodes
from visualization.graph_drawer import build_flow_figure, compute_layout
from utils.file_parser import parse_edges_from_file, save_edges_to_file, save_results_to_file
from utils.helpers import resource_path
from ui.about_dialog import AboutDialog
from ui.guide_dialog import GuideDialog

APP_TITLE = "Ford-Fulkerson Flow Solver"
ALGORITHM_NAME = "Алгоритм Форда-Фалкерсона"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x700")

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

        # Результат останнього обчислення (для перемальовування та звіту)
        self.last_flow_result = None

        self._setup_ui()

    # ------------------------------------------------------------------
    #  Інтерфейс
    # ------------------------------------------------------------------
    def _setup_ui(self):
        left_frame = ttk.Frame(self, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        nodes_subframe = ttk.Frame(input_frame)
        nodes_subframe.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))

        ttk.Label(nodes_subframe, text="Джерело:").pack(anchor=tk.W)
        self.source_entry = ttk.Entry(nodes_subframe, width=8)
        self.source_entry.pack(anchor=tk.W, pady=(2, 0))

        ttk.Label(nodes_subframe, text="Стік (витік):").pack(anchor=tk.W, pady=(4, 0))
        self.sink_entry = ttk.Entry(nodes_subframe, width=8)
        self.sink_entry.pack(anchor=tk.W, pady=(2, 0))

        action_btn_frame = ttk.Frame(input_frame)
        action_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(action_btn_frame, text="Завантажити з файлу", command=self.load_from_file).pack(fill=tk.X, pady=1)
        ttk.Button(action_btn_frame, text="Розрахувати", command=self.calculate).pack(fill=tk.X, pady=1)

        ttk.Button(left_frame, text="Зберегти мережу", command=self.save_to_file).pack(fill=tk.X, pady=1)
        ttk.Button(left_frame, text="Зберегти результати", command=self.save_results).pack(fill=tk.X, pady=1)

        ttk.Label(left_frame, text="Дуги (звідки куди пропускна_здатність):").pack(anchor=tk.W, pady=(5, 0))
        self.edges_text = tk.Text(left_frame, width=32, height=9)
        self.edges_text.pack(pady=(0, 5))

        self.file_label = ttk.Label(left_frame, text="Джерело даних: —", font=("Arial", 8, "italic"), foreground="gray")
        self.file_label.pack(anchor=tk.W, pady=(0, 5))

        view_frame = ttk.LabelFrame(left_frame, text=" Налаштування відображення ", padding=5)
        view_frame.pack(fill=tk.X, pady=(0, 10))

        self.show_cut_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            view_frame,
            text="Мінімальний переріз (червоні дуги)",
            variable=self.show_cut_var,
            command=self.draw_flow_display
        ).pack(anchor=tk.W, pady=1)

        bottom_btn_frame = ttk.Frame(left_frame)
        bottom_btn_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(bottom_btn_frame, text="Інструкція", command=self.show_guide_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(bottom_btn_frame, text="Про програму", command=self.show_about_dialog).pack(fill=tk.X, pady=2)

        ttk.Label(left_frame, text="Результати:").pack(anchor=tk.W, pady=(5, 0))

        result_frame = ttk.Frame(left_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, width=32, height=5, wrap=tk.NONE, state=tk.DISABLED)
        v_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        h_scrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        self.result_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    #  Діалоги, вихід
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    #  Дані: приклад, файли
    # ------------------------------------------------------------------
    def _set_source_name(self, name):
        self.current_source_name = name
        self.file_label.config(text=f"Джерело даних: {name}")

    def load_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Оберіть файл із даними мережі",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            filename, edges = parse_edges_from_file(filepath)
            self.edges_text.delete("1.0", tk.END)
            self.edges_text.insert("1.0", "\n".join(f"{u} {v} {c}" for u, v, c in edges))
            self._set_source_name(filename)

            # Підказка для полів: джерело - найменша вершина, стік - найбільша
            nodes = {n for u, v, _ in edges for n in (u, v)}
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, str(min(nodes)))
            self.sink_entry.delete(0, tk.END)
            self.sink_entry.insert(0, str(max(nodes)))

            messagebox.showinfo("Успіх", f"Дані з файлу '{filename}' успішно завантажено!\n"
                                         f"Джерело й стік підставлено автоматично "
                                         f"({min(nodes)} і {max(nodes)}), за потреби змініть.")
        except Exception as e:
            messagebox.showerror("Помилка файлу", str(e))

    def _read_edges(self):
        """Читає дуги з текстового поля. Повертає список або None (після показу помилки)."""
        edges = []
        for line_num, line in enumerate(self.edges_text.get("1.0", tk.END).strip().split("\n"), 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                messagebox.showerror(
                    "Помилка",
                    f"Рядок {line_num}: некоректний формат '{line}'.\n"
                    f"Формат: звідки куди пропускна_здатність")
                return None
            try:
                u, v = int(parts[0]), int(parts[1])
                c = float(parts[2])
            except ValueError:
                messagebox.showerror("Помилка", f"Рядок {line_num}: некоректні значення '{line}'")
                return None
            if c.is_integer():
                c = int(c)
            edges.append((u, v, c))
        if not edges:
            messagebox.showerror("Помилка", "Введіть або завантажте хоча б одну дугу!")
            return None
        return edges

    def save_to_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Зберегти дані мережі",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            edges = self._read_edges()
            if edges is None:
                return
            filename = save_edges_to_file(filepath, edges)
            self._set_source_name(filename)
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
            filename = save_results_to_file(
                filepath=filepath,
                source_name=self.current_source_name or "Введено вручну",
                algorithm_name=ALGORITHM_NAME,
                results_data=results_text
            )
            messagebox.showinfo("Успіх", f"Результати успішно збережено у файл '{filename}'!")
        except Exception as e:
            messagebox.showerror("Помилка збереження", f"Не вдалося зберегти результати:\n{str(e)}")

    # ------------------------------------------------------------------
    #  Обчислення
    # ------------------------------------------------------------------
    def calculate(self):
        self.last_algorithm_name = "Алгоритм Форда-Фалкерсона"
        try:
            sources = [int(t) for t in self.source_entry.get().replace(",", " ").split()]
            sinks = [int(t) for t in self.sink_entry.get().replace(",", " ").split()]
        except ValueError:
            messagebox.showerror("Помилка", "Джерела і стоки мають бути цілими числами (через кому або пропуск)!")
            return
        if not sources or not sinks:
            messagebox.showerror("Помилка", "Вкажіть хоча б одне джерело і хоча б один стік!")
            return

        edges = []
        for line in self.edges_text.get("1.0", tk.END).strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 3:
                messagebox.showerror("Помилка", f"Некоректний рядок дуги: '{line}'\nФормат: звідки куди пропускна_здатність")
                return
            try:
                u, v = int(parts[0]), int(parts[1])
                c = float(parts[2])
                if c.is_integer():
                    c = int(c)
                edges.append((u, v, c))
            except ValueError:
                messagebox.showerror("Помилка", f"Некоректні значення в рядку: '{line}'")
                return

        if not edges:
            messagebox.showerror("Помилка", "Введіть або завантажте хоча б одну дугу!")
            return

        real_edges = edges
        try:
            # кілька джерел/стоків -> додаємо фіктивні S і T (якщо по одному - нічого не змінюється)
            edges, source, sink, fake = add_super_nodes(real_edges, sources, sinks)
            result = solve_ford_fulkerson(edges, source, sink)
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return

        pos, crossings, is_planar = compute_layout(edges, source, sink)

        self.last_flow_result = {
            "edges": edges, "source": source, "sink": sink, "result": result,
            "pos": pos, "crossings": crossings, "is_planar": is_planar,
            "sources": sources, "sinks": sinks, "fake": fake,
        }
        self._update_flow_report()
        self.draw_flow_display()

    @staticmethod
    def _fmt_num(x):
        return int(x) if float(x).is_integer() else round(x, 4)

    def _update_flow_report(self):
        data = self.last_flow_result
        if not data:
            return
        edges, source, sink, res = data["edges"], data["source"], data["sink"], data["result"]
        f = self._fmt_num

        report = []
        report.append("=== РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ (ФОРД-ФАЛКЕРСОН) ===")
        report.append(f"Джерело даних: {self.current_source_name or 'Введено вручну'}")
        fake = data["fake"]
        report.append(f"Джерела: {', '.join(map(str, data['sources']))} | "
                      f"Стоки: {', '.join(map(str, data['sinks']))}")
        if fake:
            report.append(f"(службові вершини: S = {source}, T = {sink}; дуги до них мають r = ∞)")
        report.append(f"МАКСИМАЛЬНИЙ ПОТІК: {f(res['max_flow'])}\n")

        report.append("--- ПОТІК ПО ДУГАХ (x_ij / r_ij) ---")
        for (u, v, c), x in zip(edges, res["flow"]):
            if u in fake or v in fake:          # службові дуги показуємо окремо нижче
                continue
            mark = "  (насичена)" if x == c and c > 0 else ""
            report.append(f"  {u}-{v}: {f(x)} / {f(c)}{mark}")

        report.append("\n--- МІНІМАЛЬНИЙ ПЕРЕРІЗ ---")
        report.append(f"I* = {{{', '.join(map(str, sorted(res['I_star'] - fake)))}}}")
        cut = ", ".join(f"({u},{v})" for u, v, _ in res["cut_edges"]) or "(порожній)"
        report.append(f"Дуги перерізу: {{{cut}}}")
        cut_terms = " + ".join(str(f(c)) for _, _, c in res["cut_edges"]) or "0"
        report.append(f"Пропускна здатність: {cut_terms} = {f(res['cut_capacity'])}")
        report.append("Збігається з максимальним потоком (теорема Форда-Фалкерсона)."
                      if res["cut_capacity"] == res["max_flow"] else "УВАГА: переріз не збігається з потоком!")

        if fake:
            report.append("\n--- ПОТІК ЧЕРЕЗ ДЖЕРЕЛА І СТОКИ ---")
            for (u, v, _), x in zip(edges, res["flow"]):
                if u == source:
                    report.append(f"  джерело {v} віддає: {f(x)}")
            for (u, v, _), x in zip(edges, res["flow"]):
                if v == sink:
                    report.append(f"  стік {u} приймає: {f(x)}")

        report.append("\n--- МАЛЮНОК ---")
        if data["crossings"] == 0:
            report.append("Перетинів дуг немає.")
        elif data["is_planar"]:
            report.append(f"Перетинів дуг: {data['crossings']}.")
        else:
            report.append(f"Перетинів дуг: {data['crossings']}. Мережа непланарна "
                          f"(містить K5 або K3,3), тому повністю уникнути\n"
                          f"перетинів неможливо; вершини розташовано з мінімумом перетинів.")

        report.append("\n--- ХІД РОЗВ'ЯЗАННЯ (ІТЕРАЦІЇ) ---")
        iters = res["iterations"]
        for k, it in enumerate(iters, 1):
            labels = ", ".join(
                f"{n}(0,∞)" if n == source else f"{n}({f_n},{f(th)})"
                for n, (f_n, th) in it["labels"].items()
            )
            report.append(f"Ітерація {k}. Позначки: {labels}")
            if it["path"]:
                path = " -> ".join(map(str, it["path"]))
                report.append(f"  Ланцюг: {path}; θ = {f(it['theta'])}; потік = {f(it['value_after'])}")
            else:
                report.append(f"  Стік не позначено - потік максимальний ({f(it['value_after'])}).")

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "\n".join(report))
        self.result_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    #  Малювання та навігація мишею
    # ------------------------------------------------------------------
    def draw_flow_display(self):
        data = self.last_flow_result
        if not data:
            return
        res = data["result"]

        if self.canvas_widget:
            self.canvas_widget.destroy()
        plt.close('all')

        title = (f"Максимальний потік = {self._fmt_num(res['max_flow'])} "
                 f"(джерела {', '.join(map(str, data['sources']))}, "
                 f"стоки {', '.join(map(str, data['sinks']))}) | Файл: {self.current_source_name}")
        fig = build_flow_figure(
            edges=data["edges"], flow=res["flow"],
            source=data["source"], sink=data["sink"],
            I_star=res["I_star"], cut_edges=res["cut_edges"],
            pos=data["pos"], title=title, show_cut=self.show_cut_var.get(),
            fake_nodes=data["fake"]
        )
        ax = fig.gca()

        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        self._setup_mouse_navigation(canvas, fig, ax)

        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

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


def run_app():
    app = App()
    app.mainloop()

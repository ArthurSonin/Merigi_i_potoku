import tkinter as tk
from tkinter import ttk


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Про програму")
        self.geometry("420x340")
        self.resizable(False, False)

        # Робимо вікно модальним (блокує головне вікно до закриття)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок програми
        title_label = ttk.Label(
            frame, 
            text="Minty Graph Solver", 
            font=("Arial", 12, "bold"),
            wraplength=380,
            justify=tk.CENTER
        )
        title_label.pack(pady=(0, 2))

        # Версія
        version_label = ttk.Label(
            frame,
            text="Версія: 0.4",
            font=("Arial", 9, "bold"),
            foreground="gray"
        )
        version_label.pack(pady=(0, 10))

        # Основний опис
        desc_text = (
            "Програма розроблена в рамках курсового проєкту студентом 3 курсу "
            "групи 341А Чернівецького національного університету імені Юрія Федьковича "
            "Соніним А. І.\n"
            "Науковий керівник: викладач Руснак М. А.\n\n"
            "Призначення: знаходження найкоротших шляхів у зваженому орієнтованому графі "
            "за допомогою алгоритму Мінті, а також автоматична побудова та візуалізація "
            "його планарного представлення."
        )
        desc_label = ttk.Label(
            frame, 
            text=desc_text, 
            wraplength=380, 
            justify=tk.LEFT,
            font=("Arial", 9)
        )
        desc_label.pack(pady=(0, 15))

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))

        # Кнопка закриття
        close_btn = ttk.Button(frame, text="Закрити", command=self.destroy)
        close_btn.pack(side=tk.BOTTOM)
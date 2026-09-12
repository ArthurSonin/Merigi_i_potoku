import tkinter as tk
from tkinter import ttk


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Про програму")
        self.geometry("380x260")
        self.resizable(False, False)

        # Робимо вікно модальним (блокує головне вікно до закриття)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(
            frame, 
            text="Метод Мінті — Пошук найкоротших шляхів", 
            font=("Arial", 10, "bold"),
            wraplength=340,
            justify=tk.CENTER
        )
        title_label.pack(pady=(0, 10))

        # Опис додатку
        desc_text = (
            "Програма призначена для розрахунку найкоротших шляхів у зваженому "
            "орієнтованому графі за допомогою алгоритму Мінті, а також для "
            "автоматичної побудови та візуалізації планарного графа."
        )
        desc_label = ttk.Label(frame, text=desc_text, wraplength=340, justify=tk.LEFT)
        desc_label.pack(pady=(0, 15))

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))

        # Інформація про автора
        author_info = (
            "Розробник: Студент 3 курсу\n"
            "Зв'язок: email@example.com | Telegram: @username"
        )
        author_label = ttk.Label(
            frame, 
            text=author_info, 
            font=("Arial", 9, "italic"), 
            justify=tk.LEFT
        )
        author_label.pack(anchor=tk.W, pady=(0, 15))

        # Кнопка закриття
        close_btn = ttk.Button(frame, text="Закрити", command=self.destroy)
        close_btn.pack()
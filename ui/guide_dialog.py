import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GuideDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Інструкція користувача")
        self.geometry("800x650")
        self.minsize(600, 500)

        # Список сторінок гайду: (шлях_до_картинки, текст_пояснення)
        self.pages = [
            (
                "assets/g1.png",
                "Крок 1: Завантаження даних\n"
                "Натискаючи на цю кнопку, ви можете завантажити дані про граф з текстового файлу."
            ),
            (
                "assets/g2.png",
                "Крок 2: Розрахунок\n"
                "Натискаючи на цю кнопку, ви можете розрахувати найкоротші шляхи у графі."
            ),
            (
                "assets/g8.png",
                "Крок 3: Візуалізація\n"
                "Після натискання кнопки 'Розрахувати', на полотні з'явиться візуалізація графа з найкоротшими шляхами, які будуть виділені червоним кольором. Граф можна переміщувати, натискаючи та утримуючи ліву кнопку миші, а також масштабувати за допомогою коліщатка миші."
            ),
            (
                "assets/g3.png",
                "Крок 4: Точка старту\n"
                "Тут ви можете вказати початкову вершину від якої буде розраховуватися найкоротший шлях до всіх інших вершин."
            ),
            (
                "assets/g4.png",
                "Крок 5: Дані, введені вами\n"
                "Тут відображаються дані про граф, які були завантажені з файлу. Також дані можна вводити вручну. Дані повинні бути у такому форматі: 'звідки куди вага', де 'звідки' та 'куди' - це назви вершин, а 'вага' - числове значення ваги ребра між цими вершинами, інакше кажучи ціна пересуваня по цій дузі."
            ),
            (
                "assets/g5.png",
                "Крок 6: Про програму\n"
                "Натискаючи на цю кнопку, ви можете отримати інформацію про програму."
            ),
            (
                "assets/g6.png",
                "Крок 7: Звідки взяті дані\n"
                "Тут відображається джерело даних, які були завантажені з файлу."
            ),
            (
                "assets/g7.png",
                "Крок 8: Вивід результатів\n"
                "Тут відображаються результати розрахунків найкоротших шляхів у графі."
            )
        ]

        self.current_page = 0
        self.photo_img = None  # Посилання для запобігання GC у Python

        self._setup_ui()
        self._show_page(0)

        # Робимо вікно модальним
        self.transient(parent)
        self.grab_set()

    def _setup_ui(self):
        # Верхня панель із зображенням
        self.img_label = ttk.Label(self, anchor="center")
        self.img_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Текстовий блок пояснення
        self.text_label = ttk.Label(
            self, 
            wraplength=750, 
            justify=tk.LEFT, 
            font=("Arial", 10)
        )
        self.text_label.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Нижній блок керування (кнопки та лічильник)
        controls_frame = ttk.Frame(self, padding=10)
        controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.prev_btn = ttk.Button(controls_frame, text="← Назад", command=self._prev_page)
        self.prev_btn.pack(side=tk.LEFT)

        self.page_counter_label = ttk.Label(controls_frame, text="", font=("Arial", 9, "bold"))
        self.page_counter_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = ttk.Button(controls_frame, text="Вперед →", command=self._next_page)
        self.next_btn.pack(side=tk.RIGHT)

        # Оновлення зображення при зміні розміру вікна
        self.bind("<Configure>", self._on_resize)

    def _show_page(self, page_index):
        self.current_page = page_index
        img_path, text_content = self.pages[page_index]

        self.text_label.config(text=text_content)
        self.page_counter_label.config(text=f"{page_index + 1} / {len(self.pages)}")

        # Оновлюємо стан кнопок
        self.prev_btn.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if page_index < len(self.pages) - 1 else tk.DISABLED)

        # Завантажуємо та малюємо скріншот
        self._load_and_display_image(img_path)

    def _load_and_display_image(self, img_path):
        if not os.path.exists(img_path):
            self.img_label.config(text=f"[ Зображення не знайдено: {img_path} ]", image="")
            return

        # Отримуємо доступний розмір під картинку
        max_w = max(self.img_label.winfo_width(), 400)
        max_h = max(self.img_label.winfo_height(), 300)

        img = Image.open(img_path)
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        self.photo_img = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.photo_img, text="")

    def _on_resize(self, event):
        # Перемальовуємо зображення під новий розмір вікна лише якщо це resize самого Toplevel
        if event.widget == self:
            img_path, _ = self.pages[self.current_page]
            self._load_and_display_image(img_path)

    def _prev_page(self):
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)
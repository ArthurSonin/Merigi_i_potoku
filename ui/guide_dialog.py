import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.helpers import resource_path

class GuideDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Інструкція користувача")
        self.geometry("800x700")
        self.minsize(600, 500)

        # Сторінки інструкції: (шлях_до_картинки або None, текст_пояснення)
        self.pages = [
            (
                resource_path("assets/f1.png"),
                "Крок 1: Завантаження даних\n"
                "Натискаючи на цю кнопку, ви можете завантажити дані про мережу з текстового файлу."
            ),
            (
                resource_path("assets/f2.png"),
                "Крок 2: Джерело і стік\n"
                "Тут ви вказуєте номер вершини-джерела (звідки йде потік) та номер вершини-стоку (куди потік іде). Це мають бути різні вершини, які присутні в мережі. Джерел і стоків може бути декілька."
            ),
            (
                resource_path("assets/f3.png"),
                "Крок 3: Розрахунок\n"
                "Натискаючи на цю кнопку, ви запускаєте алгоритм Форда-Фалкерсона: програма знаходить максимальний потік і мінімальний переріз мережі."
            ),
            (
                resource_path("assets/f4.png"),
                "Крок 4: Візуалізація\n"
                "Після розрахунку на полотні з'являється мережа. Підпис на кожній дузі має вигляд 'потік/пропускна здатність'. Сині дуги – дуги з ненульовим потоком, сірі – порожні, червоні – дуги мінімального перерізу. Зелені вершини – множина I*, блакитні – решта. Джерело й стік обведені жирною рамкою. Вершини розташовані так, щоб дуги перетиналися якомога менше (для планарних мереж перетинів немає). Мережу можна переміщувати, утримуючи ліву кнопку миші, та масштабувати коліщатком."
            ),
            (
                resource_path("assets/f5.png"),
                "Крок 5: Збереження мережі\n"
                "Тут ви можете зберегти створену/модифіковану вами мережу у файл."
            ),
            (
                resource_path("assets/f6.png"),
                "Крок 6: Збереження результатів\n"
                "Тут ви можете зберегти результати обчислень (максимальний потік, переріз, хід розв'язання) у файл."
            ),
            (
                resource_path("assets/f7.png"),
                "Крок 7: Дані, введені вами\n"
                "Тут відображаються дані про мережу, завантажені з файлу. Також дані можна вводити вручну у такому форматі: 'звідки куди пропускна_здатність', де 'звідки' та 'куди' – номери вершин, а 'пропускна_здатність' – найбільший потік, який може пройти по цій дузі. Наприклад: 1 2 4."
            ),
            (
                resource_path("assets/f8.png"),
                "Крок 8: Звідки взяті дані\n"
                "Тут відображається джерело даних, з якого були завантажені дані."
            ),
            (
                resource_path("assets/f9.png"),
                "Крок 9: Мінімальний переріз\n"
                "Коли галочка горить, дуги мінімального перерізу виділені червоним. Це дуги, що ведуть із зелених вершин (множини I*) назовні; їхня сумарна пропускна здатність дорівнює максимальному потоку. Коли галочка не горить, червоне виділення зникає."
            ),
            (
                resource_path("assets/f10.png"),
                "Крок 10: Інструкція\n"
                "Це вікно, в якому ви зараз знаходитеся і читаєте, як користуватись програмою."
            ),
            (
                resource_path("assets/f11.png"),
                "Крок 11: Про програму\n"
                "Натискаючи на цю кнопку, ви можете отримати інформацію про програму."
            ),
            (
                resource_path("assets/f12.png"),
                "Крок 12: Вивід результатів\n"
                "Тут відображаються результати обчислення: максимальний потік; потік по кожній дузі у форматі 'потік / пропускна здатність' (насичені дуги позначені); множина I* та дуги мінімального перерізу з сумою їх пропускних здатностей; кількість перетинів дуг на малюнку; а також покроковий хід розв'язання. У ході розв'язання для кожної ітерації показані позначки вершин у форматі 'вершина(N, θ)', знайдений ланцюг від джерела до стоку та значення потоку після ітерації. Останній рядок 'Стік не позначено' означає, що алгоритм завершено і потік максимальний."
            ),
        ]

        self.current_page = 0
        self.photo_img = None  # Посилання для запобігання Garbage Collector у Python

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
        if img_path is None:
            self.img_label.config(image="", text="")
            self.photo_img = None
            return

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
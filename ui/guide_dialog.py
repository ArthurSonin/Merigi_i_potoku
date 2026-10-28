import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.helpers import resource_path

class GuideDialog(tk.Toplevel):
    def __init__(self, parent, mode="minty"):
        super().__init__(parent)
        self.title("Інструкція користувача")
        self.geometry("800x700")
        self.minsize(600, 500)

        # Список сторінок гайду: (шлях_до_картинки, текст_пояснення)
        minty_pages = [
            (
                resource_path("assets/minti/i0.png"),
                "Крок 1: Вибір алгоритму\n"
                "У цьому списку ви обираєте метод. Для знаходження максимального потоку оберіть 'Форд-Фалкерсон (максимальний потік)'."
            ),
            (
                resource_path("assets/minti/i1.png"),
                "Крок 2: Завантаження даних\n"
                "Натискаючи на цю кнопку, ви можете завантажити дані про граф з текстового файлу."
            ),
            (
                resource_path("assets/minti/i2.png"),
                "Крок 3: Розрахунок\n"
                "Натискаючи на цю кнопку, ви можете розрахувати найкоротші шляхи у графі."
            ),
            (
                resource_path("assets/minti/i3.png"),
                "Крок 4: Візуалізація\n"
                "Після натискання кнопки 'Розрахувати' на полотні з'явиться візуалізація графа з найкоротшими шляхами, які будуть виділені червоним, синім та фіолетовим кольорами залежно від бажань користувача. Граф можна переміщувати, натискаючи та утримуючи ліву кнопку миші, а також масштабувати за допомогою коліщатка миші."
            ),
            (
                resource_path("assets/minti/i4.png"),
                "Крок 5: Точка старту\n"
                "Тут ви можете вказати початкову вершину, від якої буде розраховуватися найкоротший шлях до всіх інших вершин."
            ),
            (
                resource_path("assets/minti/i5.png"),
                "Крок 6: Збереження графа\n"
                "Тут ви можете зберегти створений/модифікований вами граф."
            ), 
            (
                resource_path("assets/minti/i6.png"),
                "Крок 7: Збереження результатів\n"
                "Тут ви можете зберегти результати, отримані під час роботи з графом."
            ),                        
            (
                resource_path("assets/minti/i7.png"),
                "Крок 8: Дані, введені вами\n"
                "Тут відображаються дані про граф, які були завантажені з файлу. Також дані можна вводити вручну. Дані повинні бути у такому форматі: 'звідки куди вага', де 'звідки' та 'куди' – це назви вершин, а 'вага' – числове значення ваги ребра між цими вершинами, інакше кажучи, ціна пересування по цій дузі."
            ),
            (
                resource_path("assets/minti/i8.png"),
                "Крок 9: Звідки взяті дані\n"
                "Тут відображається джерело даних, які були завантажені з файлу."
            ),
            (
                resource_path("assets/minti/i9.png"),
                "Крок 10: Усі найкоротші шляхи\n"
                "Коли галочка горить, на малюнку червоним кольором відображаються всі найкоротші шляхи до кожної вершини графа. Коли галочка не горить, всі найкоротші шляхи перестають відображатися (дуги стають сірими), це потрібно для того, щоб при великих розмірах графа було чітко видно шлях до потрібної користувачу вершини."
            ),
            (
                resource_path("assets/minti/i10.png"),
                "Крок 11: Найкоротший серед усіх\n"
                "Коли галочка горить, на малюнку синім кольором перший найкоротший шлях відносно точки старту."
            ),    
            (
                resource_path("assets/minti/i11.png"),
                "Крок 12: Цільова вершина\n"
                "Тут ви можете вказати цільову вершину, шлях до якої буде виділений фіолетовим кольором."
            ),    
            (
                resource_path("assets/minti/i12.png"),
                "Крок 13: Інструкція\n"
                "Це вікно, в якому ви зараз знаходитеся і читаєте, як користуватись програмою. Його вміст залежить від вибраного алгоритму."
            ),                                                               
            (
                resource_path("assets/minti/i13.png"),
                "Крок 14: Про програму\n"
                "Натискаючи на цю кнопку, ви можете отримати інформацію про програму."
            ),
            (
                resource_path("assets/minti/i14.png"),
                "Крок 15: Вивід результатів\n"
                "Тут відображаються результати, утворені після обчислення та аналізу графа програмою."
            )
        ]

        flow_pages = [
            (
                resource_path("assets/fulkerson/f0.png"),
                "Крок 1: Вибір алгоритму\n"
                "У цьому списку ви обираєте метод. Для знаходження найкоротших шляхів оберіть 'Мінті (найкоротші шляхи)'."
            ),
            (
                resource_path("assets/fulkerson/f1.png"),
                "Крок 2: Завантаження даних\n"
                "Натискаючи на цю кнопку, ви можете завантажити дані про мережу з текстового файлу."
            ),
            (
                resource_path("assets/fulkerson/f2.png"),
                "Крок 3: Джерело і стік\n"
                "Тут ви вказуєте номер вершини-джерела (звідки йде потік) та номер вершини-стоку (куди потік іде). Це мають бути різні вершини, які присутні в мережі."
            ),
            (
                resource_path("assets/fulkerson/f3.png"),
                "Крок 4: Розрахунок\n"
                "Натискаючи на цю кнопку, ви запускаєте алгоритм Форда-Фалкерсона: програма знаходить максимальний потік і мінімальний переріз мережі."
            ),
            (
                resource_path("assets/fulkerson/f4.png"),
                "Крок 5: Візуалізація\n"
                "Після розрахунку на полотні з'являється мережа. Підпис на кожній дузі має вигляд 'потік/пропускна здатність'. Сині дуги – дуги з ненульовим потоком, сірі – порожні, червоні – дуги мінімального перерізу. Зелені вершини – множина I*, блакитні – решта. Джерело й стік обведені жирною рамкою. Вершини розташовані так, щоб дуги перетиналися якомога менше (для планарних мереж перетинів немає). Мережу можна переміщувати, утримуючи ліву кнопку миші, та масштабувати коліщатком."
            ),
            (
                resource_path("assets/fulkerson/f5.png"),
                "Крок 6: Збереження мережі\n"
                "Тут ви можете зберегти створену/модифіковану вами мережу у файл."
            ),
            (
                resource_path("assets/fulkerson/f6.png"),
                "Крок 7: Збереження результатів\n"
                "Тут ви можете зберегти результати обчислень (максимальний потік, переріз, хід розв'язання) у файл."
            ),
            (
                resource_path("assets/fulkerson/f7.png"),
                "Крок 8: Дані, введені вами\n"
                "Тут відображаються дані про мережу, завантажені з файлу. Також дані можна вводити вручну у такому форматі: 'звідки куди пропускна_здатність', де 'звідки' та 'куди' – номери вершин, а 'пропускна_здатність' – найбільший потік, який може пройти по цій дузі. Наприклад: 1 2 4."
            ),
            (
                resource_path("assets/fulkerson/f8.png"),
                "Крок 9: Звідки взяті дані\n"
                "Тут відображається джерело даних, які були завантажені з файлу."
            ),
            (
                resource_path("assets/fulkerson/f9.png"),
                "Крок 10: Мінімальний переріз\n"
                "Коли галочка горить, дуги мінімального перерізу виділені червоним. Це дуги, що ведуть із зелених вершин (множини I*) назовні; їхня сумарна пропускна здатність дорівнює максимальному потоку. Коли галочка не горить, червоне виділення зникає."
            ),
            (
                resource_path("assets/fulkerson/f10.png"),
                "Крок 11: Інструкція\n"
                "Це вікно, в якому ви зараз знаходитеся і читаєте, як користуватись програмою. Його вміст залежить від вибраного алгоритму."
            ),
            (
                resource_path("assets/fulkerson/f11.png"),
                "Крок 12: Про програму\n"
                "Натискаючи на цю кнопку, ви можете отримати інформацію про програму."
            ),
            (
                resource_path("assets/fulkerson/f12.png"),
                "Крок 13: Вивід результатів\n"
                "Тут відображаються результати обчислення: максимальний потік; потік по кожній дузі у форматі 'потік / пропускна здатність' (насичені дуги позначені); множина I* та дуги мінімального перерізу з сумою їх пропускних здатностей; кількість перетинів дуг на малюнку; а також покроковий хід розв'язання. У ході розв'язання для кожної ітерації показані позначки вершин у форматі 'вершина(N, θ)', знайдений ланцюг від джерела до стоку та значення потоку після ітерації. Останній рядок 'Стік не позначено' означає, що алгоритм завершено і потік максимальний."
            ),
        ]

        self.pages = flow_pages if mode == "flow" else minty_pages
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
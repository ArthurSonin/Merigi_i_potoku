import sys
import os

def resource_path(relative_path):
    """
    Повертає абсолютний шлях до ресурсу.
    Працює як під час розробки, так і після збірки в .exe (PyInstaller).
    """
    try:
        # Якщо програма зібрана в .exe, PyInstaller створює тимчасову папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
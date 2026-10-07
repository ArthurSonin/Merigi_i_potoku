from ui.gui import run_app

if __name__ == "__main__":
    run_app()

# pyinstaller --noconfirm --onefile --windowed --add-data "assets;assets" --icon="assets/icon.png" main.py Команда для створення виконуваного файлу з іконкою та ресурсами.
# pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --icon="assets/icon.png" --name "Minty Graph Solver" main.py
# pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --icon="assets/icon.png" --name "Minty Graph Solver" main.py - правильна команда

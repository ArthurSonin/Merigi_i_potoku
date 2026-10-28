from ui.gui import run_app

if __name__ == "__main__":
    run_app()

# Збірка виконуваного файлу:
# pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --icon="assets/icon.png" --name "Ford-Fulkerson Flow Solver" main.py

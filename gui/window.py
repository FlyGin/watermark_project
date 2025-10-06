import sys
import os
# Добавляем корневую папку проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.layout import create_main_layout
from gui.events import connect_events

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark Project")
        self.setCentralWidget(create_main_layout(self))
        connect_events(self)

def run():
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
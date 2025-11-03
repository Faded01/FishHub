import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

from gui.main_window import MainWindow
from core.database import DatabaseManager


def load_styles():
    """Загрузка стилей аналогично fullflash"""
    try:
        with open('data/styles.qss', 'r') as f:
            return f.read()
    except:
        return ""


def main():
    app = QApplication(sys.argv)

    # Загрузка стилей
    stylesheet = load_styles()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Инициализация БД
    db_manager = DatabaseManager()
    db_manager.init_database()

    # Создание главного окна
    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
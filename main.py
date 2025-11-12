import sys
from PyQt6.QtWidgets import QApplication
from core.database import DatabaseManager
from gui.login_window import LoginWindow
import traceback
from pathlib import Path
import os

def ensure_backup_styles():
    """Создает резервный файл стилей если его нет"""
    backup_path = Path('data/backup_styles.qss')

    if not backup_path.exists():
        # Создаем директорию если нет
        backup_path.parent.mkdir(exist_ok=True)

        # Создаем резервный файл
        fallback_styles = get_fallback_styles()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(fallback_styles)
        print("✅ Резервный файл стилей создан")

    return backup_path


def load_styles():
    """Улучшенная загрузка с автоматическим созданием резерва"""
    # Сначала убедимся что резервный файл есть
    ensure_backup_styles()

    paths_to_try = [
        'data/light_theme.qss',  # Основной
        'data/backup_styles.qss',  # Резервный файл
    ]

    for style_path in paths_to_try:
        try:
            with open(style_path, 'r', encoding='utf-8') as file:
                styles = file.read()
                print(f"[CSS] Стили загружены из: {style_path}")
                return styles
        except Exception as e:
            print(f"[CSS] Не удалось загрузить {style_path}: {e}")
            continue

    # Если все файлы недоступны - используем встроенные
    print("Все файлы стилей недоступны, используем встроенные стили")
    return get_fallback_styles()

def excepthook(exc_type, exc_value, exc_tb):
    """Глобальный обработчик исключений"""
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Критическая ошибка: {tb}")
    sys.exit(1)

sys.excepthook = excepthook


def get_fallback_styles():
    """Встроенные резервные стили"""
    return """

    /* Главное окно */
    QMainWindow {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                   stop: 0 #2c3e50, stop: 1 #34495e);
    }

    /* Карточки */
    #card {
        background-color: white;
        border-radius: 10px;
        padding: 25px;
        border: 1px solid #bdc3c7;
        margin: 10px;
    }

    /* Заголовки */
    #titleLabel, #widgetTitle, #dialogTitle {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        padding: 10px 0px;
    }

    #subtitleLabel {
        font-size: 14px;
        color: #7f8c8d;
        padding: 5px 0px;
    }

    /* Поля ввода */
    QLineEdit, QTextEdit, QComboBox {
        padding: 8px 12px;
        border: 2px solid #bdc3c7;
        border-radius: 6px;
        font-size: 14px;
        background-color: white;
        margin: 5px 0px;
    }

    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border-color: #3498db;
    }

    /* Кнопки */
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px;
    }

    QPushButton:hover {
        background-color: #2980b9;
    }

    QPushButton:pressed {
        background-color: #21618c;
    }

    #loginButton {
        background-color: #27ae60;
        padding: 12px;
        font-size: 16px;
    }

    #loginButton:hover {
        background-color: #229954;
    }

    /* Таблицы */
    QTableView, QTableWidget {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        gridline-color: #ecf0f1;
        alternate-background-color: #f8f9fa;
    }

    QHeaderView::section {
        background-color: #34495e;
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }

    /* Группы */
    QGroupBox {
        font-weight: bold;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #2c3e50;
    }

    /* Вкладки */
    QTabWidget::pane {
        border: 1px solid #bdc3c7;
        border-radius: 6px;
    }

    QTabBar::tab {
        background-color: #ecf0f1;
        color: #2c3e50;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    QTabBar::tab:selected {
        background-color: #3498db;
        color: white;
    }

    /* Статус бар */
    QStatusBar {
        background-color: #2c3e50;
        color: white;
    }
    """

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FishHub")
    app.setApplicationVersion("1.0")

    styles = load_styles()
    if styles:
        app.setStyleSheet(styles)
        print("[CSS] Стили применены к приложению!")
    else:
        print("[CSS] Стили не загружены, используется стандартный вид..")

    db_manager = DatabaseManager()
    login_window = LoginWindow(db_manager)
    login_window.show()
    return app.exec()

if __name__ == "__main__":
    main()
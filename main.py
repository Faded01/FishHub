import sys
from PyQt6.QtWidgets import QApplication
from core.database import DatabaseManager
from gui.login_window import LoginWindow
import traceback
from pathlib import Path


def ensure_backup_styles():
    backup_path = Path('data/backup_styles.qss')

    if not backup_path.exists():
        backup_path.parent.mkdir(exist_ok=True)

        # Создаем резервный файл
        fallback_styles = get_fallback_styles()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(fallback_styles)
        print("[QSS] Резервный файл стилей создан")

    return backup_path


def load_styles():
    ensure_backup_styles()

    paths_to_try = [
        'data/light_theme.qss',
        'data/backup_styles.qss',
    ]

    for style_path in paths_to_try:
        try:
            with open(style_path, 'r', encoding='utf-8') as file:
                styles = file.read()
                print(f"[QSS] Стили загружены из: {style_path}")
                return styles
        except Exception as e:
            print(f"[QSS] Не удалось загрузить {style_path}: {e}")
            continue

    print("[QSS] Все файлы стилей недоступны, используем встроенные стили")
    return get_fallback_styles()

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Критическая ошибка: {tb}")
    sys.exit(1)

sys.excepthook = excepthook


def get_fallback_styles():
    return """

/* Главное окно */
QMainWindow {
    background: #e3f2fd;
}

/* Карточки */
#card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #90caf9;
}

/* Заголовки */
#titleLabel, #widgetTitle, #dialogTitle {
    font-size: 20px;
    font-weight: bold;
    color: #1565c0;
}

/* Поля ввода */
QLineEdit, QTextEdit, QComboBox {
    padding: 8px;
    border: 1px solid #90caf9;
    border-radius: 4px;
    background: white;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #1976d2;
}

/* Кнопки */
QPushButton {
    background: #2196f3;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background: #1976d2;
}

#loginButton {
    background: #4caf50;
}

#loginButton:hover {
    background: #388e3c;
}

/* Таблицы */
QTableView, QTableWidget {
    background: white;
    border: 1px solid #90caf9;
}

QHeaderView::section {
    background: #1976d2;
    color: white;
    padding: 6px;
}

/* Группы */
QGroupBox {
    border: 1px solid #90caf9;
    border-radius: 6px;
    margin-top: 8px;
}

QGroupBox::title {
    color: #1565c0;
}

/* Вкладки */
QTabBar::tab {
    background: #bbdefb;
    padding: 8px 12px;
}

QTabBar::tab:selected {
    background: #2196f3;
    color: white;
}

/* Статус бар */
QStatusBar {
    background: #1976d2;
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
        print("[QSS] Стили применены к приложению!")
    else:
        print("[QSS] Стили не загружены, используется стандартный вид..")

    db_manager = DatabaseManager()

    db_manager.create_indexes()
    login_window = LoginWindow(db_manager)
    login_window.show()
    return app.exec()

if __name__ == "__main__":
    main()
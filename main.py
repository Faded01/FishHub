import sys
from PyQt6.QtWidgets import QApplication
from core.database import DatabaseManager
from gui.login_window import LoginWindow
import traceback
from pathlib import Path


def load_styles():
    """Загрузка файла стилей с абсолютным путем"""
    try:
        # Получаем абсолютный путь к директории проекта
        project_dir = Path(__file__).parent.absolute()
        styles_path = project_dir / 'data' / 'light_theme.qss'

        print(f"[CSS] Попытка загрузить стили из: {styles_path}")  # Для отладки

        if not styles_path.exists():
            print(f"[CSS] Файл стилей не найден: {styles_path}")
            return ""

        with open(styles_path, 'r', encoding='utf-8') as file:
            styles = file.read()
            print(f"[CSS] Стили успешно загружены, размер: {len(styles)} символов")
            return styles

    except Exception as e:
        print(f"Ошибка загрузки стилей: {e}")
        return ""

def excepthook(exc_type, exc_value, exc_tb):
    """Глобальный обработчик исключений"""
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Критическая ошибка: {tb}")
    sys.exit(1)

sys.excepthook = excepthook

def main():
    """Главная функция запуска приложения"""
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("FishHub")
    app.setApplicationVersion("1.0")

    # Загружаем стили ДО создания окон
    styles = load_styles()
    if styles:
        app.setStyleSheet(styles)
        print("[CSS] Стили применены к приложению!")
    else:
        print("[CSS] Стили не загружены, используется стандартный вид..")

    # Инициализируем базу данных
    db_manager = DatabaseManager()

    # Создаем окно авторизации
    login_window = LoginWindow(db_manager)

    # Показываем окно авторизации
    login_window.show()

    # Запускаем приложение
    return app.exec()

if __name__ == "__main__":
    main()
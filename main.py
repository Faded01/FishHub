import sys
from PyQt6.QtWidgets import QApplication
from core.database import DatabaseManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
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

    # Переменная для хранения главного окна
    main_window = None

    def on_login_success(user_data):
        """Функция вызывается при успешной авторизации"""
        nonlocal main_window
        # Создаем и показываем главное окно
        main_window = MainWindow(db_manager, user_data)
        main_window.show()
        login_window.close()

    # Подключаем обработчик успешной авторизации
    login_window.login_success.connect(on_login_success)

    # Показываем окно авторизации
    login_window.show()

    # Запускаем приложение
    return app.exec()




if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка приложения: {e}")
        sys.exit(1)
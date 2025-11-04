import sys
from PyQt6.QtWidgets import QApplication
from core.database import DatabaseManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow


def load_styles():
    """Загрузка файла стилей"""
    try:
        with open('data/styles.qss', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Ошибка загрузки стилей: {e}")
        return ""


def main():
    """Главная функция запуска приложения"""
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("FishHub")

    # Загружаем стили
    styles = load_styles()
    if styles:
        app.setStyleSheet(styles)

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

    # Подключаем обработчик успешной авторизации
    login_window.login_success.connect(on_login_success)

    # Показываем окно авторизации
    login_window.show()

    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.database import DatabaseManager
from gui.main_window import MainWindow


class LoginWindow(QMainWindow):
    """Окно авторизации FishHub"""

    # Сигнал успешной авторизации
    login_success = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Авторизация | FishHub")
        self.setGeometry(600, 300, 400, 280)
        self.init_ui()

    def init_ui(self):
        """Создание интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        # Поля ввода
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопка "Показать пароль"
        self.show_password_checkbox = QCheckBox("Показать пароль")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)

        # Кнопка входа
        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.attempt_login)

        # Компоновка
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.show_password_checkbox)
        layout.addSpacing(10)
        layout.addWidget(login_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        central_widget.setLayout(layout)

    def toggle_password_visibility(self):
        """Показать/скрыть пароль"""
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def attempt_login(self):
        """Попытка авторизации"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return

        try:
            user_data = self.db_manager.check_user(username, password)
            if not user_data:
                return  # В check_user уже есть вывод ошибки

            # Если пользователь уже был "Активен" (например, не закрыл окно ранее)
            if user_data["status"] == "Активен":
                self.db_manager.update_user_status_by_id(user_data["id"], "Отключён")

            # Активируем пользователя
            self.db_manager.update_user_status_by_id(user_data["id"], "Активен")

            # Формируем полное имя для интерфейса
            full_name = f"{user_data['surname']} {user_data['name']} {user_data['patronymic']}".strip()
            user_data["full_name"] = full_name if full_name else user_data["username"]

            # Сигнал успешного входа (если нужно использовать в main.py)
            self.login_success.emit(user_data)

            # Открываем главное окно
            self.open_main_window(user_data)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при проверке пользователя:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка при входе:\n{e}")

    def open_main_window(self, user_data):
        """Открывает главное окно и скрывает окно авторизации"""
        self.main_window = MainWindow(self.db_manager, user_data)
        self.main_window.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("data/styles.qss", "r").read())
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

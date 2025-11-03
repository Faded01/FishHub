from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import hashlib


class LoginWindow(QMainWindow):
    """Окно авторизации пользователей"""

    # Сигнал успешной авторизации (отправляет данные пользователя)
    login_success = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        """Создание интерфейса окна авторизации"""
        self.setWindowTitle("FishHub - Вход в систему")
        self.setFixedSize(450, 500)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Заголовок приложения
        title_label = QLabel("🐟 FishHub")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A90A4; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Подзаголовок
        subtitle_label = QLabel("Система автоматизации рыбоводства")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #1A3A52; font-size: 13px; margin-bottom: 20px;")
        main_layout.addWidget(subtitle_label)

        # Рамка с формой входа
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #4A90A4;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Заголовок формы
        form_title = QLabel("Вход в систему")
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A3A52;")
        form_layout.addWidget(form_title)

        # Поле логина
        login_label = QLabel("Логин:")
        login_label.setStyleSheet("color: #1A3A52; font-weight: bold;")
        form_layout.addWidget(login_label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #B8D8E8;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90A4;
            }
        """)
        form_layout.addWidget(self.login_input)

        # Поле пароля
        password_label = QLabel("Пароль:")
        password_label.setStyleSheet("color: #1A3A52; font-weight: bold;")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #B8D8E8;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90A4;
            }
        """)
        # Нажатие Enter = вход
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.password_input)

        # Кнопка входа
        self.login_button = QPushButton("Войти в систему")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90A4;
                color: white;
                padding: 14px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357A8F;
            }
            QPushButton:pressed {
                background-color: #2A5F75;
            }
        """)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)

        main_layout.addWidget(form_frame)

        # Информация для первого входа
        info_label = QLabel(
            "Для первого входа используйте:\n"
            "Логин: admin\n"
            "Пароль: admin123"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            color: #1A3A52;
            font-size: 11px;
            background-color: #FFF9E6;
            border: 1px solid #FFD966;
            border-radius: 6px;
            padding: 10px;
        """)
        main_layout.addWidget(info_label)

        main_layout.addStretch()

        # Устанавливаем фон окна
        self.setStyleSheet("QMainWindow { background-color: #E8F4F8; }")

    def login(self):
        """Обработка входа в систему"""
        # Получаем данные из полей
        username = self.login_input.text().strip()
        password = self.password_input.text()

        # Проверяем, заполнены ли поля
        if not username or not password:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, заполните все поля!"
            )
            return

        # Проверяем данные в базе
        success, user_data = self.verify_login(username, password)

        if success:
            # Успешная авторизация
            QMessageBox.information(
                self,
                "Вход выполнен",
                f"Добро пожаловать, {user_data['Name_User']}!"
            )
            # Отправляем сигнал с данными пользователя
            self.login_success.emit(user_data)
            # Закрываем окно авторизации
            self.close()
        else:
            # Ошибка авторизации
            QMessageBox.critical(
                self,
                "Ошибка входа",
                "Неверный логин или пароль!\nПроверьте правильность введенных данных."
            )
            # Очищаем поле пароля
            self.password_input.clear()
            self.password_input.setFocus()

    def verify_login(self, username, password):
        """Проверка логина и пароля в базе данных"""
        try:
            # Получаем подключение к БД
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Хешируем пароль
            password_hash = self.hash_password(password)

            # Ищем пользователя в базе
            cursor.execute('''
                SELECT u.ID_User, u.Username, u.Name_User, u.Surname_User, 
                       u.Patronymic_User, u.Status, r.Role_Name, r.Admin_Permissions
                FROM Users u
                JOIN Roles r ON u.Role_ID = r.ID_Role
                WHERE u.Username = ? AND u.Password_User = ?
            ''', (username, password_hash))

            user = cursor.fetchone()
            conn.close()

            # Проверяем, найден ли пользователь
            if user:
                # Проверяем статус пользователя
                if user[5] != 'активен':
                    return False, None

                # Формируем данные пользователя
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'full_name': f"{user[2]} {user[3]} {user[4]}",
                    'role': user[6],
                    'is_admin': bool(user[7])
                }
                return True, user_data

            return False, None

        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
            return False, None

    def hash_password(self, password):
        """Хеширование пароля"""
        # Простое хеширование SHA-256
        return hashlib.sha256(password.encode()).hexdigest()
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.database import DatabaseManager

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(dict)

    def __init__(self, db_manager=None):
        super().__init__()
        self.db_manager = db_manager or DatabaseManager()
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("FishHub - Вход в систему")
        self.setFixedSize(460, 420)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        title = QLabel("FishHub")
        title.setObjectName("titleLabel")
        card_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Пожалуйста, войдите в систему")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        # Login field
        login_label = QLabel("Логин")
        card_layout.addWidget(login_label)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        card_layout.addWidget(self.login_input)

        # Password with show button
        pwd_label = QLabel("Пароль")
        card_layout.addWidget(pwd_label)
        pwd_row = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self.password_input)

        eye_btn = QToolButton()
        eye_btn.setObjectName("eyeBtn")
        eye_btn.setText("👁")
        eye_btn.setToolTip("Показать/скрыть пароль")
        eye_btn.clicked.connect(self.toggle_password)
        pwd_row.addWidget(eye_btn)
        card_layout.addLayout(pwd_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.attempt_login)
        btn_row.addWidget(self.login_button)
        card_layout.addLayout(btn_row)

        main_layout.addWidget(card)

    def toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def attempt_login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
            return

        user = self.db_manager.check_user(username, password)
        if not user:
            QMessageBox.warning(self, "Ошибка входа", "Неверный логин или пароль!")
            return

        # Если пользователь уже активен, блокируем повторный вход
        if user.get('status') and str(user.get('status')).lower() == 'активен':
            QMessageBox.warning(self, "Ошибка", "Пользователь уже авторизован в системе.")
            return

        # ИСПРАВЛЕНИЕ: используем правильное имя метода
        self.db_manager.update_user_status_by_id(user['id'], "Активен")
        self.current_user = user
        QMessageBox.information(self, "Вход выполнен", f"Добро пожаловать, {user.get('name')}!")
        self.login_success.emit(user)
        self.close()
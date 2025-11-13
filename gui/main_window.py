from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout,
    QWidget, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from datetime import datetime
import sqlite3
from gui.widgets.monitoring_widget import MonitoringWidget
from gui.widgets.feeding_widget import FeedingWidget
from gui.widgets.reports_widget import ReportsWidget


class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_user_id = user_data.get("id")
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowTitle(f"FishHub | {self.user_data['full_name']}")
        self.setGeometry(100, 100, 1250, 800)

        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        self.monitoring_tab = MonitoringWidget(self.db_manager)
        self.feeding_tab = FeedingWidget(self.db_manager)
        self.reports_tab = ReportsWidget(self.db_manager, self.user_data)

        self.tab_widget.addTab(self.monitoring_tab, "📊 Мониторинг")
        self.tab_widget.addTab(self.feeding_tab, "🐟 Кормление")
        self.tab_widget.addTab(self.reports_tab, "📈 Отчеты")
        layout.addWidget(self.tab_widget)

        self.statusBar().showMessage(
            f"Пользователь: {self.user_data['full_name']} | "
            f"Роль: {self.user_data['role']} | Система готова"
        )

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')

        logout_action = QAction('Выход из учётной записи', self)
        logout_action.setShortcut('Ctrl+L')
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction('Выход из приложения', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.handle_exit)
        file_menu.addAction(exit_action)

        manage_menu = menubar.addMenu('Управление')

        pools_action = QAction('Бассейны', self)
        pools_action.triggered.connect(self.manage_pools)
        manage_menu.addAction(pools_action)

        sensors_action = QAction('Датчики', self)
        sensors_action.triggered.connect(self.manage_sensors)
        manage_menu.addAction(sensors_action)

        help_menu = menubar.addMenu('Справка')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)

    def update_data(self):
        self.monitoring_tab.refresh_data()
        current_time = datetime.now().strftime("%H:%M:%S")
        self.statusBar().showMessage(
            f"Пользователь: {self.user_data['full_name']} | "
            f"Роль: {self.user_data['role']} | "
            f"Обновлено: {current_time}"
        )

    def manage_pools(self):
        from gui.dialogs.pool_dialog import PoolManagerDialog
        dialog = PoolManagerDialog(self.db_manager, self)
        dialog.exec()

    def manage_sensors(self):
        from gui.dialogs.sensor_dialog import SensorManagerDialog
        dialog = SensorManagerDialog(self.db_manager, self)
        dialog.exec()

    def get_sensor_readings(self, sensor_id, limit=100):
        try:
            query = """
                SELECT * FROM Sensor_Readings 
                WHERE ID_Sensor = ? 
                ORDER BY Timestamp_Sensor DESC 
                LIMIT ?
            """
            self.cursor.execute(query, (sensor_id, limit))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний датчика: {e}")
            return []

    def show_about(self):
        QMessageBox.about(
            self,
            "О программе FishHub",
            "FishHub - Система автоматизации рыбоводческого хозяйства\n\n"
            "Версия: 1.0\n"
            "Разработчик: Тепикин Ф. М.\n\n"
            "Программа предназначена для автоматизации процессов "
            "промышленного разведения рыбы"
        )

    def logout(self):
        try:
            self.close()

            from gui.login_window import LoginWindow
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.show()
        except Exception as e:
            print(f"Ошибка при выходе: {e}")

    def handle_exit(self):
        self.close()

    def closeEvent(self, event):
        try:
            user_id = self.user_data.get("id")
            if user_id:
                self.db_manager.update_user_status_by_id(user_id, "Отключён")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось сбросить статус пользователя при выходе: {e}")
        event.accept()

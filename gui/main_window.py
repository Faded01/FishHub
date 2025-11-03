from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from datetime import datetime

from gui.widgets.monitoring_widget import MonitoringWidget
from gui.widgets.feeding_widget import FeedingWidget
from gui.widgets.reports_widget import ReportsWidget


class MainWindow(QMainWindow):
    """Главное окно приложения FishHub"""

    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data  # Данные авторизованного пользователя
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Инициализация интерфейса"""
        # Устанавливаем заголовок с именем пользователя
        self.setWindowTitle(f"FishHub - {self.user_data['full_name']}")
        self.setGeometry(100, 100, 1200, 800)

        # Создаем меню
        self.create_menu()

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        layout = QVBoxLayout(central_widget)

        # Создаем вкладки
        self.tab_widget = QTabWidget()

        # Добавляем вкладки с иконками
        self.monitoring_tab = MonitoringWidget(self.db_manager)
        self.feeding_tab = FeedingWidget(self.db_manager)
        self.reports_tab = ReportsWidget(self.db_manager)

        self.tab_widget.addTab(self.monitoring_tab, "📊 Мониторинг")
        self.tab_widget.addTab(self.feeding_tab, "🐟 Кормление")
        self.tab_widget.addTab(self.reports_tab, "📈 Отчеты")

        layout.addWidget(self.tab_widget)

        # Статус бар с информацией о пользователе
        self.statusBar().showMessage(
            f"Пользователь: {self.user_data['full_name']} | Роль: {self.user_data['role']} | Система готова"
        )

    def create_menu(self):
        """Создание меню приложения"""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        # Действие выхода
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Управление"
        manage_menu = menubar.addMenu('Управление')

        # Управление бассейнами
        pools_action = QAction('Бассейны', self)
        pools_action.triggered.connect(self.manage_pools)
        manage_menu.addAction(pools_action)

        # Управление датчиками
        sensors_action = QAction('Датчики', self)
        sensors_action.triggered.connect(self.manage_sensors)
        manage_menu.addAction(sensors_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        # О программе
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_timer(self):
        """Настройка таймера для обновления данных"""
        # Таймер обновляется каждые 5 секунд
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)

    def update_data(self):
        """Обновление данных в реальном времени"""
        # Обновляем данные на вкладке мониторинга
        self.monitoring_tab.refresh_data()

        # Обновляем время в статус баре
        current_time = datetime.now().strftime("%H:%M:%S")
        self.statusBar().showMessage(
            f"Пользователь: {self.user_data['full_name']} | "
            f"Роль: {self.user_data['role']} | "
            f"Обновлено: {current_time}"
        )

    def manage_pools(self):
        """Открыть окно управления бассейнами"""
        from gui.dialogs.pool_dialog import PoolManagerDialog
        dialog = PoolManagerDialog(self.db_manager, self)
        dialog.exec()

    def manage_sensors(self):
        """Открыть окно управления датчиками"""
        QMessageBox.information(
            self,
            "Управление датчиками",
            "Функция управления датчиками будет добавлена в следующей версии"
        )

    def show_about(self):
        """Показать окно "О программе" """
        QMessageBox.about(
            self,
            "О программе FishHub",
            "FishHub - Система автоматизации рыбоводческого хозяйства\n\n"
            "Версия: 1.0\n"
            "Разработчик: Ваше имя\n\n"
            "Программа предназначена для автоматизации процессов "
            "промышленного разведения рыбы"
        )

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Спрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            'Подтверждение выхода',
            'Вы уверены, что хотите выйти из программы?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Останавливаем таймер
            self.update_timer.stop()
            # Закрываем приложение
            event.accept()
        else:
            # Отменяем закрытие
            event.ignore()
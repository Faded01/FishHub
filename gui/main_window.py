from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from gui.widgets.monitoring_widget import MonitoringWidget
from gui.widgets.feeding_widget import FeedingWidget
from gui.widgets.reports_widget import ReportsWidget


class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowTitle("FishHub - Система автоматизации рыбоводства")
        self.setGeometry(100, 100, 1200, 800)

        # Создание меню (аналогично fullflash)
        self.create_menu()

        # Создание вкладок
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.tab_widget = QTabWidget()

        # Добавление вкладок
        self.monitoring_tab = MonitoringWidget(self.db_manager)
        self.feeding_tab = FeedingWidget(self.db_manager)
        self.reports_tab = ReportsWidget(self.db_manager)

        self.tab_widget.addTab(self.monitoring_tab, "📊 Мониторинг")
        self.tab_widget.addTab(self.feeding_tab, "🎣 Кормление")
        self.tab_widget.addTab(self.reports_tab, "📈 Отчеты")

        layout.addWidget(self.tab_widget)

        # Статус бар
        self.statusBar().showMessage("Система готова к работе")

    def create_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Настройки
        settings_menu = menubar.addMenu('Настройки')

        pools_action = QAction('Управление бассейнами', self)
        pools_action.triggered.connect(self.manage_pools)
        settings_menu.addAction(pools_action)

    def setup_timer(self):
        """Таймер для обновления данных в реальном времени"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_real_time_data)
        self.update_timer.start(5000)  # Обновление каждые 5 секунд

    def update_real_time_data(self):
        """Обновление данных мониторинга"""
        self.monitoring_tab.refresh_data()
        self.statusBar().showMessage(f"Данные обновлены: {self.get_current_time()}")

    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def manage_pools(self):
        from gui.dialogs.pool_dialog import PoolManagerDialog
        dialog = PoolManagerDialog(self.db_manager, self)
        dialog.exec()

    def closeEvent(self, event):
        """Обработчик закрытия приложения"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.update_timer.stop()
            event.accept()
        else:
            event.ignore()
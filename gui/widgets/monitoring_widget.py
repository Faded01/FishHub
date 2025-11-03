from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QGroupBox,
                             QPushButton, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
import random
from datetime import datetime


class MonitoringWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Мониторинг параметров водной среды")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Группа текущих показаний
        current_group = QGroupBox("Текущие показания")
        current_layout = QHBoxLayout()

        self.temp_label = QLabel("Температура: --°C")
        self.oxygen_label = QLabel("Кислород: -- мг/л")
        self.ph_label = QLabel("pH: --")

        current_layout.addWidget(self.temp_label)
        current_layout.addWidget(self.oxygen_label)
        current_layout.addWidget(self.ph_label)

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Таблица истории
        history_group = QGroupBox("История показаний")
        history_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Время", "Параметр", "Значение", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        history_layout.addWidget(self.table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.refresh_data)

        self.simulate_btn = QPushButton("Симулировать данные")
        self.simulate_btn.clicked.connect(self.simulate_data)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.simulate_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def refresh_data(self):
        """Обновление данных мониторинга"""
        # Здесь будет реальная логика получения данных из БД
        # Пока используем демо-данные
        self.update_current_readings()
        self.update_history_table()

    def update_current_readings(self):
        """Обновление текущих показаний"""
        temp = random.uniform(18.0, 22.0)
        oxygen = random.uniform(5.0, 8.0)
        ph = random.uniform(6.5, 7.5)

        self.temp_label.setText(f"Температура: {temp:.1f}°C")
        self.oxygen_label.setText(f"Кислород: {oxygen:.1f} мг/л")
        self.ph_label.setText(f"pH: {ph:.1f}")

    def update_history_table(self):
        """Обновление таблицы истории"""
        # Демо-данные
        data = [
            ("10:00:00", "Температура", "20.5°C", "Норма"),
            ("10:05:00", "Кислород", "6.8 мг/л", "Норма"),
            ("10:10:00", "pH", "7.2", "Норма"),
        ]

        self.table.setRowCount(len(data))
        for row, (time, param, value, status) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(time))
            self.table.setItem(row, 1, QTableWidgetItem(param))
            self.table.setItem(row, 2, QTableWidgetItem(value))
            self.table.setItem(row, 3, QTableWidgetItem(status))

    def simulate_data(self):
        """Симуляция новых данных"""
        # Логика добавления случайных данных в БД
        self.refresh_data()
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime


class MonitoringWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.setup_timer()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Мониторинг параметров водной среды")
        title.setObjectName("widgetTitle")
        layout.addWidget(title)

        # Текущие показания
        current_group = QGroupBox("Текущие показания")
        current_layout = QGridLayout()

        self.temp_label = QLabel("Температура: --°C")
        self.oxygen_label = QLabel("Кислород: -- мг/л")
        self.ph_label = QLabel("pH: --")

        current_layout.addWidget(self.temp_label, 0, 0)
        current_layout.addWidget(self.oxygen_label, 0, 1)
        current_layout.addWidget(self.ph_label, 0, 2)

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # История показаний
        history_group = QGroupBox("История показаний")
        history_layout = QVBoxLayout()

        self.readings_table = QTableWidget()
        self.readings_table.setColumnCount(5)
        self.readings_table.setHorizontalHeaderLabels([
            "Время", "Бассейн", "Параметр", "Значение", "Статус"
        ])
        self.readings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.readings_table)

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
        self.setLayout(layout)

    def setup_timer(self):
        """Настройка автообновления каждые 30 секунд"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)

    def refresh_data(self):
        """Обновление данных мониторинга"""
        try:
            # Получаем последние показания
            readings = self.db_manager.get_latest_sensor_readings()

            # Обновляем текущие показания (последние для каждого типа датчика)
            current_temp = None
            current_oxygen = None
            current_ph = None

            for reading in readings:
                sensor_type = reading['Type_Sensor']
                value = reading['Value_Sensor']

                if sensor_type == 'Температура' and current_temp is None:
                    current_temp = value
                    self.temp_label.setText(f"Температура: {value}°C")
                elif sensor_type == 'Кислород' and current_oxygen is None:
                    current_oxygen = value
                    self.oxygen_label.setText(f"Кислород: {value} мг/л")
                elif sensor_type == 'pH' and current_ph is None:
                    current_ph = value
                    self.ph_label.setText(f"pH: {value}")

            # Заполняем таблицу истории
            self.readings_table.setRowCount(len(readings))
            for row, reading in enumerate(readings):
                time = reading['Timestamp_Sensor'][:16]  # Обрезаем до даты и времени
                pool_id = reading['ID_Pool']
                sensor_type = reading['Type_Sensor']
                value = reading['Value_Sensor']
                status = reading['Status_Readings']

                # Получаем название бассейна
                pool = self.db_manager.get_pool_by_id(pool_id)
                pool_name = pool['Name_Pool'] if pool else f"Бассейн {pool_id}"

                self.readings_table.setItem(row, 0, QTableWidgetItem(time))
                self.readings_table.setItem(row, 1, QTableWidgetItem(pool_name))
                self.readings_table.setItem(row, 2, QTableWidgetItem(sensor_type))
                self.readings_table.setItem(row, 3, QTableWidgetItem(str(value)))
                self.readings_table.setItem(row, 4, QTableWidgetItem(status))

        except Exception as e:
            print(f"Ошибка обновления мониторинга: {e}")

    def simulate_data(self):
        """Симуляция новых данных для тестирования"""
        try:
            # Получаем все датчики
            pools = self.db_manager.get_all_pools()
            for pool in pools:
                sensors = self.db_manager.get_sensors_by_pool(pool['ID_Pool'])
                for sensor in sensors:
                    # Генерируем случайные значения в зависимости от типа датчика
                    sensor_type = sensor['Type_Sensor']
                    if sensor_type == 'Температура':
                        value = round(18 + (22 - 18) * (hash(str(datetime.now())) % 100 / 100), 1)
                        status = "Норма" if 19 <= value <= 21 else "Предупреждение"
                    elif sensor_type == 'Кислород':
                        value = round(6 + (8 - 6) * (hash(str(datetime.now())) % 100 / 100), 1)
                        status = "Норма" if value >= 6.5 else "Критично"
                    elif sensor_type == 'pH':
                        value = round(6.8 + (7.5 - 6.8) * (hash(str(datetime.now())) % 100 / 100), 1)
                        status = "Норма" if 6.5 <= value <= 7.5 else "Предупреждение"
                    else:
                        continue

                    self.db_manager.add_sensor_reading(sensor['ID_Sensor'], value, status)

            QMessageBox.information(self, "Симуляция", "Тестовые данные добавлены!")
            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка симуляции: {e}")
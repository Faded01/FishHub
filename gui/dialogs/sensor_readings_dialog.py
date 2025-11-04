from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QDoubleSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from datetime import datetime


class SensorReadingsDialog(QDialog):
    def __init__(self, db_manager, sensor_id, sensor_title, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sensor_id = sensor_id
        self.setWindowTitle(f"Показания датчика - {sensor_title}")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.init_ui()
        self.load_readings()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel(f"Показания датчика")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # Форма добавления показаний
        form_group = QGroupBox("Добавить показания")
        form_layout = QFormLayout()

        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-100, 1000)
        self.value_input.setDecimals(2)
        self.value_input.setSingleStep(0.1)
        form_layout.addRow("Значение:", self.value_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Норма", "Предупреждение", "Критично"])
        form_layout.addRow("Статус:", self.status_combo)

        # Кнопки формы
        form_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить показания")
        self.add_btn.clicked.connect(self.add_reading)

        self.simulate_btn = QPushButton("Симулировать данные")
        self.simulate_btn.clicked.connect(self.simulate_readings)

        form_buttons_layout.addWidget(self.add_btn)
        form_buttons_layout.addWidget(self.simulate_btn)
        form_buttons_layout.addStretch()

        form_layout.addRow(form_buttons_layout)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Таблица показаний
        table_group = QGroupBox("История показаний")
        table_layout = QVBoxLayout()

        self.readings_table = QTableWidget()
        self.readings_table.setColumnCount(4)
        self.readings_table.setHorizontalHeaderLabels([
            "Время", "Значение", "Статус", "ID записи"
        ])
        self.readings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.readings_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_readings(self):
        """Загрузка показаний датчика"""
        try:
            # Получаем все показания для этого датчика
            query = """
                SELECT * FROM Sensor_Readings 
                WHERE ID_Sensor = ? 
                ORDER BY Timestamp_Sensor DESC
                LIMIT 100
            """
            self.db_manager.cursor.execute(query, (self.sensor_id,))
            readings = self.db_manager.cursor.fetchall()

            self.readings_table.setRowCount(len(readings))

            for row, reading in enumerate(readings):
                time_str = reading['Timestamp_Sensor'][:19]  # Обрезаем до секунд
                self.readings_table.setItem(row, 0, QTableWidgetItem(time_str))
                self.readings_table.setItem(row, 1, QTableWidgetItem(str(reading['Value_Sensor'])))
                self.readings_table.setItem(row, 2, QTableWidgetItem(reading['Status_Readings']))
                self.readings_table.setItem(row, 3, QTableWidgetItem(str(reading['ID_Record'])))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки показаний: {e}")

    def add_reading(self):
        """Добавление новых показаний"""
        try:
            value = self.value_input.value()
            status = self.status_combo.currentText()

            success = self.db_manager.add_sensor_reading(self.sensor_id, value, status)

            if success:
                QMessageBox.information(self, "Успех", "Показания добавлены!")
                self.value_input.setValue(0.0)
                self.load_readings()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить показания")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def simulate_readings(self):
        """Симуляция показаний для тестирования"""
        try:
            # Добавляем несколько тестовых показаний
            import random
            from datetime import datetime, timedelta

            base_value = 20.0  # Базовое значение в зависимости от типа датчика
            variations = [-2, -1, 0, 1, 2]

            for i in range(10):
                value = base_value + random.choice(variations) + random.random()
                status = "Норма" if abs(value - base_value) < 1.5 else "Предупреждение"

                # Создаем временную метку с смещением
                time_offset = timedelta(hours=-(9 - i))
                simulated_time = (datetime.now() + time_offset).strftime("%Y-%m-%d %H:%M:%S")

                # Вставляем с конкретным временем
                query = """
                    INSERT INTO Sensor_Readings (ID_Sensor, Value_Sensor, Timestamp_Sensor, Status_Readings)
                    VALUES (?, ?, ?, ?)
                """
                self.db_manager.cursor.execute(query, (self.sensor_id, round(value, 2), simulated_time, status))

            self.db_manager.connection.commit()
            QMessageBox.information(self, "Успех", "Тестовые данные добавлены!")
            self.load_readings()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка симуляции: {e}")
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
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_readings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

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
        self.add_btn.setFixedWidth(200)

        form_buttons_layout.addWidget(self.add_btn)
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
            "ID записи", "Значение", "Статус", "Время"
        ])

        # ФИКСИРОВАННЫЕ ШИРИНЫ КОЛОНОК
        self.readings_table.setColumnWidth(0, 80)   # ID записи
        self.readings_table.setColumnWidth(1, 100)  # Значение
        self.readings_table.setColumnWidth(2, 120)  # Статус
        self.readings_table.setColumnWidth(3, 150)  # Время

        # Растягиваем последнюю колонку
        header = self.readings_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        table_layout.addWidget(self.readings_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Кнопки диалога
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_readings(self):
        """Загрузка показаний датчика"""
        try:
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
                time_str = reading['Timestamp_Sensor']
                if '.' in time_str:
                    time_str = time_str.split('.')[0]

                self.readings_table.setItem(row, 0, QTableWidgetItem(str(reading['ID_Record'])))
                self.readings_table.setItem(row, 1, QTableWidgetItem(str(reading['Value_Sensor'])))
                self.readings_table.setItem(row, 2, QTableWidgetItem(reading['Status_Readings']))
                self.readings_table.setItem(row, 3, QTableWidgetItem(time_str))

            # Автоподбор ширины колонок после заполнения данных
            self.readings_table.resizeColumnsToContents()

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
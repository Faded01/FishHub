from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


class SensorManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Управление датчиками")
        self.setModal(True)
        self.setMinimumSize(1200, 800)
        self.init_ui()
        self.load_sensors()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Управление датчиками")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form_group = QGroupBox("Добавить/Редактировать датчик")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)

        self.pool_combo = QComboBox()
        self.pool_combo.setMinimumWidth(300)
        self.load_pools()
        form_layout.addRow("Бассейн:", self.pool_combo)

        self.type_combo = QComboBox()
        self.type_combo.setMinimumWidth(200)
        self.type_combo.addItems([
            "Температура",
            "Кислород",
            "pH"
        ])
        form_layout.addRow("Тип датчика:", self.type_combo)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Модель датчика")
        self.model_input.setMinimumWidth(200)
        self.model_input.setMaxLength(50)
        form_layout.addRow("Модель:", self.model_input)

        range_layout = QHBoxLayout()
        self.range_min_input = QDoubleSpinBox()
        self.range_min_input.setRange(-1000, 1000)
        self.range_min_input.setDecimals(2)
        self.range_min_input.setSingleStep(0.1)
        self.range_min_input.setMinimumWidth(100)

        self.range_max_input = QDoubleSpinBox()
        self.range_max_input.setRange(-1000, 1000)
        self.range_max_input.setDecimals(2)
        self.range_max_input.setSingleStep(0.1)
        self.range_max_input.setMinimumWidth(100)

        range_layout.addWidget(self.range_min_input)
        range_layout.addWidget(QLabel("до"))
        range_layout.addWidget(self.range_max_input)
        range_layout.addStretch()

        form_layout.addRow("Диапазон измерений:", range_layout)

        self.installation_date = QDateEdit()
        self.installation_date.setDate(QDate.currentDate())
        self.installation_date.setCalendarPopup(True)
        self.installation_date.setMinimumWidth(120)
        form_layout.addRow("Дата установки:", self.installation_date)

        form_buttons_layout = QHBoxLayout()
        form_buttons_layout.setSpacing(10)

        self.add_btn = QPushButton("Добавить датчик")
        self.add_btn.clicked.connect(self.add_sensor)
        self.add_btn.setFixedWidth(200)

        self.update_btn = QPushButton("Сохранить изменения")
        self.update_btn.clicked.connect(self.update_sensor)
        self.update_btn.setEnabled(False)
        self.update_btn.setFixedWidth(200)

        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setFixedWidth(200)

        form_buttons_layout.addWidget(self.add_btn)
        form_buttons_layout.addWidget(self.update_btn)
        form_buttons_layout.addWidget(self.clear_btn)
        form_buttons_layout.addStretch()

        form_layout.addRow(form_buttons_layout)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        table_group = QGroupBox("Список датчиков")
        table_layout = QVBoxLayout()

        self.sensors_table = QTableWidget()
        self.sensors_table.setColumnCount(8)
        self.sensors_table.setHorizontalHeaderLabels([
            "ID", "Бассейн", "Тип", "Модель", "Диапазон от",
            "Диапазон до", "Дата установки", "Последние показания"
        ])

        self.sensors_table.setColumnWidth(0, 50)
        self.sensors_table.setColumnWidth(1, 150)
        self.sensors_table.setColumnWidth(2, 120)
        self.sensors_table.setColumnWidth(3, 180)
        self.sensors_table.setColumnWidth(4, 100)
        self.sensors_table.setColumnWidth(5, 100)
        self.sensors_table.setColumnWidth(6, 120)
        self.sensors_table.setColumnWidth(7, 180)

        header = self.sensors_table.horizontalHeader()
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self.sensors_table.cellClicked.connect(self.on_cell_clicked)
        table_layout.addWidget(self.sensors_table)

        table_buttons_layout = QHBoxLayout()
        table_buttons_layout.setSpacing(10)

        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.load_sensors)
        self.refresh_btn.setFixedWidth(200)

        self.delete_btn = QPushButton("Удалить датчик")
        self.delete_btn.clicked.connect(self.delete_sensor)
        self.delete_btn.setFixedWidth(200)

        self.readings_btn = QPushButton("Показания датчика")
        self.readings_btn.clicked.connect(self.show_sensor_readings)
        self.readings_btn.setFixedWidth(200)

        table_buttons_layout.addWidget(self.refresh_btn)
        table_buttons_layout.addWidget(self.delete_btn)
        table_buttons_layout.addWidget(self.readings_btn)
        table_buttons_layout.addStretch()

        table_layout.addLayout(table_buttons_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.current_sensor_id = None

    def load_sensors(self):
        try:
            sensors_data = []
            pools = self.db_manager.get_all_pools()

            for pool in pools:
                sensors = self.db_manager.get_sensors_by_pool(pool['ID_Pool'])
                for sensor in sensors:
                    readings = self.db_manager.get_latest_sensor_readings(pool['ID_Pool'])
                    latest_reading = "Нет данных"

                    for reading in readings:
                        if reading['ID_Sensor'] == sensor['ID_Sensor']:
                            value = reading['Value_Sensor']
                            status = reading['Status_Readings']
                            latest_reading = f"{value:.1f} ({status})"
                            break

                    sensors_data.append({
                        'sensor': sensor,
                        'pool_name': pool['Name_Pool'],
                        'latest_reading': latest_reading
                    })

            self.sensors_table.setRowCount(len(sensors_data))

            for row, data in enumerate(sensors_data):
                sensor = data['sensor']

                self.sensors_table.setItem(row, 0, QTableWidgetItem(str(sensor['ID_Sensor'])))
                self.sensors_table.setItem(row, 1, QTableWidgetItem(data['pool_name']))
                self.sensors_table.setItem(row, 2, QTableWidgetItem(sensor['Type_Sensor']))
                self.sensors_table.setItem(row, 3, QTableWidgetItem(sensor['Model_Sensor'] or '-'))

                range_min = str(sensor['Range_Min']) if sensor['Range_Min'] is not None else '-'
                self.sensors_table.setItem(row, 4, QTableWidgetItem(range_min))

                range_max = str(sensor['Range_Max']) if sensor['Range_Max'] is not None else '-'
                self.sensors_table.setItem(row, 5, QTableWidgetItem(range_max))

                self.sensors_table.setItem(row, 6, QTableWidgetItem(sensor['Installation_Date']))
                self.sensors_table.setItem(row, 7, QTableWidgetItem(data['latest_reading']))

            self.sensors_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки датчиков: {e}")

    def on_cell_clicked(self, row, column):
        try:
            sensor_id = int(self.sensors_table.item(row, 0).text())
            self.edit_sensor_by_id(sensor_id)
        except (ValueError, AttributeError) as e:
            print(f"Ошибка при выборе строки: {e}")

    def edit_sensor_by_id(self, sensor_id):
        try:
            pools = self.db_manager.get_all_pools()
            sensor_data = None

            for pool in pools:
                sensors = self.db_manager.get_sensors_by_pool(pool['ID_Pool'])
                for sensor in sensors:
                    if sensor['ID_Sensor'] == sensor_id:
                        sensor_data = sensor
                        break
                if sensor_data:
                    break

            if sensor_data:
                self.current_sensor_id = sensor_id

                index = self.pool_combo.findData(sensor_data['ID_Pool'])
                if index >= 0:
                    self.pool_combo.setCurrentIndex(index)

                index = self.type_combo.findText(sensor_data['Type_Sensor'])
                if index >= 0:
                    self.type_combo.setCurrentIndex(index)

                model_text = sensor_data['Model_Sensor'] or ''
                if len(model_text) > 50:
                    model_text = model_text[:50]
                self.model_input.setText(model_text)

                self.range_min_input.setValue(
                    float(sensor_data['Range_Min']) if sensor_data['Range_Min'] is not None else 0.0)
                self.range_max_input.setValue(
                    float(sensor_data['Range_Max']) if sensor_data['Range_Max'] is not None else 0.0)

                if sensor_data['Installation_Date']:
                    self.installation_date.setDate(QDate.fromString(sensor_data['Installation_Date'], "yyyy-MM-dd"))

                self.add_btn.setEnabled(False)
                self.update_btn.setEnabled(True)

        except Exception as e:
            print(f"Ошибка редактирования: {e}")

    def load_pools(self):
        pools = self.db_manager.get_all_pools()
        self.pool_combo.clear()
        for pool in pools:
            self.pool_combo.addItem(
                f"{pool['Name_Pool']} ({pool['Fish_Type']})",
                pool['ID_Pool']
            )

    def add_sensor(self):
        try:
            pool_id = self.pool_combo.currentData()
            sensor_type = self.type_combo.currentText()
            model = self.model_input.text().strip()
            measurement_range_min = self.range_min_input.value()
            measurement_range_max = self.range_max_input.value()
            installation_date = self.installation_date.date().toString("yyyy-MM-dd")

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            if measurement_range_min >= measurement_range_max:
                QMessageBox.warning(self, "Ошибка", "Начало диапазона должно быть меньше конца диапазона!")
                return

            if len(model) > 50:
                QMessageBox.warning(self, "Ошибка", "Модель не должна превышать 50 символов!")
                return

            success = self.add_sensor_to_db(
                pool_id, sensor_type, model, measurement_range_min, measurement_range_max, installation_date
            )

            if success:
                QMessageBox.information(self, "Успех", "Датчик добавлен!")
                self.clear_form()
                self.load_sensors()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить датчик")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def add_sensor_to_db(self, pool_id, sensor_type, model, measurement_range_min, measurement_range_max,
                         installation_date):
        try:
            query = """
                INSERT INTO Sensors (ID_Pool, Type_Sensor, Model_Sensor, Range_Min, Range_Max, Installation_Date)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.db_manager.cursor.execute(query,
                                           (pool_id, sensor_type, model, measurement_range_min, measurement_range_max,
                                            installation_date))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления датчика в БД: {e}")
            return False

    def update_sensor(self):
        try:
            if not self.current_sensor_id:
                return

            pool_id = self.pool_combo.currentData()
            sensor_type = self.type_combo.currentText()
            model = self.model_input.text().strip()
            measurement_range_min = self.range_min_input.value()
            measurement_range_max = self.range_max_input.value()
            installation_date = self.installation_date.date().toString("yyyy-MM-dd")

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            if measurement_range_min >= measurement_range_max:
                QMessageBox.warning(self, "Ошибка", "Начало диапазона должно быть меньше конца диапазона!")
                return

            if len(model) > 50:
                QMessageBox.warning(self, "Ошибка", "Модель не должна превышать 50 символов!")
                return

            success = self.update_sensor_in_db(
                self.current_sensor_id, pool_id, sensor_type, model,
                measurement_range_min, measurement_range_max, installation_date
            )

            if success:
                QMessageBox.information(self, "Успех", "Датчик обновлен!")
                self.clear_form()
                self.load_sensors()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить датчик")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {e}")

    def update_sensor_in_db(self, sensor_id, pool_id, sensor_type, model, measurement_range_min, measurement_range_max,
                            installation_date):
        try:
            query = """
                UPDATE Sensors 
                SET ID_Pool = ?, Type_Sensor = ?, Model_Sensor = ?, 
                    Range_Min = ?, Range_Max = ?, Installation_Date = ?
                WHERE ID_Sensor = ?
            """
            self.db_manager.cursor.execute(query, (
                pool_id, sensor_type, model, measurement_range_min,
                measurement_range_max, installation_date, sensor_id
            ))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления датчика в БД: {e}")
            return False

    def delete_sensor(self):
        try:
            current_row = self.sensors_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите датчик для удаления!")
                return

            sensor_id = int(self.sensors_table.item(current_row, 0).text())
            sensor_type = self.sensors_table.item(current_row, 2).text()
            pool_name = self.sensors_table.item(current_row, 1).text()

            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить датчик '{sensor_type}' из бассейна '{pool_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.delete_sensor_from_db(sensor_id)
                if success:
                    QMessageBox.information(self, "Успех", "Датчик удален!")
                    self.load_sensors()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить датчик")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def delete_sensor_from_db(self, sensor_id):
        try:
            self.db_manager.cursor.execute("DELETE FROM Sensors WHERE ID_Sensor = ?", (sensor_id,))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления датчика из БД: {e}")
            return False

    def show_sensor_readings(self):
        try:
            current_row = self.sensors_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите датчик для просмотра показаний!")
                return

            sensor_id = int(self.sensors_table.item(current_row, 0).text())
            sensor_type = self.sensors_table.item(current_row, 2).text()
            pool_name = self.sensors_table.item(current_row, 1).text()

            try:
                from gui.dialogs.sensor_readings_dialog import SensorReadingsDialog
                dialog = SensorReadingsDialog(self.db_manager, sensor_id, f"{sensor_type} - {pool_name}", self)
                dialog.exec()
            except ImportError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модуль показаний: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка открытия показаний: {e}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка показаний: {e}")

    def clear_form(self):
        self.current_sensor_id = None
        self.pool_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.model_input.clear()
        self.range_min_input.setValue(0.0)
        self.range_max_input.setValue(0.0)
        self.installation_date.setDate(QDate.currentDate())

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
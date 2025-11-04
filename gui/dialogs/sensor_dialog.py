from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDialogButtonBox, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


class SensorManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Управление датчиками")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.init_ui()
        self.load_sensors()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Управление датчиками")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # Форма добавления/редактирования
        form_group = QGroupBox("Добавить/Редактировать датчик")
        form_layout = QFormLayout()

        # Выбор бассейна
        self.pool_combo = QComboBox()
        self.load_pools()
        form_layout.addRow("Бассейн:", self.pool_combo)

        # Тип датчика
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Температура",
            "Кислород",
            "pH",
            "Соленость",
            "Мутность",
            "Аммиак"
        ])
        form_layout.addRow("Тип датчика:", self.type_combo)

        # Модель датчика
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Модель датчика")
        form_layout.addRow("Модель:", self.model_input)

        # Диапазон измерений
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Например: 0-50°C или 0-20 мг/л")
        form_layout.addRow("Диапазон измерений:", self.range_input)

        # Дата установки
        self.installation_date = QDateEdit()
        self.installation_date.setDate(QDate.currentDate())
        self.installation_date.setCalendarPopup(True)
        form_layout.addRow("Дата установки:", self.installation_date)

        # Кнопки формы
        form_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить датчик")
        self.add_btn.clicked.connect(self.add_sensor)

        self.update_btn = QPushButton("Обновить")
        self.update_btn.clicked.connect(self.update_sensor)
        self.update_btn.setEnabled(False)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_form)

        form_buttons_layout.addWidget(self.add_btn)
        form_buttons_layout.addWidget(self.update_btn)
        form_buttons_layout.addWidget(self.clear_btn)
        form_buttons_layout.addStretch()

        form_layout.addRow(form_buttons_layout)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Таблица датчиков
        table_group = QGroupBox("Список датчиков")
        table_layout = QVBoxLayout()

        self.sensors_table = QTableWidget()
        self.sensors_table.setColumnCount(7)
        self.sensors_table.setHorizontalHeaderLabels([
            "ID", "Бассейн", "Тип", "Модель", "Диапазон", "Дата установки", "Последние показания"
        ])
        self.sensors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sensors_table.cellDoubleClicked.connect(self.edit_sensor)
        table_layout.addWidget(self.sensors_table)

        # Кнопки управления таблицей
        table_buttons_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_sensors)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_sensor)

        self.readings_btn = QPushButton("Показания датчика")
        self.readings_btn.clicked.connect(self.show_sensor_readings)

        table_buttons_layout.addWidget(self.refresh_btn)
        table_buttons_layout.addWidget(self.delete_btn)
        table_buttons_layout.addWidget(self.readings_btn)
        table_buttons_layout.addStretch()

        table_layout.addLayout(table_buttons_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.current_sensor_id = None

    def load_pools(self):
        """Загрузка списка бассейнов"""
        pools = self.db_manager.get_all_pools()
        self.pool_combo.clear()
        for pool in pools:
            self.pool_combo.addItem(
                f"{pool['Name_Pool']} ({pool['Fish_Type']})",
                pool['ID_Pool']
            )

    def load_sensors(self):
        """Загрузка списка датчиков"""
        try:
            # Получаем все датчики с информацией о бассейнах
            sensors_data = []
            pools = self.db_manager.get_all_pools()

            for pool in pools:
                sensors = self.db_manager.get_sensors_by_pool(pool['ID_Pool'])
                for sensor in sensors:
                    # Получаем последние показания для датчика
                    readings = self.db_manager.get_latest_sensor_readings(pool['ID_Pool'])
                    latest_reading = "Нет данных"

                    for reading in readings:
                        if reading['ID_Sensor'] == sensor['ID_Sensor']:
                            latest_reading = f"{reading['Value_Sensor']} ({reading['Status_Readings']})"
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
                self.sensors_table.setItem(row, 4, QTableWidgetItem(sensor['Measurement_Range'] or '-'))
                self.sensors_table.setItem(row, 5, QTableWidgetItem(sensor['Installation_Date']))
                self.sensors_table.setItem(row, 6, QTableWidgetItem(data['latest_reading']))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки датчиков: {e}")

    def add_sensor(self):
        """Добавление нового датчика"""
        try:
            pool_id = self.pool_combo.currentData()
            sensor_type = self.type_combo.currentText()
            model = self.model_input.text().strip()
            measurement_range = self.range_input.text().strip()
            installation_date = self.installation_date.date().toString("yyyy-MM-dd")

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            # Добавляем метод в DatabaseManager
            success = self.add_sensor_to_db(
                pool_id, sensor_type, model, measurement_range, installation_date
            )

            if success:
                QMessageBox.information(self, "Успех", "Датчик добавлен!")
                self.clear_form()
                self.load_sensors()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить датчик")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def add_sensor_to_db(self, pool_id, sensor_type, model, measurement_range, installation_date):
        """Вспомогательный метод для добавления датчика в БД"""
        try:
            query = """
                INSERT INTO Sensors (ID_Pool, Type_Sensor, Model_Sensor, Measurement_Range, Installation_Date)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db_manager.cursor.execute(query, (pool_id, sensor_type, model, measurement_range, installation_date))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления датчика в БД: {e}")
            return False

    def edit_sensor(self, row, column):
        """Редактирование датчика по двойному клику"""
        try:
            sensor_id = int(self.sensors_table.item(row, 0).text())

            # Находим датчик в БД
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

                # Устанавливаем бассейн
                index = self.pool_combo.findData(sensor_data['ID_Pool'])
                if index >= 0:
                    self.pool_combo.setCurrentIndex(index)

                # Устанавливаем тип датчика
                index = self.type_combo.findText(sensor_data['Type_Sensor'])
                if index >= 0:
                    self.type_combo.setCurrentIndex(index)

                self.model_input.setText(sensor_data['Model_Sensor'] or '')
                self.range_input.setText(sensor_data['Measurement_Range'] or '')

                if sensor_data['Installation_Date']:
                    self.installation_date.setDate(QDate.fromString(sensor_data['Installation_Date'], "yyyy-MM-dd"))

                self.add_btn.setEnabled(False)
                self.update_btn.setEnabled(True)

        except Exception as e:
            print(f"Ошибка редактирования: {e}")

    def update_sensor(self):
        """Обновление датчика"""
        try:
            if not self.current_sensor_id:
                return

            pool_id = self.pool_combo.currentData()
            sensor_type = self.type_combo.currentText()
            model = self.model_input.text().strip()
            measurement_range = self.range_input.text().strip()
            installation_date = self.installation_date.date().toString("yyyy-MM-dd")

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            success = self.update_sensor_in_db(
                self.current_sensor_id, pool_id, sensor_type, model, measurement_range, installation_date
            )

            if success:
                QMessageBox.information(self, "Успех", "Датчик обновлен!")
                self.clear_form()
                self.load_sensors()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить датчик")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {e}")

    def update_sensor_in_db(self, sensor_id, pool_id, sensor_type, model, measurement_range, installation_date):
        """Вспомогательный метод для обновления датчика в БД"""
        try:
            query = """
                UPDATE Sensors 
                SET ID_Pool = ?, Type_Sensor = ?, Model_Sensor = ?, 
                    Measurement_Range = ?, Installation_Date = ?
                WHERE ID_Sensor = ?
            """
            self.db_manager.cursor.execute(query, (pool_id, sensor_type, model, measurement_range, installation_date,
                                                   sensor_id))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления датчика в БД: {e}")
            return False

    def delete_sensor(self):
        """Удаление выбранного датчика"""
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
        """Вспомогательный метод для удаления датчика из БД"""
        try:
            self.db_manager.cursor.execute("DELETE FROM Sensors WHERE ID_Sensor = ?", (sensor_id,))
            self.db_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления датчика из БД: {e}")
            return False

    def show_sensor_readings(self):
        """Показать окно с показаниями датчика"""
        try:
            current_row = self.sensors_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите датчик для просмотра показаний!")
                return

            sensor_id = int(self.sensors_table.item(current_row, 0).text())
            sensor_type = self.sensors_table.item(current_row, 2).text()
            pool_name = self.sensors_table.item(current_row, 1).text()

            # Создаем диалог для показаний
            from gui.dialogs.sensor_readings_dialog import SensorReadingsDialog
            dialog = SensorReadingsDialog(self.db_manager, sensor_id, f"{sensor_type} - {pool_name}", self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка показаний: {e}")

    def clear_form(self):
        """Очистка формы"""
        self.current_sensor_id = None
        self.pool_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.model_input.clear()
        self.range_input.clear()
        self.installation_date.setDate(QDate.currentDate())

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
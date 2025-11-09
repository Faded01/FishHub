from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime


class MonitoringWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.selected_pool_id = None
        self.init_ui()
        self.setup_timer()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Заголовок и выбор бассейна
        header_layout = QHBoxLayout()
        title = QLabel("Мониторинг параметров водной среды")
        title.setObjectName("widgetTitle")

        self.pool_combo = QComboBox()
        self.pool_combo.currentIndexChanged.connect(self.on_pool_changed)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Бассейн:"))
        header_layout.addWidget(self.pool_combo)

        layout.addLayout(header_layout)

        # Текущие показания по выбранному бассейну
        current_group = QGroupBox("Текущие показания выбранного бассейна")
        current_layout = QGridLayout()

        # Создаем метки для основных параметров
        self.param_labels = {}
        parameters = [
            ('Температура', '°C'),
            ('Кислород', 'мг/л'),
            ('pH', 'ед.')
        ]

        for i, (param, unit) in enumerate(parameters):
            label = QLabel(f"{param}: --{unit}")
            label.setObjectName("paramLabel")
            current_layout.addWidget(label, i // 2, i % 2)
            self.param_labels[param] = label

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Статус бассейна
        status_group = QGroupBox("Статус бассейна")
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Статус: Не выбран")
        self.fish_count_label = QLabel("Рыба: --")
        self.volume_label = QLabel("Объем: -- м³")
        self.fish_type_label = QLabel("Тип рыбы: --")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.fish_count_label)
        status_layout.addWidget(self.volume_label)
        status_layout.addWidget(self.fish_type_label)
        status_layout.addStretch()

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # История показаний с фильтрацией
        history_group = QGroupBox("История показаний")
        history_layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        self.sensor_type_combo = QComboBox()
        self.sensor_type_combo.addItems(["Все датчики", "Температура", "Кислород", "pH"])
        self.sensor_type_combo.currentTextChanged.connect(self.refresh_data)

        filter_layout.addWidget(QLabel("Тип датчика:"))
        filter_layout.addWidget(self.sensor_type_combo)
        filter_layout.addStretch()

        history_layout.addLayout(filter_layout)

        self.readings_table = QTableWidget()
        self.readings_table.setColumnCount(5)
        self.readings_table.setHorizontalHeaderLabels([
            "Время", "Бассейн", "Параметр", "Значение", "Статус"
        ])

        header = self.readings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        history_layout.addWidget(self.readings_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.refresh_data)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Загружаем список бассейнов
        self.load_pools()

    def load_pools(self):
        """Загрузка списка бассейнов"""
        try:
            pools = self.db_manager.get_all_pools()
            self.pool_combo.clear()
            self.pool_combo.addItem("Все бассейны", None)
            for pool in pools:
                self.pool_combo.addItem(
                    f"{pool['Name_Pool']} ({pool['Fish_Type']})",
                    pool['ID_Pool']
                )
        except Exception as e:
            print(f"Ошибка загрузки бассейнов: {e}")

    def on_pool_changed(self):
        """Обработчик изменения выбранного бассейна"""
        self.selected_pool_id = self.pool_combo.currentData()
        self.refresh_data()

    def refresh_data(self):
        """Обновление данных мониторинга"""
        try:
            sensor_type_filter = self.sensor_type_combo.currentText()
            if sensor_type_filter == "Все датчики":
                sensor_type_filter = None

            # Получаем данные в зависимости от выбранного бассейна
            if self.selected_pool_id:
                # Для конкретного бассейна - получаем ВСЕ данные
                readings = self.get_readings_for_selected_pool(sensor_type_filter)

                # Обновляем информацию о бассейне
                pool = self.db_manager.get_pool_by_id(self.selected_pool_id)
                if pool:
                    self.status_label.setText(f"Статус: {pool['Status_Pool']}")
                    self.fish_count_label.setText(f"Рыба: {pool['Fish_Count']} особей")
                    self.volume_label.setText(f"Объем: {pool['Volume_Pool']} м³")
                    self.fish_type_label.setText(f"Тип рыбы: {pool['Fish_Type']}")
            else:
                # Для "Все бассейны" - получаем последние данные
                readings = self.get_readings_for_all_pools(sensor_type_filter)
                self.status_label.setText("Статус: Не выбран")
                self.fish_count_label.setText("Рыба: --")
                self.volume_label.setText("Объем: -- м³")
                self.fish_type_label.setText("Тип рыбы: --")

            # Обновляем текущие показания
            self.update_current_readings(readings)

            # Заполняем таблицу истории
            self.update_readings_table(readings)

        except Exception as e:
            print(f"Ошибка обновления мониторинга: {e}")

    def get_readings_for_selected_pool(self, sensor_type_filter):
        """Получение данных для выбранного бассейна"""
        try:
            # Пробуем использовать новый метод
            if hasattr(self.db_manager, 'get_all_sensor_readings_for_pool'):
                return self.db_manager.get_all_sensor_readings_for_pool(
                    self.selected_pool_id, sensor_type_filter
                )
            else:
                # Если метода нет, используем старый с фильтрацией
                readings = self.db_manager.get_latest_sensor_readings(self.selected_pool_id)
                if sensor_type_filter:
                    readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]
                return readings
        except Exception as e:
            print(f"Ошибка получения данных для бассейна: {e}")
            return []

    def get_readings_for_all_pools(self, sensor_type_filter):
        """Получение данных для всех бассейнов"""
        try:
            readings = self.db_manager.get_latest_sensor_readings()
            if sensor_type_filter:
                readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]
            return readings
        except Exception as e:
            print(f"Ошибка получения данных для всех бассейнов: {e}")
            return []

    def update_current_readings(self, readings):
        """Обновление текущих показаний"""
        try:
            # Сбрасываем все метки
            for param in self.param_labels:
                self.param_labels[param].setText(f"{param}: --")

            if not readings:
                return

            # Группируем показания по бассейнам и типам датчиков
            pool_readings = {}
            for reading in readings:
                pool_id = reading['ID_Pool']
                sensor_type = reading['Type_Sensor']

                if pool_id not in pool_readings:
                    pool_readings[pool_id] = {}

                if sensor_type not in pool_readings[pool_id]:
                    pool_readings[pool_id][sensor_type] = reading

            # Для выбранного бассейна показываем его данные
            if self.selected_pool_id and self.selected_pool_id in pool_readings:
                for sensor_type, reading in pool_readings[self.selected_pool_id].items():
                    if sensor_type in self.param_labels:
                        self.update_param_label(sensor_type, reading)

            # Для "Все бассейны" показываем данные первого бассейна с показаниями
            elif not self.selected_pool_id and pool_readings:
                first_pool_id = list(pool_readings.keys())[0]
                for sensor_type, reading in pool_readings[first_pool_id].items():
                    if sensor_type in self.param_labels:
                        self.update_param_label(sensor_type, reading)

        except Exception as e:
            print(f"Ошибка обновления текущих показаний: {e}")

    def update_param_label(self, sensor_type, reading):
        """Обновление метки параметра"""
        try:
            unit = self.get_unit_for_sensor(sensor_type)
            value = reading['Value_Sensor']
            status = reading['Status_Readings']

            # Форматируем цвет в зависимости от статуса
            color = "green" if status == "Норма" else "orange" if status == "Предупреждение" else "red"
            self.param_labels[sensor_type].setText(
                f"{sensor_type}: <span style='color: {color}; font-weight: bold;'>{value}{unit}</span>"
            )
        except Exception as e:
            print(f"Ошибка обновления метки {sensor_type}: {e}")

    def get_unit_for_sensor(self, sensor_type):
        """Возвращает единицы измерения для типа датчика"""
        units = {
            'Температура': '°C',
            'Кислород': ' мг/л',
            'pH': ''
        }
        return units.get(sensor_type, '')

    def update_readings_table(self, readings):
        """Обновление таблицы с показаниями"""
        try:
            self.readings_table.setRowCount(len(readings))

            for row, reading in enumerate(readings):
                time_str = reading['Timestamp_Sensor'][:16] if reading['Timestamp_Sensor'] else '--'
                pool_id = reading['ID_Pool']
                sensor_type = reading['Type_Sensor']
                value = reading['Value_Sensor']
                status = reading['Status_Readings']

                # Получаем информацию о бассейне
                pool = self.db_manager.get_pool_by_id(pool_id)
                pool_name = pool['Name_Pool'] if pool else f"Бассейн {pool_id}"

                self.readings_table.setItem(row, 0, QTableWidgetItem(time_str))
                self.readings_table.setItem(row, 1, QTableWidgetItem(pool_name))
                self.readings_table.setItem(row, 2, QTableWidgetItem(sensor_type))
                self.readings_table.setItem(row, 3, QTableWidgetItem(str(value)))
                self.readings_table.setItem(row, 4, QTableWidgetItem(status))

            # Показываем количество записей в заголовке
            history_group = self.findChild(QGroupBox, "История показаний")
            if history_group:
                history_group.setTitle(f"История показаний (всего: {len(readings)})")

        except Exception as e:
            print(f"Ошибка обновления таблицы: {e}")

    def setup_timer(self):
        """Настройка автообновления каждые 30 секунд"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)
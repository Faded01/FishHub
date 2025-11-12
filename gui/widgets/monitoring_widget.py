from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer


class MonitoringWidget(QWidget):
    # Константы для единиц измерения
    SENSOR_UNITS = {
        'Температура': '°C',
        'Кислород': ' мг/л',
        'pH': ''
    }

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

        # Текущие показания
        current_group = QGroupBox("Текущие показания")
        current_layout = QGridLayout()

        # Создаем метки для основных параметров
        self.param_labels = {}
        for i, (param, unit) in enumerate(self.SENSOR_UNITS.items()):
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
        """Оптимизированное обновление данных с ограничением записей"""
        try:
            sensor_type_filter = self.sensor_type_combo.currentText()
            if sensor_type_filter == "Все датчики":
                sensor_type_filter = None

            # Используем оптимизированный метод с лимитом записей
            if self.selected_pool_id:
                readings = self.db_manager.get_optimized_sensor_readings(self.selected_pool_id, limit=50)

                # Фильтруем по типу датчика если нужно
                if sensor_type_filter:
                    readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]

                pool = self.db_manager.get_pool_by_id(self.selected_pool_id)
                if pool:
                    self.status_label.setText(f"Статус: {pool['Status_Pool']}")
                    self.fish_count_label.setText(f"Рыба: {pool['Fish_Count']} особей")
                    self.volume_label.setText(f"Объем: {pool['Volume_Pool']} м³")
                    self.fish_type_label.setText(f"Тип рыбы: {pool['Fish_Type']}")
            else:
                # Для всех бассейнов берем меньше данных
                readings = self.db_manager.get_optimized_sensor_readings(limit=30)
                if sensor_type_filter:
                    readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]

                self.status_label.setText("Статус: Все бассейны")
                self.fish_count_label.setText("Рыба: --")
                self.volume_label.setText("Объем: -- м³")
                self.fish_type_label.setText("Тип рыбы: --")

            self.update_current_readings(readings)
            self.update_readings_table(readings)

        except Exception as e:
            print(f"Ошибка обновления мониторинга: {e}")

    def get_latest_readings_for_selected_pool(self, sensor_type_filter):
        """Получение ПОСЛЕДНИХ данных для выбранного бассейна"""
        try:
            # Получаем последние показания для конкретного бассейна
            readings = self.db_manager.get_latest_sensor_readings(self.selected_pool_id)

            if sensor_type_filter:
                readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]

            return readings
        except Exception as e:
            print(f"Ошибка получения последних данных для бассейна: {e}")
            return []

    def get_readings_for_all_pools(self, sensor_type_filter):
        """Получение данных для всех бассейнов (для усреднения)"""
        try:
            # Для "Все бассейны" получаем последние данные каждого бассейна
            readings = self.db_manager.get_latest_sensor_readings()
            if sensor_type_filter:
                readings = [r for r in readings if r['Type_Sensor'] == sensor_type_filter]
            return readings
        except Exception as e:
            print(f"Ошибка получения данных для всех бассейнов: {e}")
            return []

    def update_current_readings(self, readings):
        """
        Обновление текущих показаний
        Для "Все бассейны" - средние значения, для конкретного - последние показания
        """
        try:
            # Сбрасываем все метки
            for param in self.param_labels:
                unit = self.SENSOR_UNITS.get(param, '')
                self.param_labels[param].setText(f"{param}: --{unit}")

            if not readings:
                return

            if self.selected_pool_id:
                # Для конкретного бассейна - показываем ПОСЛЕДНИЕ показания
                self.update_with_latest_readings(readings)
            else:
                # Для "Все бассейны" - показываем СРЕДНИЕ значения
                self.update_with_average_readings(readings)

        except Exception as e:
            print(f"Ошибка обновления текущих показаний: {e}")

    def update_with_latest_readings(self, readings):
        """Обновление ПОСЛЕДНИМИ показаниями для конкретного бассейна"""
        try:
            # Группируем по типам датчиков и берем последнее значение для каждого типа
            latest_readings = {}

            for reading in readings:
                sensor_type = reading['Type_Sensor']
                # Если это первый датчик такого типа или более новый, сохраняем
                if sensor_type not in latest_readings:
                    latest_readings[sensor_type] = reading
                else:
                    # Сравниваем время и берем более новое
                    current_time = reading['Timestamp_Sensor']
                    existing_time = latest_readings[sensor_type]['Timestamp_Sensor']
                    if current_time > existing_time:
                        latest_readings[sensor_type] = reading

            # Обновляем метки
            for sensor_type, reading in latest_readings.items():
                if sensor_type in self.param_labels:
                    self.update_param_label_with_single_value(sensor_type, reading)

        except Exception as e:
            print(f"Ошибка обновления последними показаниями: {e}")

    def update_with_average_readings(self, readings):
        """Обновление СРЕДНИМИ значениями для всех бассейнов"""
        try:
            # Группируем показания по типам датчиков для усреднения
            sensor_groups = {}

            for reading in readings:
                sensor_type = reading['Type_Sensor']
                if sensor_type not in sensor_groups:
                    sensor_groups[sensor_type] = []
                sensor_groups[sensor_type].append(reading)

            # Обновляем метки со средними значениями
            for sensor_type, readings_list in sensor_groups.items():
                if sensor_type in self.param_labels:
                    self.update_param_label_with_average(sensor_type, readings_list)

        except Exception as e:
            print(f"Ошибка обновления средними значениями: {e}")

    def update_param_label_with_single_value(self, sensor_type, reading):
        """Обновление метки одним значением (для конкретного бассейна)"""
        try:
            value = float(reading['Value_Sensor'])
            status = reading['Status_Readings']
            unit = self.SENSOR_UNITS.get(sensor_type, '')

            # Форматируем цвет в зависимости от статуса
            color = "green" if status == "Норма" else "orange" if status == "Предупреждение" else "red"

            # Показываем одно значение с временной меткой
            time_str = reading['Timestamp_Sensor'][11:16] if reading['Timestamp_Sensor'] else ''

            self.param_labels[sensor_type].setText(
                f"{sensor_type}: <span style='color: {color}; font-weight: bold;'>"
                f"{value:.1f}{unit}</span> "
                f"<span style='color: gray; font-size: 9pt;'>({time_str})</span>"
            )
        except Exception as e:
            print(f"Ошибка обновления метки {sensor_type}: {e}")

    def update_param_label_with_average(self, sensor_type, readings_list):
        """Обновление метки средним значением (для всех бассейнов)"""
        try:
            if not readings_list:
                return

            # Вычисляем среднее значение
            values = [float(r['Value_Sensor']) for r in readings_list]
            avg_value = sum(values) / len(values)

            # Определяем статус (берём наихудший)
            statuses = [r['Status_Readings'] for r in readings_list]
            if 'Критично' in statuses:
                status = 'Критично'
            elif 'Предупреждение' in statuses:
                status = 'Предупреждение'
            else:
                status = 'Норма'

            unit = self.SENSOR_UNITS.get(sensor_type, '')

            # Форматируем цвет в зависимости от статуса
            color = "green" if status == "Норма" else "orange" if status == "Предупреждение" else "red"

            # Форматируем среднее значение
            self.param_labels[sensor_type].setText(
                f"{sensor_type}: <span style='color: {color}; font-weight: bold;'>"
                f"{avg_value:.1f}{unit}</span> "
                f"<span style='color: gray; font-size: 9pt;'>(среднее из {len(readings_list)})</span>"
            )
        except Exception as e:
            print(f"Ошибка обновления метки {sensor_type}: {e}")

    def update_readings_table(self, readings):
        """Оптимизированное обновление таблицы"""
        try:
            # Ограничиваем количество отображаемых строк для производительности
            display_limit = 100
            display_readings = readings[:display_limit]

            self.readings_table.setRowCount(len(display_readings))

            for row, reading in enumerate(display_readings):
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
                total_count = len(readings)
                display_count = len(display_readings)
                if total_count > display_count:
                    history_group.setTitle(f"История показаний (показано: {display_count} из {total_count})")
                else:
                    history_group.setTitle(f"История показаний (всего: {total_count})")

        except Exception as e:
            print(f"Ошибка обновления таблицы: {e}")

    def setup_timer(self):
        """Настройка автообновления с увеличенным интервалом"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(15000)  # Увеличили с 5 до 15 секунд
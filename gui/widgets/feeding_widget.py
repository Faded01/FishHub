from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QComboBox, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from datetime import datetime


class FeedingWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Управление кормлением")
        title.setObjectName("widgetTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Форма добавления кормления
        form_group = QGroupBox("Добавить кормление")
        form_layout = QFormLayout()

        # Выбор бассейна
        self.pool_combo = QComboBox()
        self.load_pools()
        form_layout.addRow("Бассейн:", self.pool_combo)

        # Тип корма
        self.feed_type_combo = QComboBox()
        self.feed_type_combo.addItems([
            "Стартовый",
            "Ростовой",
            "Финишный",
            "Лечебный",
            "Гранулы для молоди",
            "Гранулы для взрослых особей",
            "Комбинации крахмальные",
            "Специализированный лечебный"
        ])
        form_layout.addRow("Тип корма:", self.feed_type_combo)

        # Количество корма
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.1, 100.0)
        self.amount_input.setSingleStep(0.1)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" кг")
        form_layout.addRow("Количество:", self.amount_input)

        # Метод кормления
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Автоматический", "Вручную"])
        form_layout.addRow("Метод:", self.method_combo)

        # Кнопка добавления
        self.add_btn = QPushButton("Добавить кормление")
        self.add_btn.clicked.connect(self.add_feeding)
        form_layout.addRow(self.add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # История кормлений
        history_group = QGroupBox("История кормлений")
        history_layout = QVBoxLayout()

        self.feeding_table = QTableWidget()
        self.feeding_table.setColumnCount(6)
        self.feeding_table.setHorizontalHeaderLabels([
            "Бассейн", "Тип корма", "Количество", "Время", "Метод", "Дата"
        ])

        # Настройка ширины колонок - растягиваем равномерно
        header = self.feeding_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Устанавливаем минимальные ширины для важных колонок
        self.feeding_table.setColumnWidth(1, 150)  # Тип корма
        self.feeding_table.setColumnWidth(2, 100)  # Количество

        history_layout.addWidget(self.feeding_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Статистика
        stats_group = QGroupBox("Статистика кормления")
        stats_layout = QHBoxLayout()

        self.today_label = QLabel("Сегодня: 0 кг")
        self.week_label = QLabel("За неделю: 0 кг")
        self.month_label = QLabel("За месяц: 0 кг")

        stats_layout.addWidget(self.today_label)
        stats_layout.addWidget(self.week_label)
        stats_layout.addWidget(self.month_label)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        self.setLayout(layout)

    def load_pools(self):
        """Загрузка списка бассейнов"""
        pools = self.db_manager.get_all_pools()
        self.pool_combo.clear()
        for pool in pools:
            self.pool_combo.addItem(
                f"{pool['Name_Pool']} ({pool['Fish_Type']})",
                pool['ID_Pool']
            )

    def refresh_data(self):
        """Оптимизированное обновление данных кормления"""
        try:
            # История кормлений с ограничением
            feedings = self.db_manager.get_feeding_history()
            display_feedings = feedings[:100]  # Ограничиваем показ 100 записями

            self.feeding_table.setRowCount(len(display_feedings))

            for row, feeding in enumerate(display_feedings):
                # Бассейн
                self.feeding_table.setItem(row, 0, QTableWidgetItem(feeding['Name_Pool']))

                # Тип корма
                feed_type = feeding['Feed_Type']
                self.feeding_table.setItem(row, 1, QTableWidgetItem(feed_type))

                # Количество
                amount = float(feeding['Feed_Amount'])
                self.feeding_table.setItem(row, 2, QTableWidgetItem(f"{amount:.1f} кг"))

                # Время
                feeding_time = feeding['Feeding_Time']
                if feeding_time and ' ' in feeding_time:
                    time_str = feeding_time.split(' ')[1][:8]
                else:
                    time_str = '--:--:--'
                self.feeding_table.setItem(row, 3, QTableWidgetItem(time_str))

                # Метод
                self.feeding_table.setItem(row, 4, QTableWidgetItem(feeding['Feeding_Method']))

                # Дата
                if feeding_time:
                    date_str = feeding_time[:10]
                else:
                    date_str = '--'
                self.feeding_table.setItem(row, 5, QTableWidgetItem(date_str))

            # Обновляем отображение таблицы
            self.feeding_table.resizeColumnsToContents()

            # Статистика
            stats = self.db_manager.get_feeding_statistics()
            if stats:
                today_amount = stats['today'] if stats['today'] else 0
                week_amount = stats['week'] if stats['week'] else 0
                month_amount = stats['month'] if stats['month'] else 0

                self.today_label.setText(f"Сегодня: {today_amount:.1f} кг")
                self.week_label.setText(f"За неделю: {week_amount:.1f} кг")
                self.month_label.setText(f"За месяц: {month_amount:.1f} кг")

        except Exception as e:
            print(f"Ошибка обновления кормления: {e}")

    def add_feeding(self):
        try:
            pool_id = self.pool_combo.currentData()
            feed_type = self.feed_type_combo.currentText()
            amount = self.amount_input.value()
            method = self.method_combo.currentText()

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            if amount <= 0:
                QMessageBox.warning(self, "Ошибка", "Введите количество корма!")
                return

            success = self.db_manager.add_feeding(
                pool_id, feed_type, amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                method
            )

            if success:
                QMessageBox.information(self, "Успех", "Кормление добавлено!")
                self.amount_input.setValue(0.1)
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить кормление")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")
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
        self.feed_type_combo.addItems(["Стартовый", "Ростовой", "Финишный", "Лечебный"])
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
        self.feeding_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        """Обновление данных кормления"""
        try:
            # История кормлений
            feedings = self.db_manager.get_feeding_history()
            self.feeding_table.setRowCount(len(feedings))

            for row, feeding in enumerate(feedings):
                self.feeding_table.setItem(row, 0, QTableWidgetItem(feeding['Name_Pool']))
                self.feeding_table.setItem(row, 1, QTableWidgetItem(feeding['Feed_Type']))
                self.feeding_table.setItem(row, 2, QTableWidgetItem(f"{feeding['Feed_Amount']} кг"))
                self.feeding_table.setItem(row, 3, QTableWidgetItem(feeding['Feeding_Time'][11:16]))  # Время
                self.feeding_table.setItem(row, 4, QTableWidgetItem(feeding['Feeding_Method']))
                self.feeding_table.setItem(row, 5, QTableWidgetItem(feeding['Feeding_Time'][:10]))  # Дата

            # Статистика
            stats = self.db_manager.get_feeding_statistics()
            if stats:
                self.today_label.setText(f"Сегодня: {stats['today'] or 0} кг")
                self.week_label.setText(f"За неделю: {stats['week'] or 0} кг")
                self.month_label.setText(f"За месяц: {stats['month'] or 0} кг")

        except Exception as e:
            print(f"Ошибка обновления кормления: {e}")

    def add_feeding(self):
        """Добавление нового кормления"""
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

            # Добавляем кормление
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
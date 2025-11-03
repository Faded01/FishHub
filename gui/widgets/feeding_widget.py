from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QLabel, QComboBox, QSpinBox,
                             QDoubleSpinBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from datetime import datetime


class FeedingWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_pools()
        self.refresh_feeding_table()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Управление кормлением")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Форма добавления кормления
        form_group = QGroupBox("Добавить кормление")
        form_layout = QFormLayout()

        self.pool_combo = QComboBox()
        self.feed_type_combo = QComboBox()
        self.feed_type_combo.addItems(["Стартовый", "Ростовой", "Финишный", "Лечебный"])

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.1, 100.0)
        self.amount_spin.setSuffix(" кг")

        self.method_combo = QComboBox()
        self.method_combo.addItems(["Автоматический", "Ручной"])

        form_layout.addRow("Бассейн:", self.pool_combo)
        form_layout.addRow("Тип корма:", self.feed_type_combo)
        form_layout.addRow("Количество:", self.amount_spin)
        form_layout.addRow("Метод:", self.method_combo)

        self.add_feeding_btn = QPushButton("Добавить кормление")
        self.add_feeding_btn.clicked.connect(self.add_feeding)

        form_layout.addRow(self.add_feeding_btn)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Таблица кормлений
        table_group = QGroupBox("История кормлений")
        table_layout = QVBoxLayout()

        self.feeding_table = QTableWidget()
        self.feeding_table.setColumnCount(5)
        self.feeding_table.setHorizontalHeaderLabels([
            "Бассейн", "Тип корма", "Количество", "Время", "Метод"
        ])
        self.feeding_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table_layout.addWidget(self.feeding_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Статистика
        stats_group = QGroupBox("Статистика кормления")
        stats_layout = QHBoxLayout()

        self.daily_stats = QLabel("Сегодня: 0 кг")
        self.weekly_stats = QLabel("За неделю: 0 кг")
        self.monthly_stats = QLabel("За месяц: 0 кг")

        stats_layout.addWidget(self.daily_stats)
        stats_layout.addWidget(self.weekly_stats)
        stats_layout.addWidget(self.monthly_stats)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

    def load_pools(self):
        """Загрузка списка бассейнов"""
        # Демо-данные
        pools = ["Бассейн 1 (Форель)", "Бассейн 2 (Осетр)", "Бассейн 3 (Карп)"]
        self.pool_combo.clear()
        self.pool_combo.addItems(pools)

    def add_feeding(self):
        """Добавление нового кормления"""
        pool = self.pool_combo.currentText()
        feed_type = self.feed_type_combo.currentText()
        amount = self.amount_spin.value()
        method = self.method_combo.currentText()

        if amount <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите количество корма")
            return

        # Сохранение в БД
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedings (pool_id, feed_type, amount, feeding_time, feeding_method)
                VALUES (?, ?, ?, ?, ?)
            ''', (1, feed_type, amount, datetime.now().isoformat(), method))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Кормление добавлено")
            self.refresh_feeding_table()
            self.update_statistics()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {str(e)}")

    def refresh_feeding_table(self):
        """Обновление таблицы кормлений"""
        # Демо-данные
        feedings = [
            ("Бассейн 1", "Ростовой", "2.5 кг", "10:00", "Автоматический"),
            ("Бассейн 2", "Стартовый", "1.8 кг", "09:30", "Ручной"),
            ("Бассейн 3", "Финишный", "3.2 кг", "11:15", "Автоматический"),
        ]

        self.feeding_table.setRowCount(len(feedings))
        for row, (pool, feed_type, amount, time, method) in enumerate(feedings):
            self.feeding_table.setItem(row, 0, QTableWidgetItem(pool))
            self.feeding_table.setItem(row, 1, QTableWidgetItem(feed_type))
            self.feeding_table.setItem(row, 2, QTableWidgetItem(amount))
            self.feeding_table.setItem(row, 3, QTableWidgetItem(time))
            self.feeding_table.setItem(row, 4, QTableWidgetItem(method))

    def update_statistics(self):
        """Обновление статистики"""
        # Демо-статистика
        self.daily_stats.setText("Сегодня: 7.5 кг")
        self.weekly_stats.setText("За неделю: 45.2 кг")
        self.monthly_stats.setText("За месяц: 180.5 кг")
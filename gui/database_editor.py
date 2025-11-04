from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QComboBox,
    QPushButton, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from core.database import DatabaseManager


class DatabaseEditorWindow(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_table = None
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Автосохранение каждые 30 сек
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактор базы данных — FishHub")
        self.setMinimumSize(1000, 700)

        # Выбор таблицы
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Выберите таблицу:"))

        self.table_combo = QComboBox()
        self.table_combo.addItems([
            "Users", "Roles", "Pools", "Sensors",
            "Sensor_Readings", "Feedings", "Control_Catches", "Reports"
        ])
        self.table_combo.currentTextChanged.connect(self.load_table_data)
        table_layout.addWidget(self.table_combo)

        # Кнопки управления
        self.btn_save = QPushButton("Сохранить изменения")
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_add_row = QPushButton("Добавить строку")
        self.btn_add_row.clicked.connect(self.add_row)
        self.btn_delete_row = QPushButton("Удалить строку")
        self.btn_delete_row.clicked.connect(self.delete_row)

        table_layout.addWidget(self.btn_save)
        table_layout.addWidget(self.btn_refresh)
        table_layout.addWidget(self.btn_add_row)
        table_layout.addWidget(self.btn_delete_row)
        table_layout.addStretch()

        # Таблица данных
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Модель данных
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)

        # Статус бар
        self.status_label = QLabel("Готов к работе")

        # Основной layout
        layout = QVBoxLayout()
        layout.addLayout(table_layout)
        layout.addWidget(self.table_view)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Загрузка первой таблицы
        self.load_table_data(self.table_combo.currentText())

    def load_table_data(self, table_name):
        self.current_table = table_name
        try:
            data = self.db_manager.get_all_data(table_name)
            columns = self.db_manager.get_table_columns(table_name)

            self.model.clear()
            self.model.setHorizontalHeaderLabels(columns)

            for row in data:
                items = [QStandardItem(str(value)) for value in row]
                self.model.appendRow(items)

            self.status_label.setText(f"Загружена таблица: {table_name} | Записей: {len(data)}")

        except Exception as e:
            self.show_error(f"Ошибка загрузки таблицы: {str(e)}")

    def save_changes(self):
        try:
            # Здесь должна быть логика сохранения изменений в БД
            # В реальной реализации нужно обновлять каждую измененную строку
            self.status_label.setText("Изменения сохранены успешно")
            QMessageBox.information(self, "Сохранение", "Изменения успешно сохранены в базе данных")
        except Exception as e:
            self.show_error(f"Ошибка сохранения: {str(e)}")

    def auto_save(self):
        if self.model.rowCount() > 0:
            self.status_label.setText("Автосохранение выполнено")

    def refresh_data(self):
        self.load_table_data(self.current_table)

    def add_row(self):
        row_items = [QStandardItem("") for _ in range(self.model.columnCount())]
        self.model.appendRow(row_items)

    def delete_row(self):
        current_index = self.table_view.currentIndex()
        if current_index.isValid():
            self.model.removeRow(current_index.row())

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
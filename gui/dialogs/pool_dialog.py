from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QTabWidget, QWidget)
from PyQt6.QtCore import QDate


class PoolManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Управление бассейнами")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
        self.load_pools()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Вкладки
        tabs = QTabWidget()

        # Вкладка списка бассейнов
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)

        # Таблица бассейнов
        self.pools_table = QTableWidget()
        self.pools_table.setColumnCount(6)
        self.pools_table.setHorizontalHeaderLabels([
            "Название", "Объем", "Тип рыбы", "Количество", "Дата зарыбления", "Статус"
        ])
        self.pools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        list_layout.addWidget(self.pools_table)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.add_btn.clicked.connect(self.add_pool)
        self.edit_btn.clicked.connect(self.edit_pool)
        self.delete_btn.clicked.connect(self.delete_pool)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        list_layout.addLayout(btn_layout)

        # Вкладка добавления/редактирования
        self.edit_tab = QWidget()
        self.setup_edit_tab()

        tabs.addTab(list_tab, "Список бассейнов")
        tabs.addTab(self.edit_tab, "Добавить/Редактировать")

        layout.addWidget(tabs)

        # Кнопки диалога
        dialog_btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)

        dialog_btn_layout.addStretch()
        dialog_btn_layout.addWidget(self.close_btn)

        layout.addLayout(dialog_btn_layout)

    def setup_edit_tab(self):
        layout = QFormLayout(self.edit_tab)

        self.name_edit = QLineEdit()
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(1, 1000)
        self.volume_spin.setSuffix(" м³")

        self.fish_type_combo = QComboBox()
        self.fish_type_combo.addItems(["Форель", "Осетр", "Карп", "Тиляпия", "Сом"])

        self.fish_count_spin = QSpinBox()
        self.fish_count_spin.setRange(0, 100000)

        self.stocking_date = QDateEdit()
        self.stocking_date.setDate(QDate.currentDate())
        self.stocking_date.setCalendarPopup(True)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["активен", "на обслуживании", "закрыт"])

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_pool)

        layout.addRow("Название:", self.name_edit)
        layout.addRow("Объем:", self.volume_spin)
        layout.addRow("Тип рыбы:", self.fish_type_combo)
        layout.addRow("Количество рыбы:", self.fish_count_spin)
        layout.addRow("Дата зарыбления:", self.stocking_date)
        layout.addRow("Статус:", self.status_combo)
        layout.addRow(self.save_btn)

    def load_pools(self):
        """Загрузка списка бассейнов"""
        # Демо-данные
        pools = [
            ("Бассейн 1", "50 м³", "Форель", "5000", "2024-01-10", "активен"),
            ("Бассейн 2", "75 м³", "Осетр", "3000", "2024-01-15", "активен"),
            ("Бассейн 3", "60 м³", "Карп", "8000", "2024-01-20", "на обслуживании"),
        ]

        self.pools_table.setRowCount(len(pools))
        for row, (name, volume, fish_type, count, date, status) in enumerate(pools):
            self.pools_table.setItem(row, 0, QTableWidgetItem(name))
            self.pools_table.setItem(row, 1, QTableWidgetItem(volume))
            self.pools_table.setItem(row, 2, QTableWidgetItem(fish_type))
            self.pools_table.setItem(row, 3, QTableWidgetItem(count))
            self.pools_table.setItem(row, 4, QTableWidgetItem(date))
            self.pools_table.setItem(row, 5, QTableWidgetItem(status))

    def add_pool(self):
        """Добавление нового бассейна"""
        self.name_edit.clear()
        self.volume_spin.setValue(50)
        self.fish_count_spin.setValue(1000)
        self.stocking_date.setDate(QDate.currentDate())
        self.status_combo.setCurrentText("активен")

    def edit_pool(self):
        """Редактирование выбранного бассейна"""
        current_row = self.pools_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите бассейн для редактирования")
            return

        # Заполнение формы данными выбранного бассейна
        name = self.pools_table.item(current_row, 0).text()
        # ... заполнение остальных полей

    def delete_pool(self):
        """Удаление бассейна"""
        current_row = self.pools_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите бассейн для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить выбранный бассейн?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Логика удаления из БД
            self.pools_table.removeRow(current_row)

    def save_pool(self):
        """Сохранение бассейна"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название бассейна")
            return

        # Логика сохранения в БД
        QMessageBox.information(self, "Успех", "Бассейн сохранен")
        self.load_pools()  # Обновление списка
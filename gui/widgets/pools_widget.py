from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLabel, QMessageBox, QHeaderView, QLineEdit, QFormLayout,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from core.database import DatabaseManager


class PoolsWidget(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_pools_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Управление бассейнами")
        title.setObjectName("widgetTitle")
        layout.addWidget(title)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить бассейн")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.add_pool)
        self.btn_edit.clicked.connect(self.edit_pool)
        self.btn_delete.clicked.connect(self.delete_pool)
        self.btn_refresh.clicked.connect(self.load_pools_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Таблица бассейнов
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            'ID', 'Название', 'Объем', 'Тип рыбы', 'Количество',
            'Дата зарыбления', 'Статус'
        ])
        self.table_view.setModel(self.model)

        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def load_pools_data(self):
        try:
            pools = self.db_manager.get_all_data('Pools')
            self.model.setRowCount(0)

            for pool in pools:
                row = [QStandardItem(str(item)) for item in pool]
                self.model.appendRow(row)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def add_pool(self):
        dialog = PoolDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_pools_data()

    def edit_pool(self):
        # Реализация редактирования
        pass

    def delete_pool(self):
        # Реализация удаления
        pass


class PoolDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавление бассейна")
        self.setFixedSize(400, 300)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.volume_input = QLineEdit()
        self.fish_type_input = QLineEdit()
        self.fish_count_input = QLineEdit()
        self.stocking_date_input = QLineEdit()
        self.status_input = QLineEdit()

        layout.addRow("Название:", self.name_input)
        layout.addRow("Объем (м³):", self.volume_input)
        layout.addRow("Тип рыбы:", self.fish_type_input)
        layout.addRow("Количество:", self.fish_count_input)
        layout.addRow("Дата зарыбления:", self.stocking_date_input)
        layout.addRow("Статус:", self.status_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)
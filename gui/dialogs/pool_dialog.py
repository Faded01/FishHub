from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


class PoolManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Управление бассейнами")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_pools()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Управление бассейнами")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # Форма добавления/редактирования
        form_group = QGroupBox("Добавить/Редактировать бассейн")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название бассейна")
        form_layout.addRow("Название:", self.name_input)

        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("Объем в м³")
        form_layout.addRow("Объем:", self.volume_input)

        self.fish_type_input = QLineEdit()
        self.fish_type_input.setPlaceholderText("Вид рыбы")
        form_layout.addRow("Тип рыбы:", self.fish_type_input)

        self.fish_count_input = QLineEdit()
        self.fish_count_input.setPlaceholderText("Количество особей")
        form_layout.addRow("Количество:", self.fish_count_input)

        self.stocking_date = QDateEdit()
        self.stocking_date.setDate(QDate.currentDate())
        self.stocking_date.setCalendarPopup(True)
        form_layout.addRow("Дата зарыбления:", self.stocking_date)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Активен", "На обслуживании"])
        form_layout.addRow("Статус:", self.status_combo)

        # Кнопки формы
        form_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_pool)

        self.update_btn = QPushButton("Обновить")
        self.update_btn.clicked.connect(self.update_pool)
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

        # Таблица бассейнов
        table_group = QGroupBox("Список бассейнов")
        table_layout = QVBoxLayout()

        self.pools_table = QTableWidget()
        self.pools_table.setColumnCount(7)
        self.pools_table.setHorizontalHeaderLabels([
            "ID", "Название", "Объем", "Тип рыбы", "Количество", "Дата зарыбления", "Статус"
        ])
        self.pools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pools_table.cellDoubleClicked.connect(self.edit_pool)
        table_layout.addWidget(self.pools_table)

        # Кнопки управления таблицей
        table_buttons_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_pools)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_pool)

        table_buttons_layout.addWidget(self.refresh_btn)
        table_buttons_layout.addWidget(self.delete_btn)
        table_buttons_layout.addStretch()

        table_layout.addLayout(table_buttons_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.current_pool_id = None

    def load_pools(self):
        """Загрузка списка бассейнов"""
        try:
            pools = self.db_manager.get_all_pools()
            self.pools_table.setRowCount(len(pools))

            for row, pool in enumerate(pools):
                self.pools_table.setItem(row, 0, QTableWidgetItem(str(pool['ID_Pool'])))
                self.pools_table.setItem(row, 1, QTableWidgetItem(pool['Name_Pool']))
                self.pools_table.setItem(row, 2, QTableWidgetItem(str(pool['Volume_Pool'])))
                self.pools_table.setItem(row, 3, QTableWidgetItem(pool['Fish_Type']))
                self.pools_table.setItem(row, 4, QTableWidgetItem(str(pool['Fish_Count'])))
                self.pools_table.setItem(row, 5, QTableWidgetItem(pool['Stocking_Date']))
                self.pools_table.setItem(row, 6, QTableWidgetItem(pool['Status_Pool']))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки бассейнов: {e}")

    def add_pool(self):
        """Добавление нового бассейна"""
        try:
            name = self.name_input.text().strip()
            volume = self.volume_input.text().strip()
            fish_type = self.fish_type_input.text().strip()
            fish_count = self.fish_count_input.text().strip()
            stocking_date = self.stocking_date.date().toString("yyyy-MM-dd")
            status = self.status_combo.currentText()

            if not all([name, volume, fish_type, fish_count]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return

            success = self.db_manager.add_pool(
                name, float(volume), fish_type, int(fish_count), stocking_date, status
            )

            if success:
                QMessageBox.information(self, "Успех", "Бассейн добавлен!")
                self.clear_form()
                self.load_pools()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить бассейн")

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность числовых значений!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def edit_pool(self, row, column):
        """Редактирование бассейна по двойному клику"""
        try:
            pool_id = int(self.pools_table.item(row, 0).text())
            pool = self.db_manager.get_pool_by_id(pool_id)

            if pool:
                self.current_pool_id = pool_id
                self.name_input.setText(pool['Name_Pool'])
                self.volume_input.setText(str(pool['Volume_Pool']))
                self.fish_type_input.setText(pool['Fish_Type'])
                self.fish_count_input.setText(str(pool['Fish_Count']))
                self.stocking_date.setDate(QDate.fromString(pool['Stocking_Date'], "yyyy-MM-dd"))
                self.status_combo.setCurrentText(pool['Status_Pool'])

                self.add_btn.setEnabled(False)
                self.update_btn.setEnabled(True)

        except Exception as e:
            print(f"Ошибка редактирования: {e}")

    def update_pool(self):
        """Обновление бассейна"""
        try:
            if not self.current_pool_id:
                return

            name = self.name_input.text().strip()
            volume = self.volume_input.text().strip()
            fish_type = self.fish_type_input.text().strip()
            fish_count = self.fish_count_input.text().strip()
            stocking_date = self.stocking_date.date().toString("yyyy-MM-dd")
            status = self.status_combo.currentText()

            if not all([name, volume, fish_type, fish_count]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return

            success = self.db_manager.update_pool(
                self.current_pool_id, name, float(volume), fish_type,
                int(fish_count), stocking_date, status
            )

            if success:
                QMessageBox.information(self, "Успех", "Бассейн обновлен!")
                self.clear_form()
                self.load_pools()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить бассейн")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {e}")

    def delete_pool(self):
        """Удаление выбранного бассейна"""
        try:
            current_row = self.pools_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн для удаления!")
                return

            pool_id = int(self.pools_table.item(current_row, 0).text())
            pool_name = self.pools_table.item(current_row, 1).text()

            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить бассейн '{pool_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.db_manager.delete_pool(pool_id)
                if success:
                    QMessageBox.information(self, "Успех", "Бассейн удален!")
                    self.load_pools()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить бассейн")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def clear_form(self):
        """Очистка формы"""
        self.current_pool_id = None
        self.name_input.clear()
        self.volume_input.clear()
        self.fish_type_input.clear()
        self.fish_count_input.clear()
        self.stocking_date.setDate(QDate.currentDate())
        self.status_combo.setCurrentIndex(0)

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
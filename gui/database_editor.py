from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QComboBox,
    QPushButton, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from core.database import DatabaseManager
from core.excel_exporter import ExcelExporter


class DatabaseEditorWindow(QWidget):
    def __init__(self, db_manager: DatabaseManager, user_data=None):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_table = None
        self.modified_cells = set()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(10000)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактор базы данных — FishHub")
        if self.user_data:
            self.setWindowTitle(
                f"Редактор базы данных — FishHub (Администратор: {self.user_data.get('full_name', 'Неизвестно')})")

        self.setMinimumSize(1300, 800)  # Увеличил минимальный размер

        # Основной layout
        main_layout = QVBoxLayout()

        # Контейнер для содержимого с отступами
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Выбор таблицы
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Выберите таблицу:"))

        self.table_combo = QComboBox()
        self.load_table_names()
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
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_export.clicked.connect(self.export_to_excel)

        table_layout.addWidget(self.btn_save)
        table_layout.addWidget(self.btn_refresh)
        table_layout.addWidget(self.btn_add_row)
        table_layout.addWidget(self.btn_delete_row)
        table_layout.addWidget(self.btn_export)
        table_layout.addStretch()

        # Таблица данных
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)

        # Настройка отображения таблицы
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Модель данных
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.on_cell_changed)
        self.table_view.setModel(self.model)

        # Статус бар
        self.status_label = QLabel("Готов к работе")

        # Собираем layout
        content_layout.addLayout(table_layout)
        content_layout.addWidget(self.table_view)
        content_layout.addWidget(self.status_label)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        # Загрузка первой таблицы
        if self.table_combo.count() > 0:
            self.load_table_data(self.table_combo.currentText())

    def load_table_data(self, russian_table_name):
        table_name = self.table_combo.currentData()
        if not table_name:
            return

        self.current_table = table_name
        try:
            data = self.db_manager.get_all_data(table_name)
            russian_columns = self.get_russian_columns(table_name)

            self.model.clear()
            self.model.setHorizontalHeaderLabels(russian_columns)

            for row in data:
                items = [QStandardItem(str(value) if value is not None else "") for value in row]
                for item in items:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model.appendRow(items)

            for i in range(self.model.columnCount()):
                self.model.setHeaderData(i, Qt.Orientation.Horizontal, Qt.AlignmentFlag.AlignCenter,
                                         Qt.ItemDataRole.TextAlignmentRole)

            for i in range(self.model.columnCount()):
                self.table_view.setColumnWidth(i, 150)

            self.status_label.setText(f"Загружена таблица: {russian_table_name} | Записей: {len(data)}")

        except Exception as e:
            self.show_error(f"Ошибка загрузки таблицы: {str(e)}")

    def load_table_names(self):
        """Автоматическая загрузка таблиц с русскими названиями"""
        table_mapping = {
            "Employees": "Сотрудники",
            "Roles": "Роли",
            "Pools": "Бассейны",
            "Sensors": "Датчики",
            "Sensor_Readings": "Показания датчиков",
            "Feedings": "Кормления",
            "Control_Catches": "Контрольные обловы",
            "Reports": "Отчеты"
        }

        actual_tables = self.db_manager.get_table_names()
        user_tables = [table for table in actual_tables if not table.startswith('sqlite_')]

        for table in user_tables:
            russian_name = table_mapping.get(table, table)
            self.table_combo.addItem(russian_name, table)

    # ... остальные методы без изменений

    def get_russian_columns(self, table_name):
        """Возвращает русские названия колонок для таблицы"""
        columns_mapping = {
            "Employees": {
                "ID_User": "ID пользователя",
                "Username": "Логин",
                "Password_User": "Пароль",
                "Name_User": "Имя",
                "Surname_User": "Фамилия",
                "Patronymic_User": "Отчество",
                "Role_ID": "ID роли",
                "Status": "Статус",
                "Created_At": "Дата создания",
                "Seriya_Passport": "Серия паспорта",
                "Number_Passport": "Номер паспорта"
            },
            "Roles": {
                "ID_Role": "ID роли",
                "Name_Role": "Название роли",
                "Role_Description": "Описание роли",
                "Admin_Permission": "Права администратора"
            },
            "Pools": {
                "ID_Pool": "ID бассейна",
                "Name_Pool": "Название бассейна",
                "Volume_Pool": "Объем",
                "Fish_Type": "Тип рыбы",
                "Fish_Count": "Количество рыбы",
                "Stocking_Date": "Дата зарыбления",
                "Status_Pool": "Статус бассейна"
            },
            "Sensors": {
                "ID_Sensor": "ID датчика",
                "ID_Pool": "ID бассейна",
                "Type_Sensor": "Тип датчика",
                "Model_Sensor": "Модель датчика",
                "Range_Min": "Диапазон от",
                "Range_Max": "Диапазон до",
                "Installation_Date": "Дата установки"
            },
            "Sensor_Readings": {
                "ID_Record": "ID записи",
                "ID_Sensor": "ID датчика",
                "Value_Sensor": "Значение",
                "Timestamp_Sensor": "Время измерения",
                "Status_Readings": "Статус показаний"
            },
            "Feedings": {
                "ID_Feeding": "ID кормления",
                "ID_Pool": "ID бассейна",
                "Feed_Type": "Тип корма",
                "Feed_Amount": "Количество корма",
                "Feeding_Time": "Время кормления",
                "Feeding_Method": "Способ кормления"
            },
            "Control_Catches": {
                "ID_Fishing": "ID облова",
                "ID_Pool": "ID бассейна",
                "Average_Weight": "Средний вес",
                "Fish_Count": "Количество рыбы",
                "Fishing_Date": "Дата облова",
                "Note": "Примечание"
            },
            "Reports": {
                "ID_Report": "ID отчета",
                "ID_Pool": "ID бассейна",
                "ID_User": "ID пользователя",
                "Report_Type": "Тип отчета",
                "Period_Start": "Начало периода",
                "Period_End": "Конец периода",
                "Date_Formation": "Дата формирования",
                "Report_Data": "Данные отчета"
            }
        }

        english_columns = self.db_manager.get_table_columns(table_name)
        russian_columns = []

        for col in english_columns:
            russian_name = columns_mapping.get(table_name, {}).get(col, col)
            russian_columns.append(russian_name)

        return russian_columns

    def on_cell_changed(self, item):
        """Обработчик изменения ячейки - автоматическое сохранение"""
        if self.current_table:
            row = item.row()
            column = item.column()
            self.modified_cells.add((row, column))
            self.status_label.setText("Изменения не сохранены (автосохранение через 10 сек)")

    def auto_save(self):
        """Автоматическое сохранение измененных ячеек"""
        if self.modified_cells and self.current_table:
            try:
                self.save_modified_cells()
                self.modified_cells.clear()
                self.status_label.setText("Автосохранение выполнено")
            except Exception as e:
                self.status_label.setText(f"Ошибка автосохранения: {str(e)}")

    def save_modified_cells(self):
        """Сохранение измененных ячеек с учетом новых строк"""
        try:
            table_name = self.table_combo.currentData()
            columns = self.db_manager.get_table_columns(table_name)

            for row, col in self.modified_cells:
                primary_key_col = 0
                primary_key_item = self.model.item(row, primary_key_col)

                if not primary_key_item:
                    continue

                primary_key = primary_key_item.text()
                new_value = self.model.item(row, col).text()
                column_name = columns[col]

                # Если primary_key пустой - это новая строка, нужно вставить
                if not primary_key.strip():
                    # Создаем новую строку в БД
                    placeholders = ", ".join(["?" for _ in range(len(columns))])
                    column_names = ", ".join(columns)

                    values = []
                    for i in range(len(columns)):
                        item = self.model.item(row, i)
                        values.append(item.text() if item else "")

                    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                    self.db_manager.cursor.execute(query, values)
                    self.db_manager.connection.commit()

                    # Обновляем ID в интерфейсе
                    new_id = self.db_manager.cursor.lastrowid
                    if new_id:
                        self.model.item(row, primary_key_col).setText(str(new_id))

                else:
                    # Обновляем существующую строку
                    query = f"UPDATE {table_name} SET {column_name} = ? WHERE {columns[0]} = ?"
                    self.db_manager.cursor.execute(query, (new_value, primary_key))

            self.db_manager.connection.commit()

        except Exception as e:
            raise Exception(f"Ошибка сохранения ячеек: {str(e)}")

    def save_changes(self):
        """Ручное сохранение изменений"""
        try:
            if self.modified_cells:
                self.save_modified_cells()
                self.modified_cells.clear()
                self.status_label.setText("Изменения сохранены успешно")
                QMessageBox.information(self, "Сохранение", "Изменения успешно сохранены в базе данных")
            else:
                self.status_label.setText("Нет изменений для сохранения")
                QMessageBox.information(self, "Сохранение", "Нет изменений для сохранения")

        except Exception as e:
            self.show_error(f"Ошибка сохранения: {str(e)}")

    def refresh_data(self):
        """Обновление данных таблицы"""
        current_table = self.table_combo.currentText()
        self.load_table_data(current_table)
        self.modified_cells.clear()

    def add_row(self):
        """Упрощенное добавление строки"""
        try:
            table_name = self.table_combo.currentData()
            if not table_name:
                QMessageBox.warning(self, "Ошибка", "Выберите таблицу!")
                return

            # Получаем колонки таблицы
            columns = self.db_manager.get_table_columns(table_name)
            if not columns:
                self.show_error("Не удалось получить структуру таблицы")
                return

            # Исключаем первую колонку (предполагаем что это ID)
            if len(columns) > 1:
                insert_columns = columns[1:]  # Все колонки кроме первой
            else:
                insert_columns = columns

            # Формируем значения по умолчанию
            values = ["Новое значение" for _ in insert_columns]

            # Формируем и выполняем INSERT запрос
            placeholders = ", ".join(["?" for _ in insert_columns])
            column_names = ", ".join(insert_columns)

            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

            print(f"DEBUG: Executing: {query}")
            print(f"DEBUG: Values: {values}")

            self.db_manager.cursor.execute(query, values)
            self.db_manager.connection.commit()

            # Обновляем интерфейс
            self.refresh_data()

            self.status_label.setText("Новая строка добавлена в базу данных")
            QMessageBox.information(self, "Успех", "Строка успешно добавлена в базу данных")

        except Exception as e:
            self.show_error(f"Ошибка добавления строки: {str(e)}")

    def get_detailed_table_info(self, table_name):
        """Получает детальную информацию о колонках таблицы"""
        try:
            self.db_manager.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.db_manager.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения информации о таблице: {e}")
            return []

    def prepare_insert_data(self, table_name, table_info):
        """Подготавливает данные для INSERT запроса"""
        columns = []
        values = []

        for col_info in table_info:
            col_name = col_info[1]
            col_type = col_info[2]
            not_null = col_info[3] == 1
            default_value = col_info[4]
            is_primary = col_info[5] == 1

            # Пропускаем AUTOINCREMENT primary keys
            if is_primary and self.is_autoincrement(table_name, col_name):
                continue

            # Для внешних ключей проверяем существование записей
            if col_name.startswith('ID_') and col_name != 'ID_User':
                if not self.has_records_for_foreign_key(table_name, col_name):
                    continue
                # Устанавливаем первый доступный ID
                values.append(1)
            else:
                # Используем значение по умолчанию из БД или наше
                if default_value is not None:
                    values.append(default_value)
                else:
                    values.append(self.get_default_value(col_name))

            columns.append(col_name)

        return {
            'columns': columns,
            'columns_str': ", ".join(columns),
            'placeholders': ", ".join(["?" for _ in columns]),
            'values': values
        }

    def is_autoincrement(self, table_name, column_name):
        """Проверяет, является ли поле AUTOINCREMENT"""
        # В SQLite поле считается AUTOINCREMENT если оно INTEGER PRIMARY KEY
        try:
            self.db_manager.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.db_manager.cursor.fetchall()

            for col in columns:
                if col[1] == column_name and col[5] == 1:  # PRIMARY KEY
                    return "INT" in col[2].upper()
            return False
        except Exception:
            return False

    def delete_row(self):
        """Удаление строки из БД"""
        try:
            current_index = self.table_view.currentIndex()
            if not current_index.isValid():
                QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления!")
                return

            table_name = self.table_combo.currentData()
            columns = self.db_manager.get_table_columns(table_name)
            row = current_index.row()

            # Получаем первичный ключ
            primary_key_item = self.model.item(row, 0)
            if not primary_key_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID строки!")
                return

            primary_key = primary_key_item.text()

            # Подтверждение удаления
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить эту строку? (ID: {primary_key})",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                query = f"DELETE FROM {table_name} WHERE {columns[0]} = ?"
                self.db_manager.cursor.execute(query, (primary_key,))
                self.db_manager.connection.commit()

                # Удаляем из модели только после успешного удаления из БД
                self.model.removeRow(row)

                self.status_label.setText("Строка удалена из базы данных")
                QMessageBox.information(self, "Успех", "Строка успешно удалена из базы данных")

        except Exception as e:
            self.show_error(f"Ошибка удаления: {str(e)}")

    def export_to_excel(self):
        """Экспорт текущей таблицы в Excel"""
        try:
            table_name = self.table_combo.currentData()
            if not table_name:
                QMessageBox.warning(self, "Ошибка", "Выберите таблицу для экспорта!")
                return

            data = self.db_manager.get_all_data(table_name)
            if not data:
                QMessageBox.warning(self, "Ошибка", "В выбранной таблице нет данных!")
                return

            russian_columns = self.get_russian_columns(table_name)

            success, message = ExcelExporter.export_table_to_excel(
                data=data,
                columns=russian_columns,
                sheet_name=table_name
            )

            if success:
                QMessageBox.information(self, "Успех", message)
                self.status_label.setText(f"Экспорт завершен: {message}")
            else:
                QMessageBox.critical(self, "Ошибка", message)
                self.status_label.setText(f"Ошибка экспорта: {message}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        try:
            user_id = self.user_data.get("id")
            if user_id:
                self.db_manager.update_user_status_by_id(user_id, "Отключён")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось сбросить статус пользователя при выходе: {e}")
        event.accept()

    def handle_exit(self):
        """Обработка выхода"""
        self.close()
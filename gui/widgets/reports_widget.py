from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from core.excel_exporter import ExcelExporter
from gui.dialogs.report_dialog import ReportDialog


class ReportsWidget(QWidget):
    def __init__(self, db_manager, user_data=None):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_report_data = []
        self.init_ui()
        self.load_report_types()
        self.load_report_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Отчетность и аналитика")
        title.setObjectName("widgetTitle")
        layout.addWidget(title)

        params_group = QGroupBox("Параметры отчета")
        params_layout = QFormLayout()

        self.report_type_combo = QComboBox()
        self.report_type_combo.currentTextChanged.connect(self.load_report_data)
        params_layout.addRow("Тип отчета:", self.report_type_combo)

        dates_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumWidth(120)
        self.start_date.dateChanged.connect(self.load_report_data)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumWidth(120)
        self.end_date.dateChanged.connect(self.load_report_data)

        dates_layout.addWidget(QLabel("С:"))
        dates_layout.addWidget(self.start_date)
        dates_layout.addWidget(QLabel("По:"))
        dates_layout.addWidget(self.end_date)
        dates_layout.addStretch()

        params_layout.addRow("Период:", dates_layout)

        buttons_layout = QHBoxLayout()
        self.export_btn = QPushButton("Экспорт в Excel")
        self.export_btn.clicked.connect(self.export_report_to_excel)

        self.create_report_btn = QPushButton("Создать отчет")
        self.create_report_btn.clicked.connect(self.create_new_report)

        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addWidget(self.create_report_btn)
        buttons_layout.addStretch()

        params_layout.addRow(buttons_layout)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        table_group = QGroupBox("Список отчетов")
        table_layout = QVBoxLayout()

        self.report_table = QTableWidget()
        self.report_table.setMinimumHeight(400)
        self.report_table.setColumnCount(8)
        self.report_table.setHorizontalHeaderLabels([
            "ID", "Тип отчета", "Бассейн", "Период", "Автор", "Дата создания", "Статус", "Действия"
        ])

        header = self.report_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(7, 80)

        table_layout.addWidget(self.report_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        self.setLayout(layout)

    def load_report_types(self):
        """Загрузка типов отчетов"""
        try:
            self.report_type_combo.clear()
            self.report_type_combo.addItem("Все отчеты")

            report_types = self.db_manager.get_all_report_types()
            for report_type in report_types:
                self.report_type_combo.addItem(report_type)
        except Exception as e:
            print(f"Ошибка загрузки типов отчетов: {e}")

    def load_report_data(self):
        """Загрузка данных отчетов"""
        try:
            report_type = self.report_type_combo.currentText()
            if report_type == "Все отчеты":
                report_type = None

            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")

            self.current_report_data = self.db_manager.get_reports_data(
                report_type, start_date, end_date
            )
            self.update_report_table()

        except Exception as e:
            print(f"Ошибка загрузки данных отчетов: {e}")

    def update_report_table(self):
        """Обновление таблицы с отчетами"""
        try:
            self.report_table.setRowCount(len(self.current_report_data))

            for row, report in enumerate(self.current_report_data):
                # Заполняем данные таблицы
                self.report_table.setItem(row, 0, QTableWidgetItem(str(report.get('ID_Report', ''))))
                self.report_table.setItem(row, 1, QTableWidgetItem(report.get('Report_Type', '')))
                self.report_table.setItem(row, 2, QTableWidgetItem(report.get('Name_Pool', 'Не указан')))

                # Период
                period_start = report.get('Period_Start', '')
                period_end = report.get('Period_End', '')
                period_text = f"{period_start} - {period_end}" if period_start and period_end else "Не указан"
                self.report_table.setItem(row, 3, QTableWidgetItem(period_text))

                # Автор
                author_name = f"{report.get('Surname_User', '')} {report.get('Name_User', '')}".strip()
                author_name = author_name if author_name else "Неизвестно"
                self.report_table.setItem(row, 4, QTableWidgetItem(author_name))

                # Дата создания
                date_formation = report.get('Date_Formation', '')
                date_str = str(date_formation)[:16] if date_formation else "Не указана"
                self.report_table.setItem(row, 5, QTableWidgetItem(date_str))

                # Статус
                has_data = bool(report.get('Report_Data'))
                status = "Заполнен" if has_data else "Пустой"
                self.report_table.setItem(row, 6, QTableWidgetItem(status))

                # Кнопка просмотра
                view_btn = QPushButton("Просмотр")
                view_btn.setFixedSize(70, 25)
                view_btn.setStyleSheet("font-size: 10px; padding: 2px;")
                view_btn.clicked.connect(lambda checked, r=row: self.view_report_details(r))
                self.report_table.setCellWidget(row, 7, view_btn)

            self.report_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка обновления таблицы: {e}")

    def view_report_details(self, row):
        """Просмотр деталей отчета"""
        try:
            if row < len(self.current_report_data):
                report = self.current_report_data[row]

                details_text = f"""
ТИП ОТЧЕТА: {report.get('Report_Type', 'Не указан')}

ДАННЫЕ ОТЧЕТА:
{report.get('Report_Data', 'Нет данных')}
                """.strip()

                QMessageBox.information(self, "Детали отчета", details_text)

        except Exception as e:
            print(f"Ошибка отображения деталей отчета: {e}")

    def export_report_to_excel(self):
        """Экспорт отчетов в Excel"""
        try:
            if not self.current_report_data:
                QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта!")
                return

            # Подготовка данных для экспорта
            headers = ["ID", "Тип отчета", "Бассейн", "Период", "Автор", "Дата создания", "Статус"]
            data_for_export = []

            for report in self.current_report_data:
                period_start = report.get('Period_Start', '')
                period_end = report.get('Period_End', '')
                period_text = f"{period_start} - {period_end}" if period_start and period_end else "Не указан"

                author_name = f"{report.get('Surname_User', '')} {report.get('Name_User', '')}".strip()
                author_name = author_name if author_name else "Неизвестно"

                has_data = bool(report.get('Report_Data'))
                status = "Заполнен" if has_data else "Пустой"

                data_for_export.append([
                    report.get('ID_Report', ''),
                    report.get('Report_Type', ''),
                    report.get('Name_Pool', 'Не указан'),
                    period_text,
                    author_name,
                    report.get('Date_Formation', ''),
                    status
                ])

            # Используем ExcelExporter для экспорта
            success, message = ExcelExporter.export_table_to_excel(
                data=data_for_export,
                columns=headers,
                sheet_name="Отчеты"
            )

            if success:
                QMessageBox.information(self, "Успех", message)
            else:
                QMessageBox.critical(self, "Ошибка", message)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def create_new_report(self):
        """Создание нового отчета"""
        try:
            dialog = ReportDialog(self.db_manager, self.user_data, self)
            result = dialog.exec()

            if result:
                QMessageBox.information(self, "Успех", "Отчет успешно создан!")
                self.load_report_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания отчета: {str(e)}")
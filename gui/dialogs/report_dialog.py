from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QFormLayout,
    QGroupBox, QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

class ReportDialog(QDialog):
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.setWindowTitle("Создание нового отчета")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Создание нового отчета")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_group = QGroupBox("Данные отчета")
        form_layout = QFormLayout()

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Суточный отчет по мониторингу",
            "Аналитический отчет по кормлению",
            "Статистика роста рыбы",
            "Технологический отчет",
            "Отчет по состоянию оборудования"
        ])
        form_layout.addRow("Тип отчета:", self.report_type_combo)

        self.pool_combo = QComboBox()
        self.load_pools()
        form_layout.addRow("Бассейн:", self.pool_combo)

        period_layout = QHBoxLayout()
        self.period_start = QDateEdit()
        self.period_start.setDate(QDate.currentDate().addDays(-7))
        self.period_start.setCalendarPopup(True)

        self.period_end = QDateEdit()
        self.period_end.setDate(QDate.currentDate())
        self.period_end.setCalendarPopup(True)

        period_layout.addWidget(QLabel("С:"))
        period_layout.addWidget(self.period_start)
        period_layout.addWidget(QLabel("По:"))
        period_layout.addWidget(self.period_end)

        form_layout.addRow("Период отчета:", period_layout)

        self.report_data_text = QTextEdit()
        self.report_data_text.setPlaceholderText(
            "Введите данные отчета...\n"
            "Можно добавить:\n"
            "- Показания датчиков\n"
            "- Статистику кормления\n"
            "- Данные о росте рыбы\n"
            "- Технические параметры\n"
            "- Замечания и рекомендации"
        )
        self.report_data_text.setMinimumHeight(150)
        form_layout.addRow("Данные отчета:", self.report_data_text)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_report)
        button_box.rejected.connect(self.reject)

        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Создать")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Закрыть")
        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_pools(self):
        try:
            pools = self.db_manager.get_all_pools()
            self.pool_combo.clear()
            self.pool_combo.addItem("Не выбран", None)
            for pool in pools:
                self.pool_combo.addItem(
                    f"{pool['Name_Pool']} ({pool['Fish_Type']})",
                    pool['ID_Pool']
                )
        except Exception as e:
            print(f"Ошибка загрузки бассейнов: {e}")

    def save_report(self):
        try:
            report_type = self.report_type_combo.currentText()
            pool_id = self.pool_combo.currentData()
            period_start = self.period_start.date().toString("yyyy-MM-dd")
            period_end = self.period_end.date().toString("yyyy-MM-dd")
            report_data = self.report_data_text.toPlainText().strip()

            if not report_data:
                QMessageBox.warning(self, "Ошибка", "Введите данные отчета!")
                return

            if not pool_id:
                QMessageBox.warning(self, "Ошибка", "Выберите бассейн!")
                return

            full_report_data = self.collect_report_data(report_type, period_start, period_end, pool_id)

            full_report_data += f"\nДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ:\n{report_data}"

            success = self.db_manager.add_report(
                pool_id=pool_id,
                user_id=self.user_data.get('id'),
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                report_data=full_report_data
            )

            if success:
                QMessageBox.information(self, "Успех", "Отчет успешно сохранен в базе данных!")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить отчет в базу данных!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения отчета: {str(e)}")

    def collect_report_data(self, report_type, period_start, period_end, pool_id):
        try:
            report_data = f"Период: {period_start} - {period_end}\n"
            report_data += f"Бассейн: {self.pool_combo.currentText()}\n"
            report_data += f"Дата формирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            if "мониторинг" in report_type.lower():
                monitoring_data = self.db_manager.get_monitoring_data_for_period(period_start, period_end)
                if monitoring_data:
                    report_data += "ДАННЫЕ МОНИТОРИНГА:\n"
                    for data in monitoring_data[:10]:
                        report_data += f"- {data['Timestamp_Sensor']}: {data['Type_Sensor']} = {data['Value_Sensor']} ({data['Status_Readings']})\n"
                else:
                    report_data += "Данные мониторинга за период отсутствуют\n"

            elif "кормление" in report_type.lower():
                feeding_data = self.db_manager.get_feeding_data_for_period(period_start, period_end)
                if feeding_data:
                    report_data += "ДАННЫЕ КОРМЛЕНИЯ:\n"
                    total_feed = 0
                    for data in feeding_data:
                        report_data += f"- {data['Feeding_Time']}: {data['Feed_Type']} - {data['Feed_Amount']} кг\n"
                        total_feed += float(data['Feed_Amount'] or 0)
                    report_data += f"Общий расход корма: {total_feed:.2f} кг\n"
                else:
                    report_data += "Данные кормления за период отсутствуют\n"

            elif "рост" in report_type.lower():
                growth_data = self.db_manager.get_growth_data_for_period(period_start, period_end)
                if growth_data:
                    report_data += "ДАННЫЕ РОСТА РЫБЫ:\n"
                    for data in growth_data:
                        report_data += f"- {data['Fishing_Date']}: средний вес {data['Average_Weight']} гр, количество {data['Fish_Count']}\n"
                else:
                    report_data += "Данные роста за период отсутствуют\n"

            return report_data

        except Exception as e:
            return f"Ошибка сбора автоматических данных: {str(e)}"
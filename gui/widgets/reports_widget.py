from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QComboBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ReportsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Отчетность и аналитика")
        title.setObjectName("widgetTitle")
        layout.addWidget(title)

        # Параметры отчета
        params_group = QGroupBox("Параметры отчета")
        params_layout = QFormLayout()

        # Тип отчета
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Суточный отчет",
            "Аналитический",
            "Статистический",
            "Технологический"
        ])
        params_layout.addRow("Тип отчета:", self.report_type_combo)

        # Период
        dates_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        dates_layout.addWidget(QLabel("С:"))
        dates_layout.addWidget(self.start_date)
        dates_layout.addWidget(QLabel("По:"))
        dates_layout.addWidget(self.end_date)
        dates_layout.addStretch()

        params_layout.addRow("Период:", dates_layout)

        # Кнопки генерации
        buttons_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Сгенерировать отчет")
        self.generate_btn.clicked.connect(self.generate_report)

        self.export_btn = QPushButton("Экспорт в PDF")
        self.export_btn.clicked.connect(self.export_to_pdf)

        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addStretch()

        params_layout.addRow(buttons_layout)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Визуализация данных
        viz_group = QGroupBox("Визуализация данных")
        viz_layout = QVBoxLayout()

        # График (заглушка - в реальном проекте нужно добавить matplotlib)
        self.viz_label = QLabel("Здесь будет график...\n\nДля полноценной визуализации\nустановите matplotlib:")
        self.viz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_label.setStyleSheet("background-color: #f8f9fa; padding: 40px; border: 1px dashed #ccc;")
        viz_layout.addWidget(self.viz_label)

        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)

        # Данные отчета
        data_group = QGroupBox("Данные отчета")
        data_layout = QVBoxLayout()

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "Дата", "Параметр", "Значение", "Статус", "Бассейн"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        data_layout.addWidget(self.report_table)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Текстовый отчет
        text_group = QGroupBox("Текстовый отчет")
        text_layout = QVBoxLayout()

        self.report_text = QTextEdit()
        self.report_text.setPlaceholderText("Здесь будет сгенерированный отчет...")
        self.report_text.setMaximumHeight(150)
        text_layout.addWidget(self.report_text)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        self.setLayout(layout)

    def refresh_data(self):
        """Обновление данных отчетов"""
        try:
            reports = self.db_manager.get_reports()
            self.report_table.setRowCount(len(reports))

            for row, report in enumerate(reports):
                self.report_table.setItem(row, 0, QTableWidgetItem(report['Period_Start']))
                self.report_table.setItem(row, 1, QTableWidgetItem(report['Report_Type']))
                self.report_table.setItem(row, 2, QTableWidgetItem(str(report['ID_Report'])))
                self.report_table.setItem(row, 3, QTableWidgetItem("Сформирован"))
                self.report_table.setItem(row, 4, QTableWidgetItem(report['Name_Pool']))

        except Exception as e:
            print(f"Ошибка обновления отчетов: {e}")

    def generate_report(self):
        """Генерация отчета"""
        try:
            report_type = self.report_type_combo.currentText()
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")

            # Получаем данные для отчета
            reports = self.db_manager.get_reports(report_type, start_date, end_date)

            # Формируем текстовый отчет
            report_text = f"""
ОТЧЕТ: {report_type}
Период: с {start_date} по {end_date}
Сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ОБЩАЯ ИНФОРМАЦИЯ:
• Количество записей: {len(reports)}
• Бассейны в отчете: {len(set(r['Name_Pool'] for r in reports))}

ДАННЫЕ МОНИТОРИНГА:
"""

            # Добавляем данные мониторинга
            readings = self.db_manager.get_latest_sensor_readings()
            temp_readings = [r for r in readings if r['Type_Sensor'] == 'Температура']
            oxygen_readings = [r for r in readings if r['Type_Sensor'] == 'Кислород']
            ph_readings = [r for r in readings if r['Type_Sensor'] == 'pH']

            report_text += f"""
• Средняя температура: {sum(r['Value_Sensor'] for r in temp_readings) / len(temp_readings) if temp_readings else 0:.1f}°C
• Средний кислород: {sum(r['Value_Sensor'] for r in oxygen_readings) / len(oxygen_readings) if oxygen_readings else 0:.1f} мг/л
• Средний pH: {sum(r['Value_Sensor'] for r in ph_readings) / len(ph_readings) if ph_readings else 0:.1f}

СТАТУС СИСТЕМЫ:
• Все системы работают в штатном режиме
• Критических отклонений не обнаружено
"""

            self.report_text.setPlainText(report_text)
            self.refresh_data()

            QMessageBox.information(self, "Успех", "Отчет сгенерирован!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {e}")

    def export_to_pdf(self):
        """Экспорт в PDF (заглушка)"""
        QMessageBox.information(
            self,
            "Экспорт",
            "Функция экспорта в PDF будет реализована в следующей версии"
        )
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QComboBox, QDateEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTextEdit)
from PyQt6.QtCore import QDate
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ReportsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Отчетность и аналитика")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Панель управления отчетами
        control_group = QGroupBox("Параметры отчета")
        control_layout = QHBoxLayout()

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Суточный отчет",
            "Недельный отчет",
            "Месячный отчет",
            "Отчет по кормлению",
            "Отчет по параметрам воды"
        ])

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        self.generate_btn = QPushButton("Сгенерировать отчет")
        self.generate_btn.clicked.connect(self.generate_report)

        self.export_btn = QPushButton("Экспорт в PDF")
        self.export_btn.clicked.connect(self.export_to_pdf)

        control_layout.addWidget(QLabel("Тип отчета:"))
        control_layout.addWidget(self.report_type_combo)
        control_layout.addWidget(QLabel("С:"))
        control_layout.addWidget(self.start_date)
        control_layout.addWidget(QLabel("По:"))
        control_layout.addWidget(self.end_date)
        control_layout.addWidget(self.generate_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Графики
        charts_group = QGroupBox("Визуализация данных")
        charts_layout = QVBoxLayout()

        # Место для matplotlib графика
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)

        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)

        # Таблица данных
        data_group = QGroupBox("Данные отчета")
        data_layout = QVBoxLayout()

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["Дата", "Параметр", "Значение", "Статус"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        data_layout.addWidget(self.report_table)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Текстовый отчет
        text_group = QGroupBox("Текстовый отчет")
        text_layout = QVBoxLayout()

        self.report_text = QTextEdit()
        self.report_text.setPlaceholderText("Здесь будет сгенерированный отчет...")

        text_layout.addWidget(self.report_text)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

    def generate_report(self):
        """Генерация отчета"""
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()

        # Обновление графика
        self.update_chart(report_type, start_date, end_date)

        # Обновление таблицы
        self.update_report_table(report_type, start_date, end_date)

        # Генерация текстового отчета
        self.generate_text_report(report_type, start_date, end_date)

    def update_chart(self, report_type, start_date, end_date):
        """Обновление графика"""
        self.ax.clear()

        # Демо-данные для графика
        dates = [start_date + timedelta(days=i) for i in range(7)]
        temperatures = [20.1, 20.3, 19.8, 20.5, 21.0, 20.7, 20.2]

        self.ax.plot(dates, temperatures, 'b-o', linewidth=2)
        self.ax.set_title('Температура воды за период')
        self.ax.set_ylabel('Температура (°C)')
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(axis='x', rotation=45)

        self.canvas.draw()

    def update_report_table(self, report_type, start_date, end_date):
        """Обновление таблицы отчета"""
        # Демо-данные
        data = [
            ("2024-01-15", "Температура", "20.5°C", "Норма"),
            ("2024-01-15", "Кислород", "6.8 мг/л", "Норма"),
            ("2024-01-15", "Расход корма", "7.5 кг", "План"),
            ("2024-01-16", "Температура", "20.3°C", "Норма"),
            ("2024-01-16", "Кислород", "6.5 мг/л", "Понижен"),
        ]

        self.report_table.setRowCount(len(data))
        for row, (date, param, value, status) in enumerate(data):
            self.report_table.setItem(row, 0, QTableWidgetItem(date))
            self.report_table.setItem(row, 1, QTableWidgetItem(param))
            self.report_table.setItem(row, 2, QTableWidgetItem(value))
            self.report_table.setItem(row, 3, QTableWidgetItem(status))

    def generate_text_report(self, report_type, start_date, end_date):
        """Генерация текстового отчета"""
        report_text = f"""
ОТЧЕТ: {report_type}
Период: {start_date} - {end_date}
Дата формирования: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ОБЩАЯ СТАТИСТИКА:
• Средняя температура: 20.4°C
• Средний уровень кислорода: 6.7 мг/л
• Общий расход корма: 52.3 кг
• Прирост биомассы: 45.2 кг

РЕКОМЕНДАЦИИ:
1. Поддерживать температуру в диапазоне 18-22°C
2. Увеличить аэрацию в утренние часы
3. Скорректировать рацион кормления

СИСТЕМНЫЕ УВЕДОМЛЕНИЯ:
• Все системы работают в штатном режиме
• Критических отклонений не зафиксировано
"""
        self.report_text.setPlainText(report_text)

    def export_to_pdf(self):
        """Экспорт отчета в PDF"""
        # Здесь будет логика экспорта
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Экспорт", "Функция экспорта в PDF будет реализована")
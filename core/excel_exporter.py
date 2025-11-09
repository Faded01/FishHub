import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import os
import pandas as pd


class ExcelExporter:
    """Класс для экспорта данных в Excel файлы"""

    @staticmethod
    def export_table_to_excel(data, columns, filename=None, sheet_name="Данные"):
        """
        Экспорт данных таблицы в Excel

        Args:
            data: список строк данных
            columns: список названий колонок
            filename: имя файла (если None - генерируется автоматически)
            sheet_name: название листа

        Returns:
            tuple: (success, message)
        """
        try:
            if not data:
                return False, "Нет данных для экспорта"

            if not columns:
                return False, "Не указаны названия колонок"

            # Генерируем имя файла если не указано
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.xlsx"

            # Создаем новую книгу Excel
            wb = openpyxl.Workbook()
            ws = wb.active

            # Обрабатываем имя листа
            safe_sheet_name = ExcelExporter._create_safe_sheet_name(sheet_name)
            ws.title = safe_sheet_name

            # Настраиваем стили
            header_font = Font(bold=True, size=12, color="FFFFFF")
            header_fill = openpyxl.styles.PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell_font = Font(size=10)
            center_alignment = Alignment(horizontal='center', vertical='center')
            border_style = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            # Добавляем заголовки
            for col_num, header in enumerate(columns, 1):
                cell = ws.cell(row=1, column=col_num, value=str(header))
                cell.font = header_font
                cell.alignment = center_alignment
                cell.border = border_style
                cell.fill = header_fill

            # Добавляем данные с обработкой None значений
            for row_num, row_data in enumerate(data, 2):
                for col_num, value in enumerate(row_data, 1):
                    # Обрабатываем None значения и неправильные типы
                    if value is None:
                        safe_value = ""
                    elif isinstance(value, (int, float)):
                        safe_value = value
                    else:
                        safe_value = str(value)

                    cell = ws.cell(row=row_num, column=col_num, value=safe_value)
                    cell.font = cell_font
                    cell.alignment = center_alignment
                    cell.border = border_style

            # Настраиваем автоширину колонок
            ExcelExporter._adjust_column_widths(ws, columns, data)

            # Сохраняем файл
            wb.save(filename)
            return True, f"Данные успешно экспортированы в файл: {filename}"

        except Exception as e:
            return False, f"Ошибка экспорта в Excel: {str(e)}"

    @staticmethod
    def _create_safe_sheet_name(name):
        """Создает безопасное имя для листа Excel"""
        if not name:
            return "Данные"

        # Заменяем запрещенные символы
        forbidden_chars = ['\\', '/', '*', '?', ':', '[', ']']
        safe_name = name
        for char in forbidden_chars:
            safe_name = safe_name.replace(char, '_')

        # Ограничиваем длину (максимум 31 символ в Excel)
        if len(safe_name) > 31:
            safe_name = safe_name[:31]

        # Убеждаемся, что имя не пустое
        if not safe_name.strip():
            safe_name = "Данные"

        return safe_name

    @staticmethod
    def export_dataframe_to_excel(dataframes, filename=None):
        """
        Экспорт нескольких DataFrame в один Excel файл на разные листы

        Args:
            dataframes: словарь {sheet_name: dataframe}
            filename: имя файла

        Returns:
            tuple: (success, message)
        """
        try:
            if not dataframes:
                return False, "Нет данных для экспорта"

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_multiple_{timestamp}.xlsx"

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in dataframes.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Получаем лист для форматирования
                    worksheet = writer.sheets[sheet_name]
                    # ИСПРАВЛЕНИЕ: исправлены опечатки в вызове метода
                    ExcelExporter._format_excel_sheet(worksheet, df.columns.tolist(), df.values.tolist())

            return True, f"Данные успешно экспортированы в файл: {filename}"

        except Exception as e:
            return False, f"Ошибка экспорта DataFrame в Excel: {str(e)}"

    @staticmethod
    def export_query_results(db_manager, query, params=None, filename=None, columns=None, sheet_name="Данные"):
        """
        Экспорт результатов SQL запроса в Excel

        Args:
            db_manager: экземпляр DatabaseManager
            query: SQL запрос
            params: параметры запроса
            filename: имя файла
            columns: названия колонок (если None - берутся из курсора)
            sheet_name: название листа

        Returns:
            tuple: (success, message)
        """
        try:
            # Выполняем запрос
            if params:
                db_manager.cursor.execute(query, params)
            else:
                db_manager.cursor.execute(query)

            data = db_manager.cursor.fetchall()

            if not data:
                return False, "Нет данных для экспорта"

            # Получаем названия колонок если не указаны
            if not columns:
                columns = [description[0] for description in db_manager.cursor.description]

            return ExcelExporter.export_table_to_excel(data, columns, filename, sheet_name)

        except Exception as e:
            return False, f"Ошибка экспорта запроса в Excel: {str(e)}"

    @staticmethod
    def _adjust_column_widths(worksheet, columns, data):
        """Настройка автоширины колонок"""
        for col_num, header in enumerate(columns, 1):
            max_length = 0
            column_letter = get_column_letter(col_num)

            # Проверяем длину заголовка
            if header:
                max_length = len(str(header))

            # Проверяем длину данных в колонке
            for row_num in range(2, len(data) + 2):
                cell_value = worksheet.cell(row=row_num, column=col_num).value
                if cell_value:
                    max_length = max(max_length, len(str(cell_value)))

            # Устанавливаем ширину с небольшим запасом
            adjusted_width = min(max_length + 2, 50)  # Максимум 50 символов
            worksheet.column_dimensions[column_letter].width = adjusted_width

    @staticmethod
    def _format_excel_sheet(worksheet, columns, data):
        """Форматирование листа Excel"""
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = openpyxl.styles.PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell_font = Font(size=10)
        center_alignment = Alignment(horizontal='center', vertical='center')
        border_style = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Форматируем заголовки
        for col_num, header in enumerate(columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.font = header_font
            cell.alignment = center_alignment
            cell.border = border_style
            cell.fill = header_fill

        # Форматируем данные
        for row_num in range(2, len(data) + 2):
            for col_num in range(1, len(columns) + 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.font = cell_font
                cell.alignment = center_alignment
                cell.border = border_style

    @staticmethod
    def get_available_tables_export(db_manager):
        """
        Возвращает список таблиц доступных для экспорта

        Args:
            db_manager: экземпляр DatabaseManager

        Returns:
            list: список таблиц
        """
        try:
            tables = db_manager.get_table_names()
            return [table for table in tables if not table.startswith('sqlite_')]
        except:
            return []

    @staticmethod
    def export_database_schema(db_manager, filename=None):
        """
        Экспорт схемы базы данных в Excel

        Args:
            db_manager: экземпляр DatabaseManager
            filename: имя файла

        Returns:
            tuple: (success, message)
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"database_schema_{timestamp}.xlsx"

            tables = ExcelExporter.get_available_tables_export(db_manager)

            # Создаем книгу Excel
            wb = openpyxl.Workbook()

            # Удаляем дефолтный лист
            wb.remove(wb.active)

            for table in tables:
                # Создаем лист для каждой таблицы
                ws = wb.create_sheet(title=table[:31])  # Ограничение длины названия листа

                # Получаем информацию о колонках
                db_manager.cursor.execute(f"PRAGMA table_info({table})")
                columns_info = db_manager.cursor.fetchall()

                # Заголовки для схемы
                schema_headers = ["Имя колонки", "Тип данных", "Обязательное", "Первичный ключ", "По умолчанию"]
                data = []

                for col_info in columns_info:
                    data.append([
                        col_info[1],  # имя колонки
                        col_info[2],  # тип данных
                        "Да" if col_info[3] else "Нет",  # NOT NULL
                        "Да" if col_info[5] else "Нет",  # PRIMARY KEY
                        col_info[4] if col_info[4] else ""  # DEFAULT
                    ])

                # Экспортируем схему таблицы
                ExcelExporter.export_table_to_excel(
                    data=data,
                    columns=schema_headers,
                    filename=filename,  # временно, потом перезапишем
                    sheet_name=table[:31]
                )

                # Переносим данные в общую книгу
                source_wb = openpyxl.load_workbook(filename)
                source_ws = source_wb.active

                for row in source_ws.iter_rows():
                    for cell in row:
                        ws[cell.coordinate].value = cell.value
                        ws[cell.coordinate].font = cell.font
                        ws[cell.coordinate].alignment = cell.alignment
                        ws[cell.coordinate].border = cell.border
                        if hasattr(cell, 'fill'):
                            ws[cell.coordinate].fill = cell.fill

                # Настраиваем ширину колонок
                ExcelExporter._adjust_column_widths(ws, schema_headers, data)

            # Сохраняем общую книгу
            wb.save(filename)
            return True, f"Схема базы данных экспортирована в файл: {filename}"

        except Exception as e:
            return False, f"Ошибка экспорта схемы БД: {str(e)}"
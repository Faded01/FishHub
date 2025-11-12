import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="data/fishhub.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print(f"[DB] Успешное подключение к {self.db_path}")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось подключиться к базе данных: {e}")
            raise  # переброс исключения для отладки

    def is_connected(self):
        """Проверяет активное соединение с БД"""
        try:
            self.cursor.execute("SELECT 1")
            return True
        except:
            return False

    def close(self):
        try:
            if self.connection:
                if self.cursor:
                    self.cursor = None
                self.connection.close()
                self.connection = None
                print("[DB] Соединение с базой данных закрыто.")
        except Exception as e:
            print(f'[DB ERROR] Ошибка при закрытии соединения: {e}')

    # ------------------------
    # Работа с пользователями
    # ------------------------
    def check_user(self, username: str, password: str):
        try:
            query = """
                SELECT e.ID_User, e.Username, e.Password_User, e.Name_User, e.Surname_User, e.Patronymic_User,
                       e.Role_ID, e.Status, e.Created_At, r.Admin_Permission
                FROM Employees e
                JOIN Roles r ON e.Role_ID = r.ID_Role
                WHERE e.Username = ? AND e.Password_User = ?
            """
            self.cursor.execute(query, (username, password))
            user = self.cursor.fetchone()

            if user:
                full_name = f"{user['Surname_User']} {user['Name_User']} {user['Patronymic_User']}".strip()

                role_query = "SELECT Name_Role FROM Roles WHERE ID_Role = ?"
                self.cursor.execute(role_query, (user['Role_ID'],))
                role_result = self.cursor.fetchone()
                role_name = role_result['Name_Role'] if role_result else "Неизвестно"

                return {
                    "id": user["ID_User"],
                    "username": user["Username"],
                    "name": user["Name_User"],
                    "surname": user["Surname_User"],
                    "patronymic": user["Patronymic_User"],
                    "full_name": full_name,
                    "role_id": user["Role_ID"],
                    "role": role_name,
                    "status": user["Status"],
                    "created_at": user["Created_At"],
                    "admin_permission": bool(user["Admin_Permission"])
                }
            return None
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка при проверке пользователя: {e}")
            return None

    def update_user_status_by_id(self, user_id: int, status: str):
        """
        Обновляет статус пользователя (Активен / Отключён)
        """
        try:
            query = "UPDATE Employees SET Status = ? WHERE ID_User = ?"
            self.cursor.execute(query, (status, user_id))
            self.connection.commit()
            print(f"[DB] Статус пользователя ID={user_id} обновлён на '{status}'")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось обновить статус пользователя: {e}")

    def add_user(self, username, password, name, surname, patronymic, role_id):
        """Добавляет нового пользователя"""
        try:
            query = """
                INSERT INTO Employees (Username, Password_User, Name_User, Surname_User, Patronymic_User, Role_ID)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (username, password, name, surname, patronymic, role_id))
            self.connection.commit()
            print(f"[DB] Пользователь '{username}' успешно добавлен.")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось добавить пользователя: {e}")

    # ------------------------
    # Работа с бассейнами
    # ------------------------
    def get_all_pools(self):
        """Получить все бассейны"""
        try:
            self.cursor.execute("SELECT * FROM Pools ORDER BY ID_Pool")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения бассейнов: {e}")
            return []

    def get_pool_by_id(self, pool_id):
        """Получить бассейн по ID"""
        try:
            self.cursor.execute("SELECT * FROM Pools WHERE ID_Pool = ?", (pool_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения бассейна: {e}")
            return None

    def add_pool(self, name, volume, fish_type, fish_count, stocking_date, status):
        """Добавить новый бассейн"""
        try:
            query = """
                INSERT INTO Pools (Name_Pool, Volume_Pool, Fish_Type, Fish_Count, Stocking_Date, Status_Pool)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (name, volume, fish_type, fish_count, stocking_date, status))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка добавления бассейна: {e}")
            return False

    def update_pool(self, pool_id, name, volume, fish_type, fish_count, stocking_date, status):
        """Обновить бассейн"""
        try:
            query = """
                UPDATE Pools 
                SET Name_Pool = ?, Volume_Pool = ?, Fish_Type = ?, Fish_Count = ?, 
                    Stocking_Date = ?, Status_Pool = ?
                WHERE ID_Pool = ?
            """
            self.cursor.execute(query, (name, volume, fish_type, fish_count, stocking_date, status, pool_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка обновления бассейна: {e}")
            return False

    def delete_pool(self, pool_id):
        """Удалить бассейн"""
        try:
            self.cursor.execute("DELETE FROM Pools WHERE ID_Pool = ?", (pool_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка удаления бассейна: {e}")
            return False

    # ------------------------
    # Работа с датчиками
    # ------------------------
    def get_sensors_by_pool(self, pool_id):
        """Получить датчики для бассейна"""
        try:
            self.cursor.execute("SELECT * FROM Sensors WHERE ID_Pool = ?", (pool_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения датчиков: {e}")
            return []

    def get_sensors_by_pool_with_range(self, pool_id):
        """Получить датчики для бассейна с информацией о диапазонах"""
        try:
            self.cursor.execute(
                "SELECT * FROM Sensors WHERE ID_Pool = ?", (pool_id,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения датчиков: {e}")
            return []

    def add_sensor_reading(self, sensor_id, value, status="Норма"):
        """Добавить показания датчика"""
        try:
            query = """
                INSERT INTO Sensor_Readings (ID_Sensor, Value_Sensor, Timestamp_Sensor, Status_Readings)
                VALUES (?, ?, datetime('now'), ?)
            """
            self.cursor.execute(query, (sensor_id, value, status))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка добавления показаний: {e}")
            return False

    def get_sensor_readings(self, sensor_id):
        """Получить показания конкретного датчика"""
        try:
            query = """
                SELECT * FROM Sensor_Readings 
                WHERE ID_Sensor = ? 
                ORDER BY Timestamp_Sensor DESC
            """
            self.cursor.execute(query, (sensor_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний датчика: {e}")
            return []

    def get_latest_sensor_readings(self, pool_id=None):
        """Получить последние показания датчиков"""
        try:
            if pool_id:
                query = """
                    SELECT sr.*, s.Type_Sensor, s.ID_Pool 
                    FROM Sensor_Readings sr
                    JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                    WHERE s.ID_Pool = ?
                    ORDER BY sr.Timestamp_Sensor DESC
                """
                self.cursor.execute(query, (pool_id,))
            else:
                query = """
                    SELECT sr.*, s.Type_Sensor, s.ID_Pool 
                    FROM Sensor_Readings sr
                    JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                    ORDER BY sr.Timestamp_Sensor DESC
                """
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний: {e}")
            return []

    def get_sensor_readings_with_pool_info(self, pool_id=None, sensor_type=None):
        """Получить показания с информацией о бассейнах"""
        try:
            query = """
                SELECT sr.*, s.Type_Sensor, s.Range_Min, s.Range_Max, p.Name_Pool, p.ID_Pool
                FROM Sensor_Readings sr
                JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                JOIN Pools p ON s.ID_Pool = p.ID_Pool
                WHERE 1=1
            """
            params = []

            if pool_id:
                query += " AND s.ID_Pool = ?"
                params.append(pool_id)

            if sensor_type and sensor_type != "Все датчики":
                query += " AND s.Type_Sensor = ?"
                params.append(sensor_type)

            query += " ORDER BY sr.Timestamp_Sensor DESC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний: {e}")
            return []

    def get_all_sensor_readings_for_pool(self, pool_id, sensor_type=None):
        """Получить ВСЕ показания датчиков для конкретного бассейна"""
        try:
            query = """
                SELECT sr.*, s.Type_Sensor, s.ID_Pool 
                FROM Sensor_Readings sr
                JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                WHERE s.ID_Pool = ?
            """
            params = [pool_id]

            if sensor_type:
                query += " AND s.Type_Sensor = ?"
                params.append(sensor_type)

            query += " ORDER BY sr.Timestamp_Sensor DESC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний для бассейна: {e}")
            return []
    # ------------------------
    # Работа с кормлениями
    # ------------------------
    def get_feeding_history(self, pool_id=None):
        """Получить историю кормлений"""
        try:
            if pool_id:
                query = """
                    SELECT f.*, p.Name_Pool 
                    FROM Feedings f
                    JOIN Pools p ON f.ID_Pool = p.ID_Pool
                    WHERE f.ID_Pool = ?
                    ORDER BY f.Feeding_Time DESC
                """
                self.cursor.execute(query, (pool_id,))
            else:
                query = """
                    SELECT f.*, p.Name_Pool 
                    FROM Feedings f
                    JOIN Pools p ON f.ID_Pool = p.ID_Pool
                    ORDER BY f.Feeding_Time DESC
                """
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения истории кормлений: {e}")
            return []

    def add_feeding(self, pool_id, feed_type, feed_amount, feeding_time, feeding_method):
        """Добавить запись о кормлении"""
        try:
            query = """
                INSERT INTO Feedings (ID_Pool, Feed_Type, Feed_Amount, Feeding_Time, Feeding_Method)
                VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (pool_id, feed_type, feed_amount, feeding_time, feeding_method))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка добавления кормления: {e}")
            return False

    def get_feeding_statistics(self, period_days=30):
        """Получить статистику кормления"""
        try:
            query = """
                SELECT 
                    SUM(CASE WHEN date(Feeding_Time) = date('now') THEN Feed_Amount ELSE 0 END) as today,
                    SUM(CASE WHEN date(Feeding_Time) >= date('now', '-7 days') THEN Feed_Amount ELSE 0 END) as week,
                    SUM(CASE WHEN date(Feeding_Time) >= date('now', '-30 days') THEN Feed_Amount ELSE 0 END) as month
                FROM Feedings
            """
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения статистики: {e}")
            return None

    # ------------------------
    # Работа с отчетами
    # ------------------------
    def get_reports_data(self, report_type=None, start_date=None, end_date=None):
        """Получение всех данных отчетов из таблицы Reports"""
        try:
            query = """
                SELECT r.*, p.Name_Pool, u.Name_User, u.Surname_User 
                FROM Reports r
                LEFT JOIN Pools p ON r.ID_Pool = p.ID_Pool
                LEFT JOIN Employees u ON r.ID_User = u.ID_User
                WHERE 1=1
            """
            params = []

            if report_type and report_type != "Все отчеты":
                query += " AND r.Report_Type = ?"
                params.append(report_type)

            if start_date:
                query += " AND r.Period_Start >= ?"
                params.append(start_date)

            if end_date:
                query += " AND r.Period_End <= ?"
                params.append(end_date)

            query += " ORDER BY r.Date_Formation DESC"

            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения данных отчетов: {e}")
            return []

    def get_all_report_types(self):
        """Получение всех типов отчетов из базы"""
        try:
            query = "SELECT DISTINCT Report_Type FROM Reports ORDER BY Report_Type"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [row['Report_Type'] for row in rows] if rows else []
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения типов отчетов: {e}")
            return []

    def add_report(self, pool_id, user_id, report_type, period_start, period_end, report_data):
        """Добавление отчета в базу данных"""
        try:
            query = """
                INSERT INTO Reports (ID_Pool, ID_User, Report_Type, Period_Start, 
                                   Period_End, Date_Formation, Report_Data)
                VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
            """
            self.cursor.execute(query, (pool_id, user_id, report_type, period_start,
                                        period_end, report_data))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка добавления отчета: {e}")
            return False

    def get_monitoring_data_for_period(self, start_date, end_date):
        """Получение всех данных мониторинга за период"""
        try:
            query = """
                SELECT sr.Timestamp_Sensor, p.Name_Pool, s.Type_Sensor, 
                       sr.Value_Sensor, sr.Status_Readings
                FROM Sensor_Readings sr
                JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                JOIN Pools p ON s.ID_Pool = p.ID_Pool
                WHERE date(sr.Timestamp_Sensor) BETWEEN ? AND ?
                ORDER BY sr.Timestamp_Sensor DESC
            """
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения данных мониторинга: {e}")
            return []

    def get_feeding_data_for_period(self, start_date, end_date):
        """Получение всех данных кормления за период"""
        try:
            query = """
                SELECT f.Feeding_Time, p.Name_Pool, f.Feed_Type, 
                       f.Feed_Amount, f.Feeding_Method
                FROM Feedings f
                JOIN Pools p ON f.ID_Pool = p.ID_Pool
                WHERE date(f.Feeding_Time) BETWEEN ? AND ?
                ORDER BY f.Feeding_Time DESC
            """
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения данных кормления: {e}")
            return []

    def get_growth_data_for_period(self, start_date, end_date):
        """Получение всех данных роста рыбы за период"""
        try:
            query = """
                SELECT cc.Fishing_Date, p.Name_Pool, cc.Average_Weight, 
                       cc.Fish_Count, cc.Note
                FROM Control_Catches cc
                JOIN Pools p ON cc.ID_Pool = p.ID_Pool
                WHERE date(cc.Fishing_Date) BETWEEN ? AND ?
                ORDER BY cc.Fishing_Date DESC
            """
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения данных роста: {e}")
            return []

    def get_sensor_statistics(self, start_date, end_date):
        """Получение статистики по датчикам за период"""
        try:
            query = """
                SELECT 
                    s.Type_Sensor,
                    p.Name_Pool,
                    COUNT(*) as reading_count,
                    AVG(sr.Value_Sensor) as avg_value,
                    MIN(sr.Value_Sensor) as min_value,
                    MAX(sr.Value_Sensor) as max_value
                FROM Sensor_Readings sr
                JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                JOIN Pools p ON s.ID_Pool = p.ID_Pool
                WHERE date(sr.Timestamp_Sensor) BETWEEN ? AND ?
                GROUP BY s.Type_Sensor, p.Name_Pool
                ORDER BY s.Type_Sensor, p.Name_Pool
            """
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения статистики датчиков: {e}")
            return []

    def get_feeding_statistics_for_period(self, start_date, end_date):
        """Получение статистики кормления за период"""
        try:
            query = """
                SELECT 
                    p.Name_Pool,
                    f.Feed_Type,
                    COUNT(*) as feeding_count,
                    SUM(f.Feed_Amount) as total_amount,
                    AVG(f.Feed_Amount) as avg_amount
                FROM Feedings f
                JOIN Pools p ON f.ID_Pool = p.ID_Pool
                WHERE date(f.Feeding_Time) BETWEEN ? AND ?
                GROUP BY p.Name_Pool, f.Feed_Type
                ORDER BY p.Name_Pool, f.Feed_Type
            """
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(row))
            return data

        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения статистики кормления: {e}")
            return []

    def get_reports(self, report_type=None, start_date=None, end_date=None):
        """Получить отчеты"""
        try:
            base_query = """
                SELECT r.*, p.Name_Pool, u.Name_User 
                FROM Reports r
                JOIN Pools p ON r.ID_Pool = p.ID_Pool
                JOIN Employees u ON r.ID_User = u.ID_User
                WHERE 1=1
            """
            params = []

            if report_type:
                base_query += " AND r.Report_Type = ?"
                params.append(report_type)
            if start_date:
                base_query += " AND r.Period_Start >= ?"
                params.append(start_date)
            if end_date:
                base_query += " AND r.Period_End <= ?"
                params.append(end_date)

            base_query += " ORDER BY r.Date_Formation DESC"

            self.cursor.execute(base_query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения отчетов: {e}")
            return []

    # ------------------------
    # Общие методы для работы с таблицами
    # ------------------------
    def get_all_data(self, table_name):
        """Получить все данные из указанной таблицы"""
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения данных из таблицы {table_name}: {e}")
            return []

    def get_table_columns(self, table_name):
        """Получить названия колонок таблицы"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()
            return [column[1] for column in columns_info]  # column[1] - название колонки
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения колонок таблицы {table_name}: {e}")
            return []

    def get_table_names(self):
        """Получить список всех таблиц в базе данных"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            return [table[0] for table in tables]
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения списка таблиц: {e}")
            return []
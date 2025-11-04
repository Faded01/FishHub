import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="data/fishhub.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            # Создаем директорию если не существует
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print(f"[DB] Успешное подключение к {self.db_path}")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось подключиться к базе данных: {e}")
            raise  # Перебрасываем исключение для отладки

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
        """
        Проверяет наличие пользователя с указанными логином и паролем.
        Возвращает словарь с данными, если пользователь найден.
        """
        try:
            query = """
                SELECT ID_User, Username, Password_User, Name_User, Surname_User, Patronymic_User,
                       Role_ID, Status, Created_At
                FROM Users
                WHERE Username = ? AND Password_User = ?
            """
            self.cursor.execute(query, (username, password))
            user = self.cursor.fetchone()

            if user:
                # Формируем полное имя
                full_name = f"{user['Surname_User']} {user['Name_User']} {user['Patronymic_User']}".strip()

                # Получаем название роли
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
                    "full_name": full_name,  # Добавляем полное имя
                    "role_id": user["Role_ID"],
                    "role": role_name,  # Добавляем название роли
                    "status": user["Status"],
                    "created_at": user["Created_At"]
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
            query = "UPDATE Users SET Status = ? WHERE ID_User = ?"
            self.cursor.execute(query, (status, user_id))
            self.connection.commit()
            print(f"[DB] Статус пользователя ID={user_id} обновлён на '{status}'")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось обновить статус пользователя: {e}")

    def logout_all_users(self):
        """
        Сбрасывает статус у всех пользователей на 'Отключён' (например, при запуске приложения)
        """
        try:
            self.cursor.execute("UPDATE Users SET Status = 'Отключён'")
            self.connection.commit()
            print("[DB] Все пользователи были отключены при запуске приложения.")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка при сбросе статусов: {e}")

    # ------------------------
    # Пример: добавление пользователя
    # ------------------------
    def add_user(self, username, password, name, surname, patronymic, role_id):
        """Добавляет нового пользователя"""
        try:
            query = """
                INSERT INTO Users (Username, Password_User, Name_User, Surname_User, Patronymic_User, Role_ID)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (username, password, name, surname, patronymic, role_id))
            self.connection.commit()
            print(f"[DB] Пользователь '{username}' успешно добавлен.")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось добавить пользователя: {e}")

    # В core/database.py добавить следующие методы:

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

    def get_sensors_by_pool(self, pool_id):
        """Получить датчики для бассейна"""
        try:
            self.cursor.execute("SELECT * FROM Sensors WHERE ID_Pool = ?", (pool_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения датчиков: {e}")
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
                    LIMIT 10
                """
                self.cursor.execute(query, (pool_id,))
            else:
                query = """
                    SELECT sr.*, s.Type_Sensor, s.ID_Pool 
                    FROM Sensor_Readings sr
                    JOIN Sensors s ON sr.ID_Sensor = s.ID_Sensor
                    ORDER BY sr.Timestamp_Sensor DESC
                    LIMIT 20
                """
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Ошибка получения показаний: {e}")
            return []

    # Добавить в core/database.py

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
                    LIMIT 50
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

    def get_reports(self, report_type=None, start_date=None, end_date=None):
        """Получить отчеты"""
        try:
            base_query = """
                SELECT r.*, p.Name_Pool, u.Name_User 
                FROM Reports r
                JOIN Pools p ON r.ID_Pool = p.ID_Pool
                JOIN Users u ON r.ID_User = u.ID_User
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
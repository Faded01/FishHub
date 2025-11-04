import sqlite3
from datetime import datetime


class DatabaseManager:
    """Класс для управления подключением и запросами к базе данных FishHub"""

    def __init__(self, db_path="data/fishhub.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()

    # ------------------------
    # Подключение и отключение
    # ------------------------
    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам по имени
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось подключиться к базе данных: {e}")

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            print("[DB] Соединение закрыто.")

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
                       ID_Role, Status
                FROM Users
                WHERE Username = ? AND Password_User = ?
            """
            self.cursor.execute(query, (username, password))
            user = self.cursor.fetchone()

            if user:
                return {
                    "id": user["ID_User"],
                    "username": user["Username"],
                    "name": user["Name_User"],
                    "surname": user["Surname_User"],
                    "patronymic": user["Patronymic_User"],
                    "role_id": user["ID_Role"],
                    "status": user["Status"]
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
                INSERT INTO Users (Username, Password_User, Name_User, Surname_User, Patronymic_User, ID_Role)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (username, password, name, surname, patronymic, role_id))
            self.connection.commit()
            print(f"[DB] Пользователь '{username}' успешно добавлен.")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Не удалось добавить пользователя: {e}")

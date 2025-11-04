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
                self.connection.close()
                self.connection = None
                self.cursor = None
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

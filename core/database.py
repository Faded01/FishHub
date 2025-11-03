import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Менеджер базы данных для FishHub"""

    def __init__(self, db_path="data/fishhub.db"):
        self.db_path = Path(db_path)
        # Создаем папку data, если её нет
        self.db_path.parent.mkdir(exist_ok=True)

    def get_connection(self):
        """Получение подключения к базе данных"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Инициализация всех таблиц базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Таблица Roles (Роли)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Roles (
                ID_Role INTEGER PRIMARY KEY AUTOINCREMENT,
                Role_Name VARCHAR(30) NOT NULL,
                Role_Description TEXT,
                Admin_Permissions BOOLEAN DEFAULT 0
            )
        ''')

        # 2. Таблица Users (Пользователи)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                ID_User INTEGER PRIMARY KEY AUTOINCREMENT,
                Username VARCHAR(50) NOT NULL UNIQUE,
                Password_User VARCHAR(255) NOT NULL,
                Name_User VARCHAR(50) NOT NULL,
                Surname_User VARCHAR(50) NOT NULL,
                Patronymic_User VARCHAR(50) NOT NULL,
                Role_ID INTEGER NOT NULL,
                Status VARCHAR(20) DEFAULT 'отключён',
                Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Role_ID) REFERENCES Roles (ID_Role)
            )
        ''')

        # 3. Таблица Pools (Бассейны)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pools (
                ID_Pool INTEGER PRIMARY KEY AUTOINCREMENT,
                Name_Pool VARCHAR(100) NOT NULL,
                Volume_Pool DECIMAL(10,2),
                Fish_Type VARCHAR(50),
                Fish_Count INTEGER,
                Stocking_Date DATE,
                Status_Pool VARCHAR(20) DEFAULT 'активен'
            )
        ''')

        # 4. Таблица Sensors (Датчики)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sensors (
                ID_Sensor INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Pool INTEGER,
                Type_Sensor VARCHAR(30) NOT NULL,
                Model_Sensor VARCHAR(50),
                Measurement_Range VARCHAR(50),
                Installation_Date DATE,
                FOREIGN KEY (ID_Pool) REFERENCES Pools (ID_Pool)
            )
        ''')

        # 5. Таблица Sensor_Readings (Показания датчиков)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sensor_Readings (
                ID_Record INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Sensor INTEGER,
                Value_Sensor DECIMAL(8,3) NOT NULL,
                Timestamp_Sensor DATETIME NOT NULL,
                Status_Readings VARCHAR(20) DEFAULT 'норма',
                FOREIGN KEY (ID_Sensor) REFERENCES Sensors (ID_Sensor)
            )
        ''')

        # 6. Таблица Feedings (Кормления)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Feedings (
                ID_Feeding INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Pool INTEGER,
                Feed_Type VARCHAR(50),
                Feed_Amount DECIMAL(8,3),
                Feeding_Time DATETIME,
                Feeding_Method VARCHAR(30),
                FOREIGN KEY (ID_Pool) REFERENCES Pools (ID_Pool)
            )
        ''')

        # 7. Таблица Control_Catches (Контрольные обловы)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Control_Catches (
                ID_Fishing INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Pool INTEGER,
                Average_Weight DECIMAL(8,3),
                Fish_Count INTEGER,
                Fishing_Date DATE,
                Note TEXT,
                FOREIGN KEY (ID_Pool) REFERENCES Pools (ID_Pool)
            )
        ''')

        # 8. Таблица Reports (Отчёты)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Reports (
                ID_Report INTEGER PRIMARY KEY AUTOINCREMENT,
                Report_Type VARCHAR(50) NOT NULL,
                Period_Start DATE,
                Period_End DATE,
                Date_Formation DATETIME,
                Report_Data TEXT
            )
        ''')

        conn.commit()
        conn.close()

        # Заполняем начальными данными
        self.fill_initial_data()

    def fill_initial_data(self):
        """Заполнение базы начальными данными"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Проверяем, есть ли уже данные
        cursor.execute('SELECT COUNT(*) FROM Roles')
        if cursor.fetchone()[0] == 0:
            # Добавляем роли
            roles = [
                ('Администратор', 'Полный доступ к системе', 1),
                ('Оператор', 'Управление бассейнами и кормлением', 0),
                ('Наблюдатель', 'Только просмотр данных', 0)
            ]
            cursor.executemany(
                'INSERT INTO Roles (Role_Name, Role_Description, Admin_Permissions) VALUES (?, ?, ?)',
                roles
            )

        # Проверяем, есть ли пользователи
        cursor.execute('SELECT COUNT(*) FROM Users')
        if cursor.fetchone()[0] == 0:
            # Добавляем администратора по умолчанию
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO Users (Username, Password_User, Name_User, Surname_User, 
                                   Patronymic_User, Role_ID, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_password, 'Иван', 'Иванов', 'Иванович', 1, 'активен'))

            # Добавляем оператора
            operator_password = hashlib.sha256('operator123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO Users (Username, Password_User, Name_User, Surname_User, 
                                   Patronymic_User, Role_ID, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('operator', operator_password, 'Петр', 'Петров', 'Петрович', 2, 'активен'))

        # Проверяем, есть ли бассейны
        cursor.execute('SELECT COUNT(*) FROM Pools')
        if cursor.fetchone()[0] == 0:
            # Добавляем бассейны
            pools = [
                ('Бассейн №1 - Форель', 50.0, 'Форель', 5000, '2024-01-15', 'активен'),
                ('Бассейн №2 - Осетр', 75.0, 'Осетр', 3000, '2024-01-20', 'активен'),
                ('Бассейн №3 - Карп', 60.0, 'Карп', 8000, '2024-02-01', 'активен'),
                ('Бассейн №4 - Форель', 45.0, 'Форель', 4500, '2024-02-10', 'на обслуживании')
            ]
            cursor.executemany('''
                INSERT INTO Pools (Name_Pool, Volume_Pool, Fish_Type, Fish_Count, 
                                   Stocking_Date, Status_Pool)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', pools)

        # Проверяем, есть ли датчики
        cursor.execute('SELECT COUNT(*) FROM Sensors')
        if cursor.fetchone()[0] == 0:
            # Добавляем датчики
            sensors = [
                (1, 'Температура', 'TempSensor-X100', '0-30°C', '2024-01-15'),
                (1, 'Кислород', 'O2Sensor-Pro', '0-15 мг/л', '2024-01-15'),
                (1, 'pH', 'pHMeter-2000', '4-10 pH', '2024-01-15'),
                (2, 'Температура', 'TempSensor-X100', '0-30°C', '2024-01-20'),
                (2, 'Кислород', 'O2Sensor-Pro', '0-15 мг/л', '2024-01-20'),
                (3, 'Температура', 'TempSensor-X100', '0-30°C', '2024-02-01'),
                (3, 'Кислород', 'O2Sensor-Pro', '0-15 мг/л', '2024-02-01')
            ]
            cursor.executemany('''
                INSERT INTO Sensors (ID_Pool, Type_Sensor, Model_Sensor, 
                                     Measurement_Range, Installation_Date)
                VALUES (?, ?, ?, ?, ?)
            ''', sensors)

        # Добавляем показания датчиков
        cursor.execute('SELECT COUNT(*) FROM Sensor_Readings')
        if cursor.fetchone()[0] == 0:
            # Текущее время
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            readings = [
                (1, 20.5, now, 'норма'),
                (2, 7.2, now, 'норма'),
                (3, 7.0, now, 'норма'),
                (4, 19.8, now, 'норма'),
                (5, 6.8, now, 'предупреждение'),
                (6, 21.2, now, 'норма'),
                (7, 7.5, now, 'норма')
            ]
            cursor.executemany('''
                INSERT INTO Sensor_Readings (ID_Sensor, Value_Sensor, 
                                             Timestamp_Sensor, Status_Readings)
                VALUES (?, ?, ?, ?)
            ''', readings)

        # Добавляем кормления
        cursor.execute('SELECT COUNT(*) FROM Feedings')
        if cursor.fetchone()[0] == 0:
            feedings = [
                (1, 'Ростовой корм', 2.5, '2024-11-03 08:00:00', 'автоматический'),
                (1, 'Ростовой корм', 2.5, '2024-11-03 14:00:00', 'автоматический'),
                (2, 'Стартовый корм', 1.8, '2024-11-03 09:00:00', 'ручной'),
                (3, 'Финишный корм', 3.2, '2024-11-03 10:00:00', 'автоматический')
            ]
            cursor.executemany('''
                INSERT INTO Feedings (ID_Pool, Feed_Type, Feed_Amount, 
                                      Feeding_Time, Feeding_Method)
                VALUES (?, ?, ?, ?, ?)
            ''', feedings)

        # Добавляем контрольные обловы
        cursor.execute('SELECT COUNT(*) FROM Control_Catches')
        if cursor.fetchone()[0] == 0:
            catches = [
                (1, 250.5, 100, '2024-10-15', 'Рыба развивается согласно плану'),
                (2, 850.0, 50, '2024-10-20', 'Хороший прирост массы'),
                (3, 180.2, 150, '2024-10-25', 'Нормальное развитие')
            ]
            cursor.executemany('''
                INSERT INTO Control_Catches (ID_Pool, Average_Weight, Fish_Count, 
                                             Fishing_Date, Note)
                VALUES (?, ?, ?, ?, ?)
            ''', catches)

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
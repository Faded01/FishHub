import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path="data/database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

    def init_database(self):
        """Инициализация базы данных аналогично fullflash"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица бассейнов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                volume REAL,
                fish_type TEXT,
                fish_count INTEGER,
                stocking_date TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')

        # Таблица датчиков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pool_id INTEGER,
                sensor_type TEXT NOT NULL,
                model TEXT,
                measurement_range TEXT,
                installation_date TEXT,
                FOREIGN KEY (pool_id) REFERENCES pools (id)
            )
        ''')

        # Таблица показаний датчиков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER,
                value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'normal',
                FOREIGN KEY (sensor_id) REFERENCES sensors (id)
            )
        ''')

        # Таблица кормлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pool_id INTEGER,
                feed_type TEXT,
                amount REAL,
                feeding_time TEXT,
                feeding_method TEXT,
                FOREIGN KEY (pool_id) REFERENCES pools (id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)
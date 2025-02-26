import sqlite3
from typing import List, Optional
from Models import UserFull

DB_NAME = "notes.db"

class DatabaseSQLite:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        """Подключение к базе данных"""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Создание таблиц, если они не существуют"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            conn.commit()

    #______ Функции для пользоваиелей ________

    def create_user(self, username: str, password: str) -> int:
        """Добавляет нового пользователя"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return cursor.lastrowid

    def get_all_users(self) -> List[UserFull]:
        """Возвращает список всех пользователей"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            result = []
            
            for row in users:
                result.append(UserFull(id=row[0], username=row[1]))
            return result

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Возвращает пользователя по ID"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return {"id": row[0], "username": row[1]} if row else None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Возвращает пользователя по username"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return {"id": row[0], "username": row[1], "password": row[2]} if row else None

    def update_user(self, user_id: int, username: str, password: str) -> bool:
        """Обновляет данные пользователя"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

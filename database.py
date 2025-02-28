import sqlite3
from typing import List, Optional
from Models import UserFull, Role

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
            conn.commit()

    #______ Функции для пользователей ________

    def create_user(self, username: str, password: str) -> UserFull:
        """Добавляет нового пользователя и возвращает объект UserFull"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            user_id = cursor.lastrowid
            return UserFull(id=user_id, username=username)

    def get_all_users(self) -> List[UserFull]:
        """Возвращает список всех пользователей в виде объектов UserFull"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users")
            users = cursor.fetchall()
            # Возвращаем пользователей без паролей для безопасности
            return [UserFull(id=row[0], username=row[1], role=row[2]) for row in users]

    def get_user_by_id(self, user_id: int) -> Optional[UserFull]:
        """Возвращает пользователя по ID в виде объекта UserFull"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return UserFull(id=row[0], username=row[1], role=row[2]) if row else None

    def get_user_by_username(self, username: str) -> Optional[UserFull]:
        """Возвращает пользователя по username в виде объекта UserFull"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            return UserFull(id=row[0], username=row[1], password=row[2], role=row[3]) if row else None

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
        
    def update_user_role(self, user_id: int, new_role: Role):
        """Обновляет роль пользователя в базе данных"""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "UPDATE users SET role = ? WHERE id = ?"
            cursor.execute(query, (new_role.value, user_id))
            conn.commit()
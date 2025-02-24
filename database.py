import sqlite3
from typing import List, Optional

DB_NAME = "notes.db"

class DatabaseInterface:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        """Подключение к базе данных"""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Создание таблицы, если она не существует"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_note(self, title: str, content: str) -> int:
        """Добавляет новую заметку и возвращает её ID"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            return cursor.lastrowid

    def get_all_notes(self) -> List[dict]:
        """Возвращает список всех заметок"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM notes")
            notes = cursor.fetchall()
            return [{"id": row[0], "title": row[1], "content": row[2]} for row in notes]

    def get_note_by_id(self, note_id: int) -> Optional[dict]:
        """Возвращает одну заметку по её ID"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return {"id": row[0], "title": row[1], "content": row[2]} if row else None

    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Обновляет заметку и возвращает True, если была изменена"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, note_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку и возвращает True, если удаление прошло успешно"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

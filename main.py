from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import DatabaseInterface

# Создаем экземпляр FastAPI
app = FastAPI()

# Создаем объект базы данных
db = DatabaseInterface()

#  Модель данных для заметки (Pydantic)
class Note(BaseModel):
    title: str
    content: str

#  POST - Создать новую заметку
@app.post("/notes/")
def create_note(note: Note):
    note_id = db.create_note(note.title, note.content)
    return {"id": note_id, "title": note.title, "content": note.content}

#  GET - Получить все заметки
@app.get("/notes/")
def get_notes():
    return db.get_all_notes()

#  GET - Получить заметку по ID
@app.get("/notes/{note_id}")
def get_note(note_id: int):
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note

#  PUT - Обновить заметку (через JSON)
@app.put("/notes/{note_id}")
def update_note(note_id: int, note: Note):
    updated = db.update_note(note_id, note.title, note.content)
    if not updated:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"message": "Заметка обновлена"}

#  DELETE - Удалить заметку
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    deleted = db.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"message": "Заметка удалена"}

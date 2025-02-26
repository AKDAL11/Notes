from pydantic import BaseModel

# ______ Модели _________

class Note(BaseModel):
    title: str
    content: str

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserFull(BaseModel):
    id: str
    username: str


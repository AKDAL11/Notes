from typing import Optional
from pydantic import BaseModel
from enum import Enum
# ______ Модели _________
class Role(Enum):
    ADMIN= 'ADMIN'
    USER='USER'

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
    id: int
    username: str
    password: Optional[str] = None
    role: Optional[Role] = Role.USER
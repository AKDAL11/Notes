from fastapi import FastAPI, HTTPException, Depends, Header
from database import DatabaseSQLite
from passlib.hash import bcrypt
from Models import Note, UserLogin, UserRegister
import jwt
import datetime

# Секретный ключ для JWT
SECRET_KEY = "supersecret"

# Создаем экземпляр FastAPI
app = FastAPI()

# Создаем объект базы данных
db = DatabaseSQLite()



# _________ Функции _______

def create_token(username: str):
    """Создает JWT-токен"""
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    """Проверяет JWT-токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")


# _________ Ркгистрация и вход ______

@app.post("/users/register/")
def register_user(user: UserRegister):
    """Регистрирует нового пользователя"""
    hashed_password = bcrypt.hash(user.password)
    user_id = db.create_user(user.username, hashed_password)
    return {"id": user_id, "username": user.username}


@app.post("/users/login/")
def login_user(user: UserLogin):
    """Вход пользователя и выдача JWT-токена"""
    stored_user = db.get_user_by_username(user.username)
    
    if not stored_user or not bcrypt.verify(user.password, stored_user["password"]):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    token = create_token(user.username)
    return {"token": token}


# ______CRUD для пользователей _________

@app.get("/users/")
def get_users(secret_code: str | None = Header(default=None)):
    print(secret_code)

    verify_token(secret_code) 
    """Получает всех пользователей"""
    users = db.get_all_users()
    
    for user in users: 
        print(user.id)
    return users


@app.get("/users/{user_id}")
def get_user(user_id: int, secret_code: str | None = Header(default=None)):
    """Получает информацию только о себе"""
    username = verify_token(secret_code)  # Проверяем токен и получаем username из него

    # Проверяем, соответствует ли user_id владельцу токена
    stored_user = db.get_user_by_username(username)
    print(stored_user)
    if stored_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Получаем пользователя из базы
    user = db.get_user_by_id(user_id)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserRegister):
    """Обновляет данные пользователя"""
    hashed_password = bcrypt.hash(user.password)
    updated = db.update_user(user_id, user.username, hashed_password)
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Пользователь обновлен"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Удаляет пользователя по ID"""
    deleted = db.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Пользователь удален"}

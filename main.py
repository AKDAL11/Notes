from fastapi import FastAPI, HTTPException, Depends, Header, Request, APIRouter
from fastapi.responses import JSONResponse
from database import DatabaseSQLite
from passlib.hash import bcrypt
from Models import Note, UserLogin, UserRegister, Role
import jwt
import datetime
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from middleware import auth_middleware
from pydantic import BaseModel


# Секретный ключ для JWT
SECRET_KEY = "supersecret"

# Создаем экземпляр FastAPI
app = FastAPI()

# Создаем объект базы данных
db = DatabaseSQLite()


# Модель для запроса на обновление роли
class RoleUpdateRequest(BaseModel):
    new_role: Role  # Роль пользователя (USER или ADMIN)

# Регистрируем middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Можно добавить свою логику проверки хоста
)

@app.middleware("http")
async def add_authentication(request: Request, call_next):
    # Применяем middleware для аутентификации
    return await auth_middleware(request, call_next)


# _________ Функции _______

def create_token(username: str):
    """Создает JWT-токен"""
    payload = {
        "sub": username,  # Сохраняем имя пользователя в качестве subject
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Устанавливаем срок действия токена (1 день)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    """Проверяет JWT-токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]  # Возвращаем username из токена
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
    
    if not stored_user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя")
    
    if not bcrypt.verify(user.password, stored_user.password):
        raise HTTPException(status_code=400, detail="Неверный пароль")

    token = create_token(user.username)
    return {"token": token}


# ______CRUD для пользователей _________

# Получение всех пользователей
@app.get("/users/")
async def get_users(request: Request):

    if not hasattr(request.state, "user_id") or not hasattr(request.state, "role"):
        raise HTTPException(status_code=401, detail="Пользователь не аутентифицирован")

    user = request.state.user_id  

    users = db.get_all_users()

    return {"users": users}

# Получение информации о пользователе
@app.get("/users/{user_id}")
def get_user(user_id: int, request: Request):
    """Получает информацию только о себе"""
    # Доступ к user_id через request.state.user_id
    if user_id != request.state.user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user

# Обновление данных пользователя
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserRegister, request: Request):
    """Обновляет данные пользователя"""

    hashed_password = bcrypt.hash(user.password)
    updated = db.update_user(user_id, user.username, hashed_password)
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {"message": "Пользователь обновлен"}

# Удаление пользователя
@app.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request):
    """Удаляет пользователя по ID"""

    deleted = db.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {"message": "Пользователь удален"}

# Изменение роли
@app.put("/admin/{user_id}/role")
def update_user_role(user_id: int, request: Request, role_update: RoleUpdateRequest):
    """Обновляет роль пользователя (только ADMIN может изменять роли)"""

    # Проверяем, существует ли пользователь
    target_user = db.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем роль в базе данных
    db.update_user_role(user_id, role_update.new_role)

    return {"message": f"Роль пользователя {user_id} обновлена до {role_update.new_role.value}"}
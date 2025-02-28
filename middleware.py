from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from database import DatabaseSQLite
from fastapi import HTTPException
from Models import Role

SECRET_KEY = "supersecret"  # Секретный ключ для JWT

# Middleware для проверки токена
async def auth_middleware(request: Request, call_next):
    # Маршруты, для которых не нужна аутентификация
    public_routes = ["/users/register/", "/users/login/"]

    # Если маршрут публичный (например, регистрация или логин), пропускаем его
    if request.url.path in public_routes:
        return await call_next(request)

    # Получаем токен из заголовков запроса
    token = request.headers.get("Authorization")

    if not token:
        return JSONResponse(status_code=401, content={"detail": "Требуется токен"})

    try:
        # Декодируем токен
        token = token.split(" ")[1]  # Берем часть после "Bearer "
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["sub"]  # Извлекаем username
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Токен истек"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Неверный токен"})

    # Проверяем пользователя в базе
    db = DatabaseSQLite()
    stored_user = db.get_user_by_username(username)

    if not stored_user:
        return JSONResponse(status_code=401, content={"detail": "Пользователь не найден"})

    # Сохраняем id и роль в request.state
    request.state.user_id = stored_user.id
    request.state.role = stored_user.role

    print(f"Авторизован: {stored_user.username}, ID: {stored_user.id}, Role: {stored_user.role}")

    # Проверка, является ли пользователь админом (если необходимо)
    if request.url.path.startswith("/admin") and stored_user.role != Role.ADMIN:
        return JSONResponse(status_code=403, content={"detail": "Доступ запрещен. Требуется роль администратора."})

    return await call_next(request)

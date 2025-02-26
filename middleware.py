from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from database import DatabaseSQLite
from fastapi import HTTPException

SECRET_KEY = "supersecret"  # Секретный ключ для вашего JWT

# Middleware для проверки токена
async def auth_middleware(request: Request, call_next):
    # Маршруты, для которых не нужна аутентификация
    public_routes = ["/users/register/", "/users/login/"]
    
    # Если маршрут публичный (например, регистрация или логин), пропускаем его
    if request.url.path in public_routes:
        return await call_next(request)

    # Получаем токен из заголовков запроса
    token = request.headers.get("Authorization")
    
    # Если токен отсутствует, возвращаем ошибку
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Требуется токен"})

    try:
        # Декодируем токен и получаем данные пользователя
        token = token.split(" ")[1]  # Получаем сам токен после "Bearer "
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["sub"]  # username сохранен в поле "sub" в токене
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Токен истек"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Неверный токен"})

    # Проверяем пользователя в базе данных
    db = DatabaseSQLite()
    stored_user = db.get_user_by_username(username)
    
    if not stored_user:
        return JSONResponse(status_code=401, content={"detail": "Пользователь не найден"})

    # Сохраняем user_id в state для дальнейшего использования
    request.state.user = stored_user

    return await call_next(request)

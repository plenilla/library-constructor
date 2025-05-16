from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.future import select

from ....core import get_db

from ....models import User, UserRole
from .schemas import UserLogin, UserCreate


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: UserLogin = Depends(UserLogin.as_form),
):
    """
    Авторизация на аккаунт

    Args:
        db (AsyncSession): Сессия базы данных.
        request (Request): Запрос на сессию для авторизации
        form_data (UserLogin): Данные для авторизации
    Returns:
        JSONResponse: Результат входа пользователя
    """
    # Поиск пользователя по username
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user:
        return JSONResponse(
            content={"error": "Пользователь не найден"}, status_code=404
        )

    # Проверка пароля
    if not pwd_context.verify(form_data.password, user.hashed_password):
        return JSONResponse(content={"error": "Неправильный пароль"}, status_code=401)

    # Сохраняем информацию о пользователе в сессии
    request.session["user_id"] = str(user.id)
    request.session["role"] = user.role.value
    is_authenticated = "user_id" in request.session
    request.session["fullname"] = user.fullname or ""

    return JSONResponse(
        content={
            "message": "Успешный вход",
            "role": user.role.value,
            "is_authenticated": is_authenticated,
            "fullname": user.fullname or "",
        },
        status_code=200,
    )


@router.get("/check_auth")
async def check_auth(request: Request):
    """
    Проверка авторизации пользователя

    Args:
        request (Request): Запрос для проверки сессии
    Returns:
        JSONResponse: Информация об аутентификации и роли пользователя
    """
    try:
        is_authenticated = "user_id" in request.session
        role = request.session.get("role", None)
        fullname = request.session.get("fullname", None)

        return JSONResponse(
            content={
                "is_authenticated": is_authenticated,
                "role": role,
                "fullname": fullname,
                "user_id": request.session.get("user_id") if is_authenticated else None,
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={"error": "Ошибка при проверке авторизации", "details": str(e)},
            status_code=500,
        )


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    # Формируем JSON‑ответ, а не RedirectResponse
    response = JSONResponse({"message": "Вы успешно вышли"}, status_code=200)
    response.delete_cookie("session", path="/")  
    return response


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: UserCreate = Depends(UserCreate.as_form),
):
    """
    Регистрация нового пользователя

    Args:
        request (Request): Запрос для установки сессии
        db (AsyncSession): Сессия базы данных
        form_data (UserCreate): Данные для регистрации

    Returns:
        JSONResponse: Результат регистрации
    """
    # Проверка совпадения паролей
    if form_data.password != form_data.password_confirm:
        return JSONResponse(content={"error": "Пароли не совпадают"}, status_code=400)

    # Проверка существования пользователя
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if user:
        return JSONResponse(
            content={"error": "Пользователь с таким логином уже существует"},
            status_code=400,
        )

    # Создание нового пользователя
    hashed_password = pwd_context.hash(form_data.password)

    try:
        new_user = User(
            username=form_data.username, 
            hashed_password=hashed_password, 
            role=UserRole.READER,
            fullname=form_data.fullname
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Автоматический вход после регистрации
        request.session["user_id"] = str(new_user.id)
        request.session["role"] = new_user.role.value
        request.session["fullname"] = new_user.fullname or ""
        
        return JSONResponse(
            content={
                "message": "Пользователь успешно зарегистрирован",
                "user_id": new_user.id,
                "username": new_user.username,
                "role": new_user.role.value,
            },
            status_code=201,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"error": "Ошибка при регистрации", "details": str(e)},
            status_code=500,
        )


# admin.py


from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel
from ....models import User
from ....core import get_db


admin_router = APIRouter()


# Функция для проверки, что текущий пользователь – администратор
def check_admin(request: Request):
    if request.session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")


# Endpoint для отдачи статической панели админа (файл adminpanel.html должен лежать в каталоге frontend)

# Endpoint для получения списка пользователей в JSON
@admin_router.get("/dashboard/users", response_class=JSONResponse)
async def get_users(request: Request, db: AsyncSession = Depends(get_db)):
    check_admin(request)
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_list = [
        {"id": user.id, "username": user.username, "role": user.role.value}
        for user in users
    ]
    return JSONResponse(content=users_list)


# Схема для обновления пользователя


# Pydantic-схема запроса
class UserUpdate(BaseModel):
    username: str
    role: str


# Endpoint для обновления данных пользователя (используем JSON)
@admin_router.put("/dashboard/users/{user_id}")
async def update_user(
    user_id: int, update: UserUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.username = update.username
        user.role = update.role

        await db.commit()
        await db.refresh(user)

        return {"id": user.id, "username": user.username, "role": user.role}

    except Exception as e:
        print("Ошибка обновления пользователя:", e)
        raise HTTPException(
            status_code=500, detail="Ошибка сервера при обновлении пользователя"
        )


# Endpoint для удаления пользователя
@admin_router.delete("/dashboard/users/{user_id}", response_class=JSONResponse)
async def delete_user(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    check_admin(request)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    return JSONResponse(content={"message": "User deleted"})

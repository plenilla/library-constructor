from fastapi import APIRouter, Form, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.future import select


from ...core.models import User, UserRole, get_db
from ..auth.auth_schemas import UserLogin, UserCreate


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: UserLogin = Depends(UserLogin.as_form),
):
    """
    Авторизации на аккаунт

    Args:
        db (AsyncSession): Сессия базы данных.
        request (Request): Запрос на сессию для авторизации
        form_data (UserLogin): Данные для авторизации
    Returns:
        HTMLResponse: Вход пользователя
    """
    # Поиск пользователя по username
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user:
        return "пользователь не найден"

    # Проверка пароля
    if not pwd_context.verify(form_data.password, user.hashed_password):
        return "неправльный пароль"

    # Сохраняем информацию о пользователе в сессии
    request.session["user_id"] = str(user.id)
    request.session["role"] = user.role.value

    # Перенаправляем пользователя в зависимости от роли
    redirect_map = {
        UserRole.READER: "/",
        UserRole.LIBRARIAN: "/exhibitions/",
        UserRole.ADMIN: "/admin_dashboard/",
    }

    return RedirectResponse(url=redirect_map.get(user.role, "/"), status_code=302)


@router.get("/check_auth")
async def check_auth(request: Request):
    """
    Проверка авторизации аккаунта

    Args:
        request (Request): Запрос на сессию для проверки
    Returns:
        HTMLResponse: Вывод авторизован ли пользователь
    """
    return {"is_authenticated": "user_id" in request.session}


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """
    Авторизации на аккаунт

    Args:
        db (AsyncSession): Сессия базы данных.
        request (Request): Запрос на сессию для выхода
    Returns:
        HTMLResponse: Вывод пользователя
    """
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_class=HTMLResponse)
async def register(
    db: AsyncSession = Depends(get_db),
    form_data: UserCreate = Depends(UserCreate.as_form),
):
    """
    Регистрация пользователя

    Args:
        db (AsyncSession): Сессия базы данных.
        form_data: Данные для регистрации.
    Returns:
        HTMLResponse: Регистрация пользователя
    """
    if form_data.password != form_data.password_confirm:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    # Проверка, существует ли уже пользователь
    result = await db.execute(select(User).where(User.username == form_data.username))

    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким логином уже существует"
        )

    hashed_password = pwd_context.hash(form_data.password)

    new_user = User(
        username=form_data.username, hashed_password=hashed_password, role="reader"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # После регистрации перенаправие пользователя на страницу логина
    return RedirectResponse(url="/user-login/", status_code=302)

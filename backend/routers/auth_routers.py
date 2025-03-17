from fastapi import APIRouter, Form, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from core.models.db_helper import get_db
from core.models import User  
from sqlalchemy.future import select

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя по username
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Сохраняем информацию о пользователе в сессии
    request.session["user_id"] = user.id
    request.session["role"] = user.role

    # Перенаправляем пользователя в зависимости от роли
    if user.role == "reader":
        return RedirectResponse(url="/reader_home", status_code=302)
    elif user.role == "librarian":
        return RedirectResponse(url="/librarian_home", status_code=302)
    else:
        # Если роль не распознана, можно перенаправить на главную страницу
        return RedirectResponse(url="/", status_code=302)

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Проверка, существует ли уже пользователь
    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password, role="reader")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # После регистрации перенаправие пользователя на страницу логина
    return RedirectResponse(url="/user-login/", status_code=302)
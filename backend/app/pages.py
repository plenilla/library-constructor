from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from ..core.models import get_db


router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# Инициализируем шаблоны
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "..", "frontend"))

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, session: AsyncSession = Depends(get_db)):
    try:
        # Проверка подключения к БД
        await session.execute(text("SELECT 1"))

        # Рендер главной страницы
        return templates.TemplateResponse(
            "index.html", {"request": request}  
        )

    except SQLAlchemyError as e:
        # Логируем ошибку
        print(f"Database error: {str(e)}")
        
        # Возвращаем HTML-страницу с ошибкой
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Database connection failed",
                "error_details": str(e)
            },
            status_code=500
        )

@router.get("/exhibitions/", response_class=HTMLResponse)
async def item_page(request: Request):
    """Это страница со списком всех выставок"""
    return templates.TemplateResponse("exhibitions.html", {"request": request})


@router.get("/user-regit/", response_class=HTMLResponse)
async def register_page(request: Request):
    """Это страница для регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/user-login/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Это страница для авторизации"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/reader_home/", response_class=HTMLResponse)
async def reader_home(request: Request):
    """Это страница читателя, главная страница по сути"""
    if request.session.get("role") != "reader":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return templates.TemplateResponse("reader_home.html", {"request": request})


@router.get("/librarian_home/", response_class=HTMLResponse)
async def librarian_home(request: Request):
    """Это для того, чтобы читатель смог попасть для теста на страницу"""
    if request.session.get("role") != "librarian":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return templates.TemplateResponse("librarian_home.html", {"request": request})

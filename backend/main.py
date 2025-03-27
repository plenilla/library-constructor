from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
import os


from routers.items import router as items_router
from routers.auth_routers import router as users_router
from routers.sectionsRazdels_routers import router as section_router
from routers.textRazdels_routers import router as content_text
from routers.contentRazdels_routers import router as razdel_router
from routers.content_book_routers import router as content_book
from core.models.db_helper import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Этот код не нужен при использовании Alembic для миграций
    # async with db_helper.engine.begin() as conn:
    #     await conn.run_async(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Подключаем роутеры
app.include_router(items_router, prefix="/items", tags=["items"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(section_router, prefix="/page", tags=["pages"])
app.include_router(content_text, prefix="/page", tags=["pages"])
app.include_router(razdel_router, prefix="/page", tags=["pages"])
app.include_router(content_book, prefix="/page", tags=["pages"])


# Добавляем SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY_HERE")

# Подключаем папку static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "frontend", "static")),
    name="static",
)
app.mount("/picture", StaticFiles(directory="picture"), name="picture")

# Инициализируем шаблоны
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "frontend"))

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Эндпоинты для рендеринга шаблонов
# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
@app.get("/")
async def root(session: AsyncSession = Depends(get_db)):
    # Пример запроса
    # result = await session.execute("SELECT 1")
    return {"message": "MySQL connection successful"}


@app.get("/item/", response_class=HTMLResponse)
async def item_page(request: Request):
    return templates.TemplateResponse("item.html", {"request": request})


@app.get("/user-regit/", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/user-login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/reader_home/", response_class=HTMLResponse)
async def reader_home(request: Request):
    if request.session.get("role") != "reader":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return templates.TemplateResponse("reader_home.html", {"request": request})


@app.get("/librarian_home/", response_class=HTMLResponse)
async def librarian_home(request: Request):
    if request.session.get("role") != "librarian":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return templates.TemplateResponse("librarian_home.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from .app.pages import BASE_DIR
from .app.middleware import setup_middleware
from .app.auth.auth_routers import router as users_router

# from .app.constructor_v1.exhibitions_routers import router as exhibitions_router_v1
from .app.constructor_v2.routers import (
    exhibition_router,
    section_router,
    content_router,
    book_router,
)
from .app.admin.admin_routers import router as admin_router
from .app.pages import router as page_router
from .app.books.routers.books import router as books_router
from .core.models import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполняется при запуске
    async with engine.begin() as conn:
        # Для создания всех таблиц
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created or already exist")

    yield  # Здесь приложение работает

    # Код выполняется при завершении
    # Можно добавить очистку ресурсов


app = FastAPI(lifespan=lifespan)


# Подключаем роутеры
## Роутеры для конструктора  ЭКВ
# app.include_router(exhibitions_router_v1, prefix="/v1", tags=["pages"])
app.include_router(exhibition_router, prefix="/v2", tags=["Выставка"])
app.include_router(section_router, prefix="/v2", tags=["Разделы"])
app.include_router(content_router, prefix="/v2", tags=["Контент"])
app.include_router(book_router, prefix="/v2", tags=["Книги для раздела"])
## Роутеры для пользователей
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(admin_router, prefix="/admin", tags=["Админ"])
## Роутеры  для страниц
app.include_router(page_router)
## Прочие роутеры
app.include_router(books_router, tags=["Книги"])

# Добавляем SessionMiddleware
setup_middleware(app)

# Подключаем папку static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "..", "frontend", "static")),
    name="static",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

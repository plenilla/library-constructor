from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from .core.pages import BASE_DIR
from .core.middleware import setup_middleware
from .core.db_helper import db_helper, get_db
from .core import Base

from .designer import (
    exhibitions_router,
    sections_router,
    contents_router,
)
from .users.api import router as users_router
from .users.admin import router as admin_router
from .core.pages import router as page_router
from .books.api import router as book_router
from .books.api2 import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created or already exist")

    yield  # Здесь приложение работает

    # Закрываем соединения при завершении
    await db_helper.close()
    print("Database connections closed")


app = FastAPI(lifespan=lifespan)

# Подключаем роутеры
app.include_router(exhibitions_router, prefix="/v2", tags=["Выставка"])
app.include_router(sections_router, prefix="/v2", tags=["Разделы"])
app.include_router(contents_router, prefix="/v2", tags=["Контент"])
app.include_router(book_router, tags=["Книги"])
app.include_router(books_router, prefix="/v2", tags=["Книги для раздела"])
app.include_router(users_router, prefix="/users", tags=["Пользователи"])
app.include_router(admin_router, prefix="/admin", tags=["Админ"])
app.include_router(page_router)

# Добавляем SessionMiddleware
setup_middleware(app)

# Подключаем папку static
app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(BASE_DIR, "..", "..", "..", "frontend", "static")
    ),
    name="static",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

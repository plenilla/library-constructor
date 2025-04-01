from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from .app.pages import BASE_DIR
from .app.middleware import setup_middleware
from .app.auth.auth_routers import router as users_router
from .app.constructor.exhibitions_routers import router as exhibitions_router
from .app.pages import router as page_router
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
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(exhibitions_router, prefix="/page", tags=["pages"])
app.include_router(page_router)

# Добавляем SessionMiddleware
setup_middleware(app)

# Подключаем папку static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "..", "frontend", "static")),
    name="static",
)
app.mount(
    "/picture",
    StaticFiles(
        directory=os.path.join(BASE_DIR, "..", "..", "frontend", "static", "picture")
    ),
    name="picture",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

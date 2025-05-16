from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from .core import BASE_DIR
from .core.middleware import setup_middleware
from .core.database import db_helper, get_db
from .models import Base


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

# Добавляем SessionMiddleware
setup_middleware(app)

# Подключаем папку static
app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(BASE_DIR, "..", "..", "..", "frontend", "public")
    ),
    name="static",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

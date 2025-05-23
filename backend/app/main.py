from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from .core import BASE_DIR, MEDIA_DIR
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
@app.get("/picture/{filename}")
def get_photo(filename: str):
    path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(path):
        return JSONResponse(status_code=404, content={"detail": "File not found"})
    return FileResponse(path)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

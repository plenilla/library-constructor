from pydantic_settings import BaseSettings
import os
from pathlib import Path

# данные для входа(в моем случае в БД)
# load_dotenv()


# # загрузка данных из .env
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = os.getenv("DB_NAME")


class Settings(BaseSettings):
    SECRET_KEY: str
    db_url: str 
    db_echo: bool = True

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

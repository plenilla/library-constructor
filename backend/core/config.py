from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

# данные для входа(в моем случае в БД)
load_dotenv()


# загрузка данных из .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")


class Setting(BaseSettings):
    db_url: str = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
    db_echo: bool = True


settings = Setting()

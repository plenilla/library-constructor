
### для обновление базы данных
alembic revision --autogenerate -m "Add column" - Создание миграцию
alembic upgrade head - применение миграции

### применение для подключения к базам данным через .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")



### подключения к базам данным
config = context.config

config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)
target_metadata = Base.metadata 
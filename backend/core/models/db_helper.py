from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


from ..config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            future=True,  # Использование современного API SQLAlchemy
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def close(self):
        """Закрыть соединение с базой данных."""
        await self.engine.dispose()


# Экземпляр DatabaseHelper (создается один раз)
db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)


async def get_db() -> AsyncSession:
    """Получение сессии для работы с базой данных."""
    async with db_helper.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()  # Корректное закрытие сессии

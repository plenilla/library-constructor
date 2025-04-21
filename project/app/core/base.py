from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

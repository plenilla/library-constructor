from sqlalchemy import Column, String, Enum
import enum


from .base import Base

""" Добавляем Enum роли """


class UserRole(enum.Enum):
    READER = "reader"
    LIBRARIAN = "librarian"
    ADMIN = "admin"


class User(Base):
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

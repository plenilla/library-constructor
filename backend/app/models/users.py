from sqlalchemy import Column, String, Enum
import enum
from sqlalchemy.orm import relationship
from .base_model import Base

""" Добавляем Enum роли """


class UserRole(enum.Enum):
    READER = "reader"
    LIBRARIAN = "librarian"
    ADMIN = "admin"


class User(Base):
    username = Column(String(50), unique=True, index=True, nullable=False)
    fullname = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    exhibitions = relationship("Exhibition", back_populates="author")
from sqlalchemy import Column, Integer, String
from .base import Base

class User(Base):
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  
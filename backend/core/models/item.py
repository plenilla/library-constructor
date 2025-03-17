from sqlalchemy import Column, Integer, String
from .base import Base

class Item(Base):
    name = Column(String(50))
    description = Column(String(255))
    color = Column(String(255))
    
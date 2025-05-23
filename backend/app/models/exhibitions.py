from sqlalchemy import (
    ForeignKey,
    Text,
    Boolean,
    Column,
    Integer,
    DateTime,
    Enum,
    CheckConstraint,
    String,
)
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base_model import Base
from .books import Book


class Exhibition(Base):
    title = Column(Text, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    is_published = Column(Boolean, default=True)
    image = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    author_id = Column(
    Integer,
    ForeignKey('users.id', ondelete="SET NULL"),  # ← сюда ondelete
    nullable=True
)
    author = relationship("User", back_populates="exhibitions")
    sections = relationship(
        "Section",
        back_populates="exhibitions",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )






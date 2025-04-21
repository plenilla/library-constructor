from sqlalchemy import (
    ForeignKey,
    Text,
    Boolean,
    Column,
    Integer,
    DateTime,
    Enum,
    CheckConstraint,
)
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...core.base import Base
from ...books.models import Book


class Exhibition(Base):
    title = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True)
    image = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime, nullable=True)
    sections = relationship(
        "Section",
        back_populates="exhibitions",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )






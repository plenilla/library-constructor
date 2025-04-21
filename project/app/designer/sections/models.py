from sqlalchemy import (
    ForeignKey,
    Text,
    Column,
    Integer,
)
from sqlalchemy.orm import relationship

from ...core.base import Base
from ...books.models import Book


class Section(Base):
    title = Column(Text, nullable=False)
    order = Column(Integer, nullable=True, default=None)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"))
    # Связи
    exhibitions = relationship(
        "Exhibition",
        back_populates="sections",
        lazy="selectin",
    )
    content_blocks = relationship(
        "ContentBlock",
        back_populates="section",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

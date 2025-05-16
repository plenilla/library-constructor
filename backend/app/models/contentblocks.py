from sqlalchemy import (
    ForeignKey,
    Text,
    Column,
    Integer,
    Enum,
    CheckConstraint,
)
import enum
from sqlalchemy.orm import relationship

from .base_model import Base

class ContentBlockType(enum.Enum):
    TEXT = "text"
    BOOK = "book"


class ContentBlock(Base):
    type = Column(Enum(ContentBlockType), nullable=False)
    text_content = Column(Text)
    # Связи
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.id"))

    section = relationship("Section", back_populates="content_blocks")
    book = relationship("Book", back_populates="content_blocks", lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            "(type = 'text' AND text_content IS NOT NULL AND book_id IS NULL) OR "
            "(type = 'book' AND book_id IS NOT NULL AND text_content IS NULL)",
            name="content_block_type_check",
        ),
    )

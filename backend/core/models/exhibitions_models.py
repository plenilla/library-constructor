from sqlalchemy import (
    ForeignKey,
    Text,
    Boolean,
    Column,
    Integer,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


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


class Section(Base):
    title = Column(Text, nullable=False)
    exhibition_id = Column(
        Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"), nullable=False
    )
    exhibitions = relationship(
        "Exhibition",
        back_populates="sections",
        lazy="selectin",
    )
    contents = relationship(
        "Content",
        back_populates="sections",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TextArray(Base):
    text_data = Column(Text, nullable=False)
    contents_text = relationship(
        "Content",
        back_populates="text_data",
        lazy="selectin",
    )


class Content(Base):
    section_id = Column(
        Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
    )
    books_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=True,
    )
    text_id = Column(
        Integer,
        ForeignKey("textarrays.id"),
        nullable=True,
    )

    books = relationship("Book", back_populates="contents", lazy="selectin")
    sections = relationship(
        "Section",
        back_populates="contents",
        lazy="selectin",
    )
    text_data = relationship(
        "TextArray",
        back_populates="contents_text",
        lazy="selectin",
    )
    __table_args__ = (
        CheckConstraint(
            "(books_id IS NOT NULL AND text_id IS NULL) OR "
            "(books_id IS NULL AND text_id IS NOT NULL)",
            name="check_content_xor",
        ),
    )


class Book(Base):
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    bo = Column(Text, nullable=True)
    image = Column(Text, nullable=False)
    contents = relationship(
        "Content",
        back_populates="books",
        lazy="selectin",
    )

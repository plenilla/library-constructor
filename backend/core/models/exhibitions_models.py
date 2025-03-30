from sqlalchemy import ForeignKey, Text, Boolean, Column, Integer
from sqlalchemy.orm import relationship
import enum

from .base import Base


class Exhibition(Base):
    title = Column(Text, nullable=False)
    is_published = Column(Boolean, default=False)
    sections = relationship(
        "Section",
        back_populates="exhibitions",
        lazy="selectin",
        cascade="all, delete-orphan",
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
    sections = relationship(
        "Section",
        back_populates="contents",
        lazy="selectin",
    )

    books_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=True,
    )
    books = relationship("Book", back_populates="contents", lazy="selectin")

    text_id = Column(
        Integer,
        ForeignKey("textarrays.id"),  
        nullable=True,
    )
    text_data = relationship(
        "TextArray",
        back_populates="contents_text",
        lazy="selectin",
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

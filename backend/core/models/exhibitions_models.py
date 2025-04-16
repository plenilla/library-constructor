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
from sqlalchemy.sql import func, text
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


class ContentBlockType(enum.Enum):
    TEXT = "text"
    BOOK = "book"


class ContentBlock(Base):
    type = Column(Enum(ContentBlockType), nullable=False)
    text_content = Column(Text)
    order = Column(Integer, nullable=True, default=None)
    # Связи
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.id"))

    section = relationship("Section", back_populates="content_blocks")
    book = relationship("Book", back_populates="content_blocks")

    __table_args__ = (
        CheckConstraint(
            "(type = 'text' AND text_content IS NOT NULL AND book_id IS NULL) OR "
            "(type = 'book' AND book_id IS NOT NULL AND text_content IS NULL)",
            name="content_block_type_check",
        ),
    )


class Book(Base):
    title = Column(Text, nullable=False)
    annotations = Column(Text)
    library_description = Column(Text)
    image_url = Column(Text)
    # СВязь
    content_blocks = relationship(
        "ContentBlock",
        back_populates="book",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# class TextArray(Base):
#     text_data = Column(Text, nullable=False)
#     contents_text = relationship(
#         "Content",
#         back_populates="text_data",
#         lazy="selectin",
#     )


# class Content(Base):
#     section_id = Column(
#         Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
#     )
#     books_id = Column(
#         Integer,
#         ForeignKey("books.id"),
#         nullable=True,
#     )
#     text_id = Column(
#         Integer,
#         ForeignKey("textarrays.id"),
#         nullable=True,
#     )

#     books = relationship("Book", back_populates="contents", lazy="selectin")
#     sections = relationship(
#         "Section",
#         back_populates="contents",
#         lazy="selectin",
#     )
#     text_data = relationship(
#         "TextArray",
#         back_populates="contents_text",
#         lazy="selectin",
#     )
#     __table_args__ = (
#         CheckConstraint(
#             "(books_id IS NOT NULL AND text_id IS NULL) OR "
#             "(books_id IS NULL AND text_id IS NOT NULL)",
#             name="check_content_xor",
#         ),
#     )


# class Book(Base):
#     title = Column(Text, nullable=True)
#     description = Column(Text, nullable=True)
#     bo = Column(Text, nullable=True)
#     image = Column(Text, nullable=False)
#     contents = relationship(
#         "Content",
#         back_populates="books",
#         lazy="selectin",
#     )

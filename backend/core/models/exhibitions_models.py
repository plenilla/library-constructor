from sqlalchemy import ForeignKey, Text, Boolean, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List


from .base import Base


class Exhibition(Base):
    title: Mapped[str] = mapped_column(Text)
    sections: Mapped[List["Section"]] = relationship(
        back_populates="exhibitions", lazy="selectin", cascade="all, delete-orphan"
    )
    is_published = Column(Boolean, default=False)


class Section(Base):
    title: Mapped[str] = mapped_column(Text)
    contents: Mapped[List["Content"]] = relationship(
        back_populates="sections", lazy="selectin", cascade="all, delete-orphan"
    )
    exhibition_id: Mapped[int] = mapped_column(
        ForeignKey("exhibitions.id", ondelete="CASCADE")
    )
    exhibitions: Mapped["Exhibition"] = relationship(
        "Exhibition",
        back_populates="sections",
        lazy="selectin",
    )


class TextArray(Base):
    text_data: Mapped[str] = mapped_column(Text)
    contents_text: Mapped["Content"] = relationship(
        back_populates="text_data",
        lazy="selectin",
    )


class Content(Base):
    section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE")
    )
    sections: Mapped["Section"] = relationship(
        "Section",
        back_populates="contents",
        lazy="selectin",
    )

    books_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        nullable=True,
    )

    books: Mapped[Optional["Book"]] = relationship(
        back_populates="contents", lazy="selectin"
    )

    text_id: Mapped[int] = mapped_column(
        ForeignKey(TextArray.id),
        nullable=True,
    )
    text_data: Mapped[Optional["TextArray"]] = relationship(
        back_populates="contents_text",
        lazy="selectin",
    )


class Book(Base):
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(Text)
    contents: Mapped["Content"] = relationship(
        "Content",
        back_populates="books",
        lazy="selectin",
    )

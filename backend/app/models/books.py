from sqlalchemy import (
    Text,
    Column,
    Integer,
    Table,
    ForeignKey,
    String
)
from sqlalchemy.orm import relationship
from .base_model import Base

book_authors = Table(
  "book_authors",
  Base.metadata,
  Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
  Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"))
)

book_genres = Table(
  "book_genres",
  Base.metadata,
  Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
  Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"))
)

class Book(Base):
    title = Column(Text, nullable=False)
    annotations = Column(Text)
    library_description = Column(Text)
    image_url = Column(Text)
    year_of_publication = Column(Text)
    # Связь
    authors = relationship(
      "Author",
      secondary=book_authors,
      back_populates="books", 
      passive_deletes=True,
      lazy="selectin",
    )
    genres = relationship(
      "Genre",
      secondary=book_genres,
      back_populates="books",
      passive_deletes=True,
      lazy="selectin",
    )
    content_blocks = relationship(
      "ContentBlock",
      back_populates="book",
      cascade="all, delete-orphan",
      passive_deletes=True,
    )
  

class Author(Base):
  name = Column(Text)
  books = relationship(
    "Book",
    secondary=book_authors,
    back_populates="authors",
    passive_deletes=True,
    lazy="selectin"
  )
  

class Genre(Base):  
    name = Column(String(255), unique=True)  
    books = relationship(
        "Book",
        secondary=book_genres,
        back_populates="genres",
        passive_deletes=True,
        lazy="selectin"
    )
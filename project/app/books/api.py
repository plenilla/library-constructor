from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List,Optional 
import uuid
import aiofiles
import json

from ..core import get_db, MEDIA_DIR, MAX_FILE_SIZE
from .models import (
    Book,
    Author,
    Genre,
)
from .schemas import (
    BookCreate,
    BookResponse,
    AuthorResponse,
    GenreResponse,
)


router_library = APIRouter(prefix="/library")


# Эндпоинты для фильтрации книг
@router_library.get("/books/", response_model=List[BookResponse])
async def get_all_books(
    db: AsyncSession = Depends(get_db),
    author_id: Optional[int] = Query(None),
    genre_id: Optional[int] = Query(None),
    sort_order: Optional[str] = Query(None)
):
    """
    Получить отфильтрованный список книг
    Ввод
      db:- база данных
      author_id: ID автора
      genre_id: ID жанра
      sort_order: сортировка по алфавиту "asc", в обратном порядке "desc"
    Вывод
      List[BookResponse] - список книг
    """
    query = select(Book).options(
        selectinload(Book.authors),
        selectinload(Book.genres)
    )

    if author_id:
        query = query.join(Book.authors).filter(Author.id == author_id)
    
    if genre_id:
        query = query.join(Book.genres).filter(Genre.id == genre_id)

    if sort_order == "asc":
        query = query.order_by(Book.title.asc())
    elif sort_order == "desc":
        query = query.order_by(Book.title.desc())
    
    result = await db.execute(query)
    books = result.scalars().unique().all()
    return books
  
  


@router_library.get("/authors/", response_model=List[AuthorResponse])
async def get_authors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author))
    return result.scalars().all()

@router_library.get("/genres/", response_model=List[GenreResponse])
async def get_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genre))
    return result.scalars().all()


# Ручка для создания книги
@router_library.post("/books/", response_model=BookResponse)
async def create_book(
    book_data: BookCreate = Depends(BookCreate.as_form),
    db: AsyncSession = Depends(get_db),
):
  """
    Модель для создания книги

    Пример корректного запроса:
    {
        "title": "Название книги",
        "genre_ids": "1,2",     # ID жанров через запятую
        "author_ids": "3",      # ID авторов через запятую
        "image_url": "файл.jpg"
    }
  """
  try:
      # Чтение файла изображения
      file_content = await book_data.image_url.read()
      if len(file_content) > MAX_FILE_SIZE:
          raise HTTPException(413, "File too large")
      # Важно: сбросить позицию курсора файла для возможного повторного чтения
      await book_data.image_url.seek(0)
      
      async with db.begin():

        authors = []
        for author_id in book_data.author_ids:
            result = await db.execute(select(Author).where(Author.id == author_id))
            author = result.scalar_one_or_none()
            if not author:
                raise HTTPException(400, detail=f"Author with id {author_id} not found")
            authors.append(author)

        # Проверка существования жанров
        genres = []
        for genre_id in book_data.genre_ids:
            result = await db.execute(select(Genre).where(Genre.id == genre_id))
            genre = result.scalar_one_or_none()
            if not genre:
                raise HTTPException(400, detail=f"Genre with id {genre_id} not found")
            genres.append(genre)
        
        # Генерация уникального имени файла
        file_ext = book_data.image_url.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = MEDIA_DIR / filename

        # Сохранение файла
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(file_content)
        except Exception as e:
            raise HTTPException(500, f"Failed to save image: {str(e)}")


      # Создание записи в БД
      new_book = Book(
          title=book_data.title,
          annotations=book_data.annotations,
          library_description=book_data.library_description,
          image_url=f"/static/picture/{filename}",
          year_of_publication=book_data.year_of_publication,
          authors=authors,
          genres=genres,
      )

      db.add(new_book)
      await db.commit()
      
      await db.refresh(new_book, ["authors", "genres"])
        
      result = await db.execute(
        select(Book)
          .options(
            selectinload(Book.authors),
            selectinload(Book.genres)
            )
            .where(Book.id == new_book.id)
        )
      book = result.scalar_one()
        
      return book
  except json.JSONDecodeError:
    await db.rollback()
    raise HTTPException(400,"Invalid")


@router_library.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(selectinload(Book.content_blocks))
    )
    book = result.scalars().first()

    if not book:
        raise HTTPException(404, "Book not found")

    # Удаление связанных content blocks
    for content_block in book.content_blocks:
        await db.delete(content_block)

    # Удаление изображения
    if book.image_url:
        filename = book.image_url.split("/")[-1]
        file_path = MEDIA_DIR / filename
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            raise HTTPException(500, f"Failed to delete image: {str(e)}")

    await db.delete(book)
    await db.commit()
    return {"status": "success"}


# Книги для контента


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from starlette.status import HTTP_404_NOT_FOUND


from ..core import (
    get_db,
)
from .models import Book
from .schemas import (
    BookResponse,
)
from ..designer.contents.models import ContentBlock


router = APIRouter(prefix="/content/{content_id}")


@router.get("/books/", response_model=List[BookResponse])
async def get_all_content_book(content_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить все книги из контент-блок
    Args:
        content_id (int): Идентификатор контент-блока.
        db (AsyncSession): Сессия базы данных.

    Returns:
        BookResponse: Полученные книги
    """
    result = await db.execute(
        select(ContentBlock).where(
            ContentBlock.id == content_id, ContentBlock.type == "book"
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Content block not found"
        )

    resultBook = await db.execute(select(Book))
    books = resultBook.scalars().all()

    return books


@router.patch("/book/{book_id}", response_model=None)
async def unlink_book_from_content(
    content_id: int, book_id: int, db: AsyncSession = Depends(get_db)
):
    # 1. Проверка, существует ли блок с таким ID и привязанной книгой
    result = await db.execute(
        select(ContentBlock).where(
            (ContentBlock.id == content_id)
            & (ContentBlock.book_id == book_id)
            & (ContentBlock.type == "book")
        )
    )
    content_block = result.scalar_one_or_none()

    if not content_block:
        raise HTTPException(
            status_code=404, detail="Content block not found or not linked to this book"
        )

    # 2. Удаляем контент-блок
    await db.execute(delete(ContentBlock).where(ContentBlock.id == content_id))

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Database error: {str(e)}")

    return {"detail": "Content block deleted"}


@router.get("/book/{book_id}", response_model=BookResponse)
async def get_content_book_by_id(
    content_id: int, book_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Получить книгу по её ID, только если она привязана к данному контент-блоку.
    """
    # проверяем, что у контент-блока есть именно этот book_id
    result = await db.execute(
        select(ContentBlock).where(
            ContentBlock.id == content_id,
            ContentBlock.type == "book",
            ContentBlock.book_id == book_id,
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Content block not found or not linked to this book",
        )

    # возвращаем книгу
    result_book = await db.execute(select(Book).where(Book.id == book_id))
    book = result_book.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Book not found")

    return book

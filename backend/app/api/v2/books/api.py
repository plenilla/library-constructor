from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List,Optional 
import uuid
import aiofiles
import json

from .services import BooksFondsService

from ....core import get_db, MEDIA_DIR, MAX_FILE_SIZE
from ....models import (
    Book,
    Author,
    Genre,
)
from .schemas import (
    BookCreate,
    BookResponse,
    AuthorResponse,
    GenreResponse,
    BookPut,
    AuthorCreate, 
    GenreCreate
)


router_library = APIRouter()


# Эндпоинты для работы с книгами
@router_library.get("/books/", response_model=List[BookResponse])
async def get_all_books(
    author_id: Optional[List[int]] = Query(None),
    genre_id: Optional[List[int]] = Query(None),
    sort_order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_filtered_books(author_id, genre_id, sort_order)


import logging
from pathlib import Path as Pathh
from typing import Optional
import aiofiles
import aiofiles.os

logger = logging.getLogger(__name__)

async def _delete_old_image(image_url: Optional[str]) -> None:
    """
    Удаляет старый файл изображения, если он существует.
    Путь к файлу определяется с помощью MEDIA_DIR.
    """
    if not image_url:
        return

    try:
        # Предполагается, что image_url хранит относительный путь от MEDIA_DIR
        filepath = MEDIA_DIR / Pathh(image_url).name

        if await aiofiles.os.path.exists(filepath):
            if await aiofiles.os.path.isfile(filepath):
                await aiofiles.os.remove(filepath)
                logger.info(f"Deleted old image: {filepath}")
            else:
                logger.warning(f"Path is not a file: {filepath}")
        else:
            logger.info(f"File not found: {filepath}")

    except Exception as e:
        logger.error(f"Error deleting file {image_url}: {str(e)}")


async def _save_image(image: UploadFile) -> str:
    """
    Сохраняет изображение в каталоге MEDIA_DIR.
    Если каталоги не существуют, создаёт их.
    """
    # Убедимся, что MEDIA_DIR существует; если нет, создаем его с родительскими директориями
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}{Pathh(image.filename).suffix}"
    filepath = MEDIA_DIR / filename

    async with aiofiles.open(filepath, "wb") as buffer:
        content = await image.read()
        await buffer.write(content)

    return filename


@router_library.put("/books/{book_id}", response_model=BookResponse)
async def put_book(
    book_id: int,
    book_data: BookPut = Depends(BookPut.as_form),
    db: AsyncSession = Depends(get_db)
):
    finded_book = await db.execute(select(Book).where(Book.id == book_id))
    book = finded_book.scalar_one_or_none()
    if not book:
        raise HTTPException(404, "book not found") 
    
    # Check if a new image is provided
    if book_data.image_url is not None:
        # Delete the old image if it exists
        if book.image_url:
            await _delete_old_image(book.image_url)
        # Save the new image
        filename = await _save_image(book_data.image_url)
        book.image_url = f"/picture/{filename}"
            
    # Update other fields only if provided
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.annotations is not None:
        book.annotations = book_data.annotations
    if book_data.library_description is not None:
        book.library_description = book_data.library_description 
    if book_data.year_of_publication is not None:
        book.year_of_publication = book_data.year_of_publication
    
    # Update genres if provided
    if book_data.genre_ids is not None:
        result = await db.execute(
            select(Genre).where(Genre.id.in_(book_data.genre_ids))
        )
        genres = result.scalars().all()
        book.genres = genres
        
    # Update authors if provided
    if book_data.author_ids is not None:   
        result = await db.execute(
            select(Author).where(Author.id.in_(book_data.author_ids))
        )
        authors = result.scalars().all()
        book.authors = authors
        
    await db.commit()
    await db.refresh(book)
    return book
    

@router_library.get("/authors/options/", response_model=List[AuthorResponse])
async def get_authors_options(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_authors()

@router_library.get("/genres/options/", response_model=List[GenreResponse])
async def get_genres_options(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_genres()

@router_library.post("/authors/", response_model=AuthorResponse)
async def create_author(
    author_data: AuthorCreate,
    db: AsyncSession = Depends(get_db)
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    author = await service.create_author(author_data)
    await db.commit()
    return author

@router_library.post("/genres/", response_model=GenreResponse)
async def create_genre(
    genre_data: GenreCreate,
    db: AsyncSession = Depends(get_db)
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    genre = await service.create_genre(genre_data)
    await db.commit()
    return genre

@router_library.get(
    "/books/{book_id}",
    response_model=BookResponse,
    summary="Получить книгу по ID"
)
async def get_book_by_id(
    book_id: int = Path(..., title="ID книги"),
    db: AsyncSession = Depends(get_db)
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        book = await service.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Книга не найдена")
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_library.post("/books/", response_model=BookResponse)
async def create_book(
    book_data: BookCreate = Depends(BookCreate.as_form),
    db: AsyncSession = Depends(get_db),
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        book = await service.create_book(book_data)
        await db.commit()
        return book
    except Exception as e:
        await db.rollback()
        raise e

@router_library.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        await service.delete_book(book_id)
        await db.commit()
        return {"status": "success"}
    except Exception as e:
        await db.rollback()
        raise e

# Эндпоинты для поиска
@router_library.get("/authors/search/", response_model=List[AuthorResponse])
async def search_authors(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.search_authors(q)

@router_library.get("/genres/search/", response_model=List[GenreResponse])
async def search_genres(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.search_genres(q)

# Базовые эндпоинты
@router_library.get("/authors/", response_model=List[AuthorResponse])
async def get_authors(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_authors()

@router_library.get("/genres/", response_model=List[GenreResponse])
async def get_genres(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_genres()


# Книги для контент
from ....models import Book
from .schemas import (
    BookResponse,
)
from ....models import ContentBlock
from .services import BooksContentService


router = APIRouter(prefix="/content/{content_id}")


@router.get("/books/", response_model=List[BookResponse])
async def get_all_content_book(
    content_id: int, 
    db: AsyncSession = Depends(get_db)
):
    service = BooksContentService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        return await service.get_content_books(content_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, str(e))

@router.patch("/book/{book_id}", response_model=None)
async def unlink_book_from_content(
    content_id: int, 
    book_id: int, 
    db: AsyncSession = Depends(get_db)
):
    service = BooksContentService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        await service.unlink_book_from_content(content_id, book_id)
        await db.commit()
        return {"detail": "Content block deleted"}
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))

@router.get("/book/{book_id}", response_model=BookResponse)
async def get_content_book_by_id(
    content_id: int, 
    book_id: int, 
    db: AsyncSession = Depends(get_db)
):
    service = BooksContentService(db, MEDIA_DIR, MAX_FILE_SIZE)
    try:
        return await service.get_linked_book(content_id, book_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, str(e))

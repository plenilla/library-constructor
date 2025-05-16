from fastapi import APIRouter, Depends, HTTPException, Query, Path
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


@router_library.get("/authors/options/", response_model=List[AuthorResponse])
async def get_authors_options(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_authors()

@router_library.get("/genres/options/", response_model=List[GenreResponse])
async def get_genres_options(db: AsyncSession = Depends(get_db)):
    service = BooksFondsService(db, MEDIA_DIR, MAX_FILE_SIZE)
    return await service.get_genres()

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

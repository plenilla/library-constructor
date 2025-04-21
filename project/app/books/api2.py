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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from starlette.status import HTTP_404_NOT_FOUND


from ....core.models import (
    ContentBlock,
    Book,
    get_db,
)
from ..schemas import (
    ContentBlockResponse,
    BookResponse,
)


router = APIRouter(prefix="/content/{content_id}")


@router.get("/books/", response_model=List[BookResponse])
async def get_all_content_book(
    content_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
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


@router.patch("/book/{book_id}", response_model=ContentBlockResponse)
async def unlink_book_from_content(
    content_id: int, 
    book_id: int, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Находим контент-блок с указанными ID и привязанной книгой
    result = await db.execute(
        select(ContentBlock).where(
            (ContentBlock.id == content_id)
            & (ContentBlock.book_id == book_id)
            & (ContentBlock.type == "book")  # Добавляем проверку типа
        )
    )
    content_block = result.scalar_one_or_none()

    if not content_block:
        raise HTTPException(
            status_code=404, detail="Content block not found or not linked to this book"
        )

    # 2. Обновляем значение
    content_block.book_id = None

    try:
        await db.commit()
        await db.refresh(content_block)  # Обновляем объект
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Database error: {str(e)}")

    return content_block

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from starlette.status import HTTP_404_NOT_FOUND


from ....core.models import (
    ContentBlock,
    get_db,
    Section,
)
from ..schemas import (
    ContentBlockCreate,
    ContentBlockResponse,
)


router = APIRouter(prefix="/sections/{section_id}")


@router.get("/content/", response_model=List[ContentBlockResponse])
async def get_section_content(
    section_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
    """
    Получить список контент-блоков для конкретного раздела.

    Args:
        section_id (int): Идентификатор раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[ContentBlockResponse]: Список контент-блоков раздела.
    """
    # Проверяем существование раздела (при необходимости)
    result = await db.execute(select(Section).where(Section.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Section not found")

    # Выбираем все контент-блоки раздела
    result = await db.execute(
        select(ContentBlock).where(ContentBlock.section_id == section_id)
    )
    content_blocks = result.scalars().all()
    return content_blocks


@router.post("/content/", response_model=ContentBlockResponse)
async def create_content_block(
    section_id: int,
    content_data: ContentBlockCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли секция
    result = await db.execute(select(Section).where(Section.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Секция не найдена")

    # Получаем максимальное значение order в секции
    max_order_result = await db.execute(
        select(func.max(ContentBlock.order)).where(ContentBlock.section_id == section_id)
    )
    max_order = max_order_result.scalar() or 0

    # Если order не задан — автоустанавливаем
    if content_data.order is None:
        content_data.order = max_order + 1
    else:
        # Проверяем, не занят ли такой order в секции
        existing_order = await db.execute(
            select(ContentBlock).where(
                ContentBlock.section_id == section_id,
                ContentBlock.order == content_data.order
            )
        )
        if existing_order.scalar():
            raise HTTPException(status_code=400, detail="Порядковый номер уже занят в этой секции")

    content_block = ContentBlock(
        section_id=section_id,
        type=content_data.type,
        order=content_data.order,
        text_content=content_data.text_content,
        book_id=content_data.book_id,
    )
    db.add(content_block)
    await db.commit()
    await db.refresh(content_block)
    return content_block


@router.delete("/content/{content_id}")
async def delete_content_text(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await db.execute(
        select(ContentBlock).where(
            and_(ContentBlock.id == content_id, ContentBlock.type == "text")
        )
    )
    content = content.scalars().first()

    await db.execute(
        delete(ContentBlock).where(
            and_(ContentBlock.id == content_id, ContentBlock.type == "text")
        )
    )
    await db.commit()

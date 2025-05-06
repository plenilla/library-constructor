from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from ....core import get_db
from ....models import Exhibition, Section


from ..sections.schemas import SectionResponse, SectionCreate


router = APIRouter(prefix="/exhibitions/{exhibition_id}")


@router.get("/sections/", response_model=List[SectionResponse])
async def get_exhibition_sections(
    exhibition_id: int, db: AsyncSession = Depends(get_db)
):
    # Проверяем наличие выставки с указанным ID
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    exhibition = result.scalar_one_or_none()
    if exhibition is None:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    result_sections = await db.execute(
        select(Section)
        .where(Section.exhibition_id == exhibition_id)
        .order_by(Section.order.asc())
    )
    sections = result_sections.scalars().all()
    return sections


@router.post("/sections/", response_model=SectionResponse)
async def create_section(
    exhibition_id: int, section_data: SectionCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    exhibition = result.scalar_one_or_none()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    # Получаем максимальное значение order в секции
    max_order_result = await db.execute(
        select(func.max(Section.order)).where(Section.exhibition_id == exhibition_id)
    )
    max_order = max_order_result.scalar() or 0

    # Если order не задан — автоустанавливаем
    if section_data.order is None:
        section_data.order = max_order + 1
    else:
        # Проверяем, не занят ли такой order в секции
        existing_order = await db.execute(
            select(Exhibition).where(
                Section.id == exhibition_id, Section.order == section_data.order
            )
        )
        if existing_order.scalar():
            raise HTTPException(
                status_code=400, detail="Порядковый номер уже занят в этой секции"
            )

    section = Section(
        title=section_data.title,
        order=section_data.order,
        exhibition_id=exhibition_id,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


@router.delete("/sections/{section_id}")
async def delete_section(
    section_id: int, exhibition_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Удалить раздел по ID.

    Args:
        section_id (int): ID раздела.
        db (AsyncSession): Сессия базы данных.
        exhibition_id (int): ID выставки

    Returns:
        Удаленный раздел.
    """
    result = await db.execute(
        select(Section)
        .where(Section.id == section_id)
        .where(Section.exhibition_id == exhibition_id)
    )

    db_delete_section = result.scalars().first()

    if not db_delete_section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="section not found")

    await db.delete(db_delete_section)
    await db.commit()
    return {"delete section"}

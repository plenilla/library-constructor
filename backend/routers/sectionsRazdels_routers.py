from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List


from core.models import Section
from schemas.razdels_schemas import (
    SectionResponse,
    SectionBase,
)
from core.models.db_helper import get_db


router = APIRouter()


# Ручка для получения всех разделов
@router.get("/sections/", response_model=List[SectionResponse])
async def get_all_sections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Section))
    sections = result.scalars().all()
    return sections


@router.post("/sections/", response_model=SectionResponse)
async def create_section(section_data: SectionBase, db: AsyncSession = Depends(get_db)):
    new_section = Section(title=section_data.title)
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    print("New Section ID:", new_section.id)
    return new_section


@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int, section_update: SectionBase, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Section).where(Section.id == section_id))
    db_update_section = result.scalars().first()
    if not db_update_section:
        raise HTTPException(status_code=404, detail="section not found")

    # Обновляем атрибуты модели вместо замены объекта
    for field, value in section_update.model_dump().items():
        setattr(db_update_section, field, value)

    await db.commit()
    await db.refresh(db_update_section)
    return db_update_section


@router.delete("/sections/{section_id}", response_model=SectionResponse)
async def update_section(section_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Section).where(Section.id == section_id))
    db_delete_section = result.scalars().first()
    if not db_delete_section:
        raise HTTPException(status_code=404, detail="section not found")

    await db.delete(db_delete_section)
    await db.commit()
    return db_delete_section

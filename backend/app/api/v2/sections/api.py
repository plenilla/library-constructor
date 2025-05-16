from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ....core import get_db, MEDIA_DIR  # убедитесь, что MEDIA_DIR импортируется отсюда
from ..sections.schemas import SectionResponse, SectionCreate
from .services import SectionService
from ..exhibitions.services import ExhibitionService  # импорт сервиса для выставок

router = APIRouter(prefix="/exhibitions/{exhibition_slug}")

# Получаем разделы выставки по slug
@router.get("/sections/", response_model=List[SectionResponse])
async def get_exhibition_sections(
    exhibition_slug: str, 
    db: AsyncSession = Depends(get_db)
):
    # Создаем сервис выставок, передавая media_dir
    exhibition_service = ExhibitionService(db, MEDIA_DIR)
    try:
        exhibition = await exhibition_service.get_exhibition_by_slug(exhibition_slug)
        if not exhibition:
            raise HTTPException(404, "Выставка не найдена")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, "Ошибка получения выставки")

    service = SectionService(db)
    try:
        return await service.get_exhibition_sections(exhibition.id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, "Internal server error")

# Создание нового раздела через slug выставки
@router.post("/sections/", response_model=SectionResponse)
async def create_section(
    exhibition_slug: str,
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_db)
):
    # Создаем сервис выставок с media_dir
    exhibition_service = ExhibitionService(db, MEDIA_DIR)
    try:
        exhibition = await exhibition_service.get_exhibition_by_slug(exhibition_slug)
        if not exhibition:
            raise HTTPException(404, "Выставка не найдена")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, "Ошибка получения выставки")

    service = SectionService(db)
    try:
        section = await service.create_section(exhibition.id, section_data)
        await db.commit()
        await db.refresh(section)
        return section
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))

# Удаление раздела через slug выставки
@router.delete("/sections/{section_id}")
async def delete_section(
    exhibition_slug: str,
    section_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Создаем сервис выставок с media_dir
    exhibition_service = ExhibitionService(db, MEDIA_DIR)
    try:
        exhibition = await exhibition_service.get_exhibition_by_slug(exhibition_slug)
        if not exhibition:
            raise HTTPException(404, "Выставка не найдена")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, "Ошибка получения выставки")

    service = SectionService(db)
    try:
        await service.delete_section(exhibition.id, section_id)
        await db.commit()
        return {"detail": "Раздел успешно удален"}
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, "Ошибка при удалении")

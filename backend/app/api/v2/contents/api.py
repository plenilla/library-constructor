from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ....core import get_db
from ....models import ContentBlock, Section
from .schemas import ContentBlockCreate, ContentBlockResponse, ContentBlockUpdate
from .services import ContentService
from ....api.v2.exhibitions.services import ExhibitionService  # импортируем сервис выставок
from ....core import MEDIA_DIR  # если используется в ExhibitionService

router = APIRouter(
    prefix="/exhibitions/{exhibition_slug}/sections/{section_id}/content",
    tags=["content"]
)

# Получение контента раздела
@router.get("/", response_model=List[ContentBlockResponse])
async def get_section_content(
    exhibition_slug: str,
    section_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Проверка существования выставки
    exhibition = await ExhibitionService(db).get_exhibition_by_slug(exhibition_slug)
    if not exhibition:
        raise HTTPException(404, "Выставка не найдена")

    # Проверка принадлежности раздела к выставке
    section = await db.get(Section, section_id)
    if not section or section.exhibition_id != exhibition.id:
        raise HTTPException(404, "Раздел не найден")

    service = ContentService(db)
    try:
        return await service.get_section_content(section_id)
    except Exception as e:
        raise HTTPException(500, "Ошибка загрузки контента")


# Создание нового блока контента в разделе выставки
@router.post("/", response_model=ContentBlockResponse)
async def create_content_block(
    exhibition_slug: str,
    section_id: int,
    content_data: ContentBlockCreate,
    db: AsyncSession = Depends(get_db),
):
    exhibition_service = ExhibitionService(db, MEDIA_DIR)
    try:
        exhibition = await exhibition_service.get_exhibition_by_slug(exhibition_slug)
        if not exhibition:
            raise HTTPException(status_code=404, detail="Выставка не найдена")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения выставки")
    
    service = ContentService(db)
    try:
        block = await service.create_content_block(section_id, content_data)
        await db.commit()
        await db.refresh(block)
        return block
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Удаление блока контента
@router.delete("/{content_id}", response_model=None)
async def delete_block(
    exhibition_slug: str,
    section_id: int,
    content_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Проверка выставки
    exhibition = await ExhibitionService(db, MEDIA_DIR).get_exhibition_by_slug(exhibition_slug)
    if not exhibition:
        raise HTTPException(404, "Выставка не найдена")

    service = ContentService(db)
    try:
        # Удаляем любой блок (text или book), не трогая сами книги
        await service.delete_block(section_id, content_id)
        await db.commit()
        return
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))


@router.put("/{content_id}", response_model=ContentBlockResponse)
async def update_content_block(
    exhibition_slug: str,
    section_id: int,
    content_id: int,
    content_data: ContentBlockUpdate,
    db: AsyncSession = Depends(get_db)
):
    exhibition_service = ExhibitionService(db, MEDIA_DIR)
    exhibition = await exhibition_service.get_exhibition_by_slug(exhibition_slug)
    if not exhibition:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    service = ContentService(db)
    try:
        block = await service.update_content_block(section_id, content_id, content_data)
        await db.commit()
        return block
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
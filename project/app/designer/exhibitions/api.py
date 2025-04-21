from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from ...core import MEDIA_DIR, get_db
from .models import (
    Exhibition,
)
from .schemas import (
    ExhibitionBase,
    ExhibitionResponse,
)
from ..sections.models import Section


router = APIRouter()


"""Ручки для взаимодействия с выставками"""


@router.get("/exhibitions/", response_model=List[ExhibitionResponse])
async def get_all_exhibition(
    published: Optional[bool] = None, db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех выставок.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[ExhibitionResponse]: Список всех выставок.
    """
    query = select(Exhibition)
    if published is True:
        query = query.where(Exhibition.is_published == True)
    result = await db.execute(query)
    exhibitions = result.scalars().all()
    return exhibitions


@router.get("/exhibitions/{exhibition_id}", response_model=ExhibitionResponse)
async def get_exhibition(exhibition_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить конкретную выставку

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        ExhibitionResponse: вывод выставки.
    """
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    exhibition = result.scalar_one_or_none()

    if not exhibition:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    return exhibition


@router.post("/exhibitions/", response_model=ExhibitionResponse)
async def create_new_exhibition(
    exhibition_data: ExhibitionBase = Depends(ExhibitionBase.as_form),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать новую выставку.

    Args:
        exhibition_data (ExhibitionBase): Данные для создания выставки.
        db (AsyncSession): Сессия базы данных.

    Returns:
        ExhibitionResponse: Созданная выставка.
    """
    file_ext = exhibition_data.image.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = MEDIA_DIR / filename

    try:
        contents = await exhibition_data.image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(500, f"File upload failed: {e}")

    if exhibition_data.is_published:
        published_at = datetime.now(timezone.utc)
    else:
        published_at = None

    db_exhibition = Exhibition(
        title=exhibition_data.title,
        description=exhibition_data.description,
        is_published=exhibition_data.is_published,
        image=f"/static/picture/{filename}",
        created_at=datetime.now(timezone.utc),
        published_at=published_at,
    )
    db.add(db_exhibition)
    await db.commit()
    await db.refresh(db_exhibition)
    return db_exhibition


@router.put("/exhibitions/{exhibition_id}", response_model=ExhibitionResponse)
async def update_exhibition(
    exhibition_id: int,
    exhibition_data: ExhibitionBase = Depends(ExhibitionBase.as_form),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить существующую выставку.

    Args:
        exhibition_id (int): Идентификатор выставки для обновления.
        exhibition_data (ExhibitionBase): Данные для обновления выставки.
        db (AsyncSession): Сессия базы данных.

    Returns:
        ExhibitionResponse: Обновлённая выставка.
    """
    # Получаем существующую выставку из базы данных
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    db_exhibition = result.scalar_one_or_none()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    # Если передан новый файл изображения, сохраняем его и обновляем путь
    if exhibition_data.image:
        try:
            file_ext = exhibition_data.image.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = MEDIA_DIR / filename

            contents = await exhibition_data.image.read()
            with open(file_path, "wb") as f:
                f.write(contents)

            db_exhibition.image = f"/static/picture/{filename}"
        except Exception as e:
            raise HTTPException(500, f"Ошибка загрузки файла: {e}")

    # Обновляем текстовые поля и состояние публикации
    db_exhibition.title = exhibition_data.title
    db_exhibition.description = exhibition_data.description
    db_exhibition.is_published = exhibition_data.is_published

    # Обновляем published_at в зависимости от статуса публикации
    if exhibition_data.is_published and not db_exhibition.published_at:
        db_exhibition.published_at = datetime.now(timezone.utc)
    elif not exhibition_data.is_published:
        db_exhibition.published_at = None

    db.add(db_exhibition)
    await db.commit()
    await db.refresh(db_exhibition)
    return db_exhibition


@router.delete("/exhibitions/{exhibition_id}")
async def delete_exhibition(exhibition_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить выставку по ID.

    Args:
        exhibition_id (int): ID выставки.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.
    """
    result = await db.execute(
        select(Exhibition)
        .where(Exhibition.id == exhibition_id)
        .options(selectinload(Exhibition.sections).selectinload(Section.content_blocks))
    )
    exhibition = result.scalars().first()

    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    await db.delete(exhibition)
    await db.commit()

    return {"message": "Exhibition and all related sections and contents deleted"}

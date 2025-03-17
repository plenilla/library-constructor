from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from core.models import (
    Content,
    TextArray,
    Book,
)
from schemas.razdels_schemas import (
    ContentResponse,
    ContentBase,
    )
from core.models.db_helper import get_db


router = APIRouter()


# ручка для создания контента, связывающее раздел и текст
@router.post("/contents/", response_model=ContentResponse)
async def create_content(content: ContentBase, db: AsyncSession = Depends(get_db)):
    new_content = Content(
        section_id = content.section_id,
        text_id = content.text_id,
        books_id = content.books_id
    )
    db.add(new_content)
    await db.commit()
    await db.refresh(new_content)
    return(new_content)


# Получение всех записей контента
@router.get("/contents/", response_model=List[ContentResponse])
async def get_contents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content))
    contents = result.scalars().all()
    return contents


@router.put("/contents/{contents_id}", response_model=ContentResponse)
async def update_content(content_id: int, content_update: ContentBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content).where(Content.id == content_id))
    db_update_content = result.scalars().first()
   
    
    # Обновляем атрибуты модели вместо замены объекта
    for field, value in content_update.model_dump().items():
        setattr(db_update_content, field, value)
        
    await db.commit()
    await db.refresh(db_update_content)
    return db_update_content


@router.delete("/contents/{content_id}")
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await db.execute(select(Content).filter(Content.id == content_id))
    content = content.scalars().first()
    
    if content:
        # Удаляем контент
        await db.delete(content)
        await db.commit()

        # Удаляем связанный текст
        text = await db.execute(select(TextArray).filter(TextArray.id == content.text_id))
        text = text.scalars().first()
        
        book = await db.execute(select(Book).filter(Book.id == content.books_id))
        
        if text:
            await db.delete(text)
            await db.commit()

        if book:
            await db.delete(book)
            await db.commit()
        # Возвращаем успешное сообщение
        return {"message": "Контент и связанный текст удалены"}
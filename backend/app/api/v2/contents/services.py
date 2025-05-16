from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from ....models import ContentBlock, Section, Book
from .schemas import ContentBlockCreate, ContentBlockUpdate
from typing import List


class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_content_block(
        self, 
        section_id: int, 
        content_id: int, 
        data: ContentBlockUpdate
    ) -> ContentBlock:
        block = await self._get_validated_block(section_id, content_id)
        
        # Очищаем противоположные поля в зависимости от типа
        update_data = data.dict(exclude_unset=True)
        if update_data.get('type') == 'text':
            update_data['book_id'] = None
        elif update_data.get('type') == 'book':
            update_data['text_content'] = None
        
        for key, value in update_data.items():
            setattr(block, key, value)
            
        await self.db.commit()
        await self.db.refresh(block)
        return block

    async def get_section_content(self, section_id: int):
        stmt = (
            select(ContentBlock)
            .options(
                selectinload(ContentBlock.book).options(
                    selectinload(Book.authors),
                    selectinload(Book.genres)
                )
            )
            .where(ContentBlock.section_id == section_id)
        )
        result = await self.db.execute(stmt)
        blocks = result.scalars().all()
        return blocks

    async def create_content_block(
        self, 
        section_id: int, 
        content_data: ContentBlockCreate
    ) -> ContentBlock:
        section = await self._validate_section(section_id)

        # Create block
        new_block = ContentBlock(
            **content_data.dict(exclude_unset=True),
            section_id=section.id
        )
        self.db.add(new_block)
        await self.db.flush()
        return new_block

    async def delete_block(self, section_id: int, content_id: int) -> None:
        # Проверяем раздел
        await self._validate_section(section_id)

        # Получаем и удаляем блок, не трогая книгу
        block = await self._get_validated_block(section_id, content_id)
        await self.db.delete(block)

    # Helper methods
    async def _validate_section(self, section_id: int) -> Section:
        result = await self.db.execute(
            select(Section).where(Section.id == section_id)
        )
        section = result.scalar_one_or_none()
        if not section:
            raise HTTPException(404, "Section not found")
        return section



    async def _get_validated_block(
    self, 
    section_id: int, 
    content_id: int
) -> ContentBlock:
        result = await self.db.execute(
            select(ContentBlock).where(
                and_(
                    ContentBlock.id == content_id,
                    ContentBlock.section_id == section_id
                )
            )
        )
        block = result.scalar_one_or_none()
        if not block:
            raise HTTPException(404, "Content block not found")
        return block
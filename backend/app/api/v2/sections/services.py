# services/section.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from ....models import Exhibition, Section
from ..sections.schemas import SectionCreate

class SectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_exhibition_sections(self, exhibition_id: int) -> list[Section]:
        await self._validate_exhibition(exhibition_id)
        
        result = await self.db.execute(
            select(Section)
            .where(Section.exhibition_id == exhibition_id)
        )
        return result.scalars().all()

    async def create_section(
        self, 
        exhibition_id: int, 
        section_data: SectionCreate
    ) -> Section:
        await self._validate_exhibition(exhibition_id)

        new_section = Section(
            **section_data.dict(),
            exhibition_id=exhibition_id
        )
        
        self.db.add(new_section)
        await self.db.flush()
        return new_section

    async def update_section(
        self, exhibition_id: int, section_id: int, section_data: SectionCreate
    ) -> Section:
        # Validate existence
        section = await self._get_validated_section(exhibition_id, section_id)
        # Update fields
        section.title = section_data.title
        # Optionally, add other updatable fields here
        self.db.add(section)
        await self.db.flush()
        return section
    
    
    async def delete_section(
        self, 
        exhibition_id: int, 
        section_id: int
    ) -> None:
        section = await self._get_validated_section(exhibition_id, section_id)
        await self.db.delete(section)

    # Helper methods
    async def _validate_exhibition(self, exhibition_id: int) -> None:
        result = await self.db.execute(
            select(Exhibition).where(Exhibition.id == exhibition_id))
        if not result.scalar_one_or_none():
            raise HTTPException(404, "Выставка не найдена")

    async def _get_validated_section(
        self, 
        exhibition_id: int, 
        section_id: int
    ) -> Section:
        result = await self.db.execute(
            select(Section)
            .where(
                Section.id == section_id,
                Section.exhibition_id == exhibition_id
            )
        )
        section = result.scalar_one_or_none()
        if not section:
            raise HTTPException(404, "Раздел не найден")
        return section
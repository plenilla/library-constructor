from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from pathlib import Path
from typing import Optional, List
import uuid
import aiofiles
import asyncio
from datetime import datetime, timezone
from fastapi import HTTPException, UploadFile
from slugify import slugify
from ....models import Exhibition, Section
from .schemas import ExhibitionBase, PaginatedResponse

class ExhibitionService:
    def __init__(self, db: AsyncSession, media_dir: Path):
        self.db = db
        self.media_dir = media_dir

    async def get_all_exhibitions(self, published: Optional[bool]) -> List[Exhibition]:
        query = (
            select(Exhibition)
            .options(selectinload(Exhibition.author))
        )
        if published is not None:
            query = query.where(Exhibition.is_published == published)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_paginated_exhibitions(self, published, page, size, search: str = None, date_from: datetime = None, date_to: datetime = None):
        query = (
            select(Exhibition)
            .options(
                selectinload(Exhibition.author),
                selectinload(Exhibition.sections)
        )
            .where((Exhibition.is_published == published) if published is not None else True)
        )
        
        # Добавляем фильтрацию по поиску
        if search:
            query = query.where(Exhibition.title.ilike(f"%{search}%"))
        
        # Добавляем фильтрацию по дате
        if date_from:
            query = query.where(Exhibition.published_at >= date_from)
        if date_to:
            query = query.where(Exhibition.published_at <= date_to)
        
        # Остальной код остается прежним
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        exhibitions = result.scalars().all()
        
        # Обновляем подсчет с учетом фильтров
        count_query = select(func.count(Exhibition.id)).where(
            (Exhibition.is_published == published) if published is not None else True
        )
        if search:
            count_query = count_query.where(Exhibition.title.ilike(f"%{search}%"))
        if date_from:
            count_query = count_query.where(Exhibition.published_at >= date_from)
        if date_to:
            count_query = count_query.where(Exhibition.published_at <= date_to)
        
        total = await self.db.scalar(count_query)
        total_pages = (total + size - 1) // size if total else 0
        
        return {
            "items": exhibitions,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        }

    async def get_exhibition_by_slug(self, slug: str) -> Exhibition:
        result = await self.db.execute(
            select(Exhibition)
            .options(selectinload(Exhibition.author))
            .where(Exhibition.slug == slug)
        )
        if exhibition := result.scalar_one_or_none():
            return exhibition
        raise HTTPException(404, "Exhibition not found")

    async def get_exhibition_by_id(self, exhibition_id: int) -> Exhibition:
        stmt = (
            select(Exhibition)
            .options(
                selectinload(Exhibition.author),
                selectinload(Exhibition.sections)   
            )
            .where(Exhibition.id == exhibition_id)
        )
        result = await self.db.execute(stmt)
        if exhibition := result.scalar_one_or_none():
            return exhibition
        raise HTTPException(404, "Exhibition not found")

    async def create_exhibition(self, data: ExhibitionBase, image: UploadFile, author_id: Optional[int] = None) -> Exhibition:
        # Generate slug and check uniqueness
        slug = slugify(data.title)
        if await self._is_slug_exists(slug):
            raise HTTPException(400, "Slug already exists")

        # Process image
        filename = await self._save_image(image)
        
        # Create exhibition
        exhibition = Exhibition(
            **data.dict(exclude={'image'}),
            slug=slug,
            image=f"/picture/{filename}",
            created_at=datetime.now(timezone.utc),
            published_at=datetime.now(timezone.utc) 
            if data.is_published else None,
            author_id=author_id
        )
        
        self.db.add(exhibition)
        await self.db.flush()
        return exhibition

    async def update_exhibition(
        self, 
        identifier: int | str, 
        data: ExhibitionBase, 
        image: Optional[UploadFile]
    ) -> Exhibition:
        # Get existing exhibition
        if isinstance(identifier, int):
            exhibition = await self.get_exhibition_by_id(identifier)
        else:
            exhibition = await self.get_exhibition_by_slug(identifier)

        # Update image if provided
        if image:
            await self._delete_old_image(exhibition.image)
            filename = await self._save_image(image)
            exhibition.image = f"/picture/{filename}"

        # Update other fields
        exhibition.title = data.title
        exhibition.description = data.description
        exhibition.is_published = data.is_published
        exhibition.slug = slugify(data.title) if data.title else exhibition.slug
        
        # Update publication date
        if data.is_published and not exhibition.published_at:
            exhibition.published_at = datetime.now(timezone.utc)
        elif not data.is_published:
            exhibition.published_at = None

        await self.db.flush()
        return exhibition

    async def delete_exhibition(self, exhibition_id: int) -> None:
        exhibition = await self.get_exhibition_by_id(exhibition_id)
        await self.db.delete(exhibition)
        await self._delete_old_image(exhibition.image)

    # Helpers
    async def _is_slug_exists(self, slug: str) -> bool:
        result = await self.db.execute(
            select(Exhibition).where(Exhibition.slug == slug))
        return result.scalar_one_or_none() is not None

    async def _save_image(self, image: UploadFile) -> str:
        file_ext = image.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = self.media_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(await image.read())
            
        return filename

    async def _delete_old_image(self, image_path: str) -> None:
        if not image_path:
            return
        filename = image_path.split('/')[-1]
        file_path = self.media_dir / filename
        if file_path.exists():
            file_path.unlink()
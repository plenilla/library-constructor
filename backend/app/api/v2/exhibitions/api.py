# routers.py
from fastapi import APIRouter, Depends, UploadFile, Form, Request
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .services import ExhibitionService
from ....core import get_db, MEDIA_DIR
from .schemas import (
    ExhibitionBase,
    ExhibitionResponse,
    PaginatedResponse,
    ExhibitionOut
)
from ....models import Exhibition

router = APIRouter()

@router.get("/exhibitions/", response_model=list[ExhibitionResponse])
async def get_all_exhibitions(
    published: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    service = ExhibitionService(db, MEDIA_DIR)
    return await service.get_all_exhibitions(published)

@router.get("/exhibitionsPage/", response_model=PaginatedResponse[ExhibitionResponse])
async def get_page_exhibition(
    published: Optional[bool] = None,
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    service = ExhibitionService(db, MEDIA_DIR)
    return await service.get_paginated_exhibitions(
        published=published,
        page=page,
        size=size,
        search=search,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/exhibitions/{identifier}", response_model=ExhibitionOut)
async def get_exhibition(
    identifier: str | int,
    db: AsyncSession = Depends(get_db)
):
    service = ExhibitionService(db, MEDIA_DIR)
    try:
        if isinstance(identifier, int) or identifier.isdigit():
            return await service.get_exhibition_by_id(int(identifier))
        return await service.get_exhibition_by_slug(identifier)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/exhibitions/", response_model=ExhibitionOut)
async def create_exhibition(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    is_published: bool = Form(False),
    image: UploadFile = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user_id = request.session.get("user_id")
    author_id = int(user_id) if user_id else None
    
    service = ExhibitionService(db, MEDIA_DIR)
    try:
        data = ExhibitionBase(
            title=title,
            description=description,
            is_published=is_published
        )
        exhibition = await service.create_exhibition(data, image, author_id)
        await db.commit()
        
        stmt = (
            select(Exhibition)
            .options(
                selectinload(Exhibition.sections),
                selectinload(Exhibition.author)
            )
            .where(Exhibition.id == exhibition.id)
        )
        result = await db.execute(stmt)
        exhibition = result.scalar_one()  
        return exhibition
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))

@router.put("/exhibitions/{identifier}", response_model=ExhibitionOut)
async def update_exhibition(
    identifier: int,
    title: str = Form(...),
    description: str = Form(...),
    is_published: bool = Form(False),
    image: Optional[UploadFile] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    service = ExhibitionService(db, MEDIA_DIR)
    try:
        data = ExhibitionBase(
            title=title,
            description=description,
            is_published=is_published
        )
        exhibition = await service.update_exhibition(identifier, data, image)
        await db.commit()
        return exhibition
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))

@router.delete("/exhibitions/{exhibition_id}")
async def delete_exhibition(
    exhibition_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ExhibitionService(db, MEDIA_DIR)
    try:
        await service.delete_exhibition(exhibition_id)
        await db.commit()
        return {"message": "Exhibition deleted successfully"}
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))
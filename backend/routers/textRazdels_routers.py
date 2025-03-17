from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select
from core.models import (
    TextArray,
)
from schemas.razdels_schemas import (
    TextArrayResponse,
    TextArrayBase
    )
from core.models.db_helper import get_db


router = APIRouter()

@router.get("/textForcontent/", response_model=List[TextArrayResponse])
async def get_all_sections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TextArray))
    sections = result.scalars().all()
    return sections

# Ручка для создания текстовго поля
@router.post("/textForcontent/", response_model=TextArrayResponse)
async def create_text(text: TextArrayBase, db: AsyncSession = Depends(get_db)):
    new_text = TextArray(text_data = text.text_data)
    db.add(new_text)
    await db.commit()
    await db.refresh(new_text)
    return(new_text)

@router.put("/textForcontent/{text_id}", response_model=TextArrayResponse)
async def update_text(text_id: int, text: TextArrayBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TextArray).where(TextArray.id == text_id))
    db_text_update = result.scalars().first()
    
    for field, value in text.model_dump().items():
        setattr(db_text_update, field, value)
        
    await db.commit()
    await db.refresh(db_text_update)
    return db_text_update


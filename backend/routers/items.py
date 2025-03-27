from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from core.models import Item
from schemas.items import ItemResponse, ItemBase
from core.models.db_helper import get_db

router = APIRouter()


@router.get("/", response_model=list[ItemResponse])
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemBase, db: AsyncSession = Depends(get_db)):
    new_item = Item(**item.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalars().first()  # Извлекаем первый результат
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int, item_updated: ItemBase, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item_updated.name
    db_item.description = item_updated.description
    db_item.color = item_updated.color
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", response_model=ItemResponse)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalars().first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(db_item)
    await db.commit()
    return db_item

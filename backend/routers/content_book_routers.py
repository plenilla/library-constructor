from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import UploadFile, File, Form
from pathlib import Path
from typing import Optional
import uuid
from sqlalchemy import select
from core.models import (
    Book,
)
from schemas.razdels_schemas import (
    BookResponse,
    )
from core.models.db_helper import get_db

"""вот эта часть далась мне трудно, поэтому не я описал этот код"""

router = APIRouter()

MEDIA_DIR = Path("picture").resolve()
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.get("/books/", response_model=List[BookResponse])
async def get_all_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book))
    sections = result.scalars().all()
    return sections

# Ручка для создания книги
@router.post("/books/", response_model=BookResponse)
async def create_book(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    bo: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Валидация файла
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid image format")
    
    file_content = await image.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    await image.seek(0)
    
    # Генерация имени файла
    file_ext = image.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = MEDIA_DIR / filename
    
    # Сохранение файла
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(500, f"Failed to save image: {str(e)}")
    
    # Создание записи в БД
    new_book = Book(
        title=title,
        description=description,
        bo=bo,
        image=f"/picture/{filename}"
    )
    
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book
    


@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    if not book:
        raise HTTPException(404, "Book not found")
    
    # Удаление изображения
    filename = book.image.split("/")[-1]
    file_path = MEDIA_DIR / filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(500, f"Failed to delete image: {str(e)}")
    
    await db.delete(book)
    await db.commit()
    return {"status": "success"}
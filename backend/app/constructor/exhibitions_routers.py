from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from typing import Optional, List
import uuid


from ...core.models import (
    Book,
    get_db,
    Section,
    Content,
    TextArray,
    Exhibition,
)
from ..constructor.exhibitions_schemas import (
    BookResponse,
    SectionResponse,
    SectionBase,
    TextArrayResponse,
    TextArrayBase,
    ContentResponse,
    ContentBase,
    ExhibitionBase,
    ExhibitionResponse,
)


router = APIRouter()


"""Ручки для взаимодействия с выставками"""


@router.get("/exhibitions/", response_model=List[ExhibitionResponse])
async def get_all_exhibition(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех выставок.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[ExhibitionResponse]: Список всех выставок.
    """
    result = await db.execute(select(Exhibition))
    exhibition = result.scalars().all()
    return exhibition


@router.post("/exhibitions/", response_model=ExhibitionResponse)
async def create_new_exhibition(
    exhibition_data: ExhibitionBase, db: AsyncSession = Depends(get_db)
):
    """
    Создать новую выставку.

    Args:
        exhibition_data (ExhibitionBase): Данные для создания выставки.
        db (AsyncSession): Сессия базы данных.

    Returns:
        ExhibitionResponse: Созданная выставка.
    """
    new_exhibition = Exhibition(**exhibition_data.model_dump())
    db.add(new_exhibition)
    await db.commit()
    await db.refresh(new_exhibition)
    return new_exhibition


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
        .options(selectinload(Exhibition.sections).selectinload(Section.contents))
    )
    exhibition = result.scalars().first()

    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    await db.delete(exhibition)
    await db.commit()

    return {"message": "Exhibition and all related sections and contents deleted"}


"""Ручки для взаимодействия с разделами"""


@router.get("/sections/", response_model=List[SectionResponse])
async def get_all_sections(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех разделов.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[SectionResponse]: Список всех разделов.
    """
    result = await db.execute(select(Section))
    sections = result.scalars().all()
    return sections


@router.post("/sections/", response_model=SectionResponse)
async def create_section(section_data: SectionBase, db: AsyncSession = Depends(get_db)):
    """
    Создать новый раздел.

    Args:
        section_data (SectionBase): Данные для создания раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        SectionResponse: Созданный раздел.
    """
    new_section = Section(title=section_data.title)
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    print("New Section ID:", new_section.id)
    return new_section


@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int, section_update: SectionBase, db: AsyncSession = Depends(get_db)
):
    """
    Обновить существующий раздел.

    Args:
        section_id (int): ID раздела.
        section_update (SectionBase): Данные для обновления раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        SectionResponse: Обновленный раздел.
    """
    result = await db.execute(select(Section).where(Section.id == section_id))
    db_update_section = result.scalars().first()
    if not db_update_section:
        raise HTTPException(status_code=404, detail="section not found")

    # Обновляем атрибуты модели вместо замены объекта
    for field, value in section_update.model_dump().items():
        setattr(db_update_section, field, value)

    await db.commit()
    await db.refresh(db_update_section)
    return db_update_section


@router.delete("/sections/{section_id}", response_model=SectionResponse)
async def update_section(section_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить раздел по ID.

    Args:
        section_id (int): ID раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        SectionResponse: Удаленный раздел.
    """
    result = await db.execute(select(Section).where(Section.id == section_id))
    db_delete_section = result.scalars().first()
    if not db_delete_section:
        raise HTTPException(status_code=404, detail="section not found")

    await db.delete(db_delete_section)
    await db.commit()
    return db_delete_section


"""Ручка для взаимодействия с книгой и его обложкой"""

MEDIA_DIR = Path("../frontend/static/picture").resolve()
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
    db: AsyncSession = Depends(get_db),
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
        title=title, description=description, bo=bo, image=f"/picture/{filename}"
    )

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


@router.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
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


""" Ручка для взаимодействия с текстом """


@router.get("/textForcontent/", response_model=List[TextArrayResponse])
async def get_all_sections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TextArray))
    sections = result.scalars().all()
    return sections


# Ручка для создания текстовго поля
@router.post("/textForcontent/", response_model=TextArrayResponse)
async def create_text(text: TextArrayBase, db: AsyncSession = Depends(get_db)):
    new_text = TextArray(text_data=text.text_data)
    db.add(new_text)
    await db.commit()
    await db.refresh(new_text)
    return new_text


@router.put("/textForcontent/{text_id}", response_model=TextArrayResponse)
async def update_text(
    text_id: int, text: TextArrayBase, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TextArray).where(TextArray.id == text_id))
    db_text_update = result.scalars().first()

    for field, value in text.model_dump().items():
        setattr(db_text_update, field, value)

    await db.commit()
    await db.refresh(db_text_update)
    return db_text_update


""" Ручка для взаимодействия связывающего раздел и текст """


# ручка для создания контента, связывающее раздел и текст
@router.post("/contents/", response_model=ContentResponse)
async def create_content(content: ContentBase, db: AsyncSession = Depends(get_db)):
    new_content = Content(
        section_id=content.section_id,
        text_id=content.text_id,
        books_id=content.books_id,
    )
    db.add(new_content)
    await db.commit()
    await db.refresh(new_content)
    return new_content


# Получение всех записей контента
@router.get("/contents/", response_model=List[ContentResponse])
async def get_contents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content))
    contents = result.scalars().all()
    return contents


@router.put("/contents/{contents_id}", response_model=ContentResponse)
async def update_content(
    content_id: int, content_update: ContentBase, db: AsyncSession = Depends(get_db)
):
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
        text = await db.execute(
            select(TextArray).filter(TextArray.id == content.text_id)
        )
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

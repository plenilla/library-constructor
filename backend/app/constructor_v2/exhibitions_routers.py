from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File, Form
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from starlette.status import HTTP_404_NOT_FOUND
import aiofiles

from ..img import MEDIA_DIR, ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from ...core.models import (
    ContentBlock,
    Book,
    get_db,
    Section,
    Exhibition,
)
from ..constructor_v2.exhibitions_schemas import (
    SectionResponse,
    ExhibitionBase,
    ExhibitionResponse,
    SectionCreate,
    ContentBlockCreate,
    ContentBlockResponse,
    BookCreate,
    BookResponse,
)


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


"""Ручки для взаимодействия с разделами"""


@router.post("/exhibitions/{exhibition_id}/sections/", response_model=SectionResponse)
async def create_section(
    exhibition_id: int,
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    exhibition = result.scalar_one_or_none()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Выставка не найдена")

    
    # Получаем максимальное значение order в секции
    max_order_result = await db.execute(
        select(func.max(Section.order)).where(Section.exhibition_id == exhibition_id)
    )
    max_order = max_order_result.scalar() or 0

    # Если order не задан — автоустанавливаем
    if section_data.order is None:
        section_data.order = max_order + 1
    else:
        # Проверяем, не занят ли такой order в секции
        existing_order = await db.execute(
            select(Exhibition).where(
                Section.id == exhibition_id,
                Section.order == section_data.order
            )
        )
        if existing_order.scalar():
            raise HTTPException(status_code=400, detail="Порядковый номер уже занят в этой секции")
        
    
    section = Section(
        title=section_data.title,
        order=section_data.order,
        exhibition_id=exhibition_id,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


@router.post("/sections/{section_id}/content/", response_model=ContentBlockResponse)
async def create_content_block(
    section_id: int,
    content_data: ContentBlockCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли секция
    result = await db.execute(select(Section).where(Section.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Секция не найдена")

    # Получаем максимальное значение order в секции
    max_order_result = await db.execute(
        select(func.max(ContentBlock.order)).where(ContentBlock.section_id == section_id)
    )
    max_order = max_order_result.scalar() or 0

    # Если order не задан — автоустанавливаем
    if content_data.order is None:
        content_data.order = max_order + 1
    else:
        # Проверяем, не занят ли такой order в секции
        existing_order = await db.execute(
            select(ContentBlock).where(
                ContentBlock.section_id == section_id,
                ContentBlock.order == content_data.order
            )
        )
        if existing_order.scalar():
            raise HTTPException(status_code=400, detail="Порядковый номер уже занят в этой секции")

    content_block = ContentBlock(
        section_id=section_id,
        type=content_data.type,
        order=content_data.order,
        text_content=content_data.text_content,
        book_id=content_data.book_id,
    )
    db.add(content_block)
    await db.commit()
    await db.refresh(content_block)
    return content_block

@router.get("/exhibitions/{exhibition_id}/sections/", response_model=List[SectionResponse])
async def get_exhibition_sections(
    exhibition_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем наличие выставки с указанным ID
    result = await db.execute(select(Exhibition).where(Exhibition.id == exhibition_id))
    exhibition = result.scalar_one_or_none()
    if exhibition is None:
        raise HTTPException(status_code=404, detail="Выставка не найдена")
    
    result_sections = await db.execute(
        select(Section)
        .where(Section.exhibition_id == exhibition_id)
        .order_by(Section.order.asc())
    )
    sections = result_sections.scalars().all()
    return sections


@router.get("/sections/{section_id}", response_model=SectionResponse)
async def get_section(section_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить конкретный раздел по ID с вложенными контент-блоками.
    
    Args:
        section_id (int): Идентификатор раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        SectionResponse: Раздел с данными и вложенными контент-блоками.
    """
    result = await db.execute(
        select(Section)
        .where(Section.id == section_id)
        .options(selectinload(Section.content_blocks))
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Section not found")
    return section


@router.get("/sections/{section_id}/content/", response_model=List[ContentBlockResponse])
async def get_section_content(section_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить список контент-блоков для конкретного раздела.

    Args:
        section_id (int): Идентификатор раздела.
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[ContentBlockResponse]: Список контент-блоков раздела.
    """
    # Проверяем существование раздела (при необходимости)
    result = await db.execute(select(Section).where(Section.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Section not found")

    # Выбираем все контент-блоки раздела
    result = await db.execute(
        select(ContentBlock).where(ContentBlock.section_id == section_id)
    )
    content_blocks = result.scalars().all()
    return content_blocks


@router.get("/content/{content_id}", response_model=ContentBlockResponse)
async def get_content_block(content_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить отдельный контент-блок по его ID.
    
    Args:
        content_id (int): Идентификатор контент-блока.
        db (AsyncSession): Сессия базы данных.

    Returns:
        ContentBlockResponse: Данные контент-блока.
    """
    result = await db.execute(select(ContentBlock).where(ContentBlock.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Content block not found")
    return content

'''Взаимодействие с книгой'''


@router.get("/books/", response_model=List[BookResponse])
async def get_all_books(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех книг.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[BookResponse]: Список всех книг.
    """
    result = await db.execute(select(Book))
    sections = result.scalars().all()
    return sections


# Ручка для создания книги
@router.post("/books/", response_model=BookResponse)
async def create_book(book_data: BookCreate = Depends(BookCreate.as_form), db: AsyncSession = Depends(get_db)):
    """
    Создать новую книгу

    Args:
        db (AsyncSession): Сессия базы данных.
        title: Форма названия книги
        description: Необезательная форма описания книги
        bo: Форма библиографиеского описания книги
        image: Форма загрузки изображения для книги

    Returns:
        BookResponse: Созданная книга
    """
    # Чтение файла изображения
    file_content = await book_data.image_url.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    # Важно: сбросить позицию курсора файла для возможного повторного чтения
    await book_data.image_url.seek(0)

    # Генерация уникального имени файла
    file_ext = book_data.image_url.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = MEDIA_DIR / filename

    # Сохранение файла (можно использовать асинхронное сохранение с aiofiles)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(file_content)
    except Exception as e:
        raise HTTPException(500, f"Failed to save image: {str(e)}")

    # Создание записи в БД
    new_book = Book(
        title=book_data.title, 
        annotations=book_data.annotations, 
        library_description=book_data.library_description, 
        image_url=f"/picture/{filename}"
    )

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


@router.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаление книги по ID

    Args:
        db (AsyncSession): Сессия базы данных.
        book_id(int): ID книги.

    Returns:
        dict: Сообщение об успешном удалении.
    """
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
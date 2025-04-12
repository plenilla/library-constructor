from certifi import where
from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from starlette.status import HTTP_404_NOT_FOUND

from ..img import MEDIA_DIR, ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from ...core.models import (
    Book,
    get_db,
    Section,
    Content,
    TextArray,
    Exhibition,
)
from ..constructor_v1.exhibitions_schemas import (
    BookResponse,
    SectionResponse,
    SectionBase,
    TextArrayResponse,
    TextArrayBase,
    ContentResponse,
    ContentBase,
    ExhibitionBase,
    ExhibitionResponse,
    ContentUpdate,
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
    Получить список всех выставок.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[ExhibitionResponse]: Список всех выставок.
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
        .options(selectinload(Exhibition.sections).selectinload(Section.contents))
    )
    exhibition = result.scalars().first()

    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    await db.delete(exhibition)
    await db.commit()

    return {"message": "Exhibition and all related sections and contents deleted"}


"""Ручки для взаимодействия с разделами"""


@router.get(
    "/exhibitions/{exhibition_id}/sections/", response_model=List[SectionResponse]
)
async def get_all_sections(exhibition_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить список всех разделов.

    Args:
        db (AsyncSession): Сессия базы данных.
        exhibition_id (int): ID выставки
    Returns:
        List[SectionResponse]: Список всех разделов.
    """
    result = await db.execute(
        select(Section).where(Section.exhibition_id == exhibition_id)
    )
    sections = result.scalars().all()
    return sections


@router.post("/exhibitions/{exhibition_id}/sections/", response_model=SectionResponse)
async def create_section(
    section_data: SectionBase, exhibition_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Создать новый раздел.

    Args:
        section_data (SectionBase): Данные для создания раздела.
        db (AsyncSession): Сессия базы данных.
        exhibition_id (int): ID выставки

    Returns:
        SectionResponse: Созданный раздел.
    """
    exhibition = await db.get(Exhibition, exhibition_id)
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    new_section = Section(title=section_data.title, exhibition_id=exhibition_id)
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    print("New Section ID:", new_section.id)
    return new_section


@router.put(
    "/exhibitions/{exhibition_id}/sections/{section_id}", response_model=SectionResponse
)
async def update_section(
    section_id: int,
    exhibition_id: int,
    section_update: SectionBase,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить существующий раздел.

    Args:
        section_id (int): ID раздела.
        section_update (SectionBase): Данные для обновления раздела.
        db (AsyncSession): Сессия базы данных.
        exhibition_id (int): ID выставки

    Returns:
        SectionResponse: Обновленный раздел.
    """
    result = await db.execute(
        select(Section)
        .where(Section.id == section_id)
        .where(Section.exhibition_id == exhibition_id)
    )

    db_update_section = result.scalars().first()
    if not db_update_section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="section not found")

    # Обновляем атрибуты модели вместо замены объекта
    for field, value in section_update.model_dump().items():
        setattr(db_update_section, field, value)

    await db.commit()
    await db.refresh(db_update_section)
    return db_update_section


@router.delete("/exhibitions/{exhibition_id}/sections/{section_id}")
async def delete_section(section_id: int, exhibition_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить раздел по ID.

    Args:
        section_id (int): ID раздела.
        db (AsyncSession): Сессия базы данных.
        exhibition_id (int): ID выставки

    Returns:
        SectionResponse: Удаленный раздел.
    """
    result = await db.execute(
        select(Section)
        .where(Section.id == section_id)
        .where(Section.exhibition_id == exhibition_id)
    )

    db_delete_section = result.scalars().first()

    if not db_delete_section:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="section not found")

    await db.delete(db_delete_section)
    await db.commit()
    return db_delete_section


"""Ручка для взаимодействия с книгой и его обложкой"""


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
async def create_book(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    bo: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
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


""" Ручка для взаимодействия с текстом """


@router.get("/textForcontent/", response_model=List[TextArrayResponse])
async def get_all_sections(db: AsyncSession = Depends(get_db)):
    """
    Получение списка текста контента

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        List[TextArrayResponse]: Вывод текста контента
    """
    result = await db.execute(select(TextArray))
    sections = result.scalars().all()
    return sections


# Ручка для создания текстовго поля
@router.post("/textForcontent/", response_model=TextArrayResponse)
async def create_text(text: TextArrayBase, db: AsyncSession = Depends(get_db)):
    """
    Создания текста для контента

    Args:
        db (AsyncSession): Сессия базы данных.
        text (TextArrayBase): Данные для создания текст раздела
    Returns:
        TextArrayResponse: Созданный текст для контента
    """
    new_text = TextArray(text_data=text.text_data)
    db.add(new_text)
    await db.commit()
    await db.refresh(new_text)
    return new_text


@router.put("/textForcontent/{text_id}", response_model=TextArrayResponse)
async def update_text(
    text_id: int, text: TextArrayBase, db: AsyncSession = Depends(get_db)
):
    """
    Обновление текста контента по ID

    Args:
        db (AsyncSession): Сессия базы данных.
        text (TextArrayBase): Данные для создания текста контента
        text_id (int): ID текст раздела
    Returns:
        TextArrayResponse: Вывод обновленного текста из контента
    """
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
    """
    Обновление текста контента по ID

    Args:
        db (AsyncSession): Сессия базы данных.
        content (ContentBase): Данные для создания книги
    Returns:
        ContentResponse: Вывод обновленного текста контента
    """
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
    """
    Получить список всех контентов

    Args:
        db (AsyncSession): Сессия базы данных.
    Returns:
        List[ContentResponse]: Вывод списка всех контентов
    """
    result = await db.execute(select(Content))
    contents = result.scalars().all()
    return contents


@router.put("/contents/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_update: ContentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление содержимого (текста или книги) по ID.

    Args:
        content_id (int): ID содержимого.
        content_update (ContentUpdate): Обновлённые данные (тип и поля).
        db (AsyncSession): Сессия базы данных.

    Returns:
        Обновлённый Content с вложенными объектами.
    """
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalars().first()

    if not content:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Content not found")

    if content_update.type == "text":
        # Обновляем или создаём TextArray
        if content.text_id:
            result = await db.execute(
                select(TextArray).where(TextArray.id == content.text_id)
            )
            text = result.scalars().first()
            text.text_data = content_update.text_data
        else:
            new_text = TextArray(text_data=content_update.text_data)
            db.add(new_text)
            await db.flush()  # Получаем ID
            content.text_id = new_text.id
            content.books_id = None

    elif content_update.type == "book":
        if content.books_id:
            result = await db.execute(select(Book).where(Book.id == content.books_id))
            book = result.scalars().first()
            book.title = content_update.title
            book.description = content_update.description
            book.image = content_update.image
        else:
            new_book = Book(
                title=content_update.title,
                description=content_update.description,
                image=content_update.image,
            )
            db.add(new_book)
            await db.flush()
            content.books_id = new_book.id
            content.text_id = None

    await db.commit()
    await db.refresh(content)

    return content


@router.delete("/contents/{content_id}")
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаление контента по ID.

    Args:
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Сообщение об успешном удалении.
    """
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
    

            

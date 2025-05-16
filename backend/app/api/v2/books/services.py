from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from pathlib import Path
from typing import List, Optional
import uuid
import aiofiles
from fastapi import HTTPException, UploadFile
from ....models import Book, Author, Genre, ContentBlock
from .schemas import BookCreate
  

class BooksFondsService:
    def __init__(self, db: AsyncSession, media_dir: Path, max_file_size: int):
        self.db = db
        self.media_dir = media_dir
        self.max_file_size = max_file_size


    async def get_filtered_books(
        self,
        search: Optional[str] = None,
        author_id: Optional[List[int]] = None,
        genre_id: Optional[List[int]] = None,
        sort_order: Optional[str] = None
    ) -> List[Book]:
        query = select(Book).options(
            selectinload(Book.authors),
            selectinload(Book.genres)
        )

        if search:
            query = query.filter(Book.title.ilike(f"%{search}%"))
    
    
    async def get_book(self, book_id: int) -> Optional[Book]:
        # Загружаем книгу с опциями selectinload для authors и genres
        stmt = (
            select(Book)
            .options(
                selectinload(Book.authors),
                selectinload(Book.genres),
            )
            .where(Book.id == book_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered_books(
        self,
        author_id: Optional[List[int]],
        genre_id: Optional[List[int]],
        sort_order: Optional[str]
    ) -> List[Book]:
        query = select(Book).options(
            selectinload(Book.authors),
            selectinload(Book.genres)
        )

        if author_id:
            query = query.filter(Book.authors.any(Author.id.in_(author_id)))
        
        if genre_id:
            query = query.filter(Book.genres.any(Genre.id.in_(genre_id)))
        
        if sort_order == "asc":
            query = query.order_by(Book.title.asc())
        elif sort_order == "desc":
            query = query.order_by(Book.title.desc())

        result = await self.db.execute(query)
        return result.scalars().unique().all()


    async def create_book(self, book_data: BookCreate) -> Book:
        try:
            # Чтение и проверка файла
            file_content = await book_data.image_url.read()
            if len(file_content) > self.max_file_size:
                raise HTTPException(status_code=413, detail="File too large")
            await book_data.image_url.seek(0)

            # Получаем авторов и жанры
            authors = [await self._get_author_by_id(aid) for aid in book_data.author_ids]
            genres = [await self._get_genre_by_id(gid) for gid in book_data.genre_ids]

            # Сохраняем изображение
            file_ext = book_data.image_url.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = self.media_dir / filename
            
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_content)

            # Создаем книгу
            new_book = Book(
                title=book_data.title,
                annotations=book_data.annotations,
                library_description=book_data.library_description,
                image_url=f"/static/picture/{filename}",
                year_of_publication=book_data.year_of_publication,
                authors=authors,
                genres=genres,
            )

            self.db.add(new_book)
            await self.db.flush()

            # Возвращаем полный объект с отношениями
            result = await self.db.execute(
                select(Book)
                .options(selectinload(Book.authors), selectinload(Book.genres))
                .where(Book.id == new_book.id)
            )
            return result.scalar_one()
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Internal server error: {str(e)}")

    async def delete_book(self, book_id: int) -> None:
        # Находим книгу с зависимостями
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.content_blocks))
            .where(Book.id == book_id)
        )
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(404, "Book not found")

        # Удаляем контент-блоки
        for block in book.content_blocks:
            await self.db.delete(block)

        # Удаляем изображение
        if book.image_url:
            filename = book.image_url.split("/")[-1]
            file_path = self.media_dir / filename
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                raise HTTPException(500, f"Failed to delete image: {str(e)}")

        await self.db.delete(book)

    async def search_authors(self, query: str) -> List[Author]:
        result = await self.db.execute(
            select(Author).where(Author.name.ilike(f"%{query}%"))
        )
        return result.scalars().all()

    async def search_genres(self, query: str) -> List[Genre]:
        result = await self.db.execute(
            select(Genre).where(Genre.name.ilike(f"%{query}%"))
        )
        return result.scalars().all()

    async def get_authors(self) -> List[Author]:
        result = await self.db.execute(select(Author))
        return result.scalars().all()

    async def get_genres(self) -> List[Genre]:
        result = await self.db.execute(select(Genre))
        return result.scalars().all()

    # Вспомогательные методы
    async def _get_author_by_id(self, author_id: int) -> Author:
        result = await self.db.execute(select(Author).where(Author.id == author_id))
        author = result.scalar_one_or_none()
        if not author:
            raise HTTPException(400, detail=f"Author {author_id} not found")
        return author

    async def _get_genre_by_id(self, genre_id: int) -> Genre:
        result = await self.db.execute(select(Genre).where(Genre.id == genre_id))
        genre = result.scalar_one_or_none()
        if not genre:
            raise HTTPException(400, detail=f"Genre {genre_id} not found")
        return genre



class BooksContentService:
    def __init__(self, db: AsyncSession, media_dir: Path, max_file_size: int):
        self.db = db
        self.media_dir = media_dir
        self.max_file_size = max_file_size
        
    async def get_content_books(self, content_id: int) -> List[Book]:
        # Проверяем существование контент-блока
        content = await self._get_content_block(content_id)
        if not content or content.type != "book":
            raise HTTPException(404, "Content block not found")
            
        # Получаем все книги (оригинальная логика из роутера)
        result = await self.db.execute(select(Book))
        return result.scalars().all()

    async def unlink_book_from_content(self, content_id: int, book_id: int) -> None:
        content_block = await self._get_linked_content_block(content_id, book_id)
        
        if not content_block:
            raise HTTPException(404, "Content block not found or not linked to this book")

        await self.db.delete(content_block)

    async def get_linked_book(self, content_id: int, book_id: int) -> Book:
        # Проверяем привязку
        content = await self._get_content_block(content_id, book_id)
        if not content:
            raise HTTPException(404, "Content block not found or not linked to this book")

        # Получаем книгу
        book = await self._get_book_by_id(book_id)
        return book

    # Вспомогательные методы
    async def _get_content_block(self, content_id: int, book_id: int = None) -> ContentBlock:
        query = select(ContentBlock).where(ContentBlock.id == content_id)
        
        if book_id:
            query = query.where(ContentBlock.book_id == book_id)
            
        query = query.where(ContentBlock.type == "book")

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_book_by_id(self, book_id: int) -> Book:
        result = await self.db.execute(
            select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(404, "Book not found")
        return book
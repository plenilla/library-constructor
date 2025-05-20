from __future__ import annotations
from typing import Optional, List, Literal, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field, validator
from pydantic.generics import GenericModel
from fastapi import UploadFile, Form, File
from datetime import datetime
from ....models import User
from ....core import ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from ..sections.schemas import SectionResponse


class ExhibitionResponse(BaseModel):
    id: int
    sections: List["SectionResponse"] = []
    title: str
    slug: str
    description: Optional[str]
    is_published: bool
    image: str
    created_at: datetime
    published_at: Optional[datetime] = None
    author: str
    model_config = ConfigDict(from_attributes=True)
    
    @validator('author', pre=True)
    def set_author(cls, author_obj):
        if author_obj and author_obj.fullname:
            return author_obj.fullname
        return "Аноним"


T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int
    total_pages: int

class ExhibitionBase(BaseModel):
    title: str
    is_published: bool
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @field_validator("image")
    def validate_image(cls, v: UploadFile):
        if v is None:
            return v
            
        # Проверка MIME-типа
        if v.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"Недопустимый формат: {v.content_type}")
        
        # Получение реального размера файла
        v.file.seek(0, 2)  # Перемещаем указатель в конец файла
        file_size = v.file.tell()
        v.file.seek(0)  # Возвращаем указатель в начало
        
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"Файл слишком большой: {file_size/1024/1024:.2f} MB")
        
        return v

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        is_published: bool = Form(False),
        image: Optional[UploadFile] = File(None),
    ):
        return cls(
            title=title,
            description=description,
            is_published=is_published,
            image=image,
        )

class ExhibitionOut(BaseModel):
    id: int
    sections: List["SectionResponse"] = []
    title: str
    slug: str
    description: Optional[str]
    is_published: bool
    image: str
    author: str
    created_at: datetime
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
    
    @validator('author', pre=True)
    def set_author(cls, author_obj):
        if author_obj and author_obj.fullname:
            return author_obj.fullname
        return "Аноним"
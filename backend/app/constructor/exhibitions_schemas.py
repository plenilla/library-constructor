from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from fastapi import UploadFile, Form, File
from datetime import datetime

from .img import ALLOWED_MIME_TYPES, MAX_FILE_SIZE


class ExhibitionBase(BaseModel):
    title: str
    is_published: bool
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @field_validator('image')
    def validate_image(cls, v: UploadFile):
        if v is None:
            return v
        if v.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError('Invalid image format')
        if v.size > MAX_FILE_SIZE:
            raise ValueError('Image too large')
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



class ExhibitionResponse(BaseModel):
    id: int
    sections: List["SectionResponse"] = []
    title: str
    description: Optional[str]
    is_published: bool
    image: str
    created_at: datetime
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    bo: Optional[str] = None


class BookResponse(BookBase):
    id: int
    image: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SectionBase(BaseModel):
    title: str


class TextArrayBase(BaseModel):
    text_data: str


class ContentBase(BaseModel):
    section_id: int
    text_id: Optional[int] = None
    books_id: Optional[int] = None


class TextArrayResponse(TextArrayBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SectionResponse(SectionBase):
    id: int
    contents: List["ContentResponse"] = []
    model_config = ConfigDict(from_attributes=True)


class ContentResponse(ContentBase):
    id: int
    section: Optional["SectionResponse"] = None
    text_data: Optional[TextArrayResponse] = None
    books: Optional[BookResponse] = None
    model_config = ConfigDict(from_attributes=True)


# Перестраиваем модели для разрешения циклических зависимостей
SectionResponse.model_rebuild()
ContentResponse.model_rebuild()

from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field
from fastapi import UploadFile, Form, File
from datetime import datetime

from ..img import ALLOWED_MIME_TYPES, MAX_FILE_SIZE

class ExhibitionBase(BaseModel):
    title: str
    is_published: bool
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @field_validator("image")
    def validate_image(cls, v: UploadFile):
        if v is None:
            return v
        if v.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError("Invalid image format")
        if v.size > MAX_FILE_SIZE:
            raise ValueError("Image too large")
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


class SectionCreate(BaseModel):
    title: str
    order: Optional[int] = Field(
        default=None,
        examples=[None],
        description="что то"
        )
    

class SectionResponse(BaseModel):
    id: int
    title: str
    order: int
    content_blocks: List["ContentBlockResponse"] = []

    model_config = ConfigDict(from_attributes=True)

class ContentBlockCreate(BaseModel):
    text_content: Optional[str] = None
    book_id: Optional[int] = None
    order: Optional[int] = Field(
        default=None,
        examples=[None],
        description="что то"
        )
    
    type: Optional[Literal["text", "book"]] = None

    
    @model_validator(mode="before")
    def infer_type_and_cleanup(cls, values: dict) -> dict:
        book_id = values.get("book_id")
        text_content = values.get("text_content")

        if book_id:
            values["type"] = "book"
            values["text_content"] = None  # очищаем
        else:
            values["type"] = "text"
            values["book_id"] = None  # очищаем

        return values

    @field_validator("text_content")
    def validate_text(cls, v: Optional[str], info) -> Optional[str]:
        inferred_type = info.data.get("type")
        if inferred_type == "text" and not v:
            raise ValueError("Поле text_content обязательно для блока с типом 'text'")
        return v

    @field_validator("book_id")
    def validate_book(cls, v: Optional[int], info) -> Optional[int]:
        inferred_type = info.data.get("type")
        if inferred_type == "book" and not v:
            raise ValueError("Поле book_id обязательно для блока с типом 'book'")
        return v


class ContentBlockResponse(BaseModel):
    id: int
    type: str
    text_content: Optional[str]
    order: int
    book_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BaseModel):
    title: str
    annotations: Optional[str] = None
    library_description: Optional[str] = None
    image_url: UploadFile
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator("image_url")
    def validate_image(cls, image_url: UploadFile) -> UploadFile:
        if image_url.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError("Invalid image format")
        return image_url

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        annotations: Optional[str] = Form(None),
        library_description: Optional[str] = Form(None),
        image_url: UploadFile = File(...),
    ):
        return cls(title=title, annotations=annotations, library_description=library_description, image_url=image_url)

class BookResponse(BaseModel):
    id: int
    title: str
    annotations: Optional[str]
    library_description: Optional[str]
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
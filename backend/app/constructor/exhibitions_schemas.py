from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ExhibitionBase(BaseModel):
    title: str
    is_published: bool = False


class ExhibitionResponse(ExhibitionBase):
    id: int
    sections: List["SectionResponse"] = []
    
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

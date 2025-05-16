from __future__ import annotations
from typing import Optional, Literal, List
from pydantic import BaseModel, ConfigDict, model_validator 
from ..books.schemas import BookResponse

class ContentBlockResponse(BaseModel):
    id: int
    type: str
    text_content: Optional[str]
    book_id: Optional[int]
    book: Optional[BookResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ContentBlockCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: Literal["text", "book"]
    text_content: Optional[str] = None
    book_id:      Optional[int] = None

    @model_validator(mode="after")
    def check_consistency(self):
        if self.type == "text":
            if self.book_id is not None:
                raise ValueError("book_id must be null for text type")
            if not self.text_content:
                raise ValueError("text_content required")
        elif self.type == "book":
            if self.text_content is not None:
                raise ValueError("text_content must be null for book type")
            if self.book_id is None:
                raise ValueError("book_id required")
        return self


class ContentBlockUpdate(BaseModel):
    type: Optional[Literal["text", "book"]] = None
    text_content: Optional[str] = None
    book_id: Optional[int] = None

    @model_validator(mode='after')
    def check_consistency(self):
        if self.type == "text":
            if self.book_id is not None:
                raise ValueError("book_id must be null for text type")
            if not self.text_content:
                raise ValueError("text_content required")
        elif self.type == "book":
            if self.text_content is not None:
                raise ValueError("text_content must be null for book type")
            if self.book_id is None:
                raise ValueError("book_id required")
        return self

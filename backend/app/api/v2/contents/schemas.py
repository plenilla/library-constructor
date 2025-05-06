from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field


class ContentBlockResponse(BaseModel):
    id: int
    type: str
    text_content: Optional[str]
    order: int
    book_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class ContentBlockCreate(BaseModel):
    text_content: Optional[str] = None
    book_id: Optional[int] = None
    order: Optional[int] = Field(default=None, examples=[None], description="что то")

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

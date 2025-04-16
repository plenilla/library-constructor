from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field
from fastapi import UploadFile, Form, File
from datetime import datetime

from ...img import ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from .sections import SectionResponse


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




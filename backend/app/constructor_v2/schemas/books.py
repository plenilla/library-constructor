from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from fastapi import UploadFile, Form, File

from ...img import ALLOWED_MIME_TYPES


class BookResponse(BaseModel):
    id: int
    title: str
    annotations: Optional[str]
    library_description: Optional[str]
    image_url: Optional[str]

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



from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from fastapi import UploadFile, Form, File
import json 
from fastapi.exceptions import HTTPException

from ....core import ALLOWED_MIME_TYPES

class AuthorResponse(BaseModel):
    id: int
    name: str

class GenreResponse(BaseModel):
    id: int
    name: str

class BookResponse(BaseModel):
    id: int
    title: str
    annotations: Optional[str]
    library_description: Optional[str]
    image_url: Optional[str]
    year_of_publication: Optional[str]
    authors: List[AuthorResponse]
    genres: List[GenreResponse]
    
    model_config = ConfigDict(from_attributes=True)

class BookCreate(BaseModel):
    title: str
    annotations: Optional[str] = None
    library_description: Optional[str] = None
    image_url: UploadFile
    year_of_publication: Optional[str] = None
    genre_ids: List[int]
    author_ids: List[int]

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
        year_of_publication: Optional[str] = Form(None),
        image_url: UploadFile = File(...),
        genre_ids: str = Form(...),  
        author_ids: str = Form(...), 
    ):
        try:
            # Преобразуем строки в списки целых чисел
            genre_ids_list = [int(x.strip()) for x in genre_ids.split(",")]
            author_ids_list = [int(x.strip()) for x in author_ids.split(",")]
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ID format: {str(e)}")

        return cls(
            title=title,
            annotations=annotations,
            library_description=library_description,
            year_of_publication=year_of_publication,
            image_url=image_url,
            genre_ids=genre_ids_list,
            author_ids=author_ids_list,
        )
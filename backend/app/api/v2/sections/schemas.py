from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from ..contents.schemas import ContentBlockResponse


class SectionResponse(BaseModel):
    id: int
    title: str
    content_blocks: List["ContentBlockResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class SectionCreate(BaseModel):
    title: str

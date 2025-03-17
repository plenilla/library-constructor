from pydantic import BaseModel, ConfigDict
from typing import Optional

# Базовая модель с общими полями
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

class ItemResponse(ItemBase):
    id: int

    class Config:
        config = ConfigDict(from_attributes=True)
from sqlalchemy import (
    Text,
    Column,
)
from sqlalchemy.orm import relationship
from ..core import Base


class Book(Base):
    title = Column(Text, nullable=False)
    annotations = Column(Text)
    library_description = Column(Text)
    image_url = Column(Text)
    # СВязь
    content_blocks = relationship(
        "ContentBlock",
        back_populates="book",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


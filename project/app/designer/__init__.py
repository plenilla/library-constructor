__all__ = (
    "contents_router",
    "exhibitions_router",
    "sections_router",
)

from .contents.api import router as contents_router
from .exhibitions.api import router as exhibitions_router
from .sections.api import router as sections_router
